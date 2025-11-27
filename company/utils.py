# --- Python Standard Library & Django Core ---
import base64
import numpy as np
import cv2 
from datetime import timedelta, date, datetime
from django.utils import timezone
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# --- Third-Party ---
import face_recognition


from .models import Attendance, WorkShift, PublicHoliday, WeeklyHoliday,LeaveApplication
from users.enums import LeaveStatus # Import necessary Enums

# Assuming serializers and helper functions are in the same directory or accessible via local import:
from .serializers import AutomaticAttendanceInputSerializer 


def format_duration(duration):
    """ Converts timedelta duration to HH:MM string, showing '00:00' for zero/None. """
    if duration is None or duration.total_seconds() <= 0:
        return '00:00'
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    # Handle negative durations (for Deficiency calculation)
    sign = '-' if duration.total_seconds() < 0 else ''
    return f"{sign}{abs(hours):02d}:{abs(minutes):02d}"
def determine_attendance_date(punch_dt, work_shift, local_tz):
    """
    [FIXED/MISSING FUNCTION] Determines the correct attendance date for a given punch_dt, 
    especially handling night shifts.
    """
    
    punch_dt_local = punch_dt.astimezone(local_tz)
    punch_date = punch_dt_local.date()
    
    # 1. Check for Night Shift (Shift ends earlier than it starts, e.g., 22:00 -> 06:00)
    if work_shift.end_time < work_shift.start_time:
        
        # Calculate Shift Start DT for 'Today' (the day the punch occurred)
        shift_start_dt_today_naive = datetime.combine(punch_date, work_shift.start_time)
        shift_start_dt_today_local = timezone.make_aware(shift_start_dt_today_naive, timezone=local_tz)

        # If punch time is BEFORE the shift started today (e.g., 04:00 AM on Tue, for a shift that started Mon 22:00), 
        # it belongs to the previous day's shift (which started yesterday).
        if punch_dt_local < shift_start_dt_today_local:
            return punch_date - timedelta(days=1)
            
        # Otherwise, the punch belongs to today's shift (which started today).
        return punch_date

    # 2. Regular Day Shift
    return punch_date


def calculate_attendance_status_and_times(attendance_record, employee_profile):
    """  Calculates derived attendance fields (duration, is_late, overtime_duration). """
    punch_in = attendance_record.punch_in_time
    punch_out = attendance_record.punch_out_time
    work_shift = employee_profile.work_shift
    
    total_work_duration = None
    is_late_calculated = False
    late_duration = timedelta(0) 
    overtime_duration = timedelta(0)

    # Only calculate if a work shift is available and punch in exists
    if work_shift and punch_in:

        local_tz = timezone.get_current_timezone() 
        
        # Get the reliable date from the local-converted PUNCH IN time (Used for Late calculation)
        comparison_date = punch_in.astimezone(local_tz).date() 

        # --- Late Calculation (Independent of Punch Out) ---
        late_count_time = work_shift.late_count_time
        if late_count_time:
            late_count_dt_naive = datetime.combine(comparison_date, late_count_time) 
            late_count_dt_local = timezone.make_aware(late_count_dt_naive, timezone=local_tz)
            
            punch_in_local = punch_in.astimezone(local_tz)
            
            if punch_in_local > late_count_dt_local:
                is_late_calculated = True
                duration_diff = punch_in_local - late_count_dt_local
                late_duration = max(timedelta(0), duration_diff) 

        # --- Duration and Overtime Calculation (Requires Punch Out) ---
        if punch_out and punch_out > punch_in:
            total_work_duration = punch_out - punch_in
            
            shift_start_time = work_shift.start_time
            shift_end_time = work_shift.end_time
            ot_delay_minutes = getattr(work_shift, 'ot_start_delay_minutes', 0)
            
            # 1. Shift End Date Calculation (NIGHT SHIFT FIX) 🚀
            
            # Start with the Punch In Date
            shift_end_date = punch_in.astimezone(local_tz).date()
            
            # Check for Night Shift: If Shift End Time is EARLIER than Shift Start Time, add one day.
            if shift_end_time < shift_start_time:
                shift_end_date += timedelta(days=1)
                
            # 2. Shift End DT Creation using the CORRECTED date
            shift_end_dt_naive = datetime.combine(shift_end_date, shift_end_time) 
            shift_end_dt_local = timezone.make_aware(shift_end_dt_naive, timezone=local_tz)
            
            # 3. Calculate Actual OT Start Time (Shift End + Delay)
            actual_ot_start_dt_local = shift_end_dt_local + timedelta(minutes=ot_delay_minutes)
            
            # 4. Punch-out time ko Local Timezone mein convert karein
            punch_out_local = punch_out.astimezone(local_tz)
            
            # 5. Compare punch_out with Actual OT Start Time
            if punch_out_local > actual_ot_start_dt_local:
                 duration_diff = punch_out_local - actual_ot_start_dt_local
                 overtime_duration = max(timedelta(0), duration_diff)

    return total_work_duration, is_late_calculated, late_duration, overtime_duration
    # [End of calculate_attendance_status_and_times body]

def get_expected_working_dates_list(from_date, to_date):
    """ 
    [NEW HELPER] Returns a list of dates between the range that are NOT a Weekly or Public Holiday. 
    This list is used to generate the report table rows.
    """
    
    weekly_offs = set(
        WeeklyHoliday.objects.filter(is_active=True).values_list('day', flat=True)
    )
    public_holiday_dates = set()
    holidays = PublicHoliday.objects.filter(
        start_date__lte=to_date,
        end_date__gte=from_date
    )
    
    # Populate public_holiday_dates set
    for holiday in holidays:
        current_date = holiday.start_date
        while current_date <= holiday.end_date and current_date <= to_date:
            if current_date >= from_date:
                public_holiday_dates.add(current_date)
            current_date += timedelta(days=1)

    expected_working_dates = []
    current_date = from_date
    while current_date <= to_date:
        is_weekly_off = current_date.strftime('%A') in weekly_offs
        is_public_holiday = current_date in public_holiday_dates
        
        # Only include the date if it's NOT a weekly off AND NOT a public holiday
        if not is_weekly_off and not is_public_holiday:
            expected_working_dates.append(current_date)
            
        current_date += timedelta(days=1)
        
    return expected_working_dates



def calculate_summary_stats(records, expected_working_dates, employee_profile, from_date, to_date):
    """ 
    Aggregates attendance records and calculates all summary metrics, 
    including accurate Total Leave count.
    """
    
    # --- 1. Base Counts and Duration Aggregation (UNCHANGED) ---
    attendance_summary = records.aggregate(
        total_work_duration_sum=Sum('total_work_duration'),
        overtime_duration_sum=Sum('overtime_duration'),
        late_duration_sum=Sum('late_duration'),
    )
    
    present_records = records.filter(is_present=True)
    total_present = present_records.count()
    total_late = present_records.filter(is_late=True).count()
    
    actual_work_duration = attendance_summary.get('total_work_duration_sum') or timedelta(0)
    overtime_duration = attendance_summary.get('overtime_duration_sum') or timedelta(0)
    total_late_duration = attendance_summary.get('late_duration_sum') or timedelta(0)
    
    # --- 2. Expected Working Days (Total Rows in the Report) (UNCHANGED) ---
    total_working_days = len(expected_working_dates)
    
    # --- 3. Expected Hours Calculation (UNCHANGED) ---
    expected_shift_duration = timedelta(0) 
    if employee_profile and employee_profile.work_shift:
        shift = employee_profile.work_shift
        start_dt = datetime.combine(date.min, shift.start_time)
        end_dt = datetime.combine(date.min, shift.end_time)
        if shift.end_time < shift.start_time:
            end_dt += timedelta(days=1) 
        expected_shift_duration = end_dt - start_dt

    expected_working_duration = expected_shift_duration * total_present
    

    
    approved_leaves_sum = LeaveApplication.objects.filter(
        employee=employee_profile.user,
        status=LeaveStatus.APPROVED,
        from_date__lte=to_date,
        to_date__gte=from_date
    ).aggregate(
        total_approved_days=Sum('number_of_days')
    )
    

    total_leave = approved_leaves_sum.get('total_approved_days') or 0.0

    total_absence = total_working_days - total_present - total_leave
    
    deficiency = expected_working_duration - actual_work_duration
    
    return {
        "Total Working Days": total_working_days,
        "Total Present": total_present,
        "Total Absence": max(0, total_absence),
        "Total Leave": total_leave, # Now correct
        "Total Late": total_late,
        "Total Late Time": format_duration(total_late_duration),
        "Expected Working Hour": format_duration(expected_working_duration),
        "Actual Working Hour": format_duration(actual_work_duration),
        "Over Time": format_duration(overtime_duration),
        "Deficiency": format_duration(deficiency),
    }






# Helper function (Assuming this is defined in attendance/utils.py or above the view)

def apply_auto_close_if_needed(attendance_record, employee_profile):
    """
    If Punch IN exists and Punch OUT is missing, calculate and set Punch OUT 
    to the WorkShift End Time.
    Returns True if auto-closed, False otherwise.
    """
    if (employee_profile.work_shift and 
        attendance_record.punch_in_time and 
        not attendance_record.punch_out_time):
        
        shift = employee_profile.work_shift
        local_tz = timezone.get_current_timezone()
        
        # Determine the date of the PUNCH IN for comparison
        punch_in_date = attendance_record.punch_in_time.astimezone(local_tz).date()

        # 1. Start DT at Punch IN Date
        shift_end_dt_naive = datetime.combine(punch_in_date, shift.end_time) 
        
        # 2. Handle Night Shift: If Shift End Time is EARLIER than Shift Start Time, add one day.
        if shift.end_time < shift.start_time:
            shift_end_dt_naive += timedelta(days=1)
            
        # 3. Convert to timezone aware
        auto_close_dt = timezone.make_aware(shift_end_dt_naive, timezone=local_tz)
        
        # 4. Apply the calculated Punch OUT time
        attendance_record.punch_out_time = auto_close_dt
        attendance_record.status = 'Auto-Closed' # Flag the record
        
        return True
    
    return False


def deserialize_face_encoding(encoding_list):
    """ Converts a list of floats (from Profile.face_encoding JSONField) 
        back into a NumPy array for use with face_recognition.compare_faces. 
    """
    if not encoding_list or not isinstance(encoding_list, list): return None
    try: return np.array(encoding_list)
    except: return None