from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from users.models import Education,Experience,User,Profile,Role
from .models import Department,Designation, Branch,Warning,Termination,Promotion,Holiday,WeeklyHoliday,LeaveType,EarnLeaveRule,PublicHoliday,LeaveApplication,LeaveBalance,WorkShift, \
Attendance,Allowance,Deduction,MonthlyPayGrade,PerformanceCategory,PerformanceCriteria,EmployeePerformance,PerformanceRating,JobPost,TrainingType,EmployeeTraining,Award,Notice,LateDeductionRule,TaxRule,\
PaySlip,PaySlipDetail
from .serializers import DepartmentSerializer,DesignationSerializer,EducationSerializer,EmployeeCreateSerializer,ExperienceSerializer,EmployeeListSerializer,EmployeeDetailSerializer
DepartmentSerializer, DesignationSerializer,
from django.db.models import Sum
from users.enums import LeaveStatus,GenderChoices
from .serializers import WarningSerializer,TerminationSerializer,PromotionSerializer,EmployeeJobStatusSerializer,HolidaySerializer,PublicHolidaySerializer,EarnLeaveRuleSerializer    
from .serializers import LeaveTypeSerializer,WeeklyHolidaySerializer,LeaveApplicationListSerializer,LeaveApplicationCreateSerializer,LeaveReportSerializer,WorkShiftSerializer, \
ManualAttendanceFilterSerializer,ManualAttendanceInputSerializer,AttendanceReportFilterSerializer,DailyAttendanceFilterSerializer,MonthlySummaryFilterSerializer,\
BranchSerializer,AllowanceSerializer,DeductionSerializer,MonthlyPayGradeSerializer,HourlyPayGradeSerializer,HourlyPayGrade,PerformanceCategorySerializer,PerformanceCriteriaSerializer,\
EmployeePerformanceSerializer,PerformanceSummarySerializer,JobPostSerializer,TrainingTypeSerializer,EmployeeTrainingSerializer,AwardSerializer,NoticeSerializer,LateDeductionRuleSerializer,TaxRuleSerializer,\
PaySlipDetailSerializer,MonthlySalaryFilterSerializer,ChangePasswordSerializer,CSVAttendanceInputSerializer,RoleSerializer

from datetime import date
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, time
from calendar import monthrange
from django.utils import timezone
from django.db.models import Prefetch
from decimal import Decimal
from .pagination import StandardResultsSetPagination
import csv
import io

class DepartmentListCreateView(APIView):
    """
    Departments ki list dekhein (Pagination aur Search ke saath) ya naya department banayein.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Department.objects.all().order_by('name')   
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # 3. Pagination Apply karna
        paginator = StandardResultsSetPagination()
        
        # Queryset ko paginator ko dein
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        # 4. Serialization
        # Serializer ko sirf current page ke items par apply karein
        serializer = DepartmentSerializer(page, many=True)
        
        # 5. Response mein paginated data return karna
        # Yeh method metadata (count, next, previous) ke saath data return karta hai
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        queryset = Designation.objects.select_related('department').all().order_by('department__name', 'name')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )
            
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = DesignationSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        queryset = Branch.objects.all().order_by('name')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )
            
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = BranchSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchDetailView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 1. Fetch ALL Profiles (no role restriction here)
        queryset = Profile.objects.select_related(
            'user', 
            'department', 
            'designation', 
            'monthly_pay_grade', 
            'hourly_pay_grade',
            'branch'
        ).all().order_by('first_name')
        
        # 2. Filtering Logic (Role filter uses iexact which is okay for text field)
        role_filter = request.query_params.get('role', None)
        if role_filter:
            # Filter works regardless of the role string used (e.g., 'Employe' or 'Admin')
            queryset = queryset.filter(user__role__iexact=role_filter)
            
        # Filter by Department ID
        department_id = request.query_params.get('department_id', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
            
        # Filter by Designation ID
        designation_id = request.query_params.get('designation_id', None)
        if designation_id:
            queryset = queryset.filter(designation_id=designation_id)

        # Filter by Status (Active/Inactive, Profile ka status)
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)


        # 3. Search Logic
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(employee_id__icontains=search_query) 
            )
            
        # 4. Pagination Apply karna
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        # 5. Serialization
        serializer = EmployeeListSerializer(page, many=True)
        
        # 6. Response mein paginated data return karna
        return paginator.get_paginated_response(serializer.data)

class EmployeeCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailView(APIView):
    """
    Retrieve, Update or Delete an employee's profile instance for ANY role.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Profile.objects.get(user__pk=pk)
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
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """ Partially update an employee profile (User, Profile, WorkShift). """
        profile = self.get_object(pk)
        serializer = EmployeeDetailSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = self.get_object(pk)
        user_to_delete = profile.user
        user_to_delete.delete() 
        return Response({"message": "Employee deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class EmployeeEducationView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, employee_pk):
        return Profile.objects.get(user__pk=employee_pk)

    # GET: All Education + POST: New Education
    def get(self, request, employee_pk):
        try:
            profile = self.get_profile(employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

        education = profile.education.all()
        serializer = EducationSerializer(education, many=True)
        return Response(serializer.data)

    def post(self, request, employee_pk):
        try:
            profile = self.get_profile(employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeEducationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, employee_pk, education_pk):
        return Education.objects.get(pk=education_pk, profile__user__pk=employee_pk)

    # GET: Single Education
    def get(self, request, employee_pk, education_pk):
        try:
            education = self.get_object(employee_pk, education_pk)
        except Education.DoesNotExist:
            return Response({"error": "Education not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationSerializer(education)
        return Response(serializer.data)

    # PUT/PATCH: Update
    def put(self, request, employee_pk, education_pk):
        return self.patch(request, employee_pk, education_pk)

    def patch(self, request, employee_pk, education_pk):
        try:
            education = self.get_object(employee_pk, education_pk)
        except Education.DoesNotExist:
            return Response({"error": "Education not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationSerializer(education, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Remove
    def delete(self, request, employee_pk, education_pk):
        try:
            education = self.get_object(employee_pk, education_pk)
        except Education.DoesNotExist:
            return Response({"error": "Education not found"}, status=status.HTTP_404_NOT_FOUND)
        
        education.delete()
        return Response({"message": "Education deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class EmployeeExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, employee_pk):
        return Profile.objects.get(user__pk=employee_pk)

    def get(self, request, employee_pk):
        try:
            profile = self.get_profile(employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

        experience = profile.experience.all()
        serializer = ExperienceSerializer(experience, many=True)
        return Response(serializer.data)

    def post(self, request, employee_pk):
        try:
            profile = self.get_profile(employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeExperienceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, employee_pk, experience_pk):
        return Experience.objects.get(pk=experience_pk, profile__user__pk=employee_pk)

    def get(self, request, employee_pk, experience_pk):
        try:
            experience = self.get_object(employee_pk, experience_pk)
        except Experience.DoesNotExist:
            return Response({"error": "Experience not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExperienceSerializer(experience)
        return Response(serializer.data)

    def put(self, request, employee_pk, experience_pk):
        return self.patch(request, employee_pk, experience_pk)

    def patch(self, request, employee_pk, experience_pk):
        try:
            experience = self.get_object(employee_pk, experience_pk)
        except Experience.DoesNotExist:
            return Response({"error": "Experience not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExperienceSerializer(experience, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee_pk, experience_pk):
        try:
            experience = self.get_object(employee_pk, experience_pk)
        except Experience.DoesNotExist:
            return Response({"error": "Experience not found"}, status=status.HTTP_404_NOT_FOUND)

        experience.delete()
        return Response({"message": "Experience deleted successfully"}, status=status.HTTP_204_NO_CONTENT)






class WarningListCreateView(APIView):
    """
    List all warnings or create a new warning.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        queryset = Warning.objects.select_related(
            'warning_to__profile', 
            'warning_by__profile'
        ).all().order_by('-warning_date', '-id')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(warning_to__profile__full_name__icontains=search_query) |
                Q(subject__icontains=search_query)                          
            )
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = WarningSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        queryset = Termination.objects.select_related(
            'terminate_to__profile', 
            'terminate_by__profile'
        ).all().order_by('-termination_date', '-id')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(terminate_to__profile__full_name__icontains=search_query) |
                Q(subject__icontains=search_query)                             
            )
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = TerminationSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):

        queryset = Promotion.objects.select_related(
            'employee__profile', 
            'promoted_department',
            'promoted_designation'
        ).all().order_by('-promotion_date', '-id')
        

        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__profile__full_name__icontains=search_query)
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PromotionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            # Find the profile of the employee using their user ID (pk)
            profile = Profile.objects.get(user__pk=pk)
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ List all holidays with search and pagination. """
        queryset = Holiday.objects.all().order_by('name')
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = HolidaySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ List all public holidays with search and pagination (Only by Holiday Name). """
        
        queryset = PublicHoliday.objects.select_related('holiday').all().order_by('-start_date')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(holiday__name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PublicHolidaySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        queryset = WeeklyHoliday.objects.all().order_by('day')
        
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(day__icontains=search_query) 
            )
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = WeeklyHolidaySerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
    
        queryset = LeaveType.objects.all().order_by('name')
        
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = LeaveTypeSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = LeaveTypeSerializer(data=request.data)
        if serializer.is_valid():
            # 1. Save the new LeaveType object
            new_leave_type = serializer.save()
            
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    GET: Employee ke liye Leave Types aur Current Balance dikhata hai .
    POST: Leave application submit karta hai (dynamic calculation aur validation ke saath).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user
        
        # 1.  FIX: LeaveBalance table se saare balance records fetch karein
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
        
        queryset = LeaveApplication.objects.filter(employee=request.user).order_by('-application_date')
        
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = LeaveApplicationListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    

class AllLeaveApplicationsView(APIView):
    """
    Admin/Manager ke liye sabhi applications ki list dikhata hai.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        queryset = LeaveApplication.objects.all().order_by('-application_date')
        
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = LeaveApplicationListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class LeaveApprovalView(APIView):
    """
    Admin/Manager endpoint to Approve or Reject a leave application (PK based).
    Includes logic to deduct balance from the LeaveBalance table upon approval.
    """
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated] 
    
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        """ List all work shifts with search and pagination. """

        queryset = WorkShift.objects.all().order_by('shift_name')

        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(shift_name__icontains=search_query) 
            )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = WorkShiftSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
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
    permission_classes = [IsAuthenticated]

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

class MyAttendanceReportView(APIView):
    """ 
    [MODIFIED] Employee-specific attendance report showing only expected working days 
    and detailed summary statistics.
    """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):
        filter_serializer = AttendanceReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        from_date = data['from_date']
        to_date = data['to_date']
        
        try:
            employee = request.user
            employee_profile = Profile.objects.select_related('work_shift').get(user=employee)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Get ALL Attendance records for the employee within the date range
        all_attendance_qs = Attendance.objects.filter(
            employee=employee, 
            attendance_date__gte=from_date, 
            attendance_date__lte=to_date
        )
        attendance_records_map = {
            record.attendance_date: record 
            for record in all_attendance_qs
        }
        
        # 2. Determine the list of dates the employee WAS EXPECTED TO WORK (excluding holidays)
        expected_working_dates = get_expected_working_dates_list(from_date, to_date)
        
        # 3. Build the Daily Records Output
        output_data = []
        records_for_summary = [] # List to hold actual Attendance objects for aggregation
        
        for current_date in expected_working_dates:
            record = attendance_records_map.get(current_date)
            
            if record:
                # Case A: Attendance record exists (Present, Late, Single Punch)
                records_for_summary.append(record)
                
                output_data.append({
                    "Date": record.attendance_date,
                    "Employee Name": employee_profile.full_name, 
                    "In Time": record.punch_in_time.strftime('%H:%M:%S') if record.punch_in_time else '--',
                    "Out Time": record.punch_out_time.strftime('%H:%M:%S') if record.punch_out_time else '--',
                    "Working Time": format_duration(record.total_work_duration),
                    "Late": "Yes" if record.is_late else "No",
                    "Late Time": format_duration(record.late_duration),       
                    "Over Time": format_duration(record.overtime_duration),    
                    "Status": "Present" if record.is_present else "Absent",
                })
            else:
                # Case B: No Attendance record exists for an expected working day (ABSENT)
                output_data.append({
                    "Date": current_date,
                    "Employee Name": employee_profile.full_name, 
                    "In Time": '--', "Out Time": '--', 
                    "Working Time": '00:00', "Late": 'No', 
                    "Late Time": '00:00', "Over Time": '00:00',    
                    "Status": "Absence",
                })
        
        # 4. Calculate Summary Statistics using all_attendance_qs (for efficiency)
        summary = calculate_summary_stats(
            all_attendance_qs, # Pass the queryset for aggregation
            expected_working_dates, 
            employee_profile,
            from_date,
            to_date
        )
        
        # 5. Return the final structured response
        return Response({
            "daily_records": output_data,
            "summary": summary
        })


class MonthlyAttendanceReportView(APIView):
    """ 
    [MODIFIED] Admin/HR view showing detailed records over a date range, filterable by employee, 
    only showing expected working days and summary.
    """
    permission_classes = [IsAuthenticated] 
    
    def get(self, request):
        filter_serializer = AttendanceReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        from_date = data['from_date']
        to_date = data['to_date']
        employee_id = data.get('employee_id') 

        # 1. Fetch the specific employee profile
        try:
            employee = User.objects.get(pk=employee_id) if employee_id else None
            employee_profile = Profile.objects.select_related('work_shift').get(user=employee) if employee else None
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        if not employee:
            # Admin view requires filtering by employee ID to show a summary/detailed table
            return Response({"error": "Employee ID is required for detailed monthly report."}, 
                            status=status.HTTP_400_BAD_REQUEST)


        # 2. Get ALL Attendance records for the employee within the date range
        all_attendance_qs = Attendance.objects.filter(
            employee=employee, 
            attendance_date__gte=from_date, 
            attendance_date__lte=to_date
        )
        attendance_records_map = {
            record.attendance_date: record 
            for record in all_attendance_qs
        }
        
        # 3. Determine the list of dates the employee WAS EXPECTED TO WORK (excluding holidays)
        expected_working_dates = get_expected_working_dates_list(from_date, to_date)
        
        # 4. Build the Daily Records Output
        output_data = []
        
        for current_date in expected_working_dates:
            record = attendance_records_map.get(current_date)
            
            if record:
                # Case A: Attendance record exists
                output_data.append({
                    "Date": record.attendance_date,
                    "Employee Name": employee_profile.full_name,
                    "Designation": employee_profile.designation.name if employee_profile.designation else '--',
                    "In Time": record.punch_in_time.strftime('%H:%M:%S') if record.punch_in_time else '--',
                    "Out Time": record.punch_out_time.strftime('%H:%M:%S') if record.punch_out_time else '--',
                    "Working Time": format_duration(record.total_work_duration),
                    "Late": "Yes" if record.is_late else "No",
                    "Late Time": format_duration(record.late_duration),       
                    "Over Time": format_duration(record.overtime_duration),    
                    "Status": "Present" if record.is_present else "Absent",
                })
            else:
                # Case B: No Attendance record exists (ABSENT)
                output_data.append({
                    "Date": current_date,
                    "Employee Name": employee_profile.full_name,
                    "Designation": employee_profile.designation.name if employee_profile.designation else '--',
                    "In Time": '--', "Out Time": '--', 
                    "Working Time": '00:00', "Late": 'No', 
                    "Late Time": '00:00', "Over Time": '00:00',    
                    "Status": "Absence",
                })
            
        # 5. Calculate Summary Statistics
        summary = calculate_summary_stats(
            all_attendance_qs, 
            expected_working_dates, 
            employee_profile,
            from_date,
            to_date
        )
            
        # 6. Return the final structured response
        return Response({
            "daily_records": output_data,
            "summary": summary
        })




class ManualAttendanceView(APIView):
    """
    Admin/HR endpoint to view employees of a department on a date (GET) 
    and manually update their attendance records (PATCH).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Filters and lists employees by Department and Date for manual entry. """
        
        filter_serializer = ManualAttendanceFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        
        dept_id = data['department_id']
        target_date = data['target_date']
        
        employees_in_dept = Profile.objects.filter(
            department_id=dept_id, 
            user__is_superuser=False, 
            user__is_active=True
        ).select_related('user', 'user__role', 'work_shift').order_by('employee_id')
        
        output = []
        for profile in employees_in_dept:
            employee = profile.user
            
            attendance_record = Attendance.objects.filter(
                employee=employee, 
                attendance_date=target_date
            ).first()

            # Time formatting
            punch_in = attendance_record.punch_in_time.time().strftime('%H:%M:%S') if attendance_record and attendance_record.punch_in_time else None
            punch_out = attendance_record.punch_out_time.time().strftime('%H:%M:%S') if attendance_record and attendance_record.punch_out_time else None
            
            # Use saved duration fields from the model
            overtime = format_duration(attendance_record.overtime_duration) if attendance_record else '00:00'
            late_time = format_duration(attendance_record.late_duration) if attendance_record else '00:00' 
            
            # Retrieve status (assuming you added a 'status' field to Attendance model)
            status_indicator = getattr(attendance_record, 'status', 'Pending') if attendance_record else 'Pending'

            output.append({
                "employee_id": employee.id,
                "fingerprint_no": profile.employee_id,
                "employee_name": profile.full_name,
                "punch_in_time": punch_in,
                "punch_out_time": punch_out,
                "is_present": attendance_record.is_present if attendance_record else False,
                "late_time": late_time,
                "overtime": overtime,
                "status": status_indicator, # Include status indicator
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
            # Use select_related for work_shift to avoid extra query
            employee_profile = Profile.objects.select_related('work_shift').get(user=employee)
            # DEBUG print statements removed for final code
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"error": f"Employee {employee_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        attendance_record, created = Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=target_date
        )

        punch_in = data.get('punch_in_time')
        punch_out = data.get('punch_out_time')
        
        # Update raw punch times if provided
        if 'punch_in_time' in data:
            attendance_record.punch_in_time = punch_in
        if 'punch_out_time' in data:
            attendance_record.punch_out_time = punch_out
        
        # Check for Punch-in before calculation
        if attendance_record.punch_in_time:
            
            # Punch Out validation (only if both are present)
            if attendance_record.punch_out_time and attendance_record.punch_out_time <= attendance_record.punch_in_time:
                return Response({"error": "Punch Out Time must be after Punch In Time."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Call calculation function (It calculates LATE time regardless of punch_out)
            (total_work_duration, 
             is_late_calculated, 
             late_duration,                
             overtime_duration) = calculate_attendance_status_and_times(attendance_record, employee_profile)
            
            # Update Late status and duration (Always run if punch_in exists)
            attendance_record.late_duration = late_duration            
            attendance_record.is_late = is_late_calculated
            
            # Update Duration/Overtime (Only updated if punch_out was present in the calc function)
            attendance_record.total_work_duration = total_work_duration
            attendance_record.overtime_duration = overtime_duration     
            attendance_record.is_present = True # Present if punch-in exists

            # --- Status Indicator Logic (Single Punch Handling) ---
            if attendance_record.punch_in_time and not attendance_record.punch_out_time:
                 # Single Punch
                 attendance_record.status = 'Single Punch' 
            else:
                 # Both punches are present
                 attendance_record.status = 'Completed'

        else:
            # If punch-in is removed or missing, reset all durations/status
            attendance_record.total_work_duration = None
            attendance_record.overtime_duration = timedelta(0)
            attendance_record.late_duration = timedelta(0)              
            
            attendance_record.is_present = data.get('is_present', False) 
            attendance_record.is_late = False 
            attendance_record.status = 'Pending' # Or 'Absent'
        
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
    permission_classes = [IsAuthenticated]

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





class AttendanceSummaryReportView(APIView):
    """ Admin/HR view showing a grid summary (P, A, L) for all employees in a given month. """
    permission_classes = [IsAuthenticated]

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
        
        
        base_filters &= Q(employee__is_active=True) 
        
        
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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """ List all Allowance instances with search and pagination. """
        queryset = Allowance.objects.all().order_by('allowance_name')
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(allowance_name__icontains=search_query) |            # 1. Allowance Name par search
                Q(allowance_type__icontains=search_query)              # 2. Allowance Type (internal value) par search
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AllowanceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """ List all Deduction instances with search and pagination. """
        queryset = Deduction.objects.all().order_by('deduction_name')

        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(deduction_name__icontains=search_query) |            # 1. Deduction Name par search
                Q(deduction_type__icontains=search_query)              # 2. Deduction Type (internal value) par search
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = DeductionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """ List all Monthly Pay Grade instances with search and pagination. """
        queryset = MonthlyPayGrade.objects.all().order_by('grade_name')

        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(grade_name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = MonthlyPayGradeSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = MonthlyPayGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() # Serializer.save() will handle all nested logic and calculation
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- MonthlyPayGradeDetailView (Updated and Fixed) ---
class MonthlyPayGradeDetailView(APIView):
    """
    Handles GET: Retrieve a single Pay Grade.
    Handles PUT: Full Update, PATCH: Partial Update, DELETE: Delete.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(MonthlyPayGrade, pk=pk)

    def get(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        serializer = MonthlyPayGradeSerializer(pay_grade)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        # Full update (partial=False)
        serializer = MonthlyPayGradeSerializer(pay_grade, data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        # Partial update (partial=True)
        serializer = MonthlyPayGradeSerializer(pay_grade, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        pay_grade.delete()
        return Response({"message": "Monthly Pay Grade deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class HourlyPayGradeListCreateView(APIView):
    """
    Handles GET: List all Hourly Pay Grades.
    Handles POST: Create a new Hourly Pay Grade.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """ List all Hourly Pay Grade instances with search and pagination. """
        queryset = HourlyPayGrade.objects.all().order_by('pay_grade_name')
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(pay_grade_name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = HourlyPayGradeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all active and inactive performance categories with search and pagination."""
        queryset = PerformanceCategory.objects.all().order_by('category_name')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(category_name__icontains=search_query)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PerformanceCategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance category."""
        serializer = PerformanceCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PerformanceCategoryDetailAPIView(APIView):
    """Handles detailed operations on a single category instance."""
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all performance criteria with search and pagination."""
        queryset = PerformanceCriteria.objects.select_related('category').all().order_by('category__category_name', 'criteria_name')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(criteria_name__icontains=search_query) |            # 1. Criteria Name par search
                Q(category__category_name__icontains=search_query)   # 2. Related Category Name par search
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PerformanceCriteriaSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance criterion."""
        serializer = PerformanceCriteriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PerformanceCriteriaDetailAPIView(APIView):
    """Handles detailed operations on a single Performance Criteria instance."""
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all performance reviews with search and pagination."""
        queryset = EmployeePerformance.objects.select_related('employee', 'reviewed_by').prefetch_related('ratings').all().order_by('-review_month')
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = EmployeePerformanceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance review with nested ratings."""
        serializer = EmployeePerformanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() # This calls the custom create() method in the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmployeePerformanceDetailAPIView(APIView):
    """Handles detailed operations on a single review instance."""
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, format=None):
        employee_id = request.query_params.get('employee_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        queryset = EmployeePerformance.objects.select_related('employee').all()
        if employee_id:
            try:
                queryset = queryset.filter(employee__id=int(employee_id)) 
            except ValueError:
                return Response({"error": "Invalid employee ID format."}, status=status.HTTP_400_BAD_REQUEST)

        if from_date and to_date:
            queryset = queryset.filter(review_month__range=[from_date, to_date])
        queryset = queryset.prefetch_related(
            Prefetch(
                'ratings',
                queryset=PerformanceRating.objects.select_related('criteria__category')
            )
        ).order_by('-review_month') 
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if not page and (employee_id or from_date):
            return Response(
                {"detail": "No performance data found for the selected filters."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PerformanceSummarySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class JobPostListCreateAPIView(APIView):
    """
    Handles GET (List) and POST (Create) operations using APIView.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """List all job posts with search and pagination."""
        queryset = JobPost.objects.select_related('published_by').all().order_by('-created_at')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(job_title__icontains=search_query) |      # 1. Job Title par search
                Q(description__icontains=search_query)      # 2. Description par search
            )
        paginator = StandardResultsSetPagination()

        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = JobPostSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
    



class TrainingTypeListCreateAPIView(APIView):
    """
    Handles GET (List) and POST (Create) operations for Training Types using APIView.
    """
    # Permission: Sirf authenticated users ko access
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all training types with search and pagination."""
        
        queryset = TrainingType.objects.all().order_by('training_type_name')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(training_type_name__icontains=search_query)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = TrainingTypeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new training type """
        serializer = TrainingTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainingTypeDetailAPIView(APIView):
    """
    Handles GET, PUT, PATCH, and DELETE operations for a single Training Type.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper to safely fetch a TrainingType instance."""
        return get_object_or_404(TrainingType, pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single training type."""
        training_type = self.get_object(pk)
        serializer = TrainingTypeSerializer(training_type)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a training type (full update)."""
        training_type = self.get_object(pk)
        serializer = TrainingTypeSerializer(training_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        """Delete a training type."""
        training_type = self.get_object(pk)
        training_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class EmployeeTrainingListCreateAPIView(APIView):
    """
    Handles GET (List - etl01.png) and POST (Create - etl02.png) operations for Employee Training.
    """
    # Permission: Sirf authenticated users ko access
    permission_classes = [IsAuthenticated] 

    def get(self, request, format=None):
        """List all employee training records with search and pagination."""
        queryset = EmployeeTraining.objects.select_related('employee', 'training_type').all().order_by('-from_date')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search_query) |            # 1. Employee Name par search
                Q(training_type__training_type_name__icontains=search_query) | # 2. Training Type Name par search
                Q(subject__icontains=search_query)                           # 3. Subject par search
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = EmployeeTrainingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new employee training record."""
        serializer = EmployeeTrainingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeTrainingDetailAPIView(APIView):
    """
    Handles GET, PUT, PATCH, and DELETE operations for a single Employee Training record.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper to safely fetch an EmployeeTraining instance."""
        # Queryset mein 'employee' aur 'training_type' relationships ko pehle hi fetch karein.
        return get_object_or_404(EmployeeTraining.objects.select_related('employee', 'training_type'), pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single training record."""
        training = self.get_object(pk)
        serializer = EmployeeTrainingSerializer(training)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a training record (full update)."""
        training = self.get_object(pk)
        serializer = EmployeeTrainingSerializer(training, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        """Delete a training record."""
        training = self.get_object(pk)
        training.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class EmployeeTrainingReportAPIView(APIView):
    """
    Handles GET request for the Employee Training Report (emt01.png) with Pagination.
    Filters training records based on employee ID provided in query parameters.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        employee_profile_id = request.query_params.get('employee_id', None)
        queryset = EmployeeTraining.objects.select_related('employee', 'training_type').all().order_by('-from_date')
        if employee_profile_id:
            try:
                employee_profile_id = int(employee_profile_id) 
                queryset = queryset.filter(employee__pk=employee_profile_id)
            except ValueError:
                return Response({"detail": "Invalid employee ID format."}, status=status.HTTP_400_BAD_REQUEST)
        paginator = StandardResultsSetPagination()

        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = EmployeeTrainingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class AwardListCreateAPIView(APIView):
    ppermission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all employee awards with search and pagination."""
        queryset = Award.objects.select_related('employee').all().order_by('-award_month')
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search_query) |  # Employee ka pura naam
                Q(award_name__icontains=search_query) |            # Award Enum value (internal value)
                Q(gift_item__icontains=search_query)              # Gift item par search
            )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AwardSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new employee award (award02.png)."""
        serializer = AwardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AwardDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper to safely fetch an Award instance."""
        # Optimize query by selecting related FKs
        return get_object_or_404(Award.objects.select_related('employee'), pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single award record."""
        award = self.get_object(pk)
        serializer = AwardSerializer(award)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a training record."""
        award = self.get_object(pk)
        serializer = AwardSerializer(award, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        """Delete an award record."""
        award = self.get_object(pk)
        award.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class NoticeListCreateAPIView(APIView):
    """
    Handles GET (Notice List - not01.png) and POST (Add New Notice - not02.png) operations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """List all notices with search and pagination."""

        queryset = Notice.objects.all().order_by('-publish_date')

        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        paginator = StandardResultsSetPagination()

        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = NoticeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new notice."""
        # Use request.data for standard fields and files
        serializer = NoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoticeDetailAPIView(APIView):
    """
    Handles GET, PUT, PATCH, and DELETE operations for a single Notice record.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper to safely fetch a Notice instance."""
        return get_object_or_404(Notice, pk=pk)

    def get(self, request, pk, format=None):
        """Retrieve a single notice record."""
        notice = self.get_object(pk)
        serializer = NoticeSerializer(notice)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a notice record (full update)."""
        notice = self.get_object(pk)
        serializer = NoticeSerializer(notice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        """Delete a notice record."""
        notice = self.get_object(pk)
        notice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class DashboardDataAPIView(APIView):
    """
    Provides key metrics (Employee count, Department count, Present/Absent count).
    Total count includes all active users EXCEPT those marked as Superuser.
    """
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        today = date.today()
        
        # 1. Total Active Employees Count (Excluding only Superuser accounts)
        
        # Define the base filter for counting all relevant staff:
        staff_base_filter = Q(is_superuser=False) & Q(is_active=True)
        
        # Count all active staff who are NOT superusers and have a linked profile
        total_employees = User.objects.filter(
            staff_base_filter,             
            profile__status='Active',            
            profile__isnull=False                
        ).count()
        
        # Total Active Departments Count (No change needed)
        total_departments = Department.objects.count()
        
        # 2. Today's Attendance Record Filtering
        
        # Filter attendance records to match the users counted in 'total_employees'
        today_attendance_records = Attendance.objects.filter(
            attendance_date=today,
            employee__in=User.objects.filter(staff_base_filter).values_list('pk', flat=True)
        ).filter(employee__profile__status='Active') # Only check attendance for active employees
        
        # Present Count
        present_count = today_attendance_records.filter(is_present=True).count()
        
        # Absent Count (Total Active Employees - Present Employees)
        absent_count = total_employees - present_count
        
        
        # --- 3. Today Attendance List (Only Present Employees' Summary) ---
        
        attendance_list = []
        today_present_records = today_attendance_records.filter(is_present=True).select_related('employee__profile')

        for record in today_present_records:
            profile = record.employee.profile
            
            in_time = record.punch_in_time.time().strftime('%I:%M %p') if record.punch_in_time else None
            out_time = record.punch_out_time.time().strftime('%I:%M %p') if record.punch_out_time else None
            
            attendance_list.append({
                "photo": profile.photo.url if profile.photo else None,
                "name": profile.full_name,
                "in_time": in_time,
                "out_time": out_time,
                "late_duration": format_duration(record.late_duration), 
            })
            
        # 4. Notice Board Data
        latest_notice = Notice.objects.filter(status='PUBLISHED').order_by('-publish_date').first()
        
        notice_data = None
        if latest_notice:
            notice_data = {
                'title': latest_notice.title,
                'publish_date': latest_notice.publish_date.strftime("%d %b %Y"),
                'description': latest_notice.description,
            }
            
        # 5. Final Response
        return Response({
            'success': True,
            'metrics': {
                'total_employee': total_employees,
                'total_department': total_departments,
                'present_today': present_count,
                'absent_today': absent_count,
            },
            'today_attendance_list': attendance_list,
            'notice_board': notice_data,
        })


class LateDeductionRuleListCreateAPIView(APIView):
    """ Handles listing all rules and creating a new rule. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Lists all Late Deduction Rules (List Action). """
        queryset = LateDeductionRule.objects.all().order_by('late_days_threshold')
        serializer = LateDeductionRuleSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """ Creates a new Late Deduction Rule (Create Action). """
        serializer = LateDeductionRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LateDeductionRuleRetrieveUpdateDestroyAPIView(APIView):
    """ Handles detail view, update, and delete for a single rule. """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(LateDeductionRule, pk=pk)

    def get(self, request, pk):
        """ Retrieves a single rule (Detail Action). """
        rule = self.get_object(pk)
        serializer = LateDeductionRuleSerializer(rule)
        return Response(serializer.data)

    def put(self, request, pk):
        """ Updates an existing rule completely (Update Action). """
        rule = self.get_object(pk)
        serializer = LateDeductionRuleSerializer(rule, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """ Deletes an existing rule (Destroy Action). """
        rule = self.get_object(pk)
        rule.delete()
        return Response({"message": "Rule deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    


# --- Helper for Recalculation (APIView ke andar ya ek utility function) ---
def _recalculate_fixed_tax(gender):
    """ 
    Recalculates fixed tax (Cumulative Tax) for all rules of a given gender.
    Must be called AFTER all rules are saved in the database.
    """
    # Rules ko limit ke ascending order mein fetch karein
    rules = TaxRule.objects.filter(gender=gender).order_by('total_income_limit')
    previous_limit = Decimal('0.00')
    
    for i, rule in enumerate(rules):
        if rule.slab_type == 'REMAINING':
            # Last slab ka fixed tax 0 hota hai
            cumulative_fixed_tax = Decimal('0.00')
        else:
            # Pichle rule se cumulative tax nikalna
            if i == 0:
                tax_on_previous_slabs = Decimal('0.00')
            else:
                # Pichle rule (i-1) ka final fixed tax uthaya
                tax_on_previous_slabs = rules[i-1].taxable_amount_fixed
            
            # Current slab mein aayi income
            taxable_income_in_slab = rule.total_income_limit - previous_limit
            
            # Tax sirf current slab ki income par calculate karein
            tax_in_this_slab = (taxable_income_in_slab * rule.tax_rate_percentage) / Decimal('100.0')
            
            # Cumulative fixed tax = Pichla Tax + Current Slab ka Tax
            cumulative_fixed_tax = tax_on_previous_slabs + tax_in_this_slab

        rule.taxable_amount_fixed = round(cumulative_fixed_tax, 2)
        rule.save(update_fields=['taxable_amount_fixed'])
        previous_limit = rule.total_income_limit # Update previous limit for the next iteration



class TaxRuleSetupAPIView(APIView):
    """
    Handles listing all Tax Rules (GET) and bulk updating/creating (PUT/POST) them.
    (Corresponds to Tax Rule Setup screen: tax01.png)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Lists all Tax Rules, grouped by gender. """
        queryset = TaxRule.objects.all().order_by('gender', 'total_income_limit')
        
        # Data ko Gender ke hisaab se group karna
        male_rules = queryset.filter(gender=GenderChoices.MALE)
        female_rules = queryset.filter(gender=GenderChoices.FEMALE)
        
        male_serializer = TaxRuleSerializer(male_rules, many=True)
        female_serializer = TaxRuleSerializer(female_rules, many=True)
        
        return Response({
            "male_rules": male_serializer.data,
            "female_rules": female_serializer.data,
        })

    def put(self, request):
        """ 
        Bulk syncs Tax Rules using Delete & Recreate strategy:
        Deletes all existing rules and creates new ones from the input list.
        """
        rules_data = request.data.get('rules', []) 
        
        if not isinstance(rules_data, list):
            return Response({"error": "Expected a list of rules under the key 'rules'."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            
            # 1. 🛑 FORCE DELETE ALL EXISTING RULES 
            # Saare purane rules ko hatana, taaki list mein jo nahi hain woh delete ho jaayen.
            TaxRule.objects.all().delete() 
            
            rules_to_save = []
            errors = []
            
            # 2. ✅ Validate and Collect Data (New Creation)
            for item in rules_data:
                
                # Naye rules create ho rahe hain, isliye ID aur fixed tax ko ignore karein
                item.pop('id', None) 
                item.pop('taxable_amount_fixed', None)
                
                # Ab hamesha Naya Serializer (Create) use hoga
                serializer = TaxRuleSerializer(data=item) 

                if serializer.is_valid():
                    rules_to_save.append(serializer)
                else:
                    errors.append({"data": item, "errors": serializer.errors})
            
            if errors:
                # Agar koi bhi validation error aaya, toh transaction revert ho jaayega (Delete bhi revert)
                return Response({"message": "Validation errors occurred. No changes saved.", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
                
            # 3. SAVE ALL NEW RULES
            for serializer in rules_to_save:
                serializer.save()
            
            # 4. RECALCULATE FIXED TAX (Correct Ordering ke saath)
            _recalculate_fixed_tax(GenderChoices.MALE)
            _recalculate_fixed_tax(GenderChoices.FEMALE)
            
            # 5. Return Updated Data (GET call, jismein ab sirf naye rules honge)
            return self.get(request)

def _calculate_unpaid_days(employee, target_date):
    """
    Calculates the total number of UNPAID days for an employee in the target month.
    Uses Attendance, Leave, and Holiday models.
    """
    
    year = target_date.year
    month = target_date.month
    
    # 1. Total Calendar Days
    days_in_month = monthrange(year, month)[1]
    total_calendar_days = Decimal(days_in_month)
    month_end_date = target_date.replace(day=days_in_month)
    
    current_date = target_date
    paid_days_count = Decimal('0.0')
    
    # 2. Fetch Static Paid Days Sources
    weekly_holidays = set(
        WeeklyHoliday.objects.filter(is_active=True).values_list('day', flat=True)
    )
    
    # 3. Fetch Public Holidays
    public_holiday_dates = set()
    ph_queryset = PublicHoliday.objects.filter(
        start_date__lte=month_end_date,
        end_date__gte=target_date
    )
    for ph in ph_queryset:
        day = ph.start_date
        while day <= ph.end_date:
            if day.month == month:
                 public_holiday_dates.add(day)
            day += timedelta(days=1)

    # 4. Fetch Approved Paid Leave
    # Filter for APPROVED status leaves within the month
    approved_paid_leaves_queryset = LeaveApplication.objects.filter(
        employee=employee,
        status=LeaveStatus.APPROVED, 
        # Assuming all LeaveTypes are considered 'paid' once approved (adjust if needed)
        from_date__lte=month_end_date,
        to_date__gte=target_date
    )
    
    approved_paid_leave_dates = set()
    for leave in approved_paid_leaves_queryset:
        day = leave.from_date
        while day <= leave.to_date:
            if day.month == month:
                approved_paid_leave_dates.add(day)
            day += timedelta(days=1)
            
    # 5. Fetch Actual Attendance
    present_dates = set(
        Attendance.objects.filter(
            employee=employee,
            attendance_date__year=year,
            attendance_date__month=month,
            is_present=True 
        ).values_list('attendance_date', flat=True)
    )

    
    # 6. Day-by-Day Reconciliation (Counting Paid Days)
    
    while current_date <= month_end_date:
        if current_date.month == month:
            # Check the day name (e.g., 'Monday', 'Tuesday')
            day_name = current_date.strftime('%A') 
            
            is_paid_day = False
            
            # Priority Check 1: Statutory Holidays/Offs (Paid regardless of presence)
            if day_name in weekly_holidays or current_date in public_holiday_dates:
                is_paid_day = True
            
            # Priority Check 2: Approved Leave (Paid)
            elif current_date in approved_paid_leave_dates:
                is_paid_day = True
            
            # Priority Check 3: Actual Work Done (Present)
            elif current_date in present_dates:
                is_paid_day = True
                
            # --- Final Tally ---
            if is_paid_day:
                paid_days_count += Decimal('1.0')
            
        current_date += timedelta(days=1)
        
    # 7. Unpaid Days Calculation
    unpaid_absence_days = total_calendar_days - paid_days_count
    
    return max(Decimal('0.0'), unpaid_absence_days)




class SinglePaySlipGenerateRetrieveAPIView(APIView):
    
    permission_classes = [IsAuthenticated] 
    
    def _calculate_monthly_tax(self, employee, taxable_income):
        """
        Calculates the monthly TDS/Tax based on Annual Tax Slabs.
        Uses cumulative fixed amounts from previous slabs correctly.
        """
        if taxable_income <= 0:
            return Decimal('0.00')

        # 1. Employee Data
        gender = employee.profile.gender if employee.profile and employee.profile.gender else 'MALE'
        annual_taxable_income = taxable_income * Decimal('12.0')
        
        # 2. Fetch Rules
        # NOTE: It is critical that TaxRule.taxable_amount_fixed stores the CUMULATIVE tax 
        # up to that slab's limit.
        tax_rules = TaxRule.objects.filter(
            gender=gender, 
            is_active=True
        ).order_by('total_income_limit')

        total_annual_tax = Decimal('0.00')
        previous_limit = Decimal('0.00')
        
        # 3. Slab-by-Slab Calculation
        for i, rule in enumerate(tax_rules):
            current_limit = rule.total_income_limit
            tax_rate = rule.tax_rate_percentage
            
            # --- Check 1: Income falls COMPLETELY ABOVE this slab ---
            if annual_taxable_income > current_limit:
                
                # If the income exceeds the slab limit, we accumulate the fixed tax for this slab.
                # NOTE: Assuming rule.taxable_amount_fixed is the CUMULATIVE tax up to current_limit.
                # If it's a REMAINING rule, it shouldn't have a fixed amount, so we handle it next.
                
                if rule.slab_type == 'REMAINING':
                    # This should ideally be the last rule. Tax the rest of the income.
                    taxable_in_slab = annual_taxable_income - previous_limit
                    tax_in_slab = (taxable_in_slab * tax_rate) / Decimal('100.0')
                    total_annual_tax += tax_in_slab
                    break # Calculation finished

                # If it's a NEXT/FIXED slab, update the total tax to the cumulative tax amount
                # and set previous_limit for the next iteration.
                total_annual_tax = rule.taxable_amount_fixed
                previous_limit = current_limit
                
            # --- Check 2: Income falls WITHIN this slab (The Stopping Point) ---
            elif annual_taxable_income > previous_limit:
                
                # 1. Pichle slabs ka CUMULATIVE FIXED TAX jodo.
                # Yeh tax pichle rule ke 'taxable_amount_fixed' mein store hona chahiye.
                tax_from_previous_slabs = Decimal('0.00')
                if i > 0:
                    # Access the CUMULATIVE tax fixed amount from the *previous* rule
                    tax_from_previous_slabs = tax_rules[i-1].taxable_amount_fixed
                    
                # Total annual tax is now set to the cumulative tax up to the previous limit
                total_annual_tax = tax_from_previous_slabs
                
                # 2. Current slab mein kitni income aayi?
                taxable_in_current_slab = annual_taxable_income - previous_limit
                
                # 3. Tax calculate karein aur jodo
                tax_in_slab = (taxable_in_current_slab * tax_rate) / Decimal('100.0')
                total_annual_tax += tax_in_slab
                
                # Calculation complete
                break 

            # --- Check 3: Income is below the current slab's starting limit ---
            # If income is below the minimum taxable limit, loop finishes and total_annual_tax remains 0.
            
        # 4. Monthly Tax
        monthly_tax = total_annual_tax / Decimal('12.0')
        return round(monthly_tax, 2)


    

    def _generate_payslip(self, employee, target_date, requesting_user):
        """ The core calculation logic, fixed for caps and consistent deductions, 
            using the MonthlyPayGrade.overtime_rate as the fixed hourly pay rate.
        """
        
        if not employee.profile or not employee.profile.monthly_pay_grade:
            raise ValueError("Employee profile or assigned Monthly Pay Grade is missing.")
            
        pay_grade = employee.profile.monthly_pay_grade
        master_basic_salary = pay_grade.basic_salary
        
        # --- STEP 1 & 2: Base Figures & Cuts ---
        year, month = target_date.year, target_date.month
        days_in_month = Decimal(monthrange(year, month)[1])
        if days_in_month == 0: raise ValueError("Invalid month range calculation.")
            
        per_day_rate_basic = master_basic_salary / days_in_month 
        per_hour_rate = per_day_rate_basic / Decimal('8.0') # Still needed for Late Deduction calculation base

        late_count = Attendance.objects.filter(
            employee=employee, attendance_date__year=year, attendance_date__month=month, is_late=True
        ).count()
        
        late_deduction_amount = Decimal('0.00')
        late_rule = LateDeductionRule.objects.filter(
            late_days_threshold__lte=late_count 
        ).order_by('-late_days_threshold').first()
        
        if late_rule:
            late_deduction_days = late_rule.deduction_days
            late_deduction_amount = late_deduction_days * per_day_rate_basic
            
        unpaid_absence_days = _calculate_unpaid_days(employee, target_date)
        unjustified_cut_amount = unpaid_absence_days * per_day_rate_basic
        
        # --- STEP 3: Adjusted Earning Calculation (Pro-Rata & Overtime) ---
        
        # Summing up all overtime_duration for the month
        total_ot_duration = Attendance.objects.filter(
            employee=employee, attendance_date__year=year, attendance_date__month=month,
        ).aggregate(total_ot=Sum('overtime_duration'))['total_ot'] or timedelta(0)
        
        # 🛑 FIX: Use Pay Grade's overtime_rate directly as the HOURLY PAY RATE
        ot_hourly_rate = pay_grade.overtime_rate 

        # Check for valid rate
        if ot_hourly_rate is None or ot_hourly_rate <= Decimal('0.00'):
            overtime_pay_amount = Decimal('0.00')
        else:
            # Calculate Total Hours from the summed timedelta
            total_ot_hours = Decimal(total_ot_duration.total_seconds() / 3600)

            # Calculation: Total Hours * Fixed Hourly Rate (No per_hour_rate multiplication)
            overtime_pay_amount = total_ot_hours * ot_hourly_rate
            
        overtime_pay_amount = round(overtime_pay_amount, 2)
        
        # Final Basic Salary Calculation (Pro-Rata)
        final_basic_salary = master_basic_salary - unjustified_cut_amount 
        final_basic_salary = round(final_basic_salary, 2)

        total_allowances_sum = Decimal('0.00')
        standard_deductions_sum = Decimal('0.00') 
        allowance_details = []
        deduction_details = []
        
        # Standard Allowances: Calculate on Adjusted Basic (Pro-Rata Allowance)
        for pg_allowance in pay_grade.paygradeallowance_set.select_related('allowance').all():
            calculated_amount = final_basic_salary * (pg_allowance.value / 100) 
            
            limit = pg_allowance.allowance.limit_per_month
            
            if limit is not None and limit > Decimal('0.00'):
                amount = min(calculated_amount, limit)
            else:
                amount = calculated_amount
            
            amount = round(amount, 2)
            total_allowances_sum += amount
            allowance_details.append({'item_name': pg_allowance.allowance.allowance_name, 'amount': amount})

        final_gross_salary = final_basic_salary + total_allowances_sum + overtime_pay_amount
        final_gross_salary = round(final_gross_salary, 2)

        # Standard Deductions (PF, ESI): Calculate on Adjusted Basic
        for pg_deduction in pay_grade.paygradededuction_set.select_related('deduction').all():
            calculated_amount = final_basic_salary * (pg_deduction.value / 100) 
            
            limit = pg_deduction.deduction.limit_per_month 
            
            if limit is not None and limit > Decimal('0.00'):
                amount = min(calculated_amount, limit)
            else:
                amount = calculated_amount
            
            amount = round(amount, 2)
            standard_deductions_sum += amount
            deduction_details.append({'item_name': pg_deduction.deduction.deduction_name, 'amount': amount})
        
        # 3. TAX DEDUCTION (TDS)
        tax_amount = self._calculate_monthly_tax(employee, final_gross_salary) 
        standard_deductions_sum += tax_amount
        if tax_amount > 0:
            deduction_details.append({'item_name': 'Income Tax (TDS)', 'amount': tax_amount})
            
        # --- STEP 4: FINAL NET CALCULATION ---

        total_deductions_for_net = standard_deductions_sum + late_deduction_amount 
        
        final_net_salary = final_gross_salary - total_deductions_for_net
        final_net_salary = round(final_net_salary, 2)

        # --- STEP 5: Store PaySlip and Details ---
        
        with transaction.atomic():
            payslip, created = PaySlip.objects.update_or_create(
                employee=employee, payment_month=target_date,
                defaults={
                    'basic_salary': final_basic_salary, 
                    'total_overtime_pay': overtime_pay_amount,    
                    'total_tax_deduction': tax_amount,
                    'total_allowances': total_allowances_sum, 
                    'total_deductions': total_deductions_for_net + unjustified_cut_amount, 
                    'gross_salary': final_gross_salary,
                    'net_salary': final_net_salary,
                    'total_days_in_month': days_in_month,
                    'working_days': days_in_month - unpaid_absence_days, 
                    'unjustified_absence': unpaid_absence_days,
                    'late_attendance_count': late_count,
                    'status': 'Calculated',
                    'generated_by': requesting_user
                }
            )

            payslip.details.all().delete()
            
            # Store Allowances (Standard)
            for item in allowance_details:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Allowance', **item)
            
            # Store Overtime Pay separately
            if overtime_pay_amount > 0:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Allowance', item_name='Overtime Pay', amount=overtime_pay_amount)
            
            # Store Standard Deductions and Tax
            for item in deduction_details:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Deduction', **item)

            # Store Transactional Cuts (Late Cut)
            if late_deduction_amount > 0:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Deduction', item_name=f'Late Attendance Cut ({late_count} Lates)', amount=late_deduction_amount)
            
            # Store Absence Cut for transparency only 
            if unjustified_cut_amount > 0:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Deduction', item_name='Unjustified Absence Cut (Days Not Paid)', amount=unjustified_cut_amount)
                
            return payslip
                    
    def post(self, request):
        """ Triggers the payslip calculation and storage. """
        
        employee_id = request.data.get('employee_id')
        month_str = request.data.get('month') 
        
        if not employee_id or not month_str:
             return Response({"error": "Employee ID and Month (YYYY-MM) are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = get_object_or_404(User, pk=employee_id)
            target_date = datetime.strptime(month_str, '%Y-%m').date().replace(day=1)
        except Exception:
            return Response({"error": "Invalid employee ID or month format."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            payslip_record = self._generate_payslip(employee, target_date, request.user)
            return Response({"message": "Payslip generated successfully.", "payslip_id": payslip_record.pk}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Payslip generation failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        """ Retrieve a specific payslip by PK (Payslip ID). """
        
        payslip = get_object_or_404(
            PaySlip.objects.select_related(
                'employee__profile__designation', 'employee__profile__department'
            ).prefetch_related('details'),
            pk=pk
        )
        
        serializer = PaySlipDetailSerializer(payslip)
        return Response(serializer.data)
    



class MonthlySalarySheetView(APIView):
    """ Lists payment status and gross salary for all employees with Pagination. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        filter_serializer = MonthlySalaryFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        target_date = filter_serializer.validated_data['month']

        # 1. Base Employee QuerySet
        employees_queryset = User.objects.filter(profile__status='Active').select_related('profile__pay_grade', 'profile').order_by('profile__full_name')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(employees_queryset, request, view=self)
        
        # 2. Payslip Prefetching (Only for paginated employees)
        # Payslip records ko sirf current page ke employee IDs ke liye fetch karo
        employee_ids_on_page = [e.id for e in page]
        
        payslips_queryset = PaySlip.objects.filter(
            payment_month=target_date,
            employee_id__in=employee_ids_on_page # Filter by paginated IDs
        ).prefetch_related('details')
        
        payslips_map = {p.employee_id: p for p in payslips_queryset}

        output = []
        # 3. Loop through the paginated list ('page')
        for employee in page: # Loop now runs only for 10-20 employees
            profile = employee.profile
            payslip = payslips_map.get(employee.id)
            
            pay_grade_name = profile.pay_grade.grade_name if profile.pay_grade else 'N/A'
            
            overtime_pay = Decimal('0.00')
            tax_deduction = Decimal('0.00')
            
            if payslip:
                for detail in payslip.details.all():
                    if detail.item_type == 'Allowance' and detail.item_name == 'Overtime Pay':
                        overtime_pay = detail.amount
                    elif detail.item_type == 'Deduction' and detail.item_name == 'Income Tax (TDS)':
                        tax_deduction = detail.amount

            output.append({
                "payslip_id": payslip.pk if payslip else None,
                "employee_name": profile.full_name,
                "pay_grade": pay_grade_name,
                "gross_salary": payslip.gross_salary if payslip else Decimal('0.00'), 
                "overtime_pay": overtime_pay,                      
                "tax_deduction": tax_deduction,                   
                "status": payslip.status if payslip else 'Pending',
                "action": "Generate Payslip" if not payslip or payslip.status == 'Pending' else "View/Re-Generate"
            })

        return paginator.get_paginated_response(output)


class ChangePasswordView(APIView):
    """
    Allows a logged-in user to change their password via POST request.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Serializer को context में request pass करें
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"message": "Password changed successfully. Please log in again with your new password."},
                status=status.HTTP_200_OK
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





class CSVAttendanceUploadView(APIView):
    """
    Handles bulk attendance upload via CSV file.
    Expects columns: employee_id, target_date (YYYY-MM-DD), punch_in_time (HH:MM:SS), punch_out_time (HH:MM:SS)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file was submitted. Please upload a file with the key 'file'."}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return Response({"error": "File must be a CSV format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode file contents using 'utf-8' and handle IO
            file_data = csv_file.read().decode("utf-8")
        except UnicodeDecodeError:
            return Response({"error": "File encoding issue. Please ensure the file is saved as UTF-8."}, status=status.HTTP_400_BAD_REQUEST)
        
        io_string = io.StringIO(file_data)
        
        # Skip the header row (assuming the first row is the header)
        try:
             next(io_string) 
        except StopIteration:
             return Response({"error": "The uploaded CSV file is empty."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.reader(io_string)
        
        successful_records = []
        failed_records = []
        
        # Use transaction.atomic for database integrity
        with transaction.atomic():
            for i, row in enumerate(reader):
                row_number = i + 2 # Accounting for 0-based index and header row

                # Check if row has expected number of fields (Employee ID, Date, In, Out)
                if len(row) < 4:
                    failed_records.append({"row": row_number, "error": "Missing required data (expected at least 4 columns)."})
                    continue
                
                # Strip whitespace from fields
                row = [item.strip() for item in row]
                
                # Prepare data structure for serializer validation
                data = {
                    'employee_id': row[0],
                    'target_date': row[1],
                    'punch_in_time': row[2] if row[2] else None, # Handle blank time strings
                    'punch_out_time': row[3] if row[3] else None,
                }
                
                serializer = CSVAttendanceInputSerializer(data=data)
                
                if not serializer.is_valid():
                    failed_records.append({"row": row_number, "employee_id": row[0], "errors": serializer.errors})
                    continue
                
                validated_data = serializer.validated_data
                
                # --- Database Lookup ---
                emp_id_str = validated_data['employee_id']
                target_date = validated_data['target_date']
                punch_in_str = validated_data['punch_in_time']
                punch_out_str = validated_data['punch_out_time']
                
                try:
                    # Lookup Profile by the string employee_id (Fingerprint/Emp No.)
                    employee_profile = Profile.objects.select_related('user', 'work_shift').get(employee_id=emp_id_str)
                    employee = employee_profile.user
                except Profile.DoesNotExist:
                    failed_records.append({"row": row_number, "employee_id": emp_id_str, "error": "Employee ID (fingerprint number) not found."})
                    continue
                
                
                # --- Timezone Aware Datetime Creation ---
                punch_in, punch_out = None, None
                local_tz = timezone.get_current_timezone()

                if punch_in_str:
                    try:
                        # Combine validated date (Date object) with validated time string
                        punch_in_dt_naive = datetime.combine(target_date, datetime.strptime(punch_in_str, "%H:%M:%S").time())
                        punch_in = timezone.make_aware(punch_in_dt_naive, timezone=local_tz)
                    except ValueError as e:
                         failed_records.append({"row": row_number, "employee_id": emp_id_str, "error": f"Error parsing Punch In Time: {e}"})
                         continue

                if punch_out_str:
                    try:
                        punch_out_dt_naive = datetime.combine(target_date, datetime.strptime(punch_out_str, "%H:%M:%S").time())
                        punch_out = timezone.make_aware(punch_out_dt_naive, timezone=local_tz)
                    except ValueError as e:
                         failed_records.append({"row": row_number, "employee_id": emp_id_str, "error": f"Error parsing Punch Out Time: {e}"})
                         continue

                
                # --- Get or Create Attendance Record ---
                attendance_record, created = Attendance.objects.get_or_create(
                    employee=employee,
                    attendance_date=target_date,
                    # Provide defaults for fields only when creating
                    defaults={'punch_in_time': punch_in, 'punch_out_time': punch_out}
                )
                
                # Update times if record already existed or was just created
                attendance_record.punch_in_time = punch_in
                attendance_record.punch_out_time = punch_out
                    
                # --- Re-run Calculation and Save (Same logic as ManualAttendanceView.patch) ---
                if punch_in:
                    
                    # Basic validation: Punch Out must be after Punch In
                    if punch_out and punch_out <= punch_in:
                        failed_records.append({"row": row_number, "employee_id": emp_id_str, "error": "Punch Out Time must be after Punch In Time."})
                        continue

                    # Call the fixed calculation function
                    (total_work_duration, is_late_calculated, late_duration, overtime_duration) = \
                        calculate_attendance_status_and_times(attendance_record, employee_profile)

                    # Update fields based on calculation
                    attendance_record.total_work_duration = total_work_duration
                    attendance_record.overtime_duration = overtime_duration
                    attendance_record.late_duration = late_duration
                    attendance_record.is_late = is_late_calculated
                    attendance_record.is_present = True
                    attendance_record.status = 'Completed' if punch_out else 'Single Punch'
                else:
                    # If punch-in is missing/removed, mark absent
                    attendance_record.total_work_duration = None
                    attendance_record.overtime_duration = timedelta(0)
                    attendance_record.late_duration = timedelta(0)
                    attendance_record.is_present = False
                    attendance_record.is_late = False
                    attendance_record.status = 'Absent'

                attendance_record.save()
                successful_records.append(f"Row {row_number} (ID: {emp_id_str})")

        # --- Final Response ---
        response_message = {
            "status": "partial_success" if failed_records else "success",
            "message": f"Successfully processed {len(successful_records)} records. {len(failed_records)} records failed.",
            "successful_rows_count": len(successful_records),
            "failed_records_count": len(failed_records),
            "failed_records": failed_records
        }
        
        if failed_records:
            return Response(response_message, status=status.HTTP_207_MULTI_STATUS) 
        
        return Response(response_message, status=status.HTTP_200_OK)
    


class RoleListView(APIView):
    """
    Handles GET (List all Roles) and POST (Create a new Role).
    Access restricted to authenticated Admin users (is_staff=True).
    """
    permission_classes = [IsAuthenticated]

    # --- GET: List all Roles ---
    def get(self, request, format=None):
        roles = Role.objects.all().order_by('name')
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    # --- POST: Create a new Role ---
    def post(self, request, format=None):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            # Role ko save karo
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Validation error hone par
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RoleDetailView(APIView):
    """
    Handles GET (Retrieve), PUT/PATCH (Update), and DELETE (Delete) for a single Role instance.
    Access restricted to authenticated Admin users (is_staff=True).
    """
    permission_classes = [IsAuthenticated]

    # Helper function to get the object, returns 404 if not found
    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    # --- GET: Retrieve Role Detail ---
    def get(self, request, pk, format=None):
        role = self.get_object(pk)
        # Check if the helper returned an error response
        if isinstance(role, Response):
            return role
            
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    # --- PUT/PATCH: Update Role ---
    def put(self, request, pk, format=None):
        role = self.get_object(pk)
        if isinstance(role, Response):
            return role
            
        # partial=True for PATCH requests, but PUT typically uses full update
        serializer = RoleSerializer(role, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE: Delete Role ---
    def delete(self, request, pk, format=None):
        role = self.get_object(pk)
        if isinstance(role, Response):
            return role
            
        # Simple deletion as requested (no safety checks)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)