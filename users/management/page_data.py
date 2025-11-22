PAGES_DATA = [

    # --- Dashboard ---
    {'module': 'Dashboard', 'name': 'Dashboard View', 'codename': 'dashboard_view', 'url_name': '/', 'module_icon': 'DashboardOutlined'},

    # --- Administration ---
    {'module': 'Administration', 'name': 'Manage Role', 'codename': 'manage_role', 'url_name': '/administration/manage-role', 'module_icon': 'SettingOutlined'},
    {'module': 'Administration', 'name': 'Add Role', 'codename': 'add_role', 'url_name': '/administration/manage-role/add-role'},
    {'module': 'Administration', 'name': 'Add Role Permission', 'codename': 'add_role_permission', 'url_name': '/administration/manage-role/add-role-permission'},
    {'module': 'Administration', 'name': 'Change Password', 'codename': 'change_password', 'url_name': '/administration/change-password'},

    # --- Employee Management ---
    {'module': 'Employee Management', 'name': 'Department', 'codename': 'manage_department', 'url_name': '/employee-management/department', 'module_icon': 'TeamOutlined'},
    {'module': 'Employee Management', 'name': 'Designation', 'codename': 'manage_designation', 'url_name': '/employee-management/designation'},
    {'module': 'Employee Management', 'name': 'Branch', 'codename': 'manage_branch', 'url_name': '/employee-management/branch'},
    {'module': 'Employee Management', 'name': 'Manage Employee', 'codename': 'manage_employee', 'url_name': '/employee-management/manage-employee'},
    {'module': 'Employee Management', 'name': 'Warning', 'codename': 'manage_warning', 'url_name': '/employee-management/warning'},
    {'module': 'Employee Management', 'name': 'Termination', 'codename': 'manage_termination', 'url_name': '/employee-management/termination'},
    {'module': 'Employee Management', 'name': 'Promotion', 'codename': 'manage_promotion', 'url_name': '/employee-management/promotion'},
    {'module': 'Employee Management', 'name': 'Employee Permanent Status', 'codename': 'employee_permanent_status', 'url_name': '/employee-management/employee-permanent'},

    # --- Leave Management ---
    {'module': 'Leave Management', 'name': 'Manage Holiday', 'codename': 'manage_holiday', 'url_name': '/leave-management/setup/manage-holiday', 'module_icon': 'CalendarOutlined'},
    {'module': 'Leave Management', 'name': 'Public Holiday', 'codename': 'public_holiday', 'url_name': '/leave-management/setup/public-holiday'},
    {'module': 'Leave Management', 'name': 'Weekly Holiday', 'codename': 'weekly_holiday', 'url_name': '/leave-management/setup/weekly-holiday'},
    {'module': 'Leave Management', 'name': 'Leave Type', 'codename': 'manage_leave_type', 'url_name': '/leave-management/setup/leave-type'},
    {'module': 'Leave Management', 'name': 'Earn Leave Configure', 'codename': 'earn_leave_configure', 'url_name': '/leave-management/setup/earn-leave-configure'},
    {'module': 'Leave Management', 'name': 'Apply for Leave', 'codename': 'apply_for_leave', 'url_name': '/leave-management/leave-application/apply-for-leave'},
    {'module': 'Leave Management', 'name': 'Requested Application', 'codename': 'view_requested_leave', 'url_name': '/leave-management/leave-application/requested-application'},
    {'module': 'Leave Management', 'name': 'Leave Report', 'codename': 'leave_report', 'url_name': '/leave-management/report/leave-report'},
    {'module': 'Leave Management', 'name': 'Leave Summary Report', 'codename': 'leave_summary_report', 'url_name': '/leave-management/report/summary-report'},
    {'module': 'Leave Management', 'name': 'My Leave Report', 'codename': 'my_leave_report', 'url_name': '/leave-management/report/my-leave-report'},

    # --- Attendance ---
    {'module': 'Attendance', 'name': 'Manage Work Shift', 'codename': 'manage_shift', 'url_name': '/attendance/setup/manage-work-shift', 'module_icon': 'ClockCircleOutlined'},
    {'module': 'Attendance', 'name': 'Dashboard Attendance', 'codename': 'dashboard_attendance_view', 'url_name': '/attendance/setup/dashboard-attendance'},
    {'module': 'Attendance', 'name': 'Daily Attendance', 'codename': 'daily_attendance', 'url_name': '/attendance/report/daily-attendance'},
    {'module': 'Attendance', 'name': 'Monthly Attendance', 'codename': 'monthly_attendance', 'url_name': '/attendance/report/monthly-attendance'},
    {'module': 'Attendance', 'name': 'My Attendance Report', 'codename': 'my_attendance_report', 'url_name': '/attendance/report/my-attendance-report'},
    {'module': 'Attendance', 'name': 'Attendance Summary Report', 'codename': 'attendance_summary_report', 'url_name': '/attendance/report/summary-report'},
    {'module': 'Attendance', 'name': 'Manual Attendance', 'codename': 'manual_attendance', 'url_name': '/attendance/manual-attendance'},

    # --- Payroll ---
    {'module': 'Payroll', 'name': 'Tax Rule Setup', 'codename': 'tax_rule_setup', 'url_name': '/payroll/setup/tax-rule-setup', 'module_icon': 'DollarOutlined'},
    {'module': 'Payroll', 'name': 'Late Configuration', 'codename': 'late_configuration', 'url_name': '/payroll/setup/late-configuration'},
    {'module': 'Payroll', 'name': 'Allowance', 'codename': 'manage_allowance', 'url_name': '/payroll/allowance'},
    {'module': 'Payroll', 'name': 'Deduction', 'codename': 'manage_deduction', 'url_name': '/payroll/deduction'},
    {'module': 'Payroll', 'name': 'Monthly Pay Grade', 'codename': 'monthly_pay_grade', 'url_name': '/payroll/monthly-pay-grade'},
    {'module': 'Payroll', 'name': 'Hourly Pay Grade', 'codename': 'hourly_pay_grade', 'url_name': '/payroll/hourly-pay-grade'},
    {'module': 'Payroll', 'name': 'Generate Salary Sheet', 'codename': 'generate_salary_sheet', 'url_name': '/payroll/generate-salary-sheet'},
    {'module': 'Payroll', 'name': 'Payment History', 'codename': 'payment_history', 'url_name': '/payroll/report/payment-history'},
    {'module': 'Payroll', 'name': 'My Payroll', 'codename': 'my_payroll', 'url_name': '/payroll/report/my-payroll'},
    {'module': 'Payroll', 'name': 'Approve Work Hour', 'codename': 'approve_work_hour', 'url_name': '/payroll/manage-work-hour/approve-work-hour'},
    {'module': 'Payroll', 'name': 'Bonus Setting', 'codename': 'bonus_setting', 'url_name': '/payroll/manage-bonus/bonus-setting'},
    {'module': 'Payroll', 'name': 'Generate Bonus', 'codename': 'generate_bonus', 'url_name': '/payroll/manage-bonus/generate-bonus'},

    # --- Performance ---
    {'module': 'Performance', 'name': 'Performance Category', 'codename': 'performance_category', 'url_name': '/performance-category', 'module_icon': 'BarChartOutlined'},
    {'module': 'Performance', 'name': 'Performance Criteria', 'codename': 'performance_criteria', 'url_name': '/performance-criteria'},
    {'module': 'Performance', 'name': 'Employee Performance Review', 'codename': 'employee_performance', 'url_name': '/EMPLOYEE-performance'},
    {'module': 'Performance', 'name': 'Performance Summary Report', 'codename': 'performance_summary_report', 'url_name': '/performance-summary-report'},

    # --- Recruitment ---
    {'module': 'Recruitment', 'name': 'Job Post', 'codename': 'job_post', 'url_name': '/job-post', 'module_icon': 'UserAddOutlined'},
    {'module': 'Recruitment', 'name': 'Job Candidate', 'codename': 'job_candidate', 'url_name': '/job-candidate'},

    # --- Training ---
    {'module': 'Training', 'name': 'Training Type', 'codename': 'training_type', 'url_name': '/training-type', 'module_icon': 'ReadOutlined'},
    {'module': 'Training', 'name': 'Training List', 'codename': 'training_list', 'url_name': '/training-list'},
    {'module': 'Training', 'name': 'Training Report', 'codename': 'training_report', 'url_name': '/training-report'},

    # --- Award ---
    {'module': 'Award', 'name': 'Award Management', 'codename': 'manage_award', 'url_name': '/award', 'module_icon': 'TrophyOutlined'},

    # --- Notice Board ---
    {'module': 'Notice Board', 'name': 'Notice Management', 'codename': 'manage_notice', 'url_name': '/notice', 'module_icon': 'NotificationOutlined'},

    # --- Settings ---
    {'module': 'Settings', 'name': 'General Settings', 'codename': 'general_settings', 'url_name': '/settings', 'module_icon': 'SettingOutlined'},
]
