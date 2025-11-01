from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from users.models import Education,Experience,User,Profile
from .models import Department,Designation, Branch,Warning,Termination,Promotion,Holiday,WeeklyHoliday,LeaveType,EarnLeaveRule,PublicHoliday,LeaveApplication,LeaveBalance,WorkShift, \
Attendance,Allowance,Deduction,MonthlyPayGrade,PerformanceCategory,PerformanceCriteria,EmployeePerformance,PerformanceRating,JobPost
from .serializers import DepartmentSerializer,DesignationSerializer,EducationSerializer,EmployeeCreateSerializer,ExperienceSerializer,EmployeeListSerializer,EmployeeDetailSerializer
DepartmentSerializer, DesignationSerializer,
from django.db.models import Sum
from users.enums import LeaveStatus
from .serializers import WarningSerializer,TerminationSerializer,PromotionSerializer,EmployeeJobStatusSerializer,HolidaySerializer,PublicHolidaySerializer,EarnLeaveRuleSerializer    
from .serializers import LeaveTypeSerializer,WeeklyHolidaySerializer,LeaveApplicationListSerializer,LeaveApplicationCreateSerializer,LeaveReportSerializer,WorkShiftSerializer, \
ManualAttendanceFilterSerializer,ManualAttendanceInputSerializer,AttendanceReportFilterSerializer,DailyAttendanceFilterSerializer,MonthlySummaryFilterSerializer,\
BranchSerializer,AllowanceSerializer,DeductionSerializer,MonthlyPayGradeSerializer,HourlyPayGradeSerializer,HourlyPayGrade,PerformanceCategorySerializer,PerformanceCriteriaSerializer,\
EmployeePerformanceSerializer,PerformanceSummarySerializer,JobPostSerializer

from datetime import date
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, time
from calendar import monthrange
from django.utils import timezone
from django.db.models import Prefetch

class DepartmentListCreateView(APIView):
    """
    Departments ki list dekhein ya naya department banayein.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentDetailView(APIView):
    """
    Ek single department ko retrieve, update ya delete karein.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    def put(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        department = self.get_object(pk)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DesignationListCreateView(APIView):
    """
    Saare designations ki list dekhein ya naya designation banayein.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        designations = Designation.objects.all()
        serializer = DesignationSerializer(designations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DesignationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DesignationDetailView(APIView):
    """
    Ek single designation ko retrieve, update ya delete karein.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Designation.objects.get(pk=pk)
        except Designation.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation)
        return Response(serializer.data)

    def put(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        designation = self.get_object(pk)
        designation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class BranchListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)

    def put(self, request, pk):
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        branch = self.get_object(pk)
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class EmployeeListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        employee_profiles = Profile.objects.filter(user__role=User.Role.EMPLOYEE)
        serializer = EmployeeListSerializer(employee_profiles, many=True)
        return Response(serializer.data)

class EmployeeCreateView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailView(APIView):
    """
    Retrieve, Update or Delete an employee's profile instance.
    The update logic is fully handled by EmployeeDetailSerializer's custom update method.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Profile.objects.get(user__pk=pk, user__role=User.Role.EMPLOYEE)
        except Profile.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        profile = self.get_object(pk)
        serializer = EmployeeDetailSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        """ Update a full employee profile (User, Profile, WorkShift). """
        profile = self.get_object(pk)
        serializer = EmployeeDetailSerializer(profile, data=request.data)
        if serializer.is_valid():
            # serializer.save() calls the custom update method which handles User and WorkShift.
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """ Partially update an employee profile (User, Profile, WorkShift). """
        profile = self.get_object(pk)
        # Use partial=True for PATCH requests
        serializer = EmployeeDetailSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            # serializer.save() calls the custom update method which handles User and WorkShift.
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = self.get_object(pk)
        user_to_delete = profile.user
        user_to_delete.delete() 
        return Response({"message": "Employee deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class EmployeeEducationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, employee_pk):
        try:
            profile = Profile.objects.get(user__pk=employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = EducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeExperienceView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, employee_pk):
        try:
            profile = Profile.objects.get(user__pk=employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = ExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class WarningListCreateView(APIView):
    """
    List all warnings or create a new warning.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        warnings = Warning.objects.all()
        serializer = WarningSerializer(warnings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WarningSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WarningDetailView(APIView):
    """
    Retrieve, update or delete a warning instance.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Warning.objects.get(pk=pk)
        except Warning.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        warning = self.get_object(pk)
        serializer = WarningSerializer(warning)
        return Response(serializer.data)

    def put(self, request, pk):
        warning = self.get_object(pk)
        serializer = WarningSerializer(warning, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        warning = self.get_object(pk)
        warning.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TerminationListCreateView(APIView):
    """
    List all terminations or create a new one.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        terminations = Termination.objects.all()
        serializer = TerminationSerializer(terminations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TerminationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TerminationDetailView(APIView):
    """
    Retrieve, update or delete a termination instance.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Termination.objects.get(pk=pk)
        except Termination.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        termination = self.get_object(pk)
        serializer = TerminationSerializer(termination)
        return Response(serializer.data)

    def put(self, request, pk):
        termination = self.get_object(pk)
        serializer = TerminationSerializer(termination, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        termination = self.get_object(pk)
        termination.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PromotionListCreateView(APIView):
    """
    List all promotions or create a new promotion.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        promotions = Promotion.objects.all()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PromotionDetailView(APIView):
    """
    Retrieve, update or delete a promotion instance.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Promotion.objects.get(pk=pk)
        except Promotion.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionSerializer(promotion)
        return Response(serializer.data)

    def put(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionSerializer(promotion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        promotion = self.get_object(pk)
        promotion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmployeeJobStatusUpdateView(APIView):
    """
    Update the job_status of a specific employee (e.g., from 'Probation' to 'Permanent').
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            # Find the profile of the employee using their user ID (pk)
            profile = Profile.objects.get(user__pk=pk, user__role=User.Role.EMPLOYEE)
        except Profile.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Use the serializer to validate and update the data
        serializer = EmployeeJobStatusSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HolidayListCreateView(APIView):
    """
    Admin can list all holiday names or create a new one.
    (Corresponds to "Manage Holiday")
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        items = Holiday.objects.all()
        serializer = HolidaySerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HolidayDetailView(APIView):
    """
    Admin can retrieve, update or delete a specific holiday name.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Holiday.objects.get(pk=pk)
        except Holiday.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = HolidaySerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = HolidaySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicHolidayListCreateView(APIView):
    """
    Admin can list all public holidays with dates or create a new one.
    (Corresponds to "Public Holiday")
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        items = PublicHoliday.objects.all()
        serializer = PublicHolidaySerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PublicHolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicHolidayDetailView(APIView):
    """
    Admin can retrieve, update or delete a specific public holiday.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return PublicHoliday.objects.get(pk=pk)
        except PublicHoliday.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = PublicHolidaySerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = PublicHolidaySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WeeklyHolidayListCreateView(APIView):
    """
    Admin can list all weekly holidays or create a new one.
    (Corresponds to "Weekly Holiday")
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        items = WeeklyHoliday.objects.all()
        serializer = WeeklyHolidaySerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WeeklyHolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WeeklyHolidayDetailView(APIView):
    """
    Admin can retrieve, update or delete a specific weekly holiday.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return WeeklyHoliday.objects.get(pk=pk)
        except WeeklyHoliday.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = WeeklyHolidaySerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = WeeklyHolidaySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveTypeListCreateView(APIView):
    """
    Admin can list all leave types or create a new one.
    (MODIFIED: Auto-allocates balance to ALL active users upon creation)
    """
    permission_classes = [IsAdminUser]
    # Assuming LeaveTypeSerializer is imported

    def get(self, request):
        items = LeaveType.objects.all()
        serializer = LeaveTypeSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveTypeSerializer(data=request.data)
        if serializer.is_valid():
            # 1. Save the new LeaveType object
            new_leave_type = serializer.save()
            
            # --- START: Automatic Leave Balance Allocation for ALL active Users ---
            default_days = new_leave_type.number_of_days

            # 2. Fetch ALL active users
            all_users = User.objects.filter(is_active=True)

            # 3. Prepare records for bulk creation
            balances_to_create = []
            for user in all_users:
                # Safety check: Prevent duplicate assignment if logic runs twice
                if not LeaveBalance.objects.filter(employee=user, leave_type=new_leave_type).exists():
                    balances_to_create.append(
                        LeaveBalance(
                            employee=user,
                            leave_type=new_leave_type,
                            entitlement=default_days,
                            available_balance=default_days
                        )
                    )
            if balances_to_create:
                LeaveBalance.objects.bulk_create(balances_to_create)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LeaveTypeDetailView(APIView):
    """
    Admin can retrieve, update or delete a specific leave type.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return LeaveType.objects.get(pk=pk)
        except LeaveType.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = LeaveTypeSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = LeaveTypeSerializer(item, data=request.data)
        
        if serializer.is_valid():
            
            if 'number_of_days' in serializer.validated_data and \
               serializer.validated_data['number_of_days'] != item.number_of_days:
                
                raise serializer.ValidationError({
                    "number_of_days": "Quota (number_of_days) cannot be updated via this endpoint after creation. Use a separate balance adjustment tool."
                })
            
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EarnLeaveRuleView(APIView):
    """
    Admin can view or update the single Earn Leave Rule.
    (Corresponds to "Earn Leave Configure")
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # get_or_create ensures there's always one rule object to edit
        rule, created = EarnLeaveRule.objects.get_or_create(id=1)
        serializer = EarnLeaveRuleSerializer(rule)
        return Response(serializer.data)

    def put(self, request):
        rule, created = EarnLeaveRule.objects.get_or_create(id=1)
        serializer = EarnLeaveRuleSerializer(rule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplyForLeaveView(APIView):
    """
    GET: Employee ke liye Leave Types aur Current Balance dikhata hai (my02.png).
    POST: Leave application submit karta hai (dynamic calculation aur validation ke saath).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user
        
        # 1. 🎯 FIX: LeaveBalance table se saare balance records fetch karein
        balance_records = LeaveBalance.objects.filter(employee=employee)
        
        balance_data = []
        for record in balance_records:
            initial_entitlement = record.entitlement
            used = initial_entitlement - record.available_balance
            current_balance = record.available_balance
            
            balance_data.append({
                "leave_type_id": record.leave_type.id,
                "leave_type_name": record.leave_type.name,
                "initial_entitlement": round(initial_entitlement, 1),
                "used_days": round(used, 1),
                "current_balance": round(max(0.0, current_balance), 1)
            })
        
        # Note: Agar koi Leave Type, employee ke balance records mein nahi hai, toh woh yahaan nahi dikhega.
        
        return Response({
            "employee_name": employee.profile.full_name if hasattr(employee, 'profile') else employee.email,
            "available_leaves": balance_data
        })

    def post(self, request):
        # Context mein request pass karein taki Serializer employee ko access kar sake
        serializer =LeaveApplicationCreateSerializer (data=request.data, context={'request': request}) 
        
        if serializer.is_valid():
            # Serializer.save() calculated number_of_days ke saath save karega
            serializer.save(employee=request.user)
            
            return Response(
                {"message": "Leave application submitted successfully."}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyLeaveApplicationsView(APIView):
    """
    Logged-in employee ki saari leave applications list karta hai (my01.png).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applications = LeaveApplication.objects.filter(employee=request.user).order_by('-application_date')
        serializer = LeaveApplicationListSerializer(applications, many=True)
        return Response(serializer.data)
    

class AllLeaveApplicationsView(APIView):
    """
    Admin/Manager ke liye sabhi applications ki list dikhata hai.
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        all_applications = LeaveApplication.objects.all().order_by('-application_date')
        
        # We still need a List Serializer to format the data for the frontend table
        serializer = LeaveApplicationListSerializer(all_applications, many=True)
        
        return Response(serializer.data)


class LeaveApprovalView(APIView):
    """
    Admin/Manager endpoint to Approve or Reject a leave application (PK based).
    Includes logic to deduct balance from the LeaveBalance table upon approval.
    """
    permission_classes = [IsAdminUser]
    
    def patch(self, request, pk):
        try:
            application = LeaveApplication.objects.get(pk=pk)
        except LeaveApplication.DoesNotExist:
            return Response({"error": f"Application ID {pk} not found."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Input Data Extraction & Validation (Manual checks)
        action = request.data.get('action')
        reason = request.data.get('rejection_reason', '')
        manager = request.user
        
        valid_actions = [LeaveStatus.APPROVED, LeaveStatus.REJECTED]
        if action not in valid_actions:
            # Note: Ensure LeaveStatus values match the input (e.g., "Approved" vs "APPROVED")
            return Response({"error": f"Invalid action specified. Must be {LeaveStatus.APPROVED} or {LeaveStatus.REJECTED}."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        # Status Check: Only PENDING can be modified
        if application.status != LeaveStatus.PENDING:
            return Response(
                {"error": f"Application is already {application.status}. Only PENDING status can be modified."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == LeaveStatus.REJECTED and not reason:
            return Response({"rejection_reason": "Rejection reason is mandatory when rejecting."}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
        # 2. CORE LOGIC: Transaction and Update
        try:
            with transaction.atomic(): 
                if action == LeaveStatus.APPROVED:
                    
                    # 2.1. Fetch & Lock Leave Balance Record (Crucial for concurrency safety)
                    balance_record = LeaveBalance.objects.select_for_update().get(
                        employee=application.employee,
                        leave_type=application.leave_type
                    )
                    
                    requested_days = application.number_of_days
                    
                    # 2.2. Final Balance Check (Safety Net)
                    if balance_record.available_balance < requested_days:
                        # Transaction rollback hoga agar yahaan fail hua
                        raise Exception("Insufficient balance to approve this leave.")

                    # 2.3. DEDUCT BALANCE
                    balance_record.available_balance -= requested_days
                    balance_record.save()
                    
                    # 2.4. Update Application Status
                    application.status = LeaveStatus.APPROVED
                    application.approved_by = manager
                    application.approved_date = date.today()
                    message = "Leave application approved and balance deducted successfully."
                    
                elif action == LeaveStatus.REJECTED:
                    # No balance change on rejection
                    application.status = LeaveStatus.REJECTED
                    application.rejected_by = manager
                    application.reject_date = date.today()
                    application.rejection_reason = reason
                    message = "Leave application rejected successfully."
                
                # Save the application status change
                application.save()
                
            return Response({"message": message, "status": application.status}, status=status.HTTP_200_OK)

        except LeaveBalance.DoesNotExist:
             return Response(
                {"error": "Cannot approve. Leave Balance record not found for this employee/type."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Handle the Insufficient balance error or any other exception inside transaction
            return Response(
                {"error": str(e) if str(e) else "An unexpected error occurred during approval."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LeaveReportBaseView(APIView):
    """
    Base view for fetching leave applications based on filters (Employee, Date Range).
    """
    permission_classes = [IsAuthenticated] 
    
    def get_filtered_applications(self, request, employee_specific=False):
        """ Filters applications based on request query parameters. """
        
        serializer = LeaveReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        filters = Q()
        
        # Filter 1: Logged-in Employee (for My Leave Report)
        if employee_specific:
            filters &= Q(employee=request.user)
            
        # Filter 2: Specific Employee ID (for Admin's Report)
        elif data.get('employee_id'):
            filters &= Q(employee__id=data['employee_id'])
        
        # Filter 3: Date Range 
        if data.get('from_date'):
            filters &= Q(from_date__gte=data['from_date']) 
            
        if data.get('to_date'):
            filters &= Q(to_date__lte=data['to_date']) 
            
        
        # Fetch applications
        applications = LeaveApplication.objects.filter(filters).order_by('employee__id', 'from_date')
        
        return applications


class EmployeeLeaveReportView(LeaveReportBaseView):
    """ 1. Report: Detailed list of applications for one or all employees"""
    permission_classes = [IsAdminUser] # Admin/Manager hi is report ko dekh sakta hai
    
    def get(self, request):
        # Admin can filter by employee_id or see all
        applications = self.get_filtered_applications(request, employee_specific=False)
        
        # LeaveApplicationListSerializer detailed data format karega
        serializer = LeaveApplicationListSerializer(applications, many=True)
        
        return Response(serializer.data)


class MyLeaveReportView(LeaveReportBaseView):
    """ 2. Report: Detailed list of applications for the logged-in employee only. (re03.png) """
    permission_classes = [IsAuthenticated] # Employee khud ki report dekh sakta hai
    
    def get(self, request):
        # Employee can only see their own applications, filter based on request.user
        applications = self.get_filtered_applications(request, employee_specific=True)
        
        serializer = LeaveApplicationListSerializer(applications, many=True)
        
        return Response(serializer.data)


class LeaveSummaryReportView(APIView):
    """ 3. Report: Consolidated summary of entitlement, consumed, and balance (re02.png). """
    permission_classes = [IsAdminUser] # Admin/Manager hi Summary Report dekhte hain

    def get(self, request):
        # Admin can view summary for a specific employee
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            # UI ke liye, agar koi Employee select nahi kiya gaya toh error dena theek hai
            return Response({"error": "Employee ID is required for the Summary Report."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_employee = User.objects.get(pk=employee_id)
        except User.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        summary_records = LeaveBalance.objects.filter(employee_id=employee_id)
        
        summary_data = []
        for record in summary_records:
            initial_entitlement = record.entitlement
            consumed = initial_entitlement - record.available_balance
            current_balance = record.available_balance
            
            summary_data.append({
                "leave_type_name": record.leave_type.name,
                "Number_of_Day": initial_entitlement,  
                "Leave_Consume": round(consumed, 1), 
                "Current_Balance": round(current_balance, 1)
            })

        return Response({
            "employee_name": target_employee.profile.full_name,
            "summary_data": summary_data
        })
    

class WorkShiftListCreateAPIView(APIView):
    """
    Handles listing all shifts (GET) and creating a new shift (POST).
    """
    permission_classes = [IsAdminUser] 

    def get(self, request, *args, **kwargs):
        """ List all work shifts  """
        shifts = WorkShift.objects.all()
        serializer = WorkShiftSerializer(shifts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """ Create a new work shift """
        serializer = WorkShiftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkShiftDetailAPIView(APIView):
    """
    Handles retrieving (GET), updating (PUT/PATCH), and deleting (DELETE) a specific shift.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, pk, *args, **kwargs):
        """ Retrieve a specific shift """
        shift = get_object_or_404(WorkShift, pk=pk)
        serializer = WorkShiftSerializer(shift)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        """ Update a specific shift (Full update) """
        shift = get_object_or_404(WorkShift, pk=pk)
        serializer = WorkShiftSerializer(shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """ Delete a specific shift """
        shift = get_object_or_404(WorkShift, pk=pk)
        shift.delete()
        return Response({"message": "Work Shift deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# --- 1. Duration Formatting (HH:MM) ---
def format_duration(duration):
    """ Converts timedelta duration to HH:MM string, showing '00:00' for zero/None. """
    if duration is None or duration.total_seconds() <= 0:
        return '00:00'
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

# --- 2. Calculation Logic (Timezone Fixed) ---
def calculate_attendance_status_and_times(attendance_record, employee_profile):
    """
    Calculates derived attendance fields (duration, is_late, late_duration, overtime_duration)
    with Timezone Awareness.
    Returns: (total_work_duration, is_late, late_duration, overtime_duration)
    """
    punch_in = attendance_record.punch_in_time
    punch_out = attendance_record.punch_out_time
    attendance_date = attendance_record.attendance_date
    work_shift = employee_profile.work_shift
    
    total_work_duration = None
    is_late_calculated = False
    late_duration = timedelta(0) 
    overtime_duration = timedelta(0)

    # Only calculate if both punches and work shift are available
    if punch_in and punch_out and punch_out > punch_in and work_shift:
        total_work_duration = punch_out - punch_in
        
        # Determine the timezone to use (using punch_in's timezone)
        # Fallback to current timezone if punch_in is somehow naive
        tz = punch_in.tzinfo if punch_in.tzinfo else timezone.get_current_timezone()
        
        # --- Late Calculation ---
        late_count_time = work_shift.late_count_time
        if late_count_time:
            late_count_dt_naive = datetime.combine(attendance_date, late_count_time)
            # FIX: Make the shift time Timezone-Aware
            late_count_dt = timezone.make_aware(late_count_dt_naive, timezone=tz)
            
            if punch_in > late_count_dt:
                is_late_calculated = True
                late_duration = punch_in - late_count_dt
        
        # --- Overtime Calculation ---
        shift_end_time = work_shift.end_time
        shift_end_dt_naive = datetime.combine(attendance_date, shift_end_time)
        # FIX: Make the shift end time Timezone-Aware
        shift_end_dt = timezone.make_aware(shift_end_dt_naive, timezone=tz)
        
        if punch_out > shift_end_dt:
            overtime_duration = punch_out - shift_end_dt
    
    return total_work_duration, is_late_calculated, late_duration, overtime_duration

# company/views.py (ManualAttendanceView)

class ManualAttendanceView(APIView):
    """
    Admin/HR endpoint to view employees of a department on a date (GET) 
    and manually update their attendance records (PATCH).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """ Filters and lists employees by Department and Date for manual entry. """
        
        filter_serializer = ManualAttendanceFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        
        dept_id = data['department_id']
        target_date = data['target_date']
        
        employees_in_dept = Profile.objects.filter(
            department_id=dept_id, 
            user__role='EMPLOYEE'
        ).select_related('user', 'work_shift').order_by('employee_id')
        
        output = []
        for profile in employees_in_dept:
            employee = profile.user
            
            attendance_record = Attendance.objects.filter(
                employee=employee, 
                attendance_date=target_date
            ).first()

            punch_in = attendance_record.punch_in_time.time().strftime('%H:%M:%S') if attendance_record and attendance_record.punch_in_time else None
            punch_out = attendance_record.punch_out_time.time().strftime('%H:%M:%S') if attendance_record and attendance_record.punch_out_time else None
            
            # Use saved duration fields from the model
            overtime = format_duration(attendance_record.overtime_duration) if attendance_record else '00:00'
            late_time = format_duration(attendance_record.late_duration) if attendance_record else '00:00' 

            output.append({
                "employee_id": employee.id,
                "fingerprint_no": profile.employee_id,
                "employee_name": profile.full_name,
                "punch_in_time": punch_in,
                "punch_out_time": punch_out,
                "is_present": attendance_record.is_present if attendance_record else False,
                "late_time": late_time,
                "overtime": overtime,
            })
            
        return Response(output)

    def patch(self, request):
        """ Manually updates a specific employee's attendance record and recalculates fields. """
        
        serializer = ManualAttendanceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        employee_id = data['employee_id']
        target_date = data['target_date']
        
        try:
            employee = User.objects.get(pk=employee_id)
            employee_profile = Profile.objects.select_related('work_shift').get(user=employee)
            print(f"\n--- DEBUG WORKSHIFT ---")
            print(f"Employee ID: {employee_id}")
            if employee_profile.work_shift:
                print(f"WorkShift Assigned: YES")
                print(f"Shift Name: {employee_profile.work_shift.shift_name}")
                print(f"Shift End Time: {employee_profile.work_shift.end_time}")
                print(f"Late Count Time: {employee_profile.work_shift.late_count_time}")
            else:
                print(f"WorkShift Assigned: NO (Value is None!)") 
            print(f"-----------------------\n")
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"error": f"Employee {employee_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        attendance_record, created = Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=target_date
        )

        punch_in = data.get('punch_in_time')
        punch_out = data.get('punch_out_time')
        
        if 'punch_in_time' in data:
            attendance_record.punch_in_time = punch_in
        if 'punch_out_time' in data:
            attendance_record.punch_out_time = punch_out
        
        if attendance_record.punch_in_time and attendance_record.punch_out_time:
            if attendance_record.punch_out_time <= attendance_record.punch_in_time:
                return Response({"error": "Punch Out Time must be after Punch In Time."}, status=status.HTTP_400_BAD_REQUEST)
                
            # Calculation function call
            (total_work_duration, 
             is_late_calculated, 
             late_duration,                
             overtime_duration) = calculate_attendance_status_and_times(attendance_record, employee_profile)
            
            # Update derived fields based on calculation
            attendance_record.total_work_duration = total_work_duration
            attendance_record.overtime_duration = overtime_duration     
            attendance_record.late_duration = late_duration            
            attendance_record.is_late = is_late_calculated
            attendance_record.is_present = True 
            
        else:
            # If punches are incomplete/removed, reset durations
            attendance_record.total_work_duration = None
            attendance_record.overtime_duration = timedelta(0)
            attendance_record.late_duration = timedelta(0)              
            
            attendance_record.is_present = data.get('is_present', attendance_record.is_present)
            attendance_record.is_late = data.get('is_late', attendance_record.is_late)
            
        attendance_record.save()
        
        return Response({"message": f"Attendance record updated successfully for Employee {employee_id} on {target_date}.",
                        "late_time": format_duration(attendance_record.late_duration),   
                        "overtime": format_duration(attendance_record.overtime_duration)}, 
                        status=status.HTTP_200_OK)


class AttendanceReportBaseView(APIView):
    # ... (Logic remains the same, used for Monthly and My Reports) ...
    permission_classes = [IsAuthenticated] 
    
    def get_filtered_attendance(self, request, employee_specific=False):
        # ... (unchanged logic) ...
        filter_serializer = AttendanceReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        
        filters = Q()
        #base_filters &= Q(employee__role=User.Role.EMPLOYEE)
        filters &= Q(employee__profile__isnull=False)
        if employee_specific:
            filters &= Q(employee=request.user)
        elif data.get('employee_id'):
            filters &= Q(employee__id=data['employee_id'])
        
        filters &= Q(attendance_date__gte=data['from_date']) 
        filters &= Q(attendance_date__lte=data['to_date']) 
            
        records = Attendance.objects.filter(filters).select_related(
            'employee__profile', 
            'employee__profile__designation'
        ).order_by('employee__profile__employee_id', 'attendance_date')
        
        return records


class DailyAttendanceReportView(APIView):
    """ Admin/HR view for daily attendance report showing Punch In/Out details for a specific date. """
    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = DailyAttendanceFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        target_date = serializer.validated_data['target_date']

        records = Attendance.objects.filter(attendance_date=target_date).select_related(
            'employee__profile', 
            'employee__profile__designation'
        ).order_by('employee__profile__department__name', 'employee__profile__employee_id')
        
        output_data = []
        for record in records:
            profile = record.employee.profile
            
            output_data.append({
                "Date": record.attendance_date,
                "Employee ID": profile.employee_id,
                "Employee Name": profile.full_name,
                "Designation": profile.designation.name if profile.designation else '--',
                "In Time": record.punch_in_time.strftime('%H:%M:%S') if record.punch_in_time else '--',
                "Out Time": record.punch_out_time.strftime('%H:%M:%S') if record.punch_out_time else '--',
                "Working Time": format_duration(record.total_work_duration),
                "Late": "Yes" if record.is_late else "No",
                "Late Time": format_duration(record.late_duration),      # <-- FIXED: Using saved field
                "Over Time": format_duration(record.overtime_duration),   
                "Status": "Present" if record.is_present else "Absent",
            })

        return Response(output_data)


class MyAttendanceReportView(AttendanceReportBaseView):
    """ Employee-specific attendance report showing their own history over a date range. """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):
        records = self.get_filtered_attendance(request, employee_specific=True)
        
        output_data = []
        for record in records:
            profile = record.employee.profile
            output_data.append({
                "Date": record.attendance_date,
                "Employee Name": profile.full_name, 
                "In Time": record.punch_in_time.strftime('%H:%M:%S') if record.punch_in_time else '--',
                "Out Time": record.punch_out_time.strftime('%H:%M:%S') if record.punch_out_time else '--',
                "Working Time": format_duration(record.total_work_duration),
                "Late": "Yes" if record.is_late else "No",
                "Late Time": format_duration(record.late_duration),       
                "Over Time": format_duration(record.overtime_duration),    
                "Status": "Present" if record.is_present else "Absent",
            })

        return Response(output_data)


class MonthlyAttendanceReportView(AttendanceReportBaseView):
    """ Admin/HR view showing detailed records over a date range, filterable by employee. """
    permission_classes = [IsAdminUser] 
    
    def get(self, request):
        records = self.get_filtered_attendance(request, employee_specific=False)
        
        output_data = []
        for record in records:
            profile = record.employee.profile
                     
            output_data.append({
                "Date": record.attendance_date,
                "Employee Name": profile.full_name,
                "Designation": profile.designation.name if profile.designation else '--',
                "In Time": record.punch_in_time.strftime('%H:%M:%S') if record.punch_in_time else '--',
                "Out Time": record.punch_out_time.strftime('%H:%M:%S') if record.punch_out_time else '--',
                "Working Time": format_duration(record.total_work_duration),
                "Late": "Yes" if record.is_late else "No",
                "Late Time": format_duration(record.late_duration),       
                "Over Time": format_duration(record.overtime_duration),    
                "Status": "Present" if record.is_present else "Absent",
            })
            
        return Response(output_data)




class AttendanceSummaryReportView(APIView):
    """ Admin/HR view showing a grid summary (P, A, L) for all employees in a given month. """
    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = MonthlySummaryFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        month_str = serializer.validated_data['month'] 
        
        try:
            year, month = map(int, month_str.split('-'))
            days_in_month = monthrange(year, month)[1] 
        except ValueError:
             return Response({"error": "Month format must be YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        base_filters = Q(attendance_date__year=year) & Q(attendance_date__month=month)
        
        
        base_filters &= Q(employee__role=User.Role.EMPLOYEE) 
        
        
        base_filters &= Q(employee__profile__isnull=False) 
        
        records = Attendance.objects.filter(base_filters).select_related(
            'employee__profile', 
            'employee__profile__designation'
        ).order_by('employee__profile__employee_id', 'attendance_date')
        # --- FIX ENDS HERE ---
        
        employee_data = {}
        for record in records:
            
            emp_id = record.employee.id
            
            if emp_id not in employee_data:
                # This line is now safe because of the filters above
                profile = record.employee.profile 
                
                # Use profile.employee_id for display if needed, but not for grouping key
                employee_data[emp_id] = {
                    "Employee Name": profile.full_name,
                    "Designation": profile.designation.name if profile.designation else "N/A",
                    "Daily_Status": {}
                }
            
            status_char = 'A'
            if record.is_present:
                # P = Present, L = Late, A = Absent
                status_char = 'L' if record.is_late else 'P' 
            
            day_key = record.attendance_date.day
            employee_data[emp_id]['Daily_Status'][day_key] = status_char

        final_output = []
        for emp_user_id, data in employee_data.items():
            row = {
                "Employee Name": data["Employee Name"],
                "Designation": data["Designation"],
            }
            # Generate columns for every day of the month (e.g., '01', '02', ..., '31')
            for day in range(1, days_in_month + 1):
                # Format day number as two digits (e.g., 1 -> '01')
                # Use '--' for days with no recorded attendance (assumed absent unless defined as holiday)
                row[f'{day:02d}'] = data['Daily_Status'].get(day, '--') 
            final_output.append(row)

        return Response(final_output)
    



class AllowanceListCreateView(APIView):
    """
    Handles LISTing all allowances (GET) and CREATING a new allowance (POST).
    Accessible only by Admin/HR.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """ List all Allowance instances. """
        allowances = Allowance.objects.all()
        serializer = AllowanceSerializer(allowances, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """ Create a new Allowance instance. """
        serializer = AllowanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllowanceDetailView(APIView):
    """
    Handles RETRIEVE (GET), UPDATE (PUT/PATCH), and DELETE for a single allowance.
    Accessible only by Admin/HR.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        """ Helper method to get the Allowance object or raise 404. """
        return get_object_or_404(Allowance, pk=pk)

    def get(self, request, pk, format=None):
        """ Retrieve a single Allowance instance. """
        allowance = self.get_object(pk)
        serializer = AllowanceSerializer(allowance)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ Fully update an Allowance instance. """
        allowance = self.get_object(pk)
        serializer = AllowanceSerializer(allowance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        """ Partially update an Allowance instance. """
        allowance = self.get_object(pk)
        serializer = AllowanceSerializer(allowance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """ Delete an Allowance instance. """
        allowance = self.get_object(pk)
        allowance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class DeductionListCreateView(APIView):
    """
    Handles LISTing all deductions (GET) and CREATING a new deduction (POST).
    Accessible only by Admin/HR.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """ List all Deduction instances. """
        deductions = Deduction.objects.all()
        serializer = DeductionSerializer(deductions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """ Create a new Deduction instance. """
        serializer = DeductionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeductionDetailView(APIView):
    """
    Handles RETRIEVE (GET), UPDATE (PUT/PATCH), and DELETE for a single deduction.
    Accessible only by Admin/HR.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        """ Helper method to get the Deduction object or raise 404. """
        return get_object_or_404(Deduction, pk=pk)

    def get(self, request, pk, format=None):
        """ Retrieve a single Deduction instance. """
        deduction = self.get_object(pk)
        serializer = DeductionSerializer(deduction)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ Fully update a Deduction instance. """
        deduction = self.get_object(pk)
        serializer = DeductionSerializer(deduction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        """ Partially update a Deduction instance. """
        deduction = self.get_object(pk)
        serializer = DeductionSerializer(deduction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """ Delete a Deduction instance. """
        deduction = self.get_object(pk)
        deduction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class MonthlyPayGradeListCreateView(APIView):
    """
    Handles GET: List all Monthly Pay Grades.
    Handles POST: Create a new Monthly Pay Grade.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        pay_grades = MonthlyPayGrade.objects.all()
        serializer = MonthlyPayGradeSerializer(pay_grades, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MonthlyPayGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- MonthlyPayGradeDetailView (Updated with PATCH) ---
class MonthlyPayGradeDetailView(APIView):
    """
    Handles GET: Retrieve a single Pay Grade.
    Handles PUT: Full Update, PATCH: Partial Update, DELETE: Delete.
    """
    permission_classes = [IsAdminUser]

    # Helper method to get the Pay Grade object or return 404
    def get_object(self, pk):
        return get_object_or_404(MonthlyPayGrade, pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a specific monthly pay grade."""
        pay_grade = self.get_object(pk)
        serializer = MonthlyPayGradeSerializer(pay_grade)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a monthly pay grade (full update)."""
        pay_grade = self.get_object(pk)
        # partial=False for PUT (Full update is the default)
        serializer = MonthlyPayGradeSerializer(pay_grade, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        """Update a monthly pay grade (partial update)."""
        pay_grade = self.get_object(pk)
        # Set partial=True for PATCH (Allows only a subset of fields)
        serializer = MonthlyPayGradeSerializer(pay_grade, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a monthly pay grade."""
        pay_grade = self.get_object(pk)
        pay_grade.delete()
        return Response({"message": "Monthly Pay Grade deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class HourlyPayGradeListCreateView(APIView):
    """
    Handles GET: List all Hourly Pay Grades.
    Handles POST: Create a new Hourly Pay Grade.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """Retrieve all hourly pay grades."""
        pay_grades = HourlyPayGrade.objects.all()
        serializer = HourlyPayGradeSerializer(pay_grades, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Create a new hourly pay grade."""
        serializer = HourlyPayGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HourlyPayGradeDetailView(APIView):
    """
    Handles GET: Retrieve a single Hourly Pay Grade.
    Handles PUT/PATCH: Update a Pay Grade.
    Handles DELETE: Delete a Pay Grade.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(HourlyPayGrade, pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a specific hourly pay grade."""
        pay_grade = self.get_object(pk)
        serializer = HourlyPayGradeSerializer(pay_grade)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update an hourly pay grade (full update)."""
        pay_grade = self.get_object(pk)
        serializer = HourlyPayGradeSerializer(pay_grade, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        """Update an hourly pay grade (partial update)."""
        pay_grade = self.get_object(pk)
        serializer = HourlyPayGradeSerializer(pay_grade, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete an hourly pay grade."""
        pay_grade = self.get_object(pk)
        pay_grade.delete()
        return Response({"message": "Hourly Pay Grade deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    



class PerformanceCategoryListCreateAPIView(APIView):
    """Handles listing all categories and creating a new category."""
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """List all active and inactive performance categories."""
        categories = PerformanceCategory.objects.all().order_by('category_name')
        serializer = PerformanceCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance category."""
        serializer = PerformanceCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PerformanceCategoryDetailAPIView(APIView):
    """Handles detailed operations on a single category instance."""
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        """Helper to safely fetch a category instance."""
        return get_object_or_404(PerformanceCategory, pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single performance category."""
        category = self.get_object(pk)
        serializer = PerformanceCategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a performance category (full update)."""
        category = self.get_object(pk)
        serializer = PerformanceCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a performance category."""
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class PerformanceCriteriaListCreateAPIView(APIView):
    """Handles listing all criteria and creating a new criterion."""
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """List all performance criteria."""
        criteria = PerformanceCriteria.objects.all().order_by('category__category_name', 'criteria_name')
        serializer = PerformanceCriteriaSerializer(criteria, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance criterion."""
        serializer = PerformanceCriteriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PerformanceCriteriaDetailAPIView(APIView):
    """Handles detailed operations on a single Performance Criteria instance."""
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        """Helper to safely fetch a criteria instance."""
        return get_object_or_404(PerformanceCriteria, pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single performance criterion."""
        criteria = self.get_object(pk)
        serializer = PerformanceCriteriaSerializer(criteria)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a performance criterion (full update)."""
        criteria = self.get_object(pk)
        serializer = PerformanceCriteriaSerializer(criteria, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a performance criterion."""
        criteria = self.get_object(pk)
        criteria.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class EmployeePerformanceListCreateAPIView(APIView):
    """Handles listing all reviews and creating a new review."""
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """List all performance reviews."""
        reviews = EmployeePerformance.objects.select_related('employee', 'reviewed_by').prefetch_related('ratings').all().order_by('-review_month')
        serializer = EmployeePerformanceSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance review with nested ratings."""
        serializer = EmployeePerformanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() # This calls the custom create() method in the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmployeePerformanceDetailAPIView(APIView):
    """Handles detailed operations on a single review instance."""
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        """Helper to safely fetch a review instance."""
        # Prefetch relations for the detail view efficiency
        return get_object_or_404(EmployeePerformance.objects.select_related('employee', 'reviewed_by').prefetch_related('ratings'), pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single performance review."""
        review = self.get_object(pk)
        serializer = EmployeePerformanceSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a performance review (full update)."""
        review = self.get_object(pk)
        serializer = EmployeePerformanceSerializer(review, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() # This calls the custom update() method in the serializer
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a performance review."""
        review = self.get_object(pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class PerformanceSummaryReportAPIView(APIView):
    """
    Generates a summary report of employee performance reviews based on filters.
    """
    permission_classes = [IsAdminUser] 
    
    def get(self, request, format=None):
        # 1. Filters ko request se nikalna (Simple Query Params)
        employee_id = request.query_params.get('employee_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        # 2. Base Query: Zaroori relationships ko pehle hi load karna
        queryset = EmployeePerformance.objects.select_related('employee').all()

        # 3. Filtering: Jo filter milta hai, woh apply karna
        if employee_id:
            try:
                queryset = queryset.filter(employee__id=int(employee_id)) 
            except ValueError:
                return Response({"error": "Invalid employee ID."}, status=status.HTTP_400_BAD_REQUEST)

        if from_date and to_date:
            queryset = queryset.filter(review_month__range=[from_date, to_date])
        
        # 4. Nested Data Optimization (Ratings detail ke liye zaroori)
        # Prefetch use karte hain taaki Serializer ka get_ratings_detail tez chale
        queryset = queryset.prefetch_related(
            Prefetch(
                'ratings',
                # sirf zaroori fields ko select karo
                queryset=PerformanceRating.objects.select_related('criteria__category')
            )
        ).order_by('-review_month') 

        
        serializer = PerformanceSummarySerializer(queryset, many=True)
        
        if not serializer.data and (employee_id or from_date):
            return Response(
                {"detail": "No performance data found for the selected filters."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.data)

class JobPostListCreateAPIView(APIView):
    """
    Handles GET (List) and POST (Create) operations using APIView.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """List all job posts (jp01.png)."""
        # Queryset mein 'published_by' relationship ko pehle hi fetch kar lo
        queryset = JobPost.objects.select_related('published_by').all().order_by('-created_at')
        serializer = JobPostSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Create a new job post (jp02.png)."""
        serializer = JobPostSerializer(data=request.data)
        if serializer.is_valid():
            # Save karte waqt 'published_by' field ko current logged-in user se set karna
            serializer.save(published_by=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobPostDetailAPIView(APIView):
    """
    Handles GET, PUT, PATCH, and DELETE operations for a single Job Post.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper to safely fetch a JobPost instance."""
        # Queryset mein 'published_by' relationship ko pehle hi fetch kar lo
        return get_object_or_404(JobPost.objects.select_related('published_by'), pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single job post."""
        job_post = self.get_object(pk)
        serializer = JobPostSerializer(job_post)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a job post (full update)."""
        job_post = self.get_object(pk)
        serializer = JobPostSerializer(job_post, data=request.data)
        if serializer.is_valid():
            # Update karte waqt published_by ko overwrite nahi karna chahiye
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        """Delete a job post."""
        job_post = self.get_object(pk)
        job_post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)