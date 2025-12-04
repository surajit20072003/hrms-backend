from rest_framework import serializers
from .models import Department,Designation,Branch,Warning ,Termination,Promotion,Holiday,WeeklyHoliday,LeaveType,EarnLeaveRule,PublicHoliday,LeaveApplication,WorkShift,LeaveBalance,\
Allowance,Deduction,MonthlyPayGrade,PayGradeAllowance,PayGradeDeduction,HourlyPayGrade,PerformanceCategory,PerformanceCriteria,PerformanceRating,EmployeePerformance,JobPost,TrainingType,\
EmployeeTraining,Award,Notice,LateDeductionRule,TaxRule,PaySlip,PaySlipDetail,BonusSetting,EmployeeBonus
from users.models import User, Profile, Education, Experience,Role,AccountDetails
from users.enums import JobStatus,LeaveStatus,SlabChoices
from django.db.models import Sum
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import face_recognition
import numpy as np
import base64
import cv2
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime

from django.core.files.base import ContentFile


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__' 

class DesignationSerializer(serializers.ModelSerializer):
    # Response me department ka naam bhi dikhayenge
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Designation
        # 'id' aur 'name' read/write hain, 'department' sirf write ke liye hai
        fields = ['id', 'name', 'department', 'department_name']
        extra_kwargs = {
            'department': {'write_only': True}
        }

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institute', 'degree', 'board', 'result', 'gpa', 'passing_year']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'organization', 'designation', 'duration', 'skill', 'responsibility']
        
class AccountDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetails
        fields = ['id', 'account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'branch_name', 'account_type', 'is_primary']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new User and their related Profile object,
    including face encoding upon enrollment.
    """
    # ... (All existing fields like email, password, role, work_shift, etc.) ...
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True, required=True)
    work_shift = serializers.PrimaryKeyRelatedField(queryset=WorkShift.objects.all(), allow_null=True, required=False)
    monthly_pay_grade = serializers.PrimaryKeyRelatedField(queryset=MonthlyPayGrade.objects.all(), allow_null=True, required=False)
    hourly_pay_grade = serializers.PrimaryKeyRelatedField(queryset=HourlyPayGrade.objects.all(), allow_null=True, required=False)
    
    # Optional field for Base64 input
    face_image_base64 = serializers.CharField(
        write_only=True, 
        required=False, 
        allow_null=True,
        help_text="Base64 string of the employee's profile photo."
    )

    class Meta:
        model = Profile
        fields = [
            'email', 'password', 'role', 'first_name', 'last_name', 'phone', 
            # ... (other profile fields) ...
            'employee_id', 'department', 'designation', 'branch', 'supervisor',
            'date_of_joining', 'date_of_leaving', 'status', 'monthly_pay_grade',
            'hourly_pay_grade', 'emergency_contact', 'work_shift',
            'face_image_base64', # Base64 input
            'photo' # Django FileField input (Form Data)
        ]

    def validate(self, data):
        # ... (Existing validation logic for Email Uniqueness and Pay Grade) ...
        return data

    
    # --- Helper 1: Encoding from Form Data (File Object) ---
    def _calculate_encoding_from_file(self, photo_file):
        """Reads a Django File object, checks for a single face, and calculates encoding."""
        try:
            # Read the file content into memory
            photo_file.seek(0) 
            img_bytes = photo_file.read() 
            img_array = np.frombuffer(img_bytes, np.uint8)
            
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if image is None:
                raise serializers.ValidationError({"photo": "Invalid image file format or corrupt file."})
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_image)

            if not encodings:
                raise serializers.ValidationError({"photo": "No face detected in the uploaded photo."})
            
            if len(encodings) > 1:
                raise serializers.ValidationError({"photo": "Multiple faces detected. Please upload a clear single-face photo."})

            return encodings[0].tolist()
            
        except serializers.ValidationError:
            raise
        except Exception as e:
            print(f"File encoding error: {e}")
            raise serializers.ValidationError({"photo": "An error occurred during face processing from file upload."})

    
    # --- Helper 2: Encoding from Base64 String ---
    def _calculate_face_encoding(self, base64_data, employee_id):
        """Helper to decode Base64 image, check for single face, and calculate encoding."""
        try:
            img_data = base64.b64decode(base64_data)
            img_array = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise serializers.ValidationError({"face_image_base64": "Invalid Base64 image format."})
                
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_image)

            if not encodings:
                raise serializers.ValidationError({"face_image_base64": "No face detected in the image."})
            if len(encodings) > 1:
                raise serializers.ValidationError({"face_image_base64": "Multiple faces detected in Base64 image."})

            # Create Django File object to save the photo (since Base64 was the input)
            file_name = f"{employee_id}_enrollment.jpg"
            photo_file = ContentFile(img_data, name=file_name) 

            return encodings[0].tolist(), photo_file
            
        except serializers.ValidationError:
            raise
        except Exception as e:
            print(f"Base64 processing error: {e}")
            raise serializers.ValidationError({"face_image_base64": "An error occurred during Base64 face processing."})

            
    @transaction.atomic
    def create(self, validated_data):
        
        # Step 0: Separate User data & Image inputs
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        role_instance = validated_data.pop('role')
        
        face_image_base64 = validated_data.pop('face_image_base64', None)
        photo_file_upload = validated_data.get('photo', None) # File object from Form Data
        
        face_encoding = None

        # Step 1: Calculate Face Encoding (Handle both input types)
        
        if photo_file_upload:
            # Path A: File Upload (Form Data)
            face_encoding = self._calculate_encoding_from_file(photo_file_upload)
            
        elif face_image_base64:
            # Path B: Base64 String Input
            employee_id = validated_data.get('employee_id', 'new_employee')
            face_encoding, photo_file = self._calculate_face_encoding(face_image_base64, employee_id)
            
            # Since input was Base64, we must save the generated file to the 'photo' field
            validated_data['photo'] = photo_file 


        # Step 2: Set Encoding Field
        if face_encoding is not None:
            validated_data['face_encoding'] = face_encoding
        else:
            # Agar koi bhi photo input nahi tha, toh encoding field null rahega (optional enrollment)
            validated_data['face_encoding'] = None
        
        # Step 3: Create User
        user_fields = {
            'email': email,
            'password': password,
            'role': role_instance,
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
        }
        user_obj = User.objects.create_user(**user_fields)
        
        # Step 4: Create Profile
        profile = Profile.objects.create(user=user_obj, **validated_data)
        
        return profile



class EmployeeListSerializer(serializers.ModelSerializer):
    # Get related fields from other models
    name = serializers.SerializerMethodField()
    # 💥 FIX APPLIED: Role name is read from the linked Role object
    role = serializers.CharField(source='user.role.name', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    designation = serializers.CharField(source='designation.name', read_only=True, allow_null=True)
    branch = serializers.CharField(source='branch.name', read_only=True, allow_null=True)
    pay_grade = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user_id',
            'photo',
            'name',
            'role',
            'department',
            'designation',
            'branch',
            'phone',
            'employee_id', 
            'pay_grade',
            'date_of_joining',
            'status',
            'job_status',
            'work_shift',
            'face_encoding'
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_pay_grade(self, obj):
        if obj.monthly_pay_grade:
            return f"{obj.monthly_pay_grade} (Monthly)"
        if obj.hourly_pay_grade:
            return f"{obj.hourly_pay_grade} (Hourly)"
        return "N/A"


class EmployeeDetailSerializer(serializers.ModelSerializer):
    # --- User Data (Display/Update) ---
    email = serializers.EmailField(source='user.email')
    
    
    role_name = serializers.CharField(source='user.role.name', read_only=True)
    
    # 💥 FIX APPLIED (Write): Allow role to be updated by ID
    role_id = serializers.PrimaryKeyRelatedField(
        source='user.role', # This links to the user.role field (the FK object)
        queryset=Role.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    # --- Nested Read-Only Data (Assuming these exist) ---
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    account_details = AccountDetailsSerializer(many=True, read_only=True)
    
    # Work Shift Handling (UNCHANGED)
    work_shift = serializers.PrimaryKeyRelatedField( 
        queryset=WorkShift.objects.all(), 
        allow_null=True, 
        required=False
    )
    work_shift_name = serializers.CharField(source='work_shift.name', read_only=True)

    # Pay Grade Handling (UNCHANGED)
    monthly_pay_grade = serializers.PrimaryKeyRelatedField(
        queryset=MonthlyPayGrade.objects.all(), allow_null=True, required=False
    )
    monthly_pay_grade_name = serializers.CharField(source='monthly_pay_grade.grade_name', read_only=True)
    hourly_pay_grade = serializers.PrimaryKeyRelatedField(
        queryset=HourlyPayGrade.objects.all(), allow_null=True, required=False
    )
    hourly_pay_grade_rate = serializers.CharField(source='hourly_pay_grade.hourly_rate', read_only=True)


    class Meta:
        model = Profile
        exclude = ['user']
        

    def update(self, instance, validated_data):
    
        user_data = validated_data.pop('user', {})
        
        # New email and role will be in user_data
        new_email = user_data.get('email')
        new_role_instance = user_data.get('role')
        
        user = instance.user
        
        # Update email
        if new_email is not None:
            user.email = new_email
            
        # Update role (if provided via role_id field)
        if new_role_instance is not None:
            user.role = new_role_instance
            
        user.save()
        
        # 2. Handle Profile update 
        updated_instance = super().update(instance, validated_data) 

        return updated_instance


class WarningSerializer(serializers.ModelSerializer):
    # For displaying names instead of IDs in GET requests
    employee_name = serializers.CharField(source='warning_to.profile.full_name', read_only=True)
    warning_by_name = serializers.CharField(source='warning_by.profile.full_name', read_only=True)

    class Meta:
        model = Warning
        fields = [
            'id', 
            'warning_to',         # Used for creating (takes user ID)
            'employee_name',      # Used for displaying
            'warning_by',         # Used for creating (takes user ID)
            'warning_by_name',    # Used for displaying
            'warning_type', 
            'subject', 
            'warning_date', 
            'description'
        ]
        # Make these fields write-only so they are only used for input
        extra_kwargs = {
            'warning_to': {'write_only': True},
            'warning_by': {'write_only': True},
        }
class TerminationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='terminate_to.profile.full_name', read_only=True, allow_null=True)
    terminated_by_name = serializers.CharField(source='terminate_by.profile.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Termination
        fields = [
            'id',
            'terminate_to',
            'employee_name',
            'terminate_by',
            'terminated_by_name',
            'termination_type',
            'termination_date',
            'notice_date',
            'subject',
            'description'
        ]
        extra_kwargs = {
            'terminate_to': {'write_only': True},
            'terminate_by': {'write_only': True},
        }
class PromotionSerializer(serializers.ModelSerializer):
    # For displaying names and other details in GET requests (read-only)
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True, allow_null=True)
    promoted_department_name = serializers.CharField(source='promoted_department.name', read_only=True, allow_null=True)
    promoted_designation_name = serializers.CharField(source='promoted_designation.name', read_only=True, allow_null=True)

    class Meta:
        model = Promotion
        fields = [
            'id',
            'employee',                 # For writing (takes user ID)
            'employee_name',            # For reading
            'promotion_date',
            'current_department_name',
            'current_designation_name',
            'current_pay_grade',
            'current_salary',
            'promoted_department',      # For writing (takes department ID)
            'promoted_department_name', # For reading
            'promoted_designation',     # For writing (takes designation ID)
            'promoted_designation_name',# For reading
            'promoted_pay_grade',
            'promoted_salary',
            'description'
        ]
        # These fields are used for input (creating/updating) but not shown in the output list
        extra_kwargs = {
            'employee': {'write_only': True},
            'promoted_department': {'write_only': True},
            'promoted_designation': {'write_only': True},
        }



class EmployeeJobStatusSerializer(serializers.ModelSerializer):
    # This field will only accept valid choices from your JobStatus enum
    job_status = serializers.ChoiceField(choices=JobStatus.choices)

    class Meta:
        model = Profile
        fields = ['job_status']


class HolidaySerializer(serializers.ModelSerializer):
    """ Serializer for the Holiday names master list. """
    class Meta:
        model = Holiday
        fields = '__all__'

class PublicHolidaySerializer(serializers.ModelSerializer):
    """ Serializer for assigning dates to a holiday. """
    # For displaying the holiday name in GET responses
    name = serializers.CharField(source='holiday.name', read_only=True)

    class Meta:
        model = PublicHoliday
        fields = ['id', 'holiday', 'name', 'start_date', 'end_date', 'comment']
        extra_kwargs = {
            # For creation (POST), we only need the holiday ID
            'holiday': {'write_only': True}
        }

class WeeklyHolidaySerializer(serializers.ModelSerializer):
    """ Serializer for weekly holidays. """
    class Meta:
        model = WeeklyHoliday
        fields = '__all__'

class LeaveTypeSerializer(serializers.ModelSerializer):
    """ Serializer for different types of leave. """
    class Meta:
        model = LeaveType
        fields = '__all__'

class EarnLeaveRuleSerializer(serializers.ModelSerializer):
    """ Serializer for the earn leave configuration rule. """
    class Meta:
        model = EarnLeaveRule
        fields = '__all__'

class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    number_of_days = serializers.FloatField(read_only=True)

    class Meta:
        model = LeaveApplication
        fields = [
            'leave_type',
            'from_date',
            'to_date',
            'purpose',
            'number_of_days'
        ]

    def validate(self, data):
        employee = self.context['request'].user
        leave_type = data['leave_type']
        from_date = data['from_date']
        to_date = data['to_date']

        # Date Validation
        if from_date > to_date:
            raise serializers.ValidationError(
                {"from_date": "Start date cannot be after end date."}
            )

        requested_days = (to_date - from_date).days + 1
        data['number_of_days'] = float(requested_days)

        if requested_days <= 0:
            raise serializers.ValidationError({
                "number_of_days": "Leave days must be greater than zero."
            })

        # Fetch balance
        balance = LeaveBalance.objects.filter(
            employee=employee,
            leave_type=leave_type
        ).first()

        if not balance:
            raise serializers.ValidationError({
                "leave_type": "No leave balance assigned."
            })

        # Check enough balance exists
        if balance.available_balance < requested_days:
            raise serializers.ValidationError({
                "message": f"Not enough balance. Available: {balance.available_balance}"
            })

        return data

    def create(self, validated_data):
        return LeaveApplication.objects.create(
            **validated_data,
            status=LeaveStatus.PENDING
        )


class LeaveApplicationListSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    approved_by_name = serializers.CharField(source='approved_by.profile.full_name', read_only=True, allow_null=True)
    rejected_by_name = serializers.CharField(source='rejected_by.profile.full_name', read_only=True, allow_null=True)
    
    request_duration = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'employee_name', 'leave_type_name', 'from_date', 'to_date',
            'application_date', 'request_duration', 'number_of_days', 'status',
            'approved_by_name', 'approved_date', 'rejected_by_name', 'reject_date',
            'rejection_reason', 'purpose'
        ]
        
    def get_request_duration(self, obj):
        try:
            from_date_str = obj.from_date.strftime("%d/%m/%Y")
            to_date_str = obj.to_date.strftime("%d/%m/%Y")
            return f"{from_date_str} to {to_date_str}"
        except AttributeError:
            return "N/A"
        

class LeaveReportSerializer(serializers.Serializer):
    """ Used for filtering reports by date range and employee. """
    employee_id = serializers.IntegerField(required=False, allow_null=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, data):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({"from_date": "From Date cannot be after To Date."})
        return data
    

class WorkShiftSerializer(serializers.ModelSerializer):
    """Serializer for creating, listing, and updating work shifts."""
    class Meta:
        model = WorkShift
        fields = ['id', 'shift_name', 'start_time', 'end_time', 'late_count_time','ot_start_delay_minutes']

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Simple validation: Start time must be before End time (assuming no midnight cross-over for simplicity)
        if start_time and end_time and start_time >= end_time:
            pass 
        return data
    
class LocalDateTimeField(serializers.DateTimeField):
    """
    Custom field to accept simple YYYY-MM-DD HH:MM:SS format and localize it 
    to the system's configured timezone (IST).
    """
    # Define the simple input format
    input_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'] 

    def to_internal_value(self, value):
        if not value:
            return None
            
        # If the input already contains timezone info (e.g., T+05:30), use the default method
        if isinstance(value, str) and ('T' in value or '+' in value or 'Z' in value):
            return super().to_internal_value(value)

        # 1. Parse the simple string using the defined input_formats
        for fmt in self.input_formats:
            try:
                naive_dt = datetime.strptime(value, fmt)
                # 2. Localize it to the system's default timezone (IST in your case)
                return timezone.make_aware(naive_dt, timezone.get_current_timezone())
            except ValueError:
                continue
                
        # If all custom formats fail
        raise serializers.ValidationError(
            f"Time format must be YYYY-MM-DD HH:MM:SS or a valid ISO 8601 string."
        )   

class ManualAttendanceFilterSerializer(serializers.Serializer):
    """ Used to filter employees by department and date for GET request. """
    department_id = serializers.IntegerField(required=True)
    target_date = serializers.DateField(required=True)
    
class ManualAttendanceInputSerializer(serializers.Serializer):
    """ Used to update attendance for a single employee via PATCH request. """
    employee_id = serializers.IntegerField(required=True)
    target_date = serializers.DateField(required=True)
    punch_in_time = LocalDateTimeField(required=False, allow_null=True)
    punch_out_time = LocalDateTimeField(required=False, allow_null=True)
    is_late = serializers.BooleanField(required=False)
    is_present = serializers.BooleanField(required=False)

class AttendanceReportFilterSerializer(serializers.Serializer):
    """ Used to filter reports by date range and optionally employee_id. """
    employee_id = serializers.IntegerField(required=False, allow_null=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    
class DailyAttendanceFilterSerializer(serializers.Serializer):
    """ Specific filter for Daily Report (only date needed). """
    target_date = serializers.DateField(required=True)

class MonthlySummaryFilterSerializer(serializers.Serializer):
    """ Specific filter for Attendance Summary Report (only month needed) """
    # Month format: YYYY-MM
    month = serializers.CharField(max_length=7, required=True)

class EmployeeProfileUpdateSerializer(serializers.ModelSerializer):
    work_shift_id = serializers.IntegerField(required=False, allow_null=True) 

    class Meta:
        model = Profile
        # Add 'work_shift_id' to your fields list
        fields = ['full_name', 'designation', 'department', 'work_shift_id', 'employee_id']




class AllowanceSerializer(serializers.ModelSerializer):
    """Serializer for Allowance List, Create, Retrieve, Update, and Delete."""
    
    # Read-only field to display the full Allowance Type name
    allowance_type_display = serializers.CharField(
        source='get_allowance_type_display', 
        read_only=True
    )

    class Meta:
        model = Allowance
        fields = [
            'id', 'allowance_name', 'allowance_type', 'allowance_type_display',
            'percentage_of_basic', 'limit_per_month', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation to ensure data consistency based on allowance type.
        """
        # If type is Fixed, percentage_of_basic must represent the fixed value
        if data.get('allowance_type') == Allowance.AllowanceType.FIXED:
            
            pass
        elif data.get('allowance_type') == Allowance.AllowanceType.PERCENTAGE:
            percentage = data.get('percentage_of_basic')
            if percentage is not None and (percentage <= 0 or percentage > 100):
                raise serializers.ValidationError(
                    {"percentage_of_basic": "Percentage must be between 0.01 and 100."}
                )

        return data
    


class DeductionSerializer(serializers.ModelSerializer):
    """Serializer for Deduction List, Create, Retrieve, Update, and Delete."""
    
    # Read-only field to display the full Deduction Type name
    deduction_type_display = serializers.CharField(
        source='get_deduction_type_display', 
        read_only=True
    )

    class Meta:
        model = Deduction
        fields = [
            'id', 'deduction_name', 'deduction_type', 'deduction_type_display',
            'percentage_of_basic', 'limit_per_month', 'is_tax_exempt',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Custom validation for percentage field."""
        deduction_type = data.get('deduction_type')
        percentage = data.get('percentage_of_basic')
        
        if deduction_type == Deduction.DeductionType.PERCENTAGE:
            if percentage is not None and (percentage < 0 or percentage > 100):
                raise serializers.ValidationError(
                    {"percentage_of_basic": "Percentage must be between 0 and 100."}
                )
        return data
    

class PayGradeAllowanceSerializer(serializers.ModelSerializer):
    """
    Handles Allowance ID input (write) and displays Allowance Name/Value (read).
    The 'value' is read-only because it is calculated/fetched in the parent serializer.
    """
    allowance_name = serializers.CharField(source='allowance.allowance_name', read_only=True)
    
    class Meta:
        model = PayGradeAllowance
        # 'value' field is NOT in extra_kwargs as write_only, it will be handled by the parent serializer
        fields = ['allowance', 'allowance_name', 'value']
        extra_kwargs = {
            'allowance': {'write_only': True},
            'value': {'read_only': True} # Read-only, as we set it internally
        } 

class PayGradeDeductionSerializer(serializers.ModelSerializer):
    """Handles Deduction ID input (write) and displays Deduction Name/Value (read)."""
    deduction_name = serializers.CharField(source='deduction.deduction_name', read_only=True)
    
    class Meta:
        model = PayGradeDeduction
        fields = ['deduction', 'deduction_name', 'value']
        extra_kwargs = {
            'deduction': {'write_only': True},
            'value': {'read_only': True}
        } 




class MonthlyPayGradeSerializer(serializers.ModelSerializer):
    
    # Read nested data (For viewing output)
    allowance_details = PayGradeAllowanceSerializer(source='paygradeallowance_set', many=True, read_only=True)
    deduction_details = PayGradeDeductionSerializer(source='paygradededuction_set', many=True, read_only=True)
    
    # Write nested data (Input for M2M relationship - sirf ID bhejni hai)
    allowances_to_add = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    deductions_to_add = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)


    class Meta:
        model = MonthlyPayGrade
        fields = [
            'id', 'grade_name', 'basic_salary', 'gross_salary', 'net_salary', 
            'overtime_rate', 'is_active', 
            'allowance_details', 'deduction_details', 
            'allowances_to_add', 'deductions_to_add'
        ]
        # Gross aur Net salary ab calculated aur stored hain.
        read_only_fields = ['id', 'gross_salary', 'net_salary'] 
        # NOTE: basic_salary ab input field hai, read_only nahi.

    # --- Calculation Core Logic (Pichle response se) ---
    def calculate_salaries(self, instance, basic_salary_input):
        # ... (Calculation logic, jismein basic, allowance, deduction, aur limits ka use hota hai) ...
        # [Use the exact code block for calculate_salaries from the previous response]
        
        basic = basic_salary_input
        total_allowance = Decimal('0.00')
        total_deduction = Decimal('0.00')

        # Calculate Total Allowances
        for pga in instance.paygradeallowance_set.select_related('allowance'):
            allowance = pga.allowance
            value = pga.value
            limit = allowance.limit_per_month or Decimal('9999999.00')

            if allowance.allowance_type == 'Percentage':
                amount = (basic * value) / Decimal('100.00')
            else: # Fixed
                amount = value
            
            total_allowance += min(amount, limit)
            
        # Calculate Total Deductions
        for pgd in instance.paygradededuction_set.select_related('deduction'):
            deduction = pgd.deduction
            value = pgd.value
            limit = deduction.limit_per_month or Decimal('9999999.00')
            
            if deduction.deduction_type == 'Percentage':
                amount = (basic * value) / Decimal('100.00')
            else: # Fixed
                amount = value
            
            total_deduction += min(amount, limit)
            
        gross = basic + total_allowance
        net = gross - total_deduction
        
        return gross, net, total_allowance, total_deduction


    # --- Helper function for M2M creation/update (Fixed logic) ---
    def _create_update_m2m(self, pay_grade_instance, allowances_data, deductions_data, is_update=False):
        
        # 1. Handle Allowances
        if allowances_data is not None:
            if is_update:
                pay_grade_instance.paygradeallowance_set.all().delete()
                
            for item in allowances_data:
                # Validation check for 'allowance' key
                if 'allowance' not in item or not item['allowance']:
                    continue
                    
                # Item['allowance'] is the ID here, fetch the object
                try:
                    allowance_obj = Allowance.objects.get(pk=item['allowance'])
                except Allowance.DoesNotExist:
                    raise serializers.ValidationError(
                        {"allowances_to_add": f"Allowance ID {item['allowance']} not found."}
                    )
                
                # Logic: Fetch the default value from the Allowance object
                default_value = allowance_obj.percentage_of_basic # Default fallback
                if allowance_obj.allowance_type == Allowance.AllowanceType.FIXED:
                    # If Fixed, use limit_per_month as the PayGrade's default value
                    default_value = allowance_obj.limit_per_month or Decimal('0.00')
                
                PayGradeAllowance.objects.create(
                    pay_grade=pay_grade_instance, 
                    allowance=allowance_obj, 
                    value=default_value # Inject the default value
                )

        
        if deductions_data is not None:
            if is_update:
                pay_grade_instance.paygradededuction_set.all().delete()
                
            for item in deductions_data:
                if 'deduction' not in item or not item['deduction']:
                    continue
                try:
                    deduction_obj = Deduction.objects.get(pk=item['deduction'])
                except Deduction.DoesNotExist:
                    raise serializers.ValidationError(
                        {"deductions_to_add": f"Deduction ID {item['deduction']} not found."}
                    )
                
                # Logic: Fetch the default value from the Deduction object
                default_value = deduction_obj.percentage_of_basic # Default fallback
                if deduction_obj.deduction_type == Deduction.DeductionType.FIXED:
                    # If Fixed, use limit_per_month as the PayGrade's default value
                    default_value = deduction_obj.limit_per_month or Decimal('0.00')
                    
                PayGradeDeduction.objects.create(
                    pay_grade=pay_grade_instance, 
                    deduction=deduction_obj, 
                    value=default_value # Inject the default value
                )
    @transaction.atomic
    def save(self, **kwargs):
        
        # Separate M2M data before calling super().save()
        allowances_data = self.validated_data.pop('allowances_to_add', None)
        deductions_data = self.validated_data.pop('deductions_to_add', None)

        # 1. Main instance ko create/update karein (Basic salary aur basic fields save ho jayenge)
        # super().save() calls create() or update()
        instance = super().save(**kwargs)

        # 2. M2M (Allowances and Deductions) ko set/update karein
        is_update = bool(self.instance)
        self._create_update_m2m(instance, allowances_data, deductions_data, is_update=is_update)
        
        # 3. Final Calculation & Storage
        # Basic salary instance se ya validated_data se fetch karein
        basic_salary_for_calc = self.validated_data.get('basic_salary', instance.basic_salary) 
        
        gross, net, _, _ = self.calculate_salaries(instance, basic_salary_for_calc)
        
        # Gross aur Net ko database mein store karein
        instance.gross_salary = gross
        instance.net_salary = net
        # Sirf calculated fields ko update karein (Performance optimization)
        instance.save(update_fields=['gross_salary', 'net_salary']) 
            
        return instance
    
class HourlyPayGradeSerializer(serializers.ModelSerializer):
    """Serializer for Hourly Pay Grade CRUD."""
    
    class Meta:
        model = HourlyPayGrade
        fields = ['id', 'pay_grade_name', 'hourly_rate', 'is_active']
        read_only_fields = ['id']




class PerformanceCategorySerializer(serializers.ModelSerializer):
    """Serializer for minimal Performance Category CRUD operations."""
    
    class Meta:
        model = PerformanceCategory
        fields = ['id', 'category_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class PerformanceCriteriaSerializer(serializers.ModelSerializer):
    """Serializer for Performance Criteria CRUD operations."""
    
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    
    class Meta:
        model = PerformanceCriteria
        fields = [
            'id', 'category', 'category_name', 'criteria_name', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PerformanceRatingSerializer(serializers.ModelSerializer):
    """Handles the detail (criteria ID and rating value)."""
    # Read-only fields to display the criteria name
    criteria_name = serializers.CharField(source='criteria.criteria_name', read_only=True)
    
    class Meta:
        model = PerformanceRating
        fields = ['criteria', 'criteria_name', 'rating_value']


class EmployeePerformanceSerializer(serializers.ModelSerializer):
    # Nested Write Field: POST/PUT/PATCH input ke liye ratings ki list
    ratings_to_add = PerformanceRatingSerializer(many=True, write_only=True)
    
    # Nested Read Field: GET output ke liye ratings ki list
    ratings = PerformanceRatingSerializer( many=True, read_only=True)
    
    # Read-only fields to display employee and reviewer names
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewed_by.username', read_only=True)

    class Meta:
        model = EmployeePerformance
        fields = [
            'id', 'employee', 'employee_name', 'review_month', 'remarks', 
            'overall_rating', 'reviewed_by', 'reviewer_name', 'created_at',
            'ratings', 'ratings_to_add'
        ]
        read_only_fields = ['id', 'overall_rating', 'reviewed_by', 'created_at']

    # --- CREATE Method (Nested Saving Logic) ---
    def create(self, validated_data):
        ratings_data = validated_data.pop('ratings_to_add')
        
        # Current user ko 'reviewed_by' set karein
        validated_data['reviewed_by'] = self.context['request'].user
        
        # 1. EmployeePerformance (Header) instance create karein
        performance_review = EmployeePerformance.objects.create(**validated_data)
        
        # 2. PerformanceRating (Detail) records create karein
        ratings_list = []
        total_rating = Decimal('0.00')
        for rating_item in ratings_data:
            ratings_list.append(
                PerformanceRating(
                    performance_review=performance_review, 
                    **rating_item
                )
            )
            total_rating += rating_item['rating_value']
            
        PerformanceRating.objects.bulk_create(ratings_list)
        
        # 3. Overall rating calculate aur save karein
        if ratings_list:
            average_rating = total_rating / len(ratings_list)
            performance_review.overall_rating = average_rating
            performance_review.save(update_fields=['overall_rating'])
            
        return performance_review

    # --- UPDATE Method (Nested Update Logic - Full replacement) ---
    def update(self, instance, validated_data):
        ratings_data = validated_data.pop('ratings_to_add', None)
        
        # Header fields update karein
        instance = super().update(instance, validated_data)
        
        # Ratings update karein (Purane delete karke naye create karna)
        if ratings_data is not None:
            instance.ratings.all().delete()
            ratings_list = []
            total_rating = Decimal('0.00')
            
            for rating_item in ratings_data:
                ratings_list.append(
                    PerformanceRating(
                        performance_review=instance, 
                        **rating_item
                    )
                )
                total_rating += rating_item['rating_value']

            PerformanceRating.objects.bulk_create(ratings_list)

            # Recalculate and save overall_rating
            if ratings_list:
                instance.overall_rating = total_rating / len(ratings_list)
                instance.save(update_fields=['overall_rating'])
        
        return instance
    

class PerformanceSummarySerializer(serializers.ModelSerializer):
    """
    Serializer to display simple summary data for the Performance Summary Report.
    """
    # Employee name property se
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    ratings_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeePerformance
        fields = [
            'id', 'employee', 'employee_name', 'review_month', 'overall_rating', 
            'remarks', 'ratings_detail'
        ]
        
    def get_ratings_detail(self, obj):
        """
        Criteria, Category aur unki ratings ko list karta hai.
        """
        # Optimized query: Fetch criteria and nested category
        ratings = obj.ratings.all().select_related('criteria__category')
        
        detail_data = [
            {
                'category_name': rating.criteria.category.category_name,
                'criteria_name': rating.criteria.criteria_name,
                'rating_value': rating.rating_value
            } 
            for rating in ratings
        ]
        return detail_data
    

class JobPostSerializer(serializers.ModelSerializer):
    """
    Serializer for Job Post CRUD operations.
    """
    # 'published_by' field ko read-only rakhte hain, aur yeh field current user se set hoga
    published_by_name = serializers.CharField(source='published_by.full_name', read_only=True)
    
    class Meta:
        model = JobPost
        fields = [
            'id', 'job_title', 'job_post', 'description', 
            'status', 'job_publish_date', 'application_end_date',
            'published_by', 'published_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'published_by', 'published_by_name', 'created_at']


class TrainingTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for Training Type CRUD operations.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TrainingType
        fields = ['id', 'training_type_name', 'status', 'status_display', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmployeeTrainingSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee Training CRUD operations.
    Handles nested reading of FK names and file uploads.
    """
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    training_type_name = serializers.CharField(source='training_type.training_type_name', read_only=True)
    
    certificate_file = serializers.FileField(use_url=True, allow_null=True, required=False)
    class Meta:
        model = EmployeeTraining
        fields = [
            'id',
            'employee', 'training_type','employee_name', 'training_type_name',
            'subject', 'from_date', 'to_date', 'description', 
            'certificate_file', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AwardSerializer(serializers.ModelSerializer):
    """
    Serializer for Award CRUD operations using Enum for Award Name.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    display_award_name = serializers.CharField(source='get_award_name_display', read_only=True)
    display_month = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Award
        fields = [
            'id', 
            'award_name', 
            'employee', 'award_month', 'gift_item',
            'employee_name', 'display_award_name', 'display_month'
        ]
        read_only_fields = ['id']

    def get_display_month(self, obj):
        # Date ko Month YYYY format mein convert karna
        return obj.award_month.strftime('%B %Y')



class NoticeSerializer(serializers.ModelSerializer):
    """
    Serializer for Notice CRUD operations.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    attach_file = serializers.FileField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'description', 'publish_date', 
            'status', 
            'status_display',
            'attach_file', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LateDeductionRuleSerializer(serializers.ModelSerializer):
    """ 
    Serializer is simple because the 'status' field is already a CharField 
    with choices matching the frontend strings.
    """
    class Meta:
        model = LateDeductionRule
        fields = [
            'id', 
            'late_days_threshold', 
            'deduction_days',      
            'status'               # 'status' field ab seedhe model se aata hai
        ]
        read_only_fields = ['id']



class TaxRuleSerializer(serializers.ModelSerializer):
    """ 
    Serializer for Tax Rule Setup. Does NOT perform fixed tax calculation
    during save to avoid race conditions in bulk updates.
    """
    
    class Meta:
        model = TaxRule
        fields = [
            'id',
            'gender',
            'slab_type',
            'total_income_limit',
            'tax_rate_percentage',
            'taxable_amount_fixed', # Is field ko PUT/POST mein allow karein (ya ignore)
            'is_active',
        ]
        read_only_fields = ['id', 'taxable_amount_fixed'] # Read-only for safety

    # Custom create/update methods ki ab zaroorat nahi hai.

# Helper Serializer for Input Validation
class MonthlySalaryFilterSerializer(serializers.Serializer):
    """Input validation for Month (YYYY-MM)."""
    month = serializers.CharField(help_text="Month in YYYY-MM format.")
    
    def validate_month(self, value):
        try:
            # We store the first day of the month as the payment_month
            return datetime.strptime(value, '%Y-%m').date().replace(day=1)
        except ValueError:
            raise serializers.ValidationError("Month must be in YYYY-MM format.")

class BulkSalaryFilterSerializer(serializers.Serializer):
    """Filter serializer for bulk salary sheet generation."""
    branch_id = serializers.IntegerField(required=False, allow_null=True, help_text="Branch ID (optional)")
    department_id = serializers.IntegerField(required=False, allow_null=True, help_text="Department ID (optional)")
    designation_id = serializers.IntegerField(required=False, allow_null=True, help_text="Designation ID (optional)")
    month = serializers.CharField(required=True, help_text="Month in YYYY-MM format")
    
    def validate_month(self, value):
        try:
            return datetime.strptime(value, '%Y-%m').date().replace(day=1)
        except ValueError:
            raise serializers.ValidationError("Month must be in YYYY-MM format.")
        
# Helper Serializer for Breakdown List
class PaySlipDetailItemSerializer(serializers.ModelSerializer):
    """Individual breakdown items ke liye."""
    class Meta:
        model = PaySlipDetail
        fields = ['item_name', 'amount']
        
# Main Output Serializer for PaySlip Detail (salary03.png)
class PaySlipDetailSerializer(serializers.ModelSerializer):
    """
    Final PaySlip Detail (salary03.png) ke liye.
    """
    
    # Profile Details (Source path adjust karein agar employee.profile relation alag hai)
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True)
    department = serializers.CharField(source='employee.profile.department.name', read_only=True)
    designation = serializers.CharField(source='employee.profile.designation.name', read_only=True)
    
    per_day_salary = serializers.SerializerMethodField()
    allowance_breakdown = serializers.SerializerMethodField()
    deduction_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = PaySlip
        fields = [
            'id', 'employee_name', 'department', 'designation', 'payment_month', 
            'total_days_in_month', 
            'working_days', # Total PAID Days
            'unjustified_absence', # Total UNPAID Days
            'late_attendance_count','total_overtime_pay',      
            'total_tax_deduction',
            'basic_salary', 'total_allowances', 'total_deductions', 'gross_salary', 'net_salary',
            'per_day_salary', 'status', 'allowance_breakdown', 'deduction_breakdown'
        ]
        
    def get_per_day_salary(self, obj):
        """ Calculate Master Basic Salary per Paid Day for Pro-rata visibility. """
        pay_grade = obj.employee.profile.monthly_pay_grade
        if pay_grade and obj.total_days_in_month and obj.total_days_in_month > 0:
            # Master Basic (Ideal) ka per day rate dikhana, jiss rate par cut laga hai
            return round(pay_grade.basic_salary / obj.total_days_in_month, 2) 
        return 0.00
        
    def get_allowance_breakdown(self, obj):
        allowances = obj.details.filter(item_type='Allowance')
        return PaySlipDetailItemSerializer(allowances, many=True).data
        
    def get_deduction_breakdown(self, obj):
        # PaySlipDetail mein sabhi deductions aur cuts shamil hain
        deductions = obj.details.filter(item_type='Deduction')
        return PaySlipDetailItemSerializer(deductions, many=True).data
    





class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for the password change endpoint.
    Validates old password correctness and new password matching.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Validate new password confirmation.
        """
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords must match."}
            )
            
        # Optional: Add password complexity/length checks
        if len(new_password) < 8:
             raise serializers.ValidationError(
                {"new_password": "New password must be at least 8 characters long."}
            )
            
        return data

    def validate_old_password(self, value):
        """
        Check if the old password matches the user's current password.
        """
        user = self.context.get('request').user
        
        # Check if the provided old password matches the stored password
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
            
        return value
    




class CSVAttendanceInputSerializer(serializers.Serializer):
    """ 
    Used to validate a single row from the CSV file. 
    Fields correspond to columns in the CSV.
    """
    
    # Employee ID is the string/fingerprint ID from Profile model
    employee_id = serializers.CharField(required=True, max_length=50) 
    
    # Date must be YYYY-MM-DD
    target_date = serializers.DateField(format="%Y-%m-%d", input_formats=['%Y-%m-%d'])
    
    # Times are validated as strings (HH:MM:SS) before combining with date in the view
    punch_in_time = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=25)
    punch_out_time = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=25)
    
    def validate(self, data):
        punch_in = data.get('punch_in_time')
        punch_out = data.get('punch_out_time')

        # Custom check for time format (HH:MM:SS)
        def check_time_format(time_str):
            if time_str:
                try:
                    datetime.strptime(time_str, "%H:%M:%S")
                except ValueError:
                    return False
            return True

        if punch_in and not check_time_format(punch_in):
            raise serializers.ValidationError({"punch_in_time": "Time must be in HH:MM:SS format."})
        
        if punch_out and not check_time_format(punch_out):
            raise serializers.ValidationError({"punch_out_time": "Time must be in HH:MM:SS format."})
            
        return data
    


class RoleSerializer(serializers.ModelSerializer):
    """ Serializer for creating, listing, and managing Role objects. """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']
        read_only_fields = ['id'] 

    def validate_name(self, value):
        """ Role name should be unique (case-insensitive). """
        queryset = Role.objects.all()
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.filter(name__iexact=value).exists():
            raise serializers.ValidationError({"name": "A role with this name already exists."})
            
        return value
    
# Assuming LocalDateTimeField is defined or imported

class AutomaticAttendanceInputSerializer(serializers.Serializer):
    """
    Used to receive punch data (live image and time) from the FRS.
    
    The employee identifier is determined by the successful face match on the server, 
    so we only need the image and time for input.
    """
    
    # Live image data, typically sent as a Base64 encoded string
    live_image_base64 = serializers.CharField(
        required=True,
        help_text="Base64 encoded string of the live face photo."
    ) 
    
    # The exact time the punch occurred (validated by LocalDateTimeField)
    punch_time = LocalDateTimeField(
        required=True,
        help_text="Timezone-aware datetime string of the punch."
    ) 
    
    # Optional hint from FRS (mostly ignored by server logic but good for debugging)
    punch_type = serializers.ChoiceField(
        choices=['IN', 'OUT'], 
        required=False,
        help_text="Optional hint from FRS indicating the desired action (IN/OUT)."
    )


class BonusSettingSerializer(serializers.ModelSerializer):
    """Serializer for Bonus Setting CRUD operations"""
    
    calculate_on_display = serializers.CharField(
        source='get_calculate_on_display',
        read_only=True
    )
    
    class Meta:
        model = BonusSetting
        fields = [
            'id', 
            'festival_name', 
            'percentage_of_basic', 
            'calculate_on',
            'calculate_on_display',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_percentage_of_basic(self, value):
        """Ensure percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Percentage must be between 0 and 100.")
        return value


class EmployeeBonusSerializer(serializers.ModelSerializer):
    """Serializer for Employee Bonus records (read-only for listing)"""
    
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True)
    employee_id_number = serializers.CharField(source='employee.profile.employee_id', read_only=True)
    department = serializers.CharField(source='employee.profile.department.name', read_only=True, allow_null=True)
    
    class Meta:
        model = EmployeeBonus
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_id_number',
            'department',
            'festival_name',
            'bonus_month',
            'basic_salary',
            'gross_salary',
            'percentage',
            'calculated_on',
            'bonus_amount',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class GenerateBonusFilterSerializer(serializers.Serializer):
    """Filter serializer for bulk bonus generation"""
    
    bonus_setting_id = serializers.IntegerField(required=True, help_text="Bonus Setting ID (Festival)")
    month = serializers.CharField(required=True, help_text="Month in YYYY-MM format")
    
    # Optional filters
    branch_id = serializers.IntegerField(required=False, allow_null=True)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    designation_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_month(self, value):
        """Validate month format"""
        try:
            return datetime.strptime(value, '%Y-%m').date().replace(day=1)
        except ValueError:
            raise serializers.ValidationError("Month must be in YYYY-MM format (e.g., 2025-11).")
    
    def validate_bonus_setting_id(self, value):
        """Ensure bonus setting exists and is active"""
        try:
            bonus_setting = BonusSetting.objects.get(id=value, is_active=True)
        except BonusSetting.DoesNotExist:
            raise serializers.ValidationError("Bonus setting not found or inactive.")
        return value



class MarkPaymentPaidSerializer(serializers.Serializer):
    """Unified serializer for marking salary/bonus as paid"""
    
    payment_type = serializers.ChoiceField(
        choices=[('salary', 'Salary'), ('bonus', 'Bonus')],
        required=True,
        help_text="Type of payment: 'salary' or 'bonus'"
    )
    item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of payslip/bonus IDs to mark as paid"
    )
    payment_method = serializers.ChoiceField(
        choices=[
            ('Manual', 'Manual Payment'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash')
        ],
        required=True
    )
    payment_reference = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Transaction ID or reference number"
    )
    payment_date = serializers.DateField(
        required=False,
        help_text="Payment date (defaults to today if not provided)"
    )
    
    def validate_item_ids(self, value):
        """Ensure at least one ID is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one item ID is required.")
        return value