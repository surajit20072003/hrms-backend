from django.urls import path
from .views import *
urlpatterns = [
    # URL for listing and creating departments
    # GET, POST -> /api/company/departments/
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('designations/', DesignationListCreateView.as_view(), name='designation-list-create'),
    path('designations/<int:pk>/', DesignationDetailView.as_view(), name='designation-detail'),
    path('branches/', BranchListCreateView.as_view(), name='branch-list-create'),
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    
    # URLs for managing a specific employee's education and experience
    path('employees/<int:employee_pk>/education/', EmployeeEducationView.as_view(), name='employee-education'),
    path('employees/<int:employee_pk>/experience/', EmployeeExperienceView.as_view(), name='employee-experience'),
    path('warnings/', WarningListCreateView.as_view(), name='warning-list-create'),
    path('warnings/<int:pk>/', WarningDetailView.as_view(), name='warning-detail'),
    path('terminations/', TerminationListCreateView.as_view(), name='termination-list-create'),
    path('terminations/<int:pk>/', TerminationDetailView.as_view(), name='termination-detail'),
    path('promotions/', PromotionListCreateView.as_view(), name='promotion-list-create'),

    path('promotions/<int:pk>/', PromotionDetailView.as_view(), name='promotion-detail'),
    path('employees/<int:pk>/update-status/', EmployeeJobStatusUpdateView.as_view(), name='employee-update-status'),

    path('leave/setup/holidays/', HolidayListCreateView.as_view(), name='holiday-list-create'),
    path('leave/setup/holidays/<int:pk>/', HolidayDetailView.as_view(), name='holiday-detail'),
    path('leave/setup/public-holidays/', PublicHolidayListCreateView.as_view(), name='public-holiday-list-create'),
    path('leave/setup/public-holidays/<int:pk>/', PublicHolidayDetailView.as_view(), name='public-holiday-detail'),
    path('leave/setup/weekly-holidays/', WeeklyHolidayListCreateView.as_view(), name='weekly-holiday-list-create'),
    path('leave/setup/weekly-holidays/<int:pk>/', WeeklyHolidayDetailView.as_view(), name='weekly-holiday-detail'),
    path('leave/setup/leave-types/', LeaveTypeListCreateView.as_view(), name='leave-type-list-create'),
    path('leave/setup/leave-types/<int:pk>/', LeaveTypeDetailView.as_view(), name='leave-type-detail'),
    path('leave/setup/earn-leave-rule/', EarnLeaveRuleView.as_view(), name='earn-leave-rule'),
    path('leave/apply/', ApplyForLeaveView.as_view(), name='apply-for-leave'), 
    path('leave/my-applications/', MyLeaveApplicationsView.as_view(), name='my-leave-applications'), 

    path('admin/leave/all-requests/', AllLeaveApplicationsView.as_view(), name='admin-all-leave-requests'),
    path('admin/leave/approve-reject/<int:pk>/', LeaveApprovalView.as_view(), name='leave-approve-reject'),


    path('leave/report/employee/', EmployeeLeaveReportView.as_view(), name='employee-leave-report'),
    path('leave/report/my-leave/', MyLeaveReportView.as_view(), name='my-leave-report'),
    path('leave/report/summary/', LeaveSummaryReportView.as_view(), name='leave-summary-report'),

    path('attendance/setup/shifts/', WorkShiftListCreateAPIView.as_view(), name='workshift-list-create'),
    
    path('attendance/setup/shifts/<int:pk>/', WorkShiftDetailAPIView.as_view(), name='workshift-detail'),


    #get and patch
    path('attendance/manual/', ManualAttendanceView.as_view(), name='manual-attendance-entry'),


    path('attendance/reports/daily/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
    path('attendance/reports/monthly/', MonthlyAttendanceReportView.as_view(), name='monthly-attendance-report'),
    path('attendance/reports/my/', MyAttendanceReportView.as_view(), name='my-attendance-report'),
    path('attendance/reports/summary/', AttendanceSummaryReportView.as_view(), name='attendance-summary-report'),


    path('payroll/allowances/', AllowanceListCreateView.as_view(), name='allowance-list-create'),
    path('payroll/allowances/<int:pk>/', AllowanceDetailView.as_view(), name='allowance-detail'),

    # --- Payroll Setup: Deduction URLs ---
    path('payroll/deductions/', DeductionListCreateView.as_view(), name='deduction-list-create'),
    path('payroll/deductions/<int:pk>/', DeductionDetailView.as_view(), name='deduction-detail'), 


    path('payroll/monthly/paygrades/',MonthlyPayGradeListCreateView.as_view(),name='monthly-paygrade-list-create'),
    path('payroll/monthly/paygrades/<int:pk>/',MonthlyPayGradeDetailView.as_view(),name='monthly-paygrade-detail'),


    path('payroll/hourly-paygrades/',HourlyPayGradeListCreateView.as_view(),name='hourly-paygrade-list-create'),
    path('payroll/hourly-paygrades/<int:pk>/',HourlyPayGradeDetailView.as_view(), name='hourly-paygrade-detail'),


    path('performance-categories/',PerformanceCategoryListCreateAPIView.as_view(),name='performance-category-list-create'),
    path('performance-categories/<int:pk>/',PerformanceCategoryDetailAPIView.as_view(),name='performance-category-detail'),



    path('performance-criteria/',PerformanceCriteriaListCreateAPIView.as_view(),name='performance-criteria-list-create'),
    path('performance-criteria/<int:pk>/',PerformanceCriteriaDetailAPIView.as_view(),name='performance-criteria-detail'),


    path('employee-performance/',EmployeePerformanceListCreateAPIView.as_view(),name='employee-performance-list-create'),
    path('employee-performance/<int:pk>/',EmployeePerformanceDetailAPIView.as_view(),name='employee-performance-detail'),

    
    path('performance-summary-report/',PerformanceSummaryReportAPIView.as_view(),name='performance-summary-report'),


    path('job-posts/', JobPostListCreateAPIView.as_view(), name='jobpost-list-create'),
    path('job-posts/<int:pk>/', JobPostDetailAPIView.as_view(), name='jobpost-detail'),


    path('training-types/',TrainingTypeListCreateAPIView.as_view(),name='training-type-list-create'),
    path('training-types/<int:pk>/',TrainingTypeDetailAPIView.as_view(),name='training-type-detail'),

    path('employee-trainings/', EmployeeTrainingListCreateAPIView.as_view(), name='employee-training-list-create'),
    path('employee-trainings/<int:pk>/', EmployeeTrainingDetailAPIView.as_view(), name='employee-training-detail'),

    path('employee-training-report/', EmployeeTrainingReportAPIView.as_view(),name='employee-training-report'),


    path('employee-awards/', AwardListCreateAPIView.as_view(), name='employee-award-list-create'),
    path('employee-awards/<int:pk>/', AwardDetailAPIView.as_view(), name='employee-award-detail'),


    path('notices/', NoticeListCreateAPIView.as_view(), name='notice-list-create'),
    path('notices/<int:pk>/', NoticeDetailAPIView.as_view(), name='notice-detail'),


    path('dashboard-data/', DashboardDataAPIView.as_view(), name='dashboard-data'),


    path('setup/late-configuration/',LateDeductionRuleListCreateAPIView.as_view(), name='late-rule-list-create-api'),
    path('setup/late-configuration/<int:pk>/',LateDeductionRuleRetrieveUpdateDestroyAPIView.as_view(),name='late-rule-crud-api'),
    
    path('setup/tax-rules/', TaxRuleSetupAPIView.as_view(),name='tax-rule-setup'),


    path('payslip/generate/', SinglePaySlipGenerateRetrieveAPIView.as_view(), name='payslip-generate'),
    # GET: Retrieves a specific payslip record by ID
    path('payslip/<int:pk>/', SinglePaySlipGenerateRetrieveAPIView.as_view(), name='payslip-retrieve'),
    path('sheet/list/', MonthlySalarySheetView.as_view(), name='monthly-salary-sheet-list'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    

    path('attendance/upload-csv/', CSVAttendanceUploadView.as_view(), name='attendance-upload-csv'),
]




















