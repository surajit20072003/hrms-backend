from django.urls import path
from .views import *
urlpatterns = [
    # URL for listing and creating departments
    # GET, POST -> /api/company/departments/
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),#done
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),#done
    path('designations/', DesignationListCreateView.as_view(), name='designation-list-create'),#done
    path('designations/<int:pk>/', DesignationDetailView.as_view(), name='designation-detail'),#done
    path('branches/', BranchListCreateView.as_view(), name='branch-list-create'),#done
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),#done
    path('employees/', EmployeeListView.as_view(), name='employee-list'),#done
    path('employees/create/', EmployeeCreateView.as_view(), name='employee-create'),#done
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),#done
    
    # URLs for managing a specific employee's education and experience
    path("employees/<int:employee_pk>/education/", EmployeeEducationView.as_view()),#done
    path("employees/<int:employee_pk>/education/<int:education_pk>/", EmployeeEducationDetailView.as_view()),#done

    path("employees/<int:employee_pk>/experience/", EmployeeExperienceView.as_view()),#done
    path("employees/<int:employee_pk>/experience/<int:experience_pk>/", EmployeeExperienceDetailView.as_view()),#done

    path("employees/<int:employee_pk>/account-details/", EmployeeAccountDetailsView.as_view()),#done
    path("employees/<int:employee_pk>/account-details/<int:account_pk>/", EmployeeAccountDetailsDetailView.as_view()),#done


    path('warnings/', WarningListCreateView.as_view(), name='warning-list-create'),#done
    path('warnings/<int:pk>/', WarningDetailView.as_view(), name='warning-detail'),#doneS
    path('terminations/', TerminationListCreateView.as_view(), name='termination-list-create'),#done
    path('terminations/<int:pk>/', TerminationDetailView.as_view(), name='termination-detail'),#done
    path('promotions/', PromotionListCreateView.as_view(), name='promotion-list-create'),#done

    path('promotions/<int:pk>/', PromotionDetailView.as_view(), name='promotion-detail'),#done
    path('employees/<int:pk>/update-status/', EmployeeJobStatusUpdateView.as_view(), name='employee-update-status'),#need to change

    path('leave/setup/holidays/', HolidayListCreateView.as_view(), name='holiday-list-create'),#done
    path('leave/setup/holidays/<int:pk>/', HolidayDetailView.as_view(), name='holiday-detail'),#done
    path('leave/setup/public-holidays/', PublicHolidayListCreateView.as_view(), name='public-holiday-list-create'),#done
    path('leave/setup/public-holidays/<int:pk>/', PublicHolidayDetailView.as_view(), name='public-holiday-detail'),#done
    path('leave/setup/weekly-holidays/', WeeklyHolidayListCreateView.as_view(), name='weekly-holiday-list-create'),#done
    path('leave/setup/weekly-holidays/<int:pk>/', WeeklyHolidayDetailView.as_view(), name='weekly-holiday-detail'),#done
    path('leave/setup/leave-types/', LeaveTypeListCreateView.as_view(), name='leave-type-list-create'),#done
    path('leave/setup/leave-types/<int:pk>/', LeaveTypeDetailView.as_view(), name='leave-type-detail'),#done
    path('leave/setup/earn-leave-rule/', EarnLeaveRuleView.as_view(), name='earn-leave-rule'),#changed
    path('leave/apply/', ApplyForLeaveView.as_view(), name='apply-for-leave'), #done 
    path('leave/my-applications/', MyLeaveApplicationsView.as_view(), name='my-leave-applications'), #done 

    path('admin/leave/all-requests/', AllLeaveApplicationsView.as_view(), name='admin-all-leave-requests'), #done 
    path('admin/leave/approve-reject/<int:pk>/', LeaveApprovalView.as_view(), name='leave-approve-reject'), #done 


    path('leave/report/employee/', EmployeeLeaveReportView.as_view(), name='employee-leave-report'),#small changes
    path('leave/report/my-leave/', MyLeaveReportView.as_view(), name='my-leave-report'),#small changes
    path('leave/report/summary/', LeaveSummaryReportView.as_view(), name='leave-summary-report'),#done

    path('attendance/setup/shifts/', WorkShiftListCreateAPIView.as_view(), name='workshift-list-create'),#done
    
    path('attendance/setup/shifts/<int:pk>/', WorkShiftDetailAPIView.as_view(), name='workshift-detail'),#done


    #get and patch
    path('attendance/manual/', ManualAttendanceView.as_view(), name='manual-attendance-entry'),#partially done


    path('attendance/reports/daily/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),#done
    path('attendance/reports/monthly/', MonthlyAttendanceReportView.as_view(), name='monthly-attendance-report'),#done
    path('attendance/reports/my/', MyAttendanceReportView.as_view(), name='my-attendance-report'),#done
    path('attendance/reports/summary/', AttendanceSummaryReportView.as_view(), name='attendance-summary-report'),#done


    path('payroll/allowances/', AllowanceListCreateView.as_view(), name='allowance-list-create'),#done
    path('payroll/allowances/<int:pk>/', AllowanceDetailView.as_view(), name='allowance-detail'),#done

    # --- Payroll Setup: Deduction URLs ---
    path('payroll/deductions/', DeductionListCreateView.as_view(), name='deduction-list-create'),#done
    path('payroll/deductions/<int:pk>/', DeductionDetailView.as_view(), name='deduction-detail'),#done 


    path('payroll/monthly/paygrades/',MonthlyPayGradeListCreateView.as_view(),name='monthly-paygrade-list-create'),#done
    path('payroll/monthly/paygrades/<int:pk>/',MonthlyPayGradeDetailView.as_view(),name='monthly-paygrade-detail'),#done


    path('payroll/hourly-paygrades/',HourlyPayGradeListCreateView.as_view(),name='hourly-paygrade-list-create'),#done
    path('payroll/hourly-paygrades/<int:pk>/',HourlyPayGradeDetailView.as_view(), name='hourly-paygrade-detail'),#done


    path('performance-categories/',PerformanceCategoryListCreateAPIView.as_view(),name='performance-category-list-create'),#done
    path('performance-categories/<int:pk>/',PerformanceCategoryDetailAPIView.as_view(),name='performance-category-detail'),#done



    path('performance-criteria/',PerformanceCriteriaListCreateAPIView.as_view(),name='performance-criteria-list-create'),#done
    path('performance-criteria/<int:pk>/',PerformanceCriteriaDetailAPIView.as_view(),name='performance-criteria-detail'),#done


    path('employee-performance/',EmployeePerformanceListCreateAPIView.as_view(),name='employee-performance-list-create'),#done #now relation with user table
    path('employee-performance/<int:pk>/',EmployeePerformanceDetailAPIView.as_view(),name='employee-performance-detail'),#done

    
    path('performance-summary-report/',PerformanceSummaryReportAPIView.as_view(),name='performance-summary-report'),#done


    path('job-posts/', JobPostListCreateAPIView.as_view(), name='jobpost-list-create'),#done
    path('job-posts/<int:pk>/', JobPostDetailAPIView.as_view(), name='jobpost-detail'),#done


    path('training-types/',TrainingTypeListCreateAPIView.as_view(),name='training-type-list-create'),#done   #now relation with user table
    path('training-types/<int:pk>/',TrainingTypeDetailAPIView.as_view(),name='training-type-detail'),#done

    path('employee-trainings/', EmployeeTrainingListCreateAPIView.as_view(), name='employee-training-list-create'),#done
    path('employee-trainings/<int:pk>/', EmployeeTrainingDetailAPIView.as_view(), name='employee-training-detail'),#done

    path('employee-training-report/', EmployeeTrainingReportAPIView.as_view(),name='employee-training-report'),#done


    path('employee-awards/', AwardListCreateAPIView.as_view(), name='employee-award-list-create'),  #done      #now relation with user table
    path('employee-awards/<int:pk>/', AwardDetailAPIView.as_view(), name='employee-award-detail'),  #done


    path('notices/', NoticeListCreateAPIView.as_view(), name='notice-list-create'),#done
    path('notices/<int:pk>/', NoticeDetailAPIView.as_view(), name='notice-detail'),#done


    path('dashboard-data/', DashboardDataAPIView.as_view(), name='dashboard-data'),#done


    path('setup/late-configuration/',LateDeductionRuleListCreateAPIView.as_view(), name='late-rule-list-create-api'),#done
    path('setup/late-configuration/<int:pk>/',LateDeductionRuleRetrieveUpdateDestroyAPIView.as_view(),name='late-rule-crud-api'),#done
    
    path('setup/tax-rules/', TaxRuleSetupAPIView.as_view(),name='tax-rule-setup'),#done


    path('payslip/generate/', SinglePaySlipGenerateRetrieveAPIView.as_view(), name='payslip-generate'),#done
    # GET: Retrieves a specific payslip record by ID
    path('payslip/<int:pk>/', SinglePaySlipGenerateRetrieveAPIView.as_view(), name='payslip-retrieve'),#done
    # POST: Generate payslips for multiple employees based on filters
    path('payslip/generate-bulk/', BulkPaySlipGenerateAPIView.as_view(), name='payslip-generate-bulk'),#done
    path('sheet/list/', MonthlySalarySheetView.as_view(), name='monthly-salary-sheet-list'),#done
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),#done
    

    path('attendance/upload-csv/', CSVAttendanceUploadView.as_view(), name='attendance-upload-csv'),#done


    path('roles/', RoleListView.as_view(), name='role-list-create'),#done
    
    # 2. API for Role Detail, Update, and Delete (GET, PUT/PATCH, DELETE)
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),#done

    path('punch/automatic/', AutomaticAttendanceView.as_view(), name='attendance-automatic-punch'),#done

    path('bonus-settings/', BonusSettingListCreateView.as_view(), name='bonus-setting-list-create'),#done
    path('bonus-settings/<int:pk>/', BonusSettingDetailView.as_view(), name='bonus-setting-detail'),#done


    path('bonus/generate/', GenerateBonusView.as_view(), name='bonus-generate'),#done
    
    # Employee Bonus List
    path('employee-bonuses/', EmployeeBonusListView.as_view(), name='employee-bonus-list'),#done


    path('payments/mark-paid/', MarkPaymentPaidView.as_view(), name='mark-payment-paid'),#done

    path('my-payroll/', MyPayrollView.as_view(), name='my-payroll'),
]




















