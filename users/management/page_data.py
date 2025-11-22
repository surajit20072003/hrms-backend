
PAGES_DATA = [
    # --- Dashboard (module_order=1) ---
    {'module': 'Dashboard', 'module_order': 1, 'name': 'Dashboard View',
     'codename': 'dashboard_view', 'url_name': '/', 'module_icon': 'DashboardOutlined', 'order': 1, 'parent_codename': None},

    # --- Administration (module_order=2) ---
    {'module': 'Administration', 'module_order': 2, 'name': 'Manage Role',
     'codename': 'manage_role', 'url_name': '/administration/manage-role', 'module_icon': 'SettingOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Administration', 'module_order': 2, 'name': 'Add Role',
     'codename': 'add_role', 'url_name': '/administration/manage-role/add-role', 'module_icon': 'PlusOutlined', 'order': 1, 'parent_codename': 'manage_role'}, # Added Icon
    {'module': 'Administration', 'module_order': 2, 'name': 'Add Role Permission',
     'codename': 'add_role_permission', 'url_name': '/administration/manage-role/add-role-permission', 'module_icon': 'UnlockOutlined', 'order': 2, 'parent_codename': 'manage_role'}, # Added Icon
    {'module': 'Administration', 'module_order': 2, 'name': 'Change Password',
     'codename': 'change_password', 'url_name': '/administration/change-password', 'module_icon': 'KeyOutlined', 'order': 2, 'parent_codename': None}, # Added Icon

    # --- Employee Management (module_order=3) ---
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Department',
     'codename': 'manage_department', 'url_name': '/employee-management/department', 'module_icon': 'TeamOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Designation',
     'codename': 'manage_designation', 'url_name': '/employee-management/designation', 'module_icon': 'UserOutlined', 'order': 2, 'parent_codename': None}, # Added Icon
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Branch',
     'codename': 'manage_branch', 'url_name': '/employee-management/branch', 'module_icon': 'BankOutlined', 'order': 3, 'parent_codename': None}, # Added Icon
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Manage Employee',
     'codename': 'manage_employee', 'url_name': '/employee-management/manage-employee', 'module_icon': 'TeamOutlined', 'order': 4, 'parent_codename': None}, # Added Icon
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Warning',
     'codename': 'manage_warning', 'url_name': '/employee-management/warning', 'module_icon': 'WarningOutlined', 'order': 5, 'parent_codename': None}, # Added Icon
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Termination',
     'codename': 'manage_termination', 'url_name': '/employee-management/termination', 'module_icon': 'UserDeleteOutlined', 'order': 6, 'parent_codename': None}, # Added Icon (Using UserDeleteOutlined)
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Promotion',
     'codename': 'manage_promotion', 'url_name': '/employee-management/promotion', 'module_icon': 'RiseOutlined', 'order': 7, 'parent_codename': None}, # Added Icon
    {'module': 'Employee Management', 'module_order': 3, 'name': 'Employee Permanent Status',
     'codename': 'employee_permanent_status', 'url_name': '/employee-management/employee-permanent', 'module_icon': 'CheckCircleOutlined', 'order': 8, 'parent_codename': None}, # Added Icon

    # --- Leave Management (module_order=4) ---
    # top-level grouping pages (Setup / Leave Application / Report)
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Setup',
     'codename': 'leave_setup', 'url_name': '/leave-management/setup', 'module_icon': 'CalendarOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Leave Application',
     'codename': 'leave_application', 'url_name': '/leave-management/leave-application', 'module_icon': 'ProfileOutlined', 'order': 2, 'parent_codename': None}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Report',
     'codename': 'leave_report_section', 'url_name': '/leave-management/report', 'module_icon': 'BarChartOutlined', 'order': 3, 'parent_codename': None}, # Added Icon

    # Setup children
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Manage Holiday',
     'codename': 'manage_holiday', 'url_name': '/leave-management/setup/manage-holiday', 'module_icon': 'CalendarOutlined', 'order': 1, 'parent_codename': 'leave_setup'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Public Holiday',
     'codename': 'public_holiday', 'url_name': '/leave-management/setup/public-holiday', 'module_icon': 'CalendarOutlined', 'order': 2, 'parent_codename': 'leave_setup'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Weekly Holiday',
     'codename': 'weekly_holiday', 'url_name': '/leave-management/setup/weekly-holiday', 'module_icon': 'CalendarOutlined', 'order': 3, 'parent_codename': 'leave_setup'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Leave Type',
     'codename': 'manage_leave_type', 'url_name': '/leave-management/setup/leave-type', 'module_icon': 'FileTextOutlined', 'order': 4, 'parent_codename': 'leave_setup'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Earn Leave Configure',
     'codename': 'earn_leave_configure', 'url_name': '/leave-management/setup/earn-leave-configure', 'module_icon': 'CalculatorOutlined', 'order': 5, 'parent_codename': 'leave_setup'}, # Added Icon

    # Leave Application children
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Apply for Leave',
     'codename': 'apply_for_leave', 'url_name': '/leave-management/leave-application/apply-for-leave', 'module_icon': 'PlusOutlined', 'order': 1, 'parent_codename': 'leave_application'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Requested Application',
     'codename': 'view_requested_leave', 'url_name': '/leave-management/leave-application/requested-application', 'module_icon': 'ScheduleOutlined', 'order': 2, 'parent_codename': 'leave_application'}, # Added Icon

    # Report children
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Leave Report',
     'codename': 'leave_report', 'url_name': '/leave-management/report/leave-report', 'module_icon': 'FileTextOutlined', 'order': 1, 'parent_codename': 'leave_report_section'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'Leave Summary Report',
     'codename': 'leave_summary_report', 'url_name': '/leave-management/report/summary-report', 'module_icon': 'BarChartOutlined', 'order': 2, 'parent_codename': 'leave_report_section'}, # Added Icon
    {'module': 'Leave Management', 'module_order': 4, 'name': 'My Leave Report',
     'codename': 'my_leave_report', 'url_name': '/leave-management/report/my-leave-report', 'module_icon': 'UserOutlined', 'order': 3, 'parent_codename': 'leave_report_section'}, # Added Icon

    # --- Attendance (module_order=5) ---
    {'module': 'Attendance', 'module_order': 5, 'name': 'Setup',
     'codename': 'attendance_setup', 'url_name': '/attendance/setup', 'module_icon': 'ClockCircleOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Attendance', 'module_order': 5, 'name': 'Report',
     'codename': 'attendance_report_section', 'url_name': '/attendance/report', 'module_icon': 'BarChartOutlined', 'order': 2, 'parent_codename': None}, # Added Icon

    # Setup children
    {'module': 'Attendance', 'module_order': 5, 'name': 'Manage Work Shift',
     'codename': 'manage_shift', 'url_name': '/attendance/setup/manage-work-shift', 'module_icon': 'ClockCircleOutlined', 'order': 1, 'parent_codename': 'attendance_setup'}, # Added Icon
    {'module': 'Attendance', 'module_order': 5, 'name': 'Dashboard Attendance',
     'codename': 'dashboard_attendance_view', 'url_name': '/attendance/setup/dashboard-attendance', 'module_icon': 'DashboardOutlined', 'order': 2, 'parent_codename': 'attendance_setup'}, # Added Icon

    # Report children
    {'module': 'Attendance', 'module_order': 5, 'name': 'Daily Attendance',
     'codename': 'daily_attendance', 'url_name': '/attendance/report/daily-attendance', 'module_icon': 'CalendarOutlined', 'order': 1, 'parent_codename': 'attendance_report_section'}, # Added Icon
    {'module': 'Attendance', 'module_order': 5, 'name': 'Monthly Attendance',
     'codename': 'monthly_attendance', 'url_name': '/attendance/report/monthly-attendance', 'module_icon': 'ScheduleOutlined', 'order': 2, 'parent_codename': 'attendance_report_section'}, # Added Icon
    {'module': 'Attendance', 'module_order': 5, 'name': 'My Attendance Report',
     'codename': 'my_attendance_report', 'url_name': '/attendance/report/my-attendance-report', 'module_icon': 'FileTextOutlined', 'order': 3, 'parent_codename': 'attendance_report_section'}, # Added Icon
    {'module': 'Attendance', 'module_order': 5, 'name': 'Attendance Summary Report',
     'codename': 'attendance_summary_report', 'url_name': '/attendance/report/summary-report', 'module_icon': 'BarChartOutlined', 'order': 4, 'parent_codename': 'attendance_report_section'}, # Added Icon

    # Manual Attendance (top-level inside Attendance)
    {'module': 'Attendance', 'module_order': 5, 'name': 'Manual Attendance',
     'codename': 'manual_attendance', 'url_name': '/attendance/manual-attendance', 'module_icon': 'EditOutlined', 'order': 3, 'parent_codename': None}, # Added Icon

    # --- Payroll (module_order=6) ---
    {'module': 'Payroll', 'module_order': 6, 'name': 'Setup',
     'codename': 'payroll_setup', 'url_name': '/payroll/setup', 'module_icon': 'DollarOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Payroll', 'module_order': 6, 'name': 'Allowance',
     'codename': 'manage_allowance', 'url_name': '/payroll/allowance', 'module_icon': 'PlusOutlined', 'order': 2, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Deduction',
     'codename': 'manage_deduction', 'url_name': '/payroll/deduction', 'module_icon': 'MinusOutlined', 'order': 3, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Monthly Pay Grade',
     'codename': 'monthly_pay_grade', 'url_name': '/payroll/monthly-pay-grade', 'module_icon': 'DollarOutlined', 'order': 4, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Hourly Pay Grade',
     'codename': 'hourly_pay_grade', 'url_name': '/payroll/hourly-pay-grade', 'module_icon': 'ClockCircleOutlined', 'order': 5, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Generate Salary Sheet',
     'codename': 'generate_salary_sheet', 'url_name': '/payroll/generate-salary-sheet', 'module_icon': 'FileTextOutlined', 'order': 6, 'parent_codename': None}, # Added Icon

    # Setup children
    {'module': 'Payroll', 'module_order': 6, 'name': 'Tax Rule Setup',
     'codename': 'tax_rule_setup', 'url_name': '/payroll/setup/tax-rule-setup', 'module_icon': 'FileTextOutlined', 'order': 1, 'parent_codename': 'payroll_setup'}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Late Configuration',
     'codename': 'late_configuration', 'url_name': '/payroll/setup/late-configuration', 'module_icon': 'ClockCircleOutlined', 'order': 2, 'parent_codename': 'payroll_setup'}, # Added Icon

    # Report grouping
    {'module': 'Payroll', 'module_order': 6, 'name': 'Report',
     'codename': 'payroll_report_section', 'url_name': '/payroll/report', 'module_icon': 'BarChartOutlined', 'order': 7, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Payment History',
     'codename': 'payment_history', 'url_name': '/payroll/report/payment-history', 'module_icon': 'FileTextOutlined', 'order': 1, 'parent_codename': 'payroll_report_section'}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'My Payroll',
     'codename': 'my_payroll', 'url_name': '/payroll/report/my-payroll', 'module_icon': 'UserOutlined', 'order': 2, 'parent_codename': 'payroll_report_section'}, # Added Icon

    # Manage Work Hour grouping
    {'module': 'Payroll', 'module_order': 6, 'name': 'Manage Work Hour',
     'codename': 'payroll_manage_work_hour', 'url_name': '/payroll/manage-work-hour', 'module_icon': 'ClockCircleOutlined', 'order': 8, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Approve Work Hour',
     'codename': 'approve_work_hour', 'url_name': '/payroll/manage-work-hour/approve-work-hour', 'module_icon': 'CheckOutlined', 'order': 1, 'parent_codename': 'payroll_manage_work_hour'}, # Added Icon

    # Manage Bonus grouping
    {'module': 'Payroll', 'module_order': 6, 'name': 'Manage Bonus',
     'codename': 'payroll_manage_bonus', 'url_name': '/payroll/manage-bonus', 'module_icon': 'GiftOutlined', 'order': 9, 'parent_codename': None}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Bonus Setting',
     'codename': 'bonus_setting', 'url_name': '/payroll/manage-bonus/bonus-setting', 'module_icon': 'SettingOutlined', 'order': 1, 'parent_codename': 'payroll_manage_bonus'}, # Added Icon
    {'module': 'Payroll', 'module_order': 6, 'name': 'Generate Bonus',
     'codename': 'generate_bonus', 'url_name': '/payroll/manage-bonus/generate-bonus', 'module_icon': 'PlusOutlined', 'order': 2, 'parent_codename': 'payroll_manage_bonus'}, # Added Icon

    # --- Performance (module_order=7) ---
    {'module': 'Performance', 'module_order': 7, 'name': 'Performance Category',
     'codename': 'performance_category', 'url_name': '/performance-category', 'module_icon': 'BarChartOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Performance', 'module_order': 7, 'name': 'Performance Criteria',
     'codename': 'performance_criteria', 'url_name': '/performance-criteria', 'module_icon': 'SafetyCertificateOutlined', 'order': 2, 'parent_codename': None}, # Added Icon
    {'module': 'Performance', 'module_order': 7, 'name': 'Employee Performance Review',
     'codename': 'employee_performance', 'url_name': '/EMPLOYEE-performance', 'module_icon': 'UserOutlined', 'order': 3, 'parent_codename': None}, # Added Icon
    {'module': 'Performance', 'module_order': 7, 'name': 'Report',
     'codename': 'performance_report_section', 'url_name': '/performance/report', 'module_icon': 'FileTextOutlined', 'order': 4, 'parent_codename': None}, # Added Icon
    {'module': 'Performance', 'module_order': 7, 'name': 'Performance Summary Report',
     'codename': 'performance_summary_report', 'url_name': '/performance-summary-report', 'module_icon': 'BarChartOutlined', 'order': 1, 'parent_codename': 'performance_report_section'}, # Added Icon

    # --- Recruitment (module_order=8) ---
    {'module': 'Recruitment', 'module_order': 8, 'name': 'Job Post',
     'codename': 'job_post', 'url_name': '/job-post', 'module_icon': 'UserAddOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Recruitment', 'module_order': 8, 'name': 'Job Candidate',
     'codename': 'job_candidate', 'url_name': '/job-candidate', 'module_icon': 'UserOutlined', 'order': 2, 'parent_codename': None}, # Added Icon

    # --- Training (module_order=9) ---
    {'module': 'Training', 'module_order': 9, 'name': 'Training Type',
     'codename': 'training_type', 'url_name': '/training-type', 'module_icon': 'ReadOutlined', 'order': 1, 'parent_codename': None},
    {'module': 'Training', 'module_order': 9, 'name': 'Training List',
     'codename': 'training_list', 'url_name': '/training-list', 'module_icon': 'CalendarOutlined', 'order': 2, 'parent_codename': None}, # Added Icon
    {'module': 'Training', 'module_order': 9, 'name': 'Training Report',
     'codename': 'training_report', 'url_name': '/training-report', 'module_icon': 'BarChartOutlined', 'order': 3, 'parent_codename': None}, # Added Icon

    # --- Award (module_order=10) ---
    {'module': 'Award', 'module_order': 10, 'name': 'Award Management',
     'codename': 'manage_award', 'url_name': '/award', 'module_icon': 'TrophyOutlined', 'order': 1, 'parent_codename': None},

    # --- Notice Board (module_order=11) ---
    {'module': 'Notice Board', 'module_order': 11, 'name': 'Notice Management',
     'codename': 'manage_notice', 'url_name': '/notice', 'module_icon': 'NotificationOutlined', 'order': 1, 'parent_codename': None},

    # --- Settings (module_order=12) ---
    {'module': 'Settings', 'module_order': 12, 'name': 'General Settings',
     'codename': 'general_settings', 'url_name': '/settings', 'module_icon': 'SettingOutlined', 'order': 1, 'parent_codename': None},
]
