from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from users.models import Education,Experience,User,Profile,Role,AccountDetails
from .models import Department,Designation, Branch,Warning,Termination,Promotion,Holiday,WeeklyHoliday,LeaveType,EarnLeaveRule,PublicHoliday,LeaveApplication,WorkShift, LeaveBalance,\
Attendance,Allowance,Deduction,MonthlyPayGrade,PerformanceCategory,PerformanceCriteria,EmployeePerformance,PerformanceRating,JobPost,TrainingType,EmployeeTraining,Award,Notice,LateDeductionRule,TaxRule,\
PaySlip,PaySlipDetail,BonusSetting,EmployeeBonus
from .serializers import DepartmentSerializer,DesignationSerializer,EducationSerializer,EmployeeCreateSerializer,ExperienceSerializer,EmployeeListSerializer,EmployeeDetailSerializer
DepartmentSerializer, DesignationSerializer,
from django.db.models import Sum
from users.enums import LeaveStatus,GenderChoices
from .serializers import WarningSerializer,TerminationSerializer,PromotionSerializer,EmployeeJobStatusSerializer,HolidaySerializer,PublicHolidaySerializer,EarnLeaveRuleSerializer    
from .serializers import LeaveTypeSerializer,WeeklyHolidaySerializer,LeaveApplicationListSerializer,LeaveApplicationCreateSerializer,LeaveReportSerializer,WorkShiftSerializer, \
ManualAttendanceFilterSerializer,ManualAttendanceInputSerializer,AttendanceReportFilterSerializer,DailyAttendanceFilterSerializer,MonthlySummaryFilterSerializer,\
BranchSerializer,AllowanceSerializer,DeductionSerializer,MonthlyPayGradeSerializer,HourlyPayGradeSerializer,HourlyPayGrade,PerformanceCategorySerializer,PerformanceCriteriaSerializer,\
EmployeePerformanceSerializer,PerformanceSummarySerializer,JobPostSerializer,TrainingTypeSerializer,EmployeeTrainingSerializer,AwardSerializer,NoticeSerializer,LateDeductionRuleSerializer,TaxRuleSerializer,\
PaySlipDetailSerializer,MonthlySalaryFilterSerializer,BulkSalaryFilterSerializer,ChangePasswordSerializer,CSVAttendanceInputSerializer,RoleSerializer,AutomaticAttendanceInputSerializer,BonusSettingSerializer,EmployeeBonusSerializer,GenerateBonusFilterSerializer,\
MarkPaymentPaidSerializer,AccountDetailsSerializer
from django.http import HttpResponse
import numpy as np
import base64
import cv2
import face_recognition
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
from django.utils import timezone
from django.core.files.base import ContentFile
import io
from .utils import apply_auto_close_if_needed, calculate_attendance_status_and_times, format_duration, get_expected_working_dates_list,calculate_summary_stats,deserialize_face_encoding,determine_attendance_date
from datetime import date

class DepartmentListCreateView(APIView):
    """
    Departments ki list dekhein (Pagination aur Search ke saath) ya naya department banayein.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import filter_by_company
        
        queryset = Department.objects.all().order_by('name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # 3. Pagination Apply karna
        paginator = StandardResultsSetPagination()
        
        # Queryset ko paginator ko dein
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        # 4. Serialization
        # Serializer ko sirf current page ke items par apply karein
        serializer = DepartmentSerializer(page, many=True, context={'request': request})
        
        # 5. Response mein paginated data return karna
        # Yeh method metadata (count, next, previous) ke saath data return karta hai
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            # Filter by company
            departments = Department.objects.filter(pk=pk)
            departments = filter_by_company(departments, self.request.user)
            department = departments.first()
            
            if not department:
                raise Http404
            return department
        except Department.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True, context={'request': request})
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
        from company.utils import filter_by_company
        
        queryset = Designation.objects.select_related('department').all().order_by('department__name', 'name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )
            
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = DesignationSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = DesignationSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            designations = Designation.objects.filter(pk=pk)
            designations = filter_by_company(designations, self.request.user)
            designation = designations.first()
            
            if not designation:
                raise Http404
            return designation
        except Designation.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        designation = self.get_object(pk)
        serializer = DesignationSerializer(designation, data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        queryset = Branch.objects.all().order_by('name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )
            
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = BranchSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BranchSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        from company.utils import filter_by_company
        
        try:
            branches = Branch.objects.filter(pk=pk)
            branches = filter_by_company(branches, self.request.user)
            branch = branches.first()
            
            if not branch:
                raise Http404
            return branch
        except Branch.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch, data=request.data, context={'request': request})
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
        from company.utils import get_company_users
        
        # 1. Get company users (includes owner + employees)
        company_users = get_company_users(request.user)
        
        # 2. Fetch Profiles for company users
        queryset = Profile.objects.select_related(
            'user', 
            'department', 
            'designation', 
            'monthly_pay_grade', 
            'hourly_pay_grade',
            'branch'
        ).filter(user__in=company_users).order_by('first_name')
        
        # 3. Filtering Logic
        role_filter = request.query_params.get('role', None)
        if role_filter:
            queryset = queryset.filter(user__role__name__iexact=role_filter)
            
        # Filter by Department ID
        department_id = request.query_params.get('department_id', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
            
        # Filter by Designation ID
        designation_id = request.query_params.get('designation_id', None)
        if designation_id:
            queryset = queryset.filter(designation_id=designation_id)

        # Filter by Status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)

        # 4. Search Logic
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(employee_id__icontains=search_query) 
            )
            
        # 5. Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        # 6. Serialization
        serializer = EmployeeListSerializer(page, many=True, context={'request': request})
        
        # 7. Response
        return paginator.get_paginated_response(serializer.data)

class EmployeeCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data, context={'request': request})
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
        from company.utils import get_company_users
        
        try:
            # Get company users to verify access
            company_users = get_company_users(self.request.user)
            
            # Fetch profile and verify it belongs to company
            profile = Profile.objects.select_related('user').get(user__pk=pk)
            
            # Check if user belongs to the same company
            if profile.user not in company_users:
                raise Http404
                
            return profile
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
        from company.utils import get_company_users
        
        # Verify employee belongs to same company
        company_users = get_company_users(self.request.user)
        
        try:
            profile = Profile.objects.select_related('user').get(user__pk=employee_pk)
            
            if profile.user not in company_users:
                raise Profile.DoesNotExist
                
            return profile
        except Profile.DoesNotExist:
            raise Profile.DoesNotExist

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

        serializer = EducationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeEducationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, employee_pk, education_pk):
        from company.utils import get_company_users
        
        # Verify employee belongs to same company
        company_users = get_company_users(self.request.user)
        
        try:
            education = Education.objects.select_related('profile__user').get(
                pk=education_pk, 
                profile__user__pk=employee_pk
            )
            
            if education.profile.user not in company_users:
                raise Education.DoesNotExist
                
            return education
        except Education.DoesNotExist:
            raise Education.DoesNotExist

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
        from company.utils import get_company_users
        
        # Verify employee belongs to same company
        company_users = get_company_users(self.request.user)
        
        try:
            profile = Profile.objects.select_related('user').get(user__pk=employee_pk)
            
            if profile.user not in company_users:
                raise Profile.DoesNotExist
                
            return profile
        except Profile.DoesNotExist:
            raise Profile.DoesNotExist

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

        serializer = ExperienceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeExperienceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, employee_pk, experience_pk):
        from company.utils import get_company_users
        
        # Verify employee belongs to same company
        company_users = get_company_users(self.request.user)
        
        try:
            experience = Experience.objects.select_related('profile__user').get(
                pk=experience_pk, 
                profile__user__pk=employee_pk
            )
            
            if experience.profile.user not in company_users:
                raise Experience.DoesNotExist
                
            return experience
        except Experience.DoesNotExist:
            raise Experience.DoesNotExist

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



# Account Details Views
class EmployeeAccountDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, employee_pk):
        from company.utils import get_company_users
        
        # Verify employee belongs to same company
        company_users = get_company_users(self.request.user)
        
        try:
            profile = Profile.objects.select_related('user').get(user__pk=employee_pk)
            
            if profile.user not in company_users:
                raise Profile.DoesNotExist
                
            return profile
        except Profile.DoesNotExist:
            raise Profile.DoesNotExist

    def get(self, request, employee_pk):
        try:
            profile = self.get_profile(employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

        account_details = profile.account_details.all()
        serializer = AccountDetailsSerializer(account_details, many=True)
        return Response(serializer.data)

    def post(self, request, employee_pk):
        try:
            profile = self.get_profile(employee_pk)
        except Profile.DoesNotExist:
            return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDetailsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeAccountDetailsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, employee_pk, account_pk):
        from company.utils import get_company_users
        
        # Verify employee belongs to same company
        company_users = get_company_users(self.request.user)
        
        try:
            account_detail = AccountDetails.objects.select_related('profile__user').get(
                pk=account_pk, 
                profile__user__pk=employee_pk
            )
            
            if account_detail.profile.user not in company_users:
                raise AccountDetails.DoesNotExist
                
            return account_detail
        except AccountDetails.DoesNotExist:
            raise AccountDetails.DoesNotExist

    def get(self, request, employee_pk, account_pk):
        try:
            account_detail = self.get_object(employee_pk, account_pk)
        except:
            return Response({"error": "Account detail not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDetailsSerializer(account_detail)
        return Response(serializer.data)

    def put(self, request, employee_pk, account_pk):
        return self.patch(request, employee_pk, account_pk)

    def patch(self, request, employee_pk, account_pk):
        try:
            account_detail = self.get_object(employee_pk, account_pk)
        except:
            return Response({"error": "Account detail not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDetailsSerializer(account_detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee_pk, account_pk):
        try:
            account_detail = self.get_object(employee_pk, account_pk)
        except:
            return Response({"error": "Account detail not found"}, status=status.HTTP_404_NOT_FOUND)

        account_detail.delete()
        return Response({"message": "Account detail deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class WarningListCreateView(APIView):
    """
    List all warnings or create a new warning.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import filter_by_employee_company
        
        queryset = Warning.objects.select_related(
            'warning_to__profile', 
            'warning_by__profile'
        ).all().order_by('-warning_date', '-id')
        
        # Filter by company through warning_to (employee)
        queryset = filter_by_employee_company(queryset, request.user, 'warning_to')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(warning_to__profile__full_name__icontains=search_query) |
                Q(subject__icontains=search_query)                          
            )
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = WarningSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
    
    def post(self, request):
        serializer = WarningSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        try:
            queryset = Warning.objects.filter(pk=pk)
            queryset = filter_by_employee_company(queryset, self.request.user, 'warning_to')
            warning = queryset.first()
            
            if not warning:
                raise Http404
            return warning
        except Warning.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        warning = self.get_object(pk)
        serializer = WarningSerializer(warning, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        warning = self.get_object(pk)
        serializer = WarningSerializer(warning, data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        queryset = Termination.objects.select_related(
            'terminate_to__profile', 
            'terminate_by__profile'
        ).all().order_by('-termination_date', '-id')
        
        # Filter by company through terminate_to (employee)
        queryset = filter_by_employee_company(queryset, request.user, 'terminate_to')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(terminate_to__profile__full_name__icontains=search_query) |
                Q(subject__icontains=search_query)                             
            )
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = TerminationSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TerminationSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        try:
            queryset = Termination.objects.filter(pk=pk)
            queryset = filter_by_employee_company(queryset, self.request.user, 'terminate_to')
            termination = queryset.first()
            
            if not termination:
                raise Http404
            return termination
        except Termination.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        termination = self.get_object(pk)
        serializer = TerminationSerializer(termination, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        termination = self.get_object(pk)
        serializer = TerminationSerializer(termination, data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        queryset = Promotion.objects.select_related(
            'employee__profile', 
            'promoted_department',
            'promoted_designation'
        ).all().order_by('-promotion_date', '-id')
        
        # Filter by company through employee
        queryset = filter_by_employee_company(queryset, request.user, 'employee')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__profile__full_name__icontains=search_query)
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PromotionSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PromotionSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        try:
            queryset = Promotion.objects.filter(pk=pk)
            queryset = filter_by_employee_company(queryset, self.request.user, 'employee')
            promotion = queryset.first()
            
            if not promotion:
                raise Http404
            return promotion
        except Promotion.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionSerializer(promotion, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionSerializer(promotion, data=request.data, context={'request': request})
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
        from company.utils import get_company_users
        
        # ✅ MULTI-TENANCY: Filter by company
        company_users = get_company_users(request.user)
        
        try:
            # Find the profile of the employee using their user ID (pk)
            profile = Profile.objects.get(user__pk=pk, user__in=company_users)
        except Profile.DoesNotExist:
            return Response({"error": "Employee not found or does not belong to your company."}, status=status.HTTP_404_NOT_FOUND)
        
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
        from company.utils import filter_by_company
        
        queryset = Holiday.objects.all().order_by('name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = HolidaySerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = HolidaySerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            holidays = Holiday.objects.filter(pk=pk)
            holidays = filter_by_company(holidays, self.request.user)
            holiday = holidays.first()
            
            if not holiday:
                raise Http404
            return holiday
        except Holiday.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        holiday = self.get_object(pk)
        serializer = HolidaySerializer(holiday, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        holiday = self.get_object(pk)
        serializer = HolidaySerializer(holiday, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        holiday = self.get_object(pk)
        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicHolidayListCreateView(APIView):
    """
    Admin can list all public holidays with dates or create a new one.
    (Corresponds to "Public Holiday")
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ List all public holidays with search and pagination (Only by Holiday Name). """
        from company.utils import get_company_owner
        
        queryset = PublicHoliday.objects.select_related('holiday').all().order_by('start_date')  # Fixed: date -> start_date
        
        # Filter by company through holiday relationship
        if request.user.is_superuser:
            pass  # Superuser sees all
        else:
            company_owner = get_company_owner(request.user)
            if company_owner:
                queryset = queryset.filter(holiday__parent=company_owner)
            else:
                queryset = queryset.none()
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(holiday__name__icontains=search_query)  # Fixed: name -> holiday__name
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PublicHolidaySerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PublicHolidaySerializer(data=request.data, context={'request': request})
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
        from company.utils import get_company_owner
        
        try:
            company_owner = get_company_owner(self.request.user)
            
            if self.request.user.is_superuser:
                holiday = PublicHoliday.objects.filter(pk=pk).first()
            elif company_owner:
                holiday = PublicHoliday.objects.filter(
                    pk=pk,
                    holiday__parent=company_owner
                ).first()
            else:
                holiday = None
            
            if not holiday:
                raise Http404
            return holiday
        except PublicHoliday.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        holiday = self.get_object(pk)
        serializer = PublicHolidaySerializer(holiday, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        holiday = self.get_object(pk)
        serializer = PublicHolidaySerializer(holiday, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        holiday = self.get_object(pk)
        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WeeklyHolidayListCreateView(APIView):
    """
    Admin can list all weekly holidays or create a new one.
    (Corresponds to "Weekly Holiday")
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import filter_by_company
        
        queryset = WeeklyHoliday.objects.all().order_by('day')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(day__icontains=search_query) 
            )
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = WeeklyHolidaySerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        serializer = WeeklyHolidaySerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            holidays = WeeklyHoliday.objects.filter(pk=pk)
            holidays = filter_by_company(holidays, self.request.user)
            holiday = holidays.first()
            
            if not holiday:
                raise Http404
            return holiday
        except WeeklyHoliday.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        holiday = self.get_object(pk)
        serializer = WeeklyHolidaySerializer(holiday, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        holiday = self.get_object(pk)
        serializer = WeeklyHolidaySerializer(holiday, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        holiday = self.get_object(pk)
        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveTypeListCreateView(APIView):
    """
    Admin can list all leave types or create a new one.
    (MODIFIED: Auto-allocates balance to ALL active users upon creation)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import filter_by_company
        
        queryset = LeaveType.objects.all().order_by('name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) 
            )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = LeaveTypeSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = LeaveTypeSerializer(data=request.data, context={'request': request})
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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        from company.utils import filter_by_company
        
        try:
            leave_types = LeaveType.objects.filter(pk=pk)
            leave_types = filter_by_company(leave_types, self.request.user)
            leave_type = leave_types.first()
            
            if not leave_type:
                raise Http404
            return leave_type
        except LeaveType.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = LeaveTypeSerializer(item, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = LeaveTypeSerializer(item, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()  # now number_of_days update allowed
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EarnLeaveRuleView(APIView):
    """
    Manage single Earn Leave Rule per company.
    GET: Returns existing rule or creates with default (day_of_earn_leave=0)
    PUT: Updates rule (only day_of_earn_leave is editable)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import get_company_owner
        
        company_owner = get_company_owner(request.user)
        
        # Get or create rule for this company
        rule, created = EarnLeaveRule.objects.get_or_create(
            parent=company_owner,
            defaults={
                'for_month': 1,  # Fixed
                'day_of_earn_leave': 0,  # Default 0
                'created_by': request.user
            }
        )
        
        serializer = EarnLeaveRuleSerializer(rule, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        """Update existing rule (only day_of_earn_leave is editable)"""
        from company.utils import get_company_owner
        
        company_owner = get_company_owner(request.user)
        
        try:
            rule = EarnLeaveRule.objects.get(parent=company_owner)
        except EarnLeaveRule.DoesNotExist:
            return Response(
                {"error": "Earn leave rule not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EarnLeaveRuleSerializer(rule, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApplyForLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = request.user
        leave_balances = LeaveBalance.objects.filter(employee=employee)

        data = []
        for lb in leave_balances:
            used_days = LeaveApplication.objects.filter(
                employee=employee,
                leave_type=lb.leave_type,
                status=LeaveStatus.APPROVED
            ).aggregate(total=Sum("number_of_days"))['total'] or 0

            current_balance = lb.entitlement - used_days

            data.append({
                "leave_type_id": lb.leave_type.id,
                "leave_type_name": lb.leave_type.name,
                "entitlement": lb.entitlement,
                "used_days": used_days,
                "current_balance": max(0, current_balance)
            })

        return Response({
            "employee": employee.email,
            "leave_summary": data
        })

    def post(self, request):
        serializer = LeaveApplicationCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(employee=request.user)
            return Response(
                {"message": "Leave applied successfully! Pending approval."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MyLeaveApplicationsView(APIView):
    """
    Logged-in employee ki saari leave applications list karta hai (my01.png).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Employee's own leave applications (already filtered by employee=request.user)
        queryset = LeaveApplication.objects.filter(employee=request.user).order_by('-application_date')
        
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = LeaveApplicationListSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    

class AllLeaveApplicationsView(APIView):
    """
    Admin/Manager ke liye sabhi applications ki list dikhata hai.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from company.utils import filter_by_employee_company
        
        queryset = LeaveApplication.objects.all().order_by('-application_date')
        
        # Filter by company through employee
        queryset = filter_by_employee_company(queryset, request.user, 'employee')
        
        paginator = StandardResultsSetPagination()
        
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        serializer = LeaveApplicationListSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)


class LeaveApprovalView(APIView):
    """
    Admin/Manager endpoint to Approve or Reject a leave application (PK based).
    Includes logic to deduct balance from the LeaveBalance table upon approval.
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        from company.utils import filter_by_employee_company
        
        try:
            # ✅ MULTI-TENANCY: Verify leave application belongs to company
            applications = LeaveApplication.objects.filter(pk=pk)
            applications = filter_by_employee_company(applications, request.user, 'employee')
            application = applications.first()
            
            if not application:
                raise LeaveApplication.DoesNotExist
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
        from company.utils import filter_by_employee_company
        
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
        
        # Filter by company through employee relationship
        applications = filter_by_employee_company(applications, request.user, 'employee')
        
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
        from company.utils import get_company_owner, get_company_users
        
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
        
        # ✅ MULTI-TENANCY: Verify employee belongs to same company
        if not request.user.is_superuser:
            company_users = get_company_users(request.user)
            if not company_users.filter(id=target_employee.id).exists():
                return Response({"error": "Employee not found in your company."}, 
                                status=status.HTTP_403_FORBIDDEN)

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

    def get(self, request):
        from company.utils import filter_by_company
        
        queryset = WorkShift.objects.all().order_by('shift_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(shift_name__icontains=search_query) 
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = WorkShiftSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """ Create a new work shift """
        serializer = WorkShiftSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkShiftDetailAPIView(APIView):
    """
    Handles retrieving (GET), updating (PUT/PATCH), and deleting (DELETE) a specific shift.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        from company.utils import filter_by_company
        
        try:
            workshifts = WorkShift.objects.filter(pk=pk)
            workshifts = filter_by_company(workshifts, self.request.user)
            workshift = workshifts.first()
            
            if not workshift:
                raise Http404
            return workshift
        except WorkShift.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        """ Retrieve a specific shift """
        shift = self.get_object(pk)
        serializer = WorkShiftSerializer(shift)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        """ Update a specific shift (Full update) """
        shift = self.get_object(pk)
        serializer = WorkShiftSerializer(shift, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """ Delete a specific shift """
        shift = self.get_object(pk)
        shift.delete()
        return Response({"message": "Work Shift deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

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

        # CRITICAL FIX 1: Get the local timezone reference (Asia/Kolkata)
        local_tz = timezone.get_current_timezone() 
        
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
                
                # CRITICAL FIX 2: Apply Timezone Localization for Display
                punch_in_local = None
                if record.punch_in_time:
                    punch_in_local = record.punch_in_time.astimezone(local_tz).strftime('%H:%M:%S')

                punch_out_local = None
                if record.punch_out_time:
                    punch_out_local = record.punch_out_time.astimezone(local_tz).strftime('%H:%M:%S')
                
                output_data.append({
                    "Date": record.attendance_date,
                    "Employee Name": employee_profile.full_name, 
                    "In Time": punch_in_local if punch_in_local else '--', # <-- FIXED
                    "Out Time": punch_out_local if punch_out_local else '--', # <-- FIXED
                    "Working Time": format_duration(record.total_work_duration),
                    "Late": "Yes" if record.is_late else "No",
                    "Late Time": format_duration(record.late_duration),       
                    "Over Time": format_duration(record.overtime_duration),    
                    "Status": record.status if hasattr(record, 'status') else ("Present" if record.is_present else "Absent"),
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

        # CRITICAL FIX 1: Get the local timezone reference (Asia/Kolkata)
        local_tz = timezone.get_current_timezone() 
        
        # 1. Fetch the specific employee profile
        from company.utils import get_company_users
        
        try:
            employee = User.objects.get(pk=employee_id) if employee_id else None
            employee_profile = Profile.objects.select_related('work_shift').get(user=employee) if employee else None
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        if not employee:
            # Admin view requires filtering by employee ID to show a summary/detailed table
            return Response({"error": "Employee ID is required for detailed monthly report."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ MULTI-TENANCY: Verify employee belongs to same company
        if not request.user.is_superuser:
            company_users = get_company_users(request.user)
            if not company_users.filter(id=employee.id).exists():
                return Response({"error": "Employee not found in your company."}, 
                                status=status.HTTP_403_FORBIDDEN)

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
                
                # CRITICAL FIX 2: Apply Timezone Localization for Display
                punch_in_local = None
                if record.punch_in_time:
                    punch_in_local = record.punch_in_time.astimezone(local_tz).strftime('%H:%M:%S')

                punch_out_local = None
                if record.punch_out_time:
                    punch_out_local = record.punch_out_time.astimezone(local_tz).strftime('%H:%M:%S')
                
                output_data.append({
                    "Date": record.attendance_date,
                    "Employee Name": employee_profile.full_name,
                    "Designation": employee_profile.designation.name if employee_profile.designation else '--',
                    "In Time": punch_in_local if punch_in_local else '--', # <-- FIXED
                    "Out Time": punch_out_local if punch_out_local else '--', # <-- FIXED
                    "Working Time": format_duration(record.total_work_duration),
                    "Late": "Yes" if record.is_late else "No",
                    "Late Time": format_duration(record.late_duration),       
                    "Over Time": format_duration(record.overtime_duration),    
                    "Status": record.status if hasattr(record, 'status') else ("Present" if record.is_present else "Absent"),
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
        from company.utils import filter_by_company, get_company_users
        
        filter_serializer = ManualAttendanceFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        
        dept_id = data['department_id']
        target_date = data['target_date']
        
        # ✅ MULTI-TENANCY: Verify department belongs to company
        departments = Department.objects.filter(pk=dept_id)
        departments = filter_by_company(departments, request.user)
        if not departments.exists():
            return Response({"error": "Department not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get company users only
        company_users = get_company_users(request.user)
        
        employees_in_dept = Profile.objects.filter(
            department_id=dept_id, 
            user__in=company_users,  # ✅ Only company users (includes owner)
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
            punch_in = None
            if attendance_record and attendance_record.punch_in_time:
                punch_in = attendance_record.punch_in_time.strftime('%H:%M:%S')

            punch_out = None
            if attendance_record and attendance_record.punch_out_time:
                punch_out = attendance_record.punch_out_time.strftime('%H:%M:%S')

            # Use saved duration fields from the model
            
            # 💥 FIX/ADDITION: Include total_work_duration (Working Time) 💥
            total_work_duration_str = format_duration(attendance_record.total_work_duration) if attendance_record and attendance_record.total_work_duration else '00:00'
            
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
                "total_work_duration": total_work_duration_str, 
                "late_time": late_time,
                "overtime": overtime,
                "status": status_indicator, 
            })
            
        return Response(output)

    def patch(self, request):
        """ Manually updates a specific employee's attendance record and recalculates fields. """
        from company.utils import get_company_users
        
        serializer = ManualAttendanceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        employee_id = data['employee_id']
        target_date = data['target_date']
        
        try:
            employee = User.objects.get(pk=employee_id)
            employee_profile = Profile.objects.select_related('work_shift').get(user=employee)
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"error": f"Employee {employee_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # ✅ MULTI-TENANCY: Verify employee belongs to same company
        if not request.user.is_superuser:
            company_users = get_company_users(request.user)
            if not company_users.filter(id=employee.id).exists():
                return Response({"error": "You cannot modify attendance for employees from other companies."}, 
                                status=status.HTTP_403_FORBIDDEN)

        attendance_record, created = Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=target_date
        )

        punch_in_data = data.get('punch_in_time')
        punch_out_data = data.get('punch_out_time')
        
        # 1. Update raw punch times based on manual input
        if 'punch_in_time' in data:
            attendance_record.punch_in_time = punch_in_data
        if 'punch_out_time' in data:
            attendance_record.punch_out_time = punch_out_data
        
        # Flag to track if auto-close was executed
        is_auto_closed = False

        if attendance_record.punch_in_time:
            
            # 2. Punch Out validation
            if attendance_record.punch_out_time and attendance_record.punch_out_time <= attendance_record.punch_in_time:
                return Response({"error": "Punch Out Time must be after Punch In Time."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. APPLY AUTO-CLOSE RULE
            is_auto_closed = apply_auto_close_if_needed(attendance_record, employee_profile)
            
            # 4. Final Calculation (This is where all metrics are generated)
            (total_work_duration, 
             is_late_calculated, 
             late_duration,                
             overtime_duration) = calculate_attendance_status_and_times(attendance_record, employee_profile)
            
            # 5. Update Status and Metrics (Saving the calculated values to the model)
            attendance_record.late_duration = late_duration            
            attendance_record.is_late = is_late_calculated
            attendance_record.total_work_duration = total_work_duration # ✅ Working time saved
            attendance_record.overtime_duration = overtime_duration     
            attendance_record.is_present = True 

            # Set final status 
            if not is_auto_closed:
                attendance_record.status = 'Completed' if attendance_record.punch_out_time else 'Single Punch' 
            # Note: If is_auto_closed is True, the helper must set the status to 'Auto-Closed'

        else:
            # If Punch-in is removed or missing, reset all durations/status
            attendance_record.total_work_duration = None
            attendance_record.overtime_duration = timedelta(0)
            attendance_record.late_duration = timedelta(0)              
            
            attendance_record.is_present = data.get('is_present', False) 
            attendance_record.is_late = False 
            attendance_record.status = 'Pending' 
        
        attendance_record.save()
        
        # Return the updated calculated metrics to the frontend
        return Response({"message": f"Attendance record updated successfully for Employee {employee_id} on {target_date}.",
                        "total_work_duration": format_duration(attendance_record.total_work_duration), 
                        "late_time": format_duration(attendance_record.late_duration),   
                        "overtime": format_duration(attendance_record.overtime_duration),
                        "status": attendance_record.status}, 
                        status=status.HTTP_200_OK)


class AttendanceReportBaseView(APIView):
    # ... (Logic remains the same, used for Monthly and My Reports) ...
    permission_classes = [IsAuthenticated] 
    
    def get_filtered_attendance(self, request, employee_specific=False):
        from company.utils import get_company_users
        
        filter_serializer = AttendanceReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data
        
        filters = Q()
        filters &= Q(employee__profile__isnull=False)
        
        # ✅ MULTI-TENANCY: Filter by company users first
        if not request.user.is_superuser:
            company_users = get_company_users(request.user)
            filters &= Q(employee__in=company_users)
        
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
        from company.utils import get_company_users
        
        serializer = DailyAttendanceFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        target_date = serializer.validated_data['target_date']
        
        # 1. CRITICAL: Get the local timezone reference (Asia/Kolkata)
        local_tz = timezone.get_current_timezone() 
        
        # 2. Filter by company users
        if not request.user.is_superuser:
            company_users = get_company_users(request.user)
            records = Attendance.objects.filter(
                attendance_date=target_date,
                employee__in=company_users
            ).select_related(
                'employee__profile', 
                'employee__profile__designation'
            ).order_by('employee__profile__department__name', 'employee__profile__employee_id')
        else:
            records = Attendance.objects.filter(attendance_date=target_date).select_related(
                'employee__profile', 
                'employee__profile__designation'
            ).order_by('employee__profile__department__name', 'employee__profile__employee_id')

        output_data = []
        for record in records:
            profile = record.employee.profile
            
            # 2. FIX: Convert UTC to Local Time before formatting for display
            punch_in_local = record.punch_in_time.astimezone(local_tz).strftime('%H:%M:%S') if record.punch_in_time else '--'
            punch_out_local = record.punch_out_time.astimezone(local_tz).strftime('%H:%M:%S') if record.punch_out_time else '--'
            
            output_data.append({
                "Date": record.attendance_date,
                "Employee ID": profile.employee_id,
                "Employee Name": profile.full_name,
                "Designation": profile.designation.name if profile.designation else '--',
                "In Time": punch_in_local, # Now shows the correct IST time (e.g., 20:50:00)
                "Out Time": punch_out_local, # Now shows the correct IST time (e.g., 06:00:00)
                "Working Time": format_duration(record.total_work_duration),
                "Late": "Yes" if record.is_late else "No",
                "Late Time": format_duration(record.late_duration),
                "Over Time": format_duration(record.overtime_duration),   
                "Status": "Present" if record.is_present else "Absent",
            })

        return Response(output_data)

class AttendanceSummaryReportView(APIView):
    """ Admin/HR view showing a grid summary (P, A, L) for all employees in a given month. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import get_company_users
        
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
        
        # ✅ MULTI-TENANCY: Filter by company users
        if not request.user.is_superuser:
            company_users = get_company_users(request.user)
            base_filters &= Q(employee__in=company_users)
        
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
        from company.utils import filter_by_company
        
        queryset = Allowance.objects.all().order_by('allowance_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

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
        serializer = AllowanceSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            allowances = Allowance.objects.filter(pk=pk)
            allowances = filter_by_company(allowances, self.request.user)
            allowance = allowances.first()
            
            if not allowance:
                raise Http404
            return allowance
        except Allowance.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """ Retrieve a single Allowance instance. """
        allowance = self.get_object(pk)
        serializer = AllowanceSerializer(allowance)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ Fully update an Allowance instance. """
        allowance = self.get_object(pk)
        serializer = AllowanceSerializer(allowance, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        """ Partially update an Allowance instance. """
        allowance = self.get_object(pk)
        serializer = AllowanceSerializer(allowance, data=request.data, partial=True, context={'request': request})
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
        from company.utils import filter_by_company
        
        queryset = Deduction.objects.all().order_by('deduction_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

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
        serializer = DeductionSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            deductions = Deduction.objects.filter(pk=pk)
            deductions = filter_by_company(deductions, self.request.user)
            deduction = deductions.first()
            
            if not deduction:
                raise Http404
            return deduction
        except Deduction.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """ Retrieve a single Deduction instance. """
        deduction = self.get_object(pk)
        serializer = DeductionSerializer(deduction)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """ Fully update a Deduction instance. """
        deduction = self.get_object(pk)
        serializer = DeductionSerializer(deduction, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        """ Partially update a Deduction instance. """
        deduction = self.get_object(pk)
        serializer = DeductionSerializer(deduction, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """ Delete an Deduction instance. """
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
        from company.utils import filter_by_company
        
        queryset = MonthlyPayGrade.objects.all().order_by('grade_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

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
        serializer = MonthlyPayGradeSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            pay_grades = MonthlyPayGrade.objects.filter(pk=pk)
            pay_grades = filter_by_company(pay_grades, self.request.user)
            pay_grade = pay_grades.first()
            
            if not pay_grade:
                raise Http404
            return pay_grade
        except MonthlyPayGrade.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        serializer = MonthlyPayGradeSerializer(pay_grade)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        # Full update (partial=False)
        serializer = MonthlyPayGradeSerializer(pay_grade, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        pay_grade = self.get_object(pk)
        # Partial update (partial=True)
        serializer = MonthlyPayGradeSerializer(pay_grade, data=request.data, partial=True, context={'request': request})
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
        from company.utils import filter_by_company
        
        queryset = HourlyPayGrade.objects.all().order_by('pay_grade_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

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
        serializer = HourlyPayGradeSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            pay_grades = HourlyPayGrade.objects.filter(pk=pk)
            pay_grades = filter_by_company(pay_grades, self.request.user)
            pay_grade = pay_grades.first()
            
            if not pay_grade:
                raise Http404
            return pay_grade
        except HourlyPayGrade.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """Retrieve a specific hourly pay grade."""
        pay_grade = self.get_object(pk)
        serializer = HourlyPayGradeSerializer(pay_grade)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update an hourly pay grade (full update)."""
        pay_grade = self.get_object(pk)
        serializer = HourlyPayGradeSerializer(pay_grade, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        """Update an hourly pay grade (partial update)."""
        pay_grade = self.get_object(pk)
        serializer = HourlyPayGradeSerializer(pay_grade, data=request.data, partial=True, context={'request': request})
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
        from company.utils import filter_by_company
        
        queryset = PerformanceCategory.objects.all().order_by('category_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(category_name__icontains=search_query)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = PerformanceCategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new performance category."""
        serializer = PerformanceCategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PerformanceCategoryDetailAPIView(APIView):
    """Handles detailed operations on a single category instance."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        from company.utils import filter_by_company
        
        try:
            categories = PerformanceCategory.objects.filter(pk=pk)
            categories = filter_by_company(categories, self.request.user)
            category = categories.first()
            
            if not category:
                raise Http404
            return category
        except PerformanceCategory.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """Retrieve a single performance category."""
        category = self.get_object(pk)
        serializer = PerformanceCategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a performance category (full update)."""
        category = self.get_object(pk)
        serializer = PerformanceCategorySerializer(category, data=request.data, context={'request': request})
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
        from company.utils import get_company_owner
        
        queryset = PerformanceCriteria.objects.select_related('category').all().order_by('category__category_name', 'criteria_name')
        
        # Filter by company through category's parent
        if not request.user.is_superuser:
            company_owner = get_company_owner(request.user)
            if company_owner:
                queryset = queryset.filter(category__parent=company_owner)
            else:
                queryset = queryset.none()

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
        serializer = PerformanceCriteriaSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PerformanceCriteriaDetailAPIView(APIView):
    """Handles detailed operations on a single Performance Criteria instance."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        from company.utils import get_company_owner
        
        try:
            criterias = PerformanceCriteria.objects.filter(pk=pk)
            
            # Filter by company through category's parent
            if not self.request.user.is_superuser:
                company_owner = get_company_owner(self.request.user)
                if company_owner:
                    criterias = criterias.filter(category__parent=company_owner)
                else:
                    criterias = criterias.none()
            
            criteria = criterias.first()
            
            if not criteria:
                raise Http404
            return criteria
        except PerformanceCriteria.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """Retrieve a single performance criterion."""
        criteria = self.get_object(pk)
        serializer = PerformanceCriteriaSerializer(criteria)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Update a performance criterion (full update)."""
        criteria = self.get_object(pk)
        serializer = PerformanceCriteriaSerializer(criteria, data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        queryset = EmployeePerformance.objects.select_related('employee', 'reviewed_by').prefetch_related('ratings').all().order_by('-review_month')
        
        # Filter by company through employee relationship
        queryset = filter_by_employee_company(queryset, request.user, employee_field='employee')

        search_query = request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(employee__profile__first_name__icontains=search_query) |
                Q(employee__profile__last_name__icontains=search_query)
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
        from company.utils import filter_by_employee_company
        
        try:
            # Prefetch relations for the detail view efficiency
            reviews = EmployeePerformance.objects.select_related('employee', 'reviewed_by').prefetch_related('ratings').filter(pk=pk)
            reviews = filter_by_employee_company(reviews, self.request.user, employee_field='employee')
            review = reviews.first()
            
            if not review:
                raise Http404
            return review
        except EmployeePerformance.DoesNotExist:
            raise Http404

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
        from company.utils import filter_by_employee_company
        
        employee_id = request.query_params.get('employee_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        queryset = EmployeePerformance.objects.select_related('employee').all()
        
        # Filter by company through employee relationship
        queryset = filter_by_employee_company(queryset, request.user, employee_field='employee')

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
        from company.utils import filter_by_company
        
        queryset = JobPost.objects.select_related('published_by').all().order_by('-created_at')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

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
        serializer = JobPostSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            # Helper to safely fetch a JobPost instance.
            # Queryset mein 'published_by' relationship ko pehle hi fetch kar lo
            job_posts = JobPost.objects.select_related('published_by').filter(pk=pk)
            job_posts = filter_by_company(job_posts, self.request.user)
            job_post = job_posts.first()
            
            if not job_post:
                raise Http404
            return job_post
        except JobPost.DoesNotExist:
            raise Http404

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
        from company.utils import filter_by_company
        
        queryset = TrainingType.objects.all().order_by('training_type_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(training_type_name__icontains=search_query)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = TrainingTypeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new training type """
        serializer = TrainingTypeSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            # Helper to safely fetch a TrainingType instance.
            training_types = TrainingType.objects.filter(pk=pk)
            training_types = filter_by_company(training_types, self.request.user)
            training_type = training_types.first()
            
            if not training_type:
                raise Http404
            return training_type
        except TrainingType.DoesNotExist:
            raise Http404

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
        from company.utils import filter_by_employee_company
        
        queryset = EmployeeTraining.objects.select_related('employee', 'training_type').all().order_by('-from_date')
        
        # Filter by company through employee relationship
        queryset = filter_by_employee_company(queryset, request.user, employee_field='employee')

        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__profile__first_name__icontains=search_query) |      # 1. Employee First Name par search
                Q(employee__profile__last_name__icontains=search_query) |       # 2. Employee Last Name par search
                Q(training_type__training_type_name__icontains=search_query) | # 3. Training Type Name par search
                Q(subject__icontains=search_query)                           # 4. Subject par search
            )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = EmployeeTrainingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new employee training record."""
        serializer = EmployeeTrainingSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_employee_company
        
        try:
            # Helper to safely fetch an EmployeeTraining instance.
            # Queryset mein 'employee' aur 'training_type' relationships ko pehle hi fetch karein.
            trainings = EmployeeTraining.objects.select_related('employee', 'training_type').filter(pk=pk)
            trainings = filter_by_employee_company(trainings, self.request.user, employee_field='employee')
            training = trainings.first()
            
            if not training:
                raise Http404
            return training
        except EmployeeTraining.DoesNotExist:
            raise Http404

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
        from company.utils import filter_by_employee_company
        
        employee_id = request.query_params.get('employee_id', None)
        
        queryset = EmployeeTraining.objects.select_related('employee', 'training_type').all().order_by('-from_date')
        
        # Filter by company through employee relationship
        queryset = filter_by_employee_company(queryset, request.user, employee_field='employee')

        if employee_id:
            try:
                employee_id = int(employee_id) 
                queryset = queryset.filter(employee__pk=employee_id)
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
        from company.utils import filter_by_employee_company
        
        queryset = Award.objects.select_related('employee').all().order_by('-award_month')
        
        # Filter by company through employee relationship
        queryset = filter_by_employee_company(queryset, request.user, employee_field='employee')

        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__profile__first_name__icontains=search_query) |  # Employee first name
                Q(employee__profile__last_name__icontains=search_query) |   # Employee last name
                Q(award_name__icontains=search_query) |            # Award Enum value
                Q(gift_item__icontains=search_query)              # Gift item
            )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = AwardSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        """Create a new employee award (award02.png)."""
        serializer = AwardSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AwardDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        from company.utils import filter_by_employee_company
        
        try:
            # Helper to safely fetch an Award instance.
            # Optimize query by selecting related FKs
            awards = Award.objects.select_related('employee').filter(pk=pk)
            awards = filter_by_employee_company(awards, self.request.user, employee_field='employee')
            award = awards.first()
            
            if not award:
                raise Http404
            return award
        except Award.DoesNotExist:
            raise Http404

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
        from company.utils import filter_by_company
        
        queryset = Notice.objects.all().order_by('-publish_date')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

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
        serializer = NoticeSerializer(data=request.data, context={'request': request})
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
        from company.utils import filter_by_company
        
        try:
            # Helper to safely fetch a Notice instance.
            notices = Notice.objects.filter(pk=pk)
            notices = filter_by_company(notices, self.request.user)
            notice = notices.first()
            
            if not notice:
                raise Http404
            return notice
        except Notice.DoesNotExist:
            raise Http404

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
        from company.utils import get_company_users, filter_by_company
        
        today = date.today()
        
        # ✅ MULTI-TENANCY: Get company users
        company_users = get_company_users(request.user)
        
        # 1. Total Active Employees Count (Company-specific)
        staff_base_filter = Q(is_superuser=False) & Q(is_active=True)
        
        total_employees = company_users.filter(
            staff_base_filter,             
            profile__status='Active',            
            profile__isnull=False                
        ).count()
        
        # 2. Total Active Departments Count (Company-specific)
        departments = Department.objects.all()
        departments = filter_by_company(departments, request.user)
        total_departments = departments.count()
        
        # 3. Today's Attendance (Company-specific)
        today_attendance_records = Attendance.objects.filter(
            attendance_date=today,
            employee__in=company_users.filter(staff_base_filter).values_list('pk', flat=True)
        ).filter(employee__profile__status='Active')
        
        # Present Count
        present_count = today_attendance_records.filter(is_present=True).count()
        
        # Absent Count
        absent_count = total_employees - present_count
        
        # --- 4. Today Attendance List (Only Present Employees) ---
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
            
        # --- 5. Latest Notice (Company-specific) ---
        notices = Notice.objects.filter(status='PUBLISHED')
        notices = filter_by_company(notices, request.user)
        latest_notice = notices.order_by('-publish_date').first()
        
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
        from company.utils import filter_by_company
        
        queryset = LateDeductionRule.objects.all().order_by('late_days_threshold')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

        serializer = LateDeductionRuleSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """ Creates a new Late Deduction Rule (Create Action). """
        serializer = LateDeductionRuleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LateDeductionRuleRetrieveUpdateDestroyAPIView(APIView):
    """ Handles detail view, update, and delete for a single rule. """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        from company.utils import filter_by_company
        
        try:
            rules = LateDeductionRule.objects.filter(pk=pk)
            rules = filter_by_company(rules, self.request.user)
            rule = rules.first()
            
            if not rule:
                raise Http404
            return rule
        except LateDeductionRule.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """ Retrieves a single rule (Detail Action). """
        rule = self.get_object(pk)
        serializer = LateDeductionRuleSerializer(rule, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        """ Updates an existing rule completely (Update Action). """
        rule = self.get_object(pk)
        serializer = LateDeductionRuleSerializer(rule, data=request.data, context={'request': request}) 
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
def _recalculate_fixed_tax(gender, requesting_user):
    """ 
    Recalculates fixed tax (Cumulative Tax) for all rules of a given gender.
    Must be called AFTER all rules are saved in the database.
    """
    # Rules ko limit ke ascending order mein fetch karein
    from company.utils import filter_by_company
    
    rules = TaxRule.objects.filter(gender=gender)
    
    # ✅ MULTI-TENANCY: Filter tax rules by company
    rules = filter_by_company(rules, requesting_user)
    
    rules = rules.order_by('total_income_limit')
    previous_limit = Decimal('0.00')
    
    for i, rule in enumerate(rules):
        if rule.slab_type == 'REMAINING':
            # Last slab ka fixed tax 0 hota hai
            cumulative_fixed_tax = Decimal('0.00')
        else:
            # Pichla rule (i-1) ka final fixed tax uthaya
            if i == 0:
                tax_on_previous_slabs = Decimal('0.00')
            else:
                # Pichla rule (i-1) ka final fixed tax uthaya
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
        from company.utils import filter_by_company
        
        queryset = TaxRule.objects.all().order_by('gender', 'total_income_limit')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

        # Data ko Gender ke hisaab se group karna
        male_rules = queryset.filter(gender=GenderChoices.MALE)
        female_rules = queryset.filter(gender=GenderChoices.FEMALE)
        
        male_serializer = TaxRuleSerializer(male_rules, many=True, context={'request': request})
        female_serializer = TaxRuleSerializer(female_rules, many=True, context={'request': request})
        
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
            from company.utils import filter_by_company
            
            # 1. 🛑 DELETE ONLY COMPANY'S EXISTING RULES
            # ✅ MULTI-TENANCY: Only delete rules from the same company
            existing_rules = TaxRule.objects.all()
            existing_rules = filter_by_company(existing_rules, request.user)
            existing_rules.delete() 
            
            rules_to_save = []
            errors = []
            
            # 2. ✅ Validate and Collect Data (New Creation)
            for item in rules_data:
                
                # Naye rules create ho rahe hain, isliye ID aur fixed tax ko ignore karein
                item.pop('id', None) 
                item.pop('taxable_amount_fixed', None)
                
                # Ab hamesha Naya Serializer (Create) use hoga
                serializer = TaxRuleSerializer(data=item, context={'request': request}) 

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
            _recalculate_fixed_tax(GenderChoices.MALE, request.user)
            _recalculate_fixed_tax(GenderChoices.FEMALE, request.user)
            
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
    from company.utils import filter_by_company
    
    weekly_holidays_qs = WeeklyHoliday.objects.filter(is_active=True)
    # ✅ MULTI-TENANCY: Filter weekly holidays by company
    weekly_holidays_qs = filter_by_company(weekly_holidays_qs, employee)
    weekly_holidays = set(weekly_holidays_qs.values_list('day', flat=True))
    
    # 3. Fetch Public Holidays
    public_holiday_dates = set()
    
    # ✅ MULTI-TENANCY: Filter public holidays through Holiday's parent field
    # PublicHoliday -> Holiday -> parent (company owner)
    from company.utils import get_company_owner
    company_owner = get_company_owner(employee)
    
    ph_queryset = PublicHoliday.objects.filter(
        start_date__lte=month_end_date,
        end_date__gte=target_date,
        holiday__parent=company_owner  # Filter through Holiday's parent
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
    
    # --- TAX CALCULATION (Remains Unchanged) ---
    def _calculate_monthly_tax(self, employee, taxable_income, requesting_user):
        # ... (Your existing _calculate_monthly_tax logic here, unchanged) ...
        
        if taxable_income <= 0:
            return Decimal('0.00')

        # 1. Employee Data
        gender = employee.profile.gender if employee.profile and employee.profile.gender else 'MALE'
        annual_taxable_income = taxable_income * Decimal('12.0')
        
        # 2. Fetch Tax Rules for the employee's gender
        from company.utils import filter_by_company
        
        tax_rules = TaxRule.objects.filter(gender=gender)
        
        # ✅ MULTI-TENANCY: Filter tax rules by company
        tax_rules = filter_by_company(tax_rules, requesting_user)
        
        tax_rules = tax_rules.order_by('total_income_limit')

        total_annual_tax = Decimal('0.00')
        previous_limit = Decimal('0.00')
        
        # 3. Slab-by-Slab Calculation
        for i, rule in enumerate(tax_rules):
            current_limit = rule.total_income_limit
            tax_rate = rule.tax_rate_percentage
            
            # ... (Slab checking logic) ...
            if annual_taxable_income > current_limit:
                if rule.slab_type == 'REMAINING':
                    taxable_in_slab = annual_taxable_income - previous_limit
                    tax_in_slab = (taxable_in_slab * tax_rate) / Decimal('100.0')
                    total_annual_tax += tax_in_slab
                    break 
                total_annual_tax = rule.taxable_amount_fixed
                previous_limit = current_limit
                
            elif annual_taxable_income > previous_limit:
                tax_from_previous_slabs = Decimal('0.00')
                if i > 0:
                    tax_from_previous_slabs = tax_rules[i-1].taxable_amount_fixed
                    
                total_annual_tax = tax_from_previous_slabs
                taxable_in_current_slab = annual_taxable_income - previous_limit
                tax_in_slab = (taxable_in_current_slab * tax_rate) / Decimal('100.0')
                total_annual_tax += tax_in_slab
                break 

        monthly_tax = total_annual_tax / Decimal('12.0')
        return round(monthly_tax, 2)
    
    # ----------------------------------------------------------------------------------
    #                                MONTHLY PAYSLIP LOGIC
    # ----------------------------------------------------------------------------------

    def _calculate_monthly_payslip(self, employee, target_date, requesting_user):
        """ Calculates payslip for employees with a MonthlyPayGrade (Your original logic). """
        
        pay_grade = employee.profile.monthly_pay_grade
        master_basic_salary = pay_grade.basic_salary
        
        # --- STEP 1 & 2: Base Figures & Cuts ---
        year, month = target_date.year, target_date.month
        days_in_month = Decimal(monthrange(year, month)[1])
        if days_in_month == 0: raise ValueError("Invalid month range calculation.")
            
        per_day_rate_basic = master_basic_salary / days_in_month 

        # Calculate Late Deduction
        late_count = Attendance.objects.filter(
            employee=employee, attendance_date__year=year, attendance_date__month=month, is_late=True
        ).count()
        late_deduction_amount = Decimal('0.00')
        
        # ✅ MULTI-TENANCY: Filter late deduction rules by company
        from company.utils import filter_by_company
        
        late_rules = LateDeductionRule.objects.filter(
            late_days_threshold__lte=late_count 
        )
        late_rules = filter_by_company(late_rules, requesting_user)
        late_rule = late_rules.order_by('-late_days_threshold').first()
        
        if late_rule:
            late_deduction_days = late_rule.deduction_days
            late_deduction_amount = late_deduction_days * per_day_rate_basic
            
        # Calculate Absence Cut (Unpaid Days)
        unpaid_absence_days = _calculate_unpaid_days(employee, target_date)
        unjustified_cut_amount = unpaid_absence_days * per_day_rate_basic
        
        # --- STEP 3: Adjusted Earning Calculation (Pro-Rata & Overtime) ---
        
        # Overtime Calculation
        total_ot_duration = Attendance.objects.filter(
            employee=employee, attendance_date__year=year, attendance_date__month=month,
        ).aggregate(total_ot=Sum('overtime_duration'))['total_ot'] or timedelta(0)
        
        ot_hourly_rate = pay_grade.overtime_rate 
        overtime_pay_amount = Decimal('0.00')
        if ot_hourly_rate is not None and ot_hourly_rate > Decimal('0.00'):
            total_ot_hours = Decimal(total_ot_duration.total_seconds() / 3600)
            overtime_pay_amount = total_ot_hours * ot_hourly_rate
            
        overtime_pay_amount = round(overtime_pay_amount, 2)
        
        # Final Basic Salary (Pro-Rata)
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
            amount = min(calculated_amount, limit) if limit is not None and limit > Decimal('0.00') else calculated_amount
            amount = round(amount, 2)
            total_allowances_sum += amount
            allowance_details.append({'item_name': pg_allowance.allowance.allowance_name, 'amount': amount})

        final_gross_salary = final_basic_salary + total_allowances_sum + overtime_pay_amount
        final_gross_salary = round(final_gross_salary, 2)

        # Standard Deductions (PF, ESI): Calculate on Adjusted Basic
        for pg_deduction in pay_grade.paygradededuction_set.select_related('deduction').all():
            calculated_amount = final_basic_salary * (pg_deduction.value / 100) 
            limit = pg_deduction.deduction.limit_per_month 
            amount = min(calculated_amount, limit) if limit is not None and limit > Decimal('0.00') else calculated_amount
            amount = round(amount, 2)
            standard_deductions_sum += amount
            deduction_details.append({'item_name': pg_deduction.deduction.deduction_name, 'amount': amount})
        
        # 3. TAX DEDUCTION (TDS)
        tax_amount = self._calculate_monthly_tax(employee, final_gross_salary, requesting_user) 
        standard_deductions_sum += tax_amount
        if tax_amount > 0:
            deduction_details.append({'item_name': 'Income Tax (TDS)', 'amount': tax_amount})
            
        # --- STEP 4: FINAL NET CALCULATION ---
        total_deductions_for_net = standard_deductions_sum + late_deduction_amount 
        final_net_salary = final_gross_salary - total_deductions_for_net
        final_net_salary = round(final_net_salary, 2)
        
        # Prepare PaySlip defaults dictionary
        payslip_defaults = {
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
        
        # Return all calculated components for storage
        return payslip_defaults, allowance_details, deduction_details, late_deduction_amount, unjustified_cut_amount



    def _calculate_hourly_payslip(self, employee, target_date, requesting_user):
        """ Calculates payslip for employees with an HourlyPayGrade. """
        
        hourly_pay_grade = employee.profile.hourly_pay_grade
        hourly_rate = hourly_pay_grade.hourly_rate
        year, month = target_date.year, target_date.month
        days_in_month = Decimal(monthrange(year, month)[1])
        
        # 1. Fetch Total Paid Hours (Regular + Overtime)
        attendance_records = Attendance.objects.filter(
            employee=employee, attendance_date__year=year, attendance_date__month=month
        )

        # Sum total_work_duration (Regular Hours) and overtime_duration
        total_durations = attendance_records.aggregate(
            total_work=Sum('total_work_duration'),
            total_ot=Sum('overtime_duration')
        )
        
        total_work_duration = total_durations['total_work'] or timedelta(0)
        total_ot_duration = total_durations['total_ot'] or timedelta(0)

        # Convert to Decimal Hours
        total_regular_hours = Decimal(total_work_duration.total_seconds() / 3600)
        total_ot_hours = Decimal(total_ot_duration.total_seconds() / 3600)

        # 2. Calculate Earnings
        # In hourly grades, the "Basic Salary" is the sum of (Regular Hours * Rate)
        final_basic_salary = total_regular_hours * hourly_rate
        
        # Overtime Pay (Assuming Overtime is paid at 1.5x the standard rate, adjust if needed)
        ot_rate = hourly_rate * Decimal('1.0') 
        overtime_pay_amount = total_ot_hours * ot_rate
        
        final_gross_salary = final_basic_salary + overtime_pay_amount
        final_gross_salary = round(final_gross_salary, 2)
        
        # 3. Deductions (Assuming PF/ESI/Allowances are NOT calculated as % of hourly pay grade, 
        # or are handled via external logic/fixed amounts not shown here)
        standard_deductions_sum = Decimal('0.00') 
        deduction_details = []
        allowance_details = [] # No allowances structure visible for HourlyPayGrade

        # TAX DEDUCTION (TDS) - based on gross salary
        tax_amount = self._calculate_monthly_tax(employee, final_gross_salary, requesting_user) 
        standard_deductions_sum += tax_amount
        if tax_amount > 0:
            deduction_details.append({'item_name': 'Income Tax (TDS)', 'amount': tax_amount})
            
        # Late/Unpaid Absence Cuts: Handled intrinsically by not having paid/worked hours in attendance.
        # But if the requirement is to show the total calendar days:
        unpaid_absence_days = _calculate_unpaid_days(employee, target_date)
        late_count = attendance_records.filter(is_late=True).count()
        
        # Since pay is based only on hours worked, there is typically no separate 'Late Cut' or 'Unjustified Cut'
        # based on a per-day-rate (as there is no fixed monthly salary to cut from).
        late_deduction_amount = Decimal('0.00')
        unjustified_cut_amount = Decimal('0.00')
        
        # --- STEP 4: FINAL NET CALCULATION ---
        total_deductions_for_net = standard_deductions_sum 
        final_net_salary = final_gross_salary - total_deductions_for_net
        final_net_salary = round(final_net_salary, 2)

        # Prepare PaySlip defaults dictionary
        payslip_defaults = {
            'basic_salary': final_basic_salary, # Total Regular Pay
            'total_overtime_pay': overtime_pay_amount,    
            'total_tax_deduction': tax_amount,
            'total_allowances': Decimal('0.00'), # Assuming zero based on models provided
            'total_deductions': total_deductions_for_net + unjustified_cut_amount, 
            'gross_salary': final_gross_salary,
            'net_salary': final_net_salary,
            'total_days_in_month': days_in_month,
            'working_days': total_regular_hours / Decimal('8.0'), # Display equivalent working days (8hr assumption)
            'unjustified_absence': unpaid_absence_days, # Still relevant for tracking
            'late_attendance_count': late_count,
            'status': 'Calculated',
            'generated_by': requesting_user
        }
        
        return payslip_defaults, allowance_details, deduction_details, late_deduction_amount, unjustified_cut_amount


    
    def _generate_payslip(self, employee, target_date, requesting_user):
        """ Main function to determine pay grade type and call the correct calculation logic. """

        if not employee.profile:
            raise ValueError("Employee profile is missing.")

        if employee.profile.monthly_pay_grade:
            # Call Monthly Logic
            payslip_defaults, allowance_details, deduction_details, late_deduction_amount, unjustified_cut_amount = self._calculate_monthly_payslip(
                employee, target_date, requesting_user
            )
        elif employee.profile.hourly_pay_grade:
            # Call Hourly Logic
            payslip_defaults, allowance_details, deduction_details, late_deduction_amount, unjustified_cut_amount = self._calculate_hourly_payslip(
                employee, target_date, requesting_user
            )
        else:
            raise ValueError("Employee must be assigned a Monthly or Hourly Pay Grade.")

        # --- STEP 5: Store PaySlip and Details (Common Storage Logic) ---
        
        with transaction.atomic():
            payslip, created = PaySlip.objects.update_or_create(
                employee=employee, payment_month=target_date,
                defaults=payslip_defaults
            )

            payslip.details.all().delete()
            
            # Store Allowances 
            for item in allowance_details:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Allowance', **item)
            
            # Store Overtime Pay separately (Amount is already in total_overtime_pay, grab name from defaults)
            if payslip_defaults['total_overtime_pay'] > 0:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Allowance', item_name='Overtime Pay', amount=payslip_defaults['total_overtime_pay'])
            
            # Store Standard Deductions and Tax
            for item in deduction_details:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Deduction', **item)

            # Store Transactional Cuts (Late Cut - mostly for Monthly)
            if late_deduction_amount > 0:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Deduction', item_name=f'Late Attendance Cut ({payslip_defaults["late_attendance_count"]} Lates)', amount=late_deduction_amount)
            
            # Store Absence Cut (mostly for Monthly)
            if unjustified_cut_amount > 0:
                PaySlipDetail.objects.create(payslip=payslip, item_type='Deduction', item_name='Unjustified Absence Cut (Days Not Paid)', amount=unjustified_cut_amount)
                
            return payslip
            
    #

    def post(self, request):
        """ Triggers the payslip calculation and storage. """
        from company.utils import filter_by_company
        
        employee_id = request.data.get('employee_id')
        month_str = request.data.get('month') 
        
        if not employee_id or not month_str:
             return Response({"error": "Employee ID and Month (YYYY-MM) are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # ✅ MULTI-TENANCY: Filter employee by company
            employee_queryset = User.objects.filter(pk=employee_id)
            employee_queryset = filter_by_company(employee_queryset, request.user)
            employee = employee_queryset.first()
            
            if not employee:
                return Response({"error": "Employee not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
            
            target_date = datetime.strptime(month_str, '%Y-%m').date().replace(day=1)
        except ValueError:
            return Response({"error": "Invalid month format. Use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Invalid request: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payslip_record = self._generate_payslip(employee, target_date, request.user)
            return Response({"message": "Payslip generated successfully.", "payslip_id": payslip_record.pk}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error (not shown here)
            return Response({"error": f"Payslip generation failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        """ Retrieve a specific payslip by PK (Payslip ID). """
        from company.utils import filter_by_employee_company
        
        # ✅ MULTI-TENANCY: Filter payslip by company through employee
        payslip_queryset = PaySlip.objects.select_related(
            'employee__profile__designation', 'employee__profile__department'
        ).prefetch_related('details').filter(pk=pk)
        
        payslip_queryset = filter_by_employee_company(payslip_queryset, request.user, 'employee')
        payslip = payslip_queryset.first()
        
        if not payslip:
            return Response({"error": "Payslip not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaySlipDetailSerializer(payslip)
        return Response(serializer.data)

class MonthlySalarySheetView(APIView):
    """ Lists payment status and gross salary for all employees with Pagination. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from company.utils import filter_by_company
        
        filter_serializer = MonthlySalaryFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        target_date = filter_serializer.validated_data['month']

        # 1. Base Employee QuerySet (BOTH pay grades)
        employees_queryset = User.objects.filter(
            profile__status='Active'
        ).select_related(
            'profile__monthly_pay_grade',  # ✅ Monthly
            'profile__hourly_pay_grade',   # ✅ Hourly
            'profile'
        ).order_by('profile__first_name')
        
        # Filter by company
        employees_queryset = filter_by_company(employees_queryset, request.user)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(employees_queryset, request, view=self)
        
        # 2. Payslip Prefetching
        employee_ids_on_page = [e.id for e in page]
        
        payslips_queryset = PaySlip.objects.filter(
            payment_month=target_date,
            employee_id__in=employee_ids_on_page
        ).prefetch_related('details')
        
        payslips_map = {p.employee_id: p for p in payslips_queryset}

        output = []
        # 3. Loop through employees
        for employee in page:
            profile = employee.profile
            payslip = payslips_map.get(employee.id)
            
            # ✅ FIXED: Handle BOTH pay grade types
            if profile.monthly_pay_grade:
                pay_grade_name = f"{profile.monthly_pay_grade.grade_name} (Monthly)"
            elif profile.hourly_pay_grade:
                pay_grade_name = f"{profile.hourly_pay_grade.pay_grade_name} (Hourly)"
            else:
                pay_grade_name = 'N/A'
            
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
                "employee_id": employee.profile.employee_id,
                "pay_grade": pay_grade_name,
                "gross_salary": payslip.gross_salary if payslip else Decimal('0.00'), 
                "overtime_pay": overtime_pay,                      
                "tax_deduction": tax_deduction,                   
                "status": payslip.status if payslip else 'Pending',
                "action": "Generate Payslip" if not payslip or payslip.status == 'Pending' else "View/Re-Generate"
            })

        return paginator.get_paginated_response(output)


class BulkPaySlipGenerateAPIView(APIView):
    """
    Generate salary sheets for multiple employees at once based on filters.
    Filters: Branch, Department, Designation (all optional) + Month (required)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/payslip/generate-bulk/
        Body: {
            "branch_id": 1,  # optional
            "department_id": 2,  # optional
            "designation_id": 3,  # optional
            "month": "2025-11"  # required
        }
        """
        # Step 1: Validate input filters
        serializer = BulkSalaryFilterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        branch_id = validated_data.get('branch_id')
        department_id = validated_data.get('department_id')
        designation_id = validated_data.get('designation_id')
        target_date = validated_data['month']
        
        # Step 2: Build employee queryset based on filters
        from company.utils import filter_by_company
        
        queryset = User.objects.filter(
            profile__status='Active'  # Only active employees
        ).select_related('profile__monthly_pay_grade', 'profile__hourly_pay_grade', 'profile')
        
        # ✅ MULTI-TENANCY: Filter by company
        queryset = filter_by_company(queryset, request.user)
        
        # Apply filters if provided
        if branch_id:
            queryset = queryset.filter(profile__branch_id=branch_id)
        
        if department_id:
            queryset = queryset.filter(profile__department_id=department_id)
        
        if designation_id:
            queryset = queryset.filter(profile__designation_id=designation_id)
        
        # Only include employees with assigned pay grades
        queryset = queryset.filter(
            Q(profile__monthly_pay_grade__isnull=False) | 
            Q(profile__hourly_pay_grade__isnull=False)
        )
        
        employees = list(queryset)
        
        if not employees:
            return Response({
                "message": "No employees found matching the filters.",
                "total_employees": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }, status=status.HTTP_200_OK)
        
        # Step 3: Generate payslips for all matching employees
        total_employees = len(employees)
        successful = 0
        failed = 0
        success_list = []  # ✅ Track successful generations
        errors = []
        
        # Get reference to the salary generation logic
        single_payslip_view = SinglePaySlipGenerateRetrieveAPIView()
        
        for employee in employees:
            try:
                # Reuse existing _generate_payslip method
                payslip = single_payslip_view._generate_payslip(employee, target_date, request.user)
                successful += 1
                
                # ✅ Add to success list with details
                success_list.append({
                    "employee_id": employee.id,
                    "employee_name": employee.profile.full_name if hasattr(employee, 'profile') else employee.email,
                    "employee_code": employee.profile.employee_id if hasattr(employee, 'profile') else None,
                    "payslip_id": payslip.pk,
                    "gross_salary": float(payslip.gross_salary),
                    "net_salary": float(payslip.net_salary)
                })
            except Exception as e:
                failed += 1
                errors.append({
                    "employee_id": employee.id,
                    "employee_name": employee.profile.full_name if hasattr(employee, 'profile') else employee.email,
                    "employee_code": employee.profile.employee_id if hasattr(employee, 'profile') else None,
                    "error": str(e)
                })
        
        # Step 4: Return detailed summary
        return Response({
            "message": f"Bulk generation completed. {successful} successful, {failed} failed.",
            "total_employees": total_employees,
            "successful": successful,
            "failed": failed,
            "success_details": success_list,  # ✅ Detailed success list
            "errors": errors  # Detailed error list
        }, status=status.HTTP_200_OK)


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
                    # ✅ MULTI-TENANCY: Lookup Profile by employee_id and filter by company
                    from company.utils import get_company_users
                    
                    # Get all users in the requesting user's company
                    company_users = get_company_users(request.user)
                    
                    # Lookup Profile by the string employee_id (Fingerprint/Emp No.)
                    employee_profile = Profile.objects.select_related('user', 'work_shift').filter(
                        employee_id=emp_id_str,
                        user__in=company_users  # ✅ Filter by company
                    ).first()
                    
                    if not employee_profile:
                        failed_records.append({
                            "row": row_number, 
                            "employee_id": emp_id_str, 
                            "error": "Employee ID not found or does not belong to your company."
                        })
                        continue
                    
                    employee = employee_profile.user
                except Exception as e:
                    failed_records.append({
                        "row": row_number, 
                        "employee_id": emp_id_str, 
                        "error": f"Error looking up employee: {str(e)}"
                    })
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
        from company.utils import filter_by_company
        
        roles = Role.objects.all().order_by('name')
        # ✅ MULTI-TENANCY: Filter roles by company
        roles = filter_by_company(roles, request.user)
        serializer = RoleSerializer(roles, many=True, context={'request': request})
        return Response(serializer.data)

    # --- POST: Create a new Role ---
    def post(self, request, format=None):
        serializer = RoleSerializer(data=request.data, context={'request': request})
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
    def get_object(self, pk, user):
        from company.utils import filter_by_company
        
        try:
            # ✅ MULTI-TENANCY: Filter role by company
            roles = Role.objects.filter(pk=pk)
            roles = filter_by_company(roles, user)
            role = roles.first()
            
            if not role:
                raise Role.DoesNotExist
            return role
        except Role.DoesNotExist:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

    # --- GET: Retrieve Role Detail ---
    def get(self, request, pk, format=None):
        role = self.get_object(pk, request.user)
        # Check if the helper returned an error response
        if isinstance(role, Response):
            return role
            
        serializer = RoleSerializer(role, context={'request': request})
        return Response(serializer.data)

    # --- PUT/PATCH: Update Role ---
    def put(self, request, pk, format=None):
        role = self.get_object(pk, request.user)
        if isinstance(role, Response):
            return role
            
        # partial=True for PATCH requests, but PUT typically uses full update
        serializer = RoleSerializer(role, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE: Delete Role ---
    def delete(self, request, pk, format=None):
        role = self.get_object(pk, request.user)
        if isinstance(role, Response):
            return role
            
        # Simple deletion as requested (no safety checks)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AutomaticAttendanceView(APIView):
    """
    Endpoint for automatic attendance recording via face recognition.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [] 
    # Threshold for matching faces (Lower value means stricter match)
    MATCH_THRESHOLD = 0.6 

    def post(self, request, *args, **kwargs):
        # 1. Validate Input (Ensures 'punch_type' and other fields exist)
        # Assuming AutomaticAttendanceInputSerializer is correctly defined and handles validation
        serializer = AutomaticAttendanceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        live_image_base64 = data['live_image_base64']
        punch_dt = data['punch_time'] 
        punch_type = data['punch_type'].upper() # Ensure punch_type is upper-case ('IN'/'OUT')

        # --- A. Face Recognition and Employee Identification ---
        employee_profile = None
        img_data = None 

        try:
            # --- Decode and Face Detection ---
            try:
                img_data = base64.b64decode(live_image_base64)
            except base64.binascii.Error:
                 return Response({"error": "Base64 Decoding Failed. Invalid Base64 string format."}, status=status.HTTP_400_BAD_REQUEST)

            nparr = np.frombuffer(img_data, np.uint8)
            live_image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if live_image_np is None:
                return Response({"error": "Image Decoding Failed. Not a recognized image format."}, status=status.HTTP_400_BAD_REQUEST)
                
            live_image_rgb = cv2.cvtColor(live_image_np, cv2.COLOR_BGR2RGB)
            live_encodings = face_recognition.face_encodings(live_image_rgb)
            
            if not live_encodings:
                return Response({"error": "No face detected for punch."}, status=status.HTTP_404_NOT_FOUND)
            if len(live_encodings) > 1:
                return Response({"error": "Multiple faces detected for punch."}, status=status.HTTP_400_BAD_REQUEST)
                
            live_encoding = live_encodings[0]

            # --- Database Matching ---
            # ✅ MULTI-TENANCY: Filter by company (since endpoint is now authenticated)
            from company.utils import get_company_users
            
            company_users = get_company_users(request.user)
            potential_matches = Profile.objects.filter(
                face_encoding__isnull=False,
                user__is_active=True,
                user__in=company_users  # ✅ Only company employees
            ).select_related('user', 'work_shift')
            known_encodings = []
            profiles_map = {} 
            for profile in potential_matches:
                known_face_np = deserialize_face_encoding(profile.face_encoding)
                if known_face_np is not None:
                    known_encodings.append(known_face_np)
                    profiles_map[len(known_encodings) - 1] = profile
            
            if not known_encodings:
                return Response({"error": "No enrolled employee faces found."}, status=status.HTTP_404_NOT_FOUND)

            known_encodings_array = np.array(known_encodings)
            face_distances = face_recognition.face_distance(known_encodings_array, live_encoding)
            best_match_index = np.argmin(face_distances)
            min_distance = face_distances[best_match_index]
            
            if min_distance <= self.MATCH_THRESHOLD:
                employee_profile = profiles_map[best_match_index]
                employee = employee_profile.user
            else:
                return Response({"error": f"Face not recognized. Min distance ({min_distance:.3f}) > threshold ({self.MATCH_THRESHOLD})."}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            # You should refine exception handling for deployment
            return Response({"error": f"Recognition process failed: {type(e).__name__} - {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
        # --- B. Attendance Logic (Simple IN/OUT + Auto-Close) ---

        local_tz = timezone.get_current_timezone()
        
        # 2. Determine the correct attendance date (Handles night shifts)
        if employee_profile.work_shift:
            # Ensure determine_attendance_date takes punch_dt as a timezone-aware datetime
            attendance_date = determine_attendance_date(punch_dt, employee_profile.work_shift, local_tz)
        else:
            attendance_date = punch_dt.astimezone(local_tz).date() 

        message = ""
        is_punch_recorded = False

        # 3. Prepare Live Photo File
        punch_photo_file = None
        if img_data:
            try:
                # Use employee.id (User PK) or employee_profile.employee_id (Fingerprint No.)
                file_name = f"{employee.id}_{punch_dt.strftime('%Y%m%d%H%M%S')}.jpg"
                punch_photo_file = ContentFile(img_data, name=file_name) 
            except Exception:
                # Log or handle file creation error, but don't crash the punch
                pass 
            
        # 4. Get or Create Attendance Record
        attendance_record, created = Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=attendance_date
        )
        
        # 5. Simple Action Based on punch_type
        if punch_type == 'IN':
            # Check for existing punch-in time and update only if it's the first punch or a later punch (to avoid missed early punches)
            if attendance_record.punch_in_time is None or punch_dt < attendance_record.punch_in_time:
                attendance_record.punch_in_time = punch_dt
                if punch_photo_file: attendance_record.punch_in_photo = punch_photo_file 
                message = "Punch In recorded successfully."
                is_punch_recorded = True
            else:
                 return Response({"warning": "Punch ignored: Time is later than existing Punch In."}, status=status.HTTP_200_OK)

        elif punch_type == 'OUT':
            if attendance_record.punch_in_time is None:
                return Response({"error": "Cannot Punch OUT without a Punch IN record."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Punch Out Time must be strictly after Punch In Time
            if punch_dt <= attendance_record.punch_in_time:
                 return Response({"error": "Punch Out Time must be strictly after Punch In Time."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update punch-out only if it's the first punch-out or a later punch
            if attendance_record.punch_out_time is None or punch_dt > attendance_record.punch_out_time:
                attendance_record.punch_out_time = punch_dt
                if punch_photo_file: attendance_record.punch_out_photo = punch_photo_file 
                message = "Punch Out recorded successfully."
                is_punch_recorded = True
            else:
                 return Response({"warning": "Punch ignored: Time is earlier than existing Punch Out."}, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "Invalid 'punch_type'. Must be 'IN' or 'OUT'."}, status=status.HTTP_400_BAD_REQUEST)

        
        # 6. APPLY AUTO-CLOSE RULE (Runs only if Punch OUT is still missing)
        is_auto_closed = False
        if is_punch_recorded and punch_type == 'IN':
            # Check if auto-close applies only if the punch was an IN and OUT is still null
            if attendance_record.punch_out_time is None:
                is_auto_closed = apply_auto_close_if_needed(attendance_record, employee_profile)
        
        
        # 7. Recalculate and Finalize Current Record
        if attendance_record.punch_in_time:
            # Recalculate metrics based on the current state of the record
            (total_work_duration, 
             is_late_calculated, 
             late_duration, 
             overtime_duration) = calculate_attendance_status_and_times(attendance_record, employee_profile)
            
            attendance_record.total_work_duration = total_work_duration
            attendance_record.is_late = is_late_calculated
            attendance_record.late_duration = late_duration
            attendance_record.overtime_duration = overtime_duration
            attendance_record.is_present = True
            
            # Set final status
            if is_auto_closed:
                attendance_record.status = 'Auto-Closed'
            else:
                attendance_record.status = 'Completed' if attendance_record.punch_out_time else 'Single Punch' 
            
        else:
            # If punch-in was nullified (e.g., if a previous punch was ignored)
            attendance_record.is_present = False
            attendance_record.status = 'Pending' 
        
        # 8. Save the current record (Only if data was changed/created)
        if is_punch_recorded or is_auto_closed or created:
            attendance_record.save()
        
        # 9. Return the final structured response
        full_name = employee_profile.full_name # Assuming full_name is a property on Profile
        
        return Response({
            "success": True, 
            "message": message,
            "id": employee.id,
            "employee_id":employee_profile.employee_id,
            "employee_name": full_name,
            "date": attendance_record.attendance_date,
            "working_time": format_duration(attendance_record.total_work_duration),
            "late_time": format_duration(attendance_record.late_duration),
            "overtime": format_duration(attendance_record.overtime_duration),
            "status": attendance_record.status
        }, status=status.HTTP_200_OK)


# ============================================
# BONUS MANAGEMENT VIEWS
# ============================================

class BonusSettingListCreateView(APIView):
    """
    List all bonus settings or create a new one.
    GET: List with pagination and search
    POST: Create new bonus setting
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from company.utils import filter_by_company
        
        queryset = BonusSetting.objects.all().order_by('festival_name')
        
        # Filter by company
        queryset = filter_by_company(queryset, request.user)

        # Search filter
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(festival_name__icontains=search_query)
            )
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = BonusSettingSerializer(page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        serializer = BonusSettingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BonusSettingDetailView(APIView):
    """
    Retrieve, update or delete a bonus setting.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        from company.utils import filter_by_company
        
        try:
            bonus_settings = BonusSetting.objects.filter(pk=pk)
            bonus_settings = filter_by_company(bonus_settings, self.request.user)
            bonus_setting = bonus_settings.first()
            
            if not bonus_setting:
                raise Http404
            return bonus_setting
        except BonusSetting.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        bonus_setting = self.get_object(pk)
        serializer = BonusSettingSerializer(bonus_setting, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        bonus_setting = self.get_object(pk)
        serializer = BonusSettingSerializer(bonus_setting, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        bonus_setting = self.get_object(pk)
        serializer = BonusSettingSerializer(bonus_setting, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        bonus_setting = self.get_object(pk)
        bonus_setting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateBonusView(APIView):
    """
    Generate bonuses for multiple employees based on filters.
    POST: Generate bonuses for all matching employees
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/bonus/generate/
        Body: {
            "bonus_setting_id": 1,  # required
            "month": "2025-11",     # required
            "branch_id": 1,         # optional
            "department_id": 2,     # optional
            "designation_id": 3     # optional
        }
        """
        # Step 1: Validate input
        serializer = GenerateBonusFilterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        bonus_setting_id = validated_data['bonus_setting_id']
        bonus_month = validated_data['month']
        branch_id = validated_data.get('branch_id')
        department_id = validated_data.get('department_id')
        designation_id = validated_data.get('designation_id')
        
        # Step 2: Get bonus setting
        # ✅ MULTI-TENANCY: Filter bonus setting by company
        from company.utils import filter_by_company
        
        bonus_settings = BonusSetting.objects.filter(id=bonus_setting_id, is_active=True)
        bonus_settings = filter_by_company(bonus_settings, request.user)
        bonus_setting = bonus_settings.first()
        
        if not bonus_setting:
            return Response(
                {"error": "Bonus setting not found, inactive, or does not belong to your company."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Step 3: Build employee queryset
        queryset = User.objects.filter(
            profile__status='Active'
        ).select_related('profile__monthly_pay_grade', 'profile')
        
        # ✅ MULTI-TENANCY: Filter employees by company
        queryset = filter_by_company(queryset, request.user)
        
        # Apply filters
        if branch_id:
            queryset = queryset.filter(profile__branch_id=branch_id)
        if department_id:
            queryset = queryset.filter(profile__department_id=department_id)
        if designation_id:
            queryset = queryset.filter(profile__designation_id=designation_id)
        
        # Only employees with monthly pay grade
        queryset = queryset.filter(profile__monthly_pay_grade__isnull=False)
        
        employees = list(queryset)
        
        if not employees:
            return Response({
                "message": "No employees found matching the filters.",
                "total_employees": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }, status=status.HTTP_200_OK)
        
        # Step 4: Generate bonuses
        total_employees = len(employees)
        successful = 0
        failed = 0
        errors = []
        
        for employee in employees:
            try:
                profile = employee.profile
                pay_grade = profile.monthly_pay_grade
                
                if not pay_grade:
                    raise ValueError("No pay grade assigned")
                
                # Get basic and gross salary
                basic_salary = pay_grade.basic_salary
                gross_salary = pay_grade.gross_salary
                
                # Calculate bonus based on setting
                if bonus_setting.calculate_on == 'BASIC':
                    bonus_amount = (basic_salary * bonus_setting.percentage_of_basic) / Decimal('100.00')
                else:  # GROSS
                    bonus_amount = (gross_salary * bonus_setting.percentage_of_basic) / Decimal('100.00')
                
                bonus_amount = round(bonus_amount, 2)
                
                # Create or update bonus record
                EmployeeBonus.objects.update_or_create(
                    employee=employee,
                    festival_name=bonus_setting.festival_name,
                    bonus_month=bonus_month,
                    defaults={
                        'bonus_setting': bonus_setting,
                        'basic_salary': basic_salary,
                        'gross_salary': gross_salary,
                        'percentage': bonus_setting.percentage_of_basic,
                        'calculated_on': bonus_setting.calculate_on,
                        'bonus_amount': bonus_amount,
                        'generated_by': request.user
                    }
                )
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append({
                    "employee_id": employee.id,
                    "employee_name": profile.full_name if hasattr(employee, 'profile') else employee.email,
                    "error": str(e)
                })
        
        # Step 5: Return summary
        return Response({
            "message": f"Bonus generation completed. {successful} successful, {failed} failed.",
            "total_employees": total_employees,
            "successful": successful,
            "failed": failed,
            "errors": errors
        }, status=status.HTTP_200_OK)

class EmployeeBonusListView(APIView):
    """
    List all employee bonuses with filters and pagination.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from company.utils import filter_by_employee_company
        
        queryset = EmployeeBonus.objects.select_related(
            'employee__profile__department',
            'bonus_setting'
        ).all().order_by('-bonus_month', '-created_at')
        
        # ✅ MULTI-TENANCY: Filter by company through employee
        queryset = filter_by_employee_company(queryset, request.user, 'employee')
        
        # Filters
        festival_name = request.query_params.get('festival_name', None)
        month = request.query_params.get('month', None)
        employee_id = request.query_params.get('employee_id', None)
        
        if festival_name:
            queryset = queryset.filter(festival_name__icontains=festival_name)
        
        if month:
            try:
                month_date = datetime.strptime(month, '%Y-%m').date().replace(day=1)
                queryset = queryset.filter(bonus_month=month_date)
            except ValueError:
                pass
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(employee__profile__first_name__icontains=search_query) |
                Q(employee__profile__last_name__icontains=search_query) |
                Q(festival_name__icontains=search_query)
            )
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = EmployeeBonusSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)






class MarkPaymentPaidView(APIView):
    """
    Unified endpoint to mark salary or bonus as paid.
    POST: Update payment status to 'Paid' and optionally return CSV
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/payments/mark-paid/?export=csv  (optional query param for CSV)
        Body: {
            "payment_type": "salary",  // or "bonus"
            "item_ids": [1, 2, 3],
            "payment_method": "Manual",
            "payment_reference": "TXN123456",  // optional
            "payment_date": "2025-11-27"      // optional
        }
        """
        # Step 1: Validate input
        serializer = MarkPaymentPaidSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        payment_type = validated_data['payment_type']
        item_ids = validated_data['item_ids']
        payment_method = validated_data['payment_method']
        payment_reference = validated_data.get('payment_reference', '')
        payment_date = validated_data.get('payment_date', date.today())
        
        # Check if CSV export is requested
        export_csv = request.query_params.get('export', '').lower() == 'csv'
        
        # Step 2: Route to appropriate handler
        if payment_type == 'salary':
            return self._mark_salary_paid(
                item_ids, payment_method, payment_reference, payment_date, request.user, export_csv
            )
        else:  # bonus
            return self._mark_bonus_paid(
                item_ids, payment_method, payment_reference, payment_date, request.user, export_csv
            )
    
    def _mark_salary_paid(self, payslip_ids, payment_method, payment_reference, payment_date, user, export_csv=False):
        """Mark payslips as paid and optionally generate CSV"""
        from company.utils import filter_by_employee_company
        
        payslips = PaySlip.objects.filter(id__in=payslip_ids).select_related(
            'employee__profile',
            'employee__profile__department',
            'employee__profile__designation',
            'employee__profile__branch'
        ).prefetch_related('employee__profile__account_details')
        
        # ✅ MULTI-TENANCY: Filter payslips by company
        payslips = filter_by_employee_company(payslips, user, 'employee')
        
        if not payslips.exists():
            return Response(
                {"error": "No payslips found with the provided IDs."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_count = 0
        already_paid = 0
        errors = []
        paid_payslips = []
        
        for payslip in payslips:
            try:
                if payslip.status == 'Paid':
                    already_paid += 1
                    paid_payslips.append(payslip)  # Include already paid for CSV
                    continue
                
                payslip.status = 'Paid'
                payslip.payment_date = payment_date
                payslip.payment_method = payment_method
                payslip.payment_reference = payment_reference
                payslip.paid_by = user
                payslip.save()
                
                updated_count += 1
                paid_payslips.append(payslip)
                
            except Exception as e:
                errors.append({
                    "payslip_id": payslip.id,
                    "employee": payslip.employee.email,
                    "error": str(e)
                })
        
        # Generate CSV if requested
        if export_csv and paid_payslips:
            return self._generate_salary_csv(paid_payslips, payment_date)
        
        return Response({
            "message": f"Salary payment status updated. {updated_count} marked as paid.",
            "payment_type": "salary",
            "total_requested": len(payslip_ids),
            "updated": updated_count,
            "already_paid": already_paid,
            "failed": len(errors),
            "errors": errors
        }, status=status.HTTP_200_OK)
    
    def _mark_bonus_paid(self, bonus_ids, payment_method, payment_reference, payment_date, user, export_csv=False):
        """Mark bonuses as paid and optionally generate CSV"""
        from company.utils import filter_by_employee_company
        
        bonuses = EmployeeBonus.objects.filter(id__in=bonus_ids).select_related(
            'employee__profile',
            'employee__profile__department',
            'employee__profile__designation',
            'employee__profile__branch'
        ).prefetch_related('employee__profile__account_details')
        
        # ✅ MULTI-TENANCY: Filter bonuses by company
        bonuses = filter_by_employee_company(bonuses, user, 'employee')
        
        if not bonuses.exists():
            return Response(
                {"error": "No bonuses found with the provided IDs."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_count = 0
        already_paid = 0
        errors = []
        paid_bonuses = []
        
        for bonus in bonuses:
            try:
                if bonus.status == 'Paid':
                    already_paid += 1
                    paid_bonuses.append(bonus)  # Include already paid for CSV
                    continue
                
                bonus.status = 'Paid'
                bonus.payment_date = payment_date
                bonus.payment_method = payment_method
                bonus.payment_reference = payment_reference
                bonus.paid_by = user
                bonus.save()
                
                updated_count += 1
                paid_bonuses.append(bonus)
                
            except Exception as e:
                errors.append({
                    "bonus_id": bonus.id,
                    "employee": bonus.employee.email,
                    "error": str(e)
                })
        
        # Generate CSV if requested
        if export_csv and paid_bonuses:
            return self._generate_bonus_csv(paid_bonuses, payment_date)
        
        return Response({
            "message": f"Bonus payment status updated. {updated_count} marked as paid.",
            "payment_type": "bonus",
            "total_requested": len(bonus_ids),
            "updated": updated_count,
            "already_paid": already_paid,
            "failed": len(errors),
            "errors": errors
        }, status=status.HTTP_200_OK)
    
    def _generate_salary_csv(self, payslips, payment_date):
        """Generate CSV file for salary payments"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="salary_payments_{payment_date}.csv"'
        
        writer = csv.writer(response)
        
        # CSV Headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Email', 'Department', 'Designation', 'Branch',
            'Payment Month', 'Basic Salary', 'Gross Salary', 'Total Deductions', 'Net Salary',
            'Overtime Pay', 'Tax Deduction', 'Payment Status', 'Payment Date', 'Payment Method',
            'Payment Reference', 'Account Holder Name', 'Bank Name', 'Account Number', 
            'IFSC Code', 'Branch Name', 'Account Type'
        ])
        
        # CSV Data Rows
        for payslip in payslips:
            profile = payslip.employee.profile
            
            # Get primary account details
            primary_account = profile.account_details.filter(is_primary=True).first()
            if not primary_account:
                primary_account = profile.account_details.first()
            
            writer.writerow([
                profile.employee_id or 'N/A',
                profile.full_name,
                payslip.employee.email,
                profile.department.name if profile.department else 'N/A',
                profile.designation.name if profile.designation else 'N/A',
                profile.branch.name if profile.branch else 'N/A',
                payslip.payment_month.strftime('%Y-%m'),
                payslip.basic_salary,
                payslip.gross_salary,
                payslip.total_deductions,
                payslip.net_salary,
                payslip.total_overtime_pay or 0,
                payslip.total_tax_deduction or 0,
                payslip.status,
                payslip.payment_date.strftime('%Y-%m-%d') if payslip.payment_date else 'N/A',
                payslip.payment_method or 'N/A',
                payslip.payment_reference or 'N/A',
                primary_account.account_holder_name if primary_account else 'N/A',
                primary_account.bank_name if primary_account else 'N/A',
                primary_account.account_number if primary_account else 'N/A',
                primary_account.ifsc_code if primary_account else 'N/A',
                primary_account.branch_name if primary_account else 'N/A',
                primary_account.account_type if primary_account else 'N/A',
            ])
        
        return response
    
    def _generate_bonus_csv(self, bonuses, payment_date):
        """Generate CSV file for bonus payments"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bonus_payments_{payment_date}.csv"'
        
        writer = csv.writer(response)
        
        # CSV Headers
        writer.writerow([
            'Employee ID', 'Employee Name', 'Email', 'Department', 'Designation', 'Branch',
            'Bonus Month', 'Bonus Amount', 'Festival Name', 'Payment Status', 'Payment Date', 
            'Payment Method', 'Payment Reference', 'Account Holder Name', 'Bank Name', 
            'Account Number', 'IFSC Code', 'Branch Name', 'Account Type'
        ])
        
        # CSV Data Rows
        for bonus in bonuses:
            profile = bonus.employee.profile
            
            # Get primary account details
            primary_account = profile.account_details.filter(is_primary=True).first()
            if not primary_account:
                primary_account = profile.account_details.first()
            
            writer.writerow([
                profile.employee_id or 'N/A',
                profile.full_name,
                bonus.employee.email,
                profile.department.name if profile.department else 'N/A',
                profile.designation.name if profile.designation else 'N/A',
                profile.branch.name if profile.branch else 'N/A',
                bonus.bonus_month.strftime('%Y-%m'),
                bonus.bonus_amount,
                bonus.festival_name or 'N/A',  # Fixed: Use festival_name instead of bonus_type
                bonus.status,
                bonus.payment_date.strftime('%Y-%m-%d') if bonus.payment_date else 'N/A',
                bonus.payment_method or 'N/A',
                bonus.payment_reference or 'N/A',
                primary_account.account_holder_name if primary_account else 'N/A',
                primary_account.bank_name if primary_account else 'N/A',
                primary_account.account_number if primary_account else 'N/A',
                primary_account.ifsc_code if primary_account else 'N/A',
                primary_account.branch_name if primary_account else 'N/A',
                primary_account.account_type if primary_account else 'N/A',
            ])
        
        return response


class MyPayrollView(APIView):
    """Employee's own payroll history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        employee = request.user
        queryset = PaySlip.objects.filter(
            employee=employee,
            status='Paid'  # Only show paid payslips
        ).select_related(
            'employee__profile', 'employee__profile__monthly_pay_grade',
            'employee__profile__hourly_pay_grade'
        ).order_by('-payment_month')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        output = []
        for payslip in page:
            profile = employee.profile
            pay_grade_name = "N/A"
            if profile.monthly_pay_grade:
                pay_grade_name = profile.monthly_pay_grade.grade_name
            elif profile.hourly_pay_grade:
                pay_grade_name = profile.hourly_pay_grade.pay_grade_name
            
            output.append({
                "payslip_id": payslip.pk,
                "month": payslip.payment_month.strftime('%B %Y'),
                "employee_name": profile.full_name,
                "photo": request.build_absolute_uri(profile.photo.url) if profile.photo else None,
                "pay_grade": pay_grade_name,
                "basic_salary": payslip.basic_salary,
                "gross_salary": payslip.gross_salary,
                "status": payslip.status,
            })
        
        return paginator.get_paginated_response(output)