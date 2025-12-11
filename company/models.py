from django.db import models
from django.conf import settings
from users.enums import DayOfWeek,LeaveStatus,Status,NoticeStatus
from decimal import Decimal
from users.enums import JOB_STATUS_CHOICES,AwardName,SlabChoices,GenderChoices

class Department(models.Model):
    name = models.CharField(max_length=100)  # Removed unique=True for multi-tenancy
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='departments_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this department"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_created'
    )
    class Meta:
        unique_together = ('parent', 'name')  # Unique per company
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Designation(models.Model):
    name = models.CharField(max_length=100)
    # Har designation ko ek department se joda gaya hai
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='designations_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this designation"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='designations_created'
    )

    class Meta:
        unique_together = ('parent', 'name', 'department')  # Unique per company per department
        verbose_name = "Designation"
        verbose_name_plural = "Designations"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Branch(models.Model):
    name = models.CharField(max_length=100)  # Removed unique=True
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='branches_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this branch"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='branches_created'
    )

    class Meta:
        unique_together = ('parent', 'name')  # Unique per company
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        ordering = ['name']

    def __str__(self):
        return self.name
    

class Warning(models.Model):
    # The employee who receives the warning
    warning_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='warnings_received'
    )
    
    # The admin who gives the warning
    warning_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='warnings_given',
        null=True
    )
    
    warning_type = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    warning_date = models.DateField()
    description = models.TextField()
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warnings_created'
    )

    def __str__(self):
        return f"Warning for {self.warning_to.email} - {self.subject}"
    

class Termination(models.Model):
    terminate_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='terminations'
    )
    terminate_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='terminations_given',
        null=True
    )
    termination_type = models.CharField(max_length=100)
    termination_date = models.DateField()
    notice_date = models.DateField()
    description = models.TextField()
    subject = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='terminations_created'
    )

    def __str__(self):
        return f"Termination for {self.terminate_to.email}"

class Promotion(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='promotions')
    promotion_date = models.DateField()
    
    # Current details (can be captured at the time of promotion)
    current_department_name = models.CharField(max_length=100)
    current_designation_name = models.CharField(max_length=100)
    current_salary = models.CharField(max_length=50)
    current_pay_grade = models.CharField(max_length=100, null=True, blank=True) 

    # Promoted details5
    promoted_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='promoted_employees')
    promoted_designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, related_name='promoted_employees')
    promoted_pay_grade = models.CharField(max_length=100, null=True, blank=True)
    promoted_salary = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotions_created'
    )    
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Promotion for {self.employee.email} on {self.promotion_date}"

class Holiday(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Christmas, Diwali")  # Removed unique=True
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='holidays_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this holiday"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='holidays_created'
    )
    
    class Meta:
        unique_together = ('parent', 'name')  # Unique per company
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        ordering = ['name']
    
    def __str__(self): 
        return self.name

# Model for "Public Holiday" (Naam ko date assign karega)
class PublicHoliday(models.Model):
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    comment = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='public_holidays_created'
    )
    def __str__(self): return f"{self.holiday.name} ({self.start_date})"

# Baaki models waise hi rahenge
class WeeklyHoliday(models.Model):
    day = models.CharField(max_length=10, choices=DayOfWeek.choices)  # Removed unique=True
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='weekly_holidays_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this weekly holiday"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_holidays_created'
    )
    
    class Meta:
        unique_together = ('parent', 'day')  # Unique per company
        verbose_name = "Weekly Holiday"
        verbose_name_plural = "Weekly Holidays"
        ordering = ['day']
    
    def __str__(self): 
        return self.day

class LeaveType(models.Model):
    name = models.CharField(max_length=100)  # Removed unique=True
    number_of_days = models.PositiveIntegerField()
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='leave_types_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this leave type"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_types_created'
    )
    
    class Meta:
        unique_together = ('parent', 'name')  # Unique per company
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"
        ordering = ['name']
    
    def __str__(self): 
        return self.name

class EarnLeaveRule(models.Model):
    for_month = models.PositiveIntegerField(default=1, editable=False)  # ✅ Fixed at 1 month
    day_of_earn_leave = models.FloatField(default=0)  # ✅ Default 0, editable
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='earn_leave_rules_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this earn leave rule"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='earn_leave_rules_created'
    )
    
    class Meta:
        verbose_name = "Earn Leave Rule"
        verbose_name_plural = "Earn Leave Rules"
        unique_together = ('parent',)  # ✅ Only one rule per company
    
    def __str__(self):
        return f"{self.day_of_earn_leave} days per {self.for_month} month(s)"
    
class LeaveApplication(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='leave_applications'
    )
    leave_type = models.ForeignKey(
        'LeaveType', 
        on_delete=models.SET_NULL, 
        null=True
    )
    from_date = models.DateField()
    to_date = models.DateField()
    number_of_days = models.FloatField()
    purpose = models.TextField()
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=LeaveStatus.choices, 
        default=LeaveStatus.PENDING
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='leaves_approved'
    )
    approved_date = models.DateField(null=True, blank=True)

    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='leaves_rejected'
    )
    reject_date = models.DateField(null=True, blank=True)

    rejection_reason = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_applications_created'
    )

    def __str__(self):
        return f"{self.employee.email} - {self.leave_type} ({self.status})"
    
class LeaveBalance(models.Model):
    """
    Stores the current entitlement and available balance for each employee and leave type.
    """
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        'LeaveType', 
        on_delete=models.CASCADE
    )
    # Total days allocated (initial entitlement)
    entitlement = models.FloatField(
        default=0.0, 
        help_text="Total days allocated for this leave type in the current cycle."
    )
    # Current available balance (will be deducted upon approval)
    available_balance = models.FloatField(
        default=0.0, 
        help_text="Current balance available to the employee."
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_balances_created'
    )   
    class Meta:
        # Ensures an employee has only one balance record per leave type
        unique_together = ('employee', 'leave_type')

    def __str__(self):
        return f"{self.employee.email} - {self.leave_type.name}: {self.available_balance}/{self.entitlement}"
    





class WorkShift(models.Model):
    """Stores different work shifts defined by the company."""
    shift_name = models.CharField(max_length=100, verbose_name="Work Shift Name")  # Removed unique=True
    start_time = models.TimeField(verbose_name="Start Time") # e.g., 09:00:00
    end_time = models.TimeField(verbose_name="End Time")     # e.g., 18:00:00
    
    # Time after which arrival is considered late
    late_count_time = models.TimeField(verbose_name="Late Count Time", null=True, blank=True) 
    ot_start_delay_minutes = models.PositiveIntegerField(
        default=60, # Default: 30 minutes grace period
        verbose_name="OT Start Delay (Minutes)"
    )
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='work_shifts_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this work shift"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_shifts_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shift_name

    class Meta:
        unique_together = ('parent', 'shift_name')  # Unique per company
        verbose_name = "Work Shift"
        verbose_name_plural = "Work Shifts"
        ordering = ['start_time']



class Attendance(models.Model):
    """Records attendance records."""
    employee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField()
    punch_in_time = models.DateTimeField(null=True, blank=True)
    punch_out_time = models.DateTimeField(null=True, blank=True)
    punch_in_photo = models.ImageField(
        upload_to='attendance/in_photos/%Y/%m/%d/',
        null=True, 
        blank=True,
        help_text="Live photo captured at Punch-In time."
    )
    punch_out_photo = models.ImageField(
        upload_to='attendance/out_photos/%Y/%m/%d/',
        null=True, 
        blank=True,
        help_text="Live photo captured at Punch-Out time."
    )
    is_late = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)
    total_work_duration = models.DurationField(null=True, blank=True)
    overtime_duration = models.DurationField(null=True, blank=True)
    late_duration = models.DurationField(null=True, blank=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances_created'
    )


    class Meta:
        unique_together = ('employee', 'attendance_date')
        ordering = ['-attendance_date']




class Allowance(models.Model):
    """Stores different types of allowances (e.g., House Rent, Medical)."""

    class AllowanceType(models.TextChoices):
        PERCENTAGE = 'Percentage', 'Percentage of Basic'
        FIXED = 'Fixed', 'Fixed Amount'

    allowance_name = models.CharField(max_length=100, verbose_name="Allowance Name")  # Removed unique=True
    allowance_type = models.CharField(
        max_length=10,
        choices=AllowanceType.choices,
        default=AllowanceType.PERCENTAGE,
        verbose_name="Allowance Type"
    )
    
    
    percentage_of_basic = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, 
        verbose_name="Percentage of Basic/Fixed Value"
    ) 

    # Maximum limit that can be given for this allowance per month (e.g., 2500)
    limit_per_month = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, 
        verbose_name="Limit Per Month"
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='allowances_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this allowance"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allowances_created'
    )

    def __str__(self):
        return self.allowance_name

    class Meta:
        unique_together = ('parent', 'allowance_name')  # Unique per company
        verbose_name = "Allowance"
        verbose_name_plural = "Allowances"
        ordering = ['allowance_name']


class Deduction(models.Model):
    """Stores different types of deductions (e.g., Provident Fund, Income Tax)."""

    class DeductionType(models.TextChoices):
        PERCENTAGE = 'Percentage', 'Percentage of Basic'
        FIXED = 'Fixed', 'Fixed Amount'

    deduction_name = models.CharField(max_length=100, verbose_name="Deduction Name")  # Removed unique=True
    deduction_type = models.CharField(
        max_length=10,
        choices=DeductionType.choices,
        default=DeductionType.PERCENTAGE,
        verbose_name="Deduction Type"
    )
    
    
    percentage_of_basic = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, 
        verbose_name="Percentage/Fixed Value"
    ) 

    # Maximum limit that can be deducted per month
    limit_per_month = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, 
        default=Decimal('0.00'), # Default is 0 as shown in the screenshot
        verbose_name="Limit Per Month"
    )
    
    is_tax_exempt = models.BooleanField(default=False, verbose_name="Is Tax Exempt")
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='deductions_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this deduction"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deductions_created'
    )

    def __str__(self):
        return self.deduction_name

    class Meta:
        unique_together = ('parent', 'deduction_name')  # Unique per company
        verbose_name = "Deduction"
        verbose_name_plural = "Deductions"
        ordering = ['deduction_name']





class MonthlyPayGrade(models.Model):
    grade_name = models.CharField(max_length=100, verbose_name="Grade Name")  # Removed unique=True for multi-tenancy
    
    # Input Field (Admin sets this value)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Calculated Fields (Stored for easy querying/reporting)
    gross_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Calculated Gross Salary"
    )
    net_salary = models.DecimalField( 
        max_digits=10, decimal_places=2, default=0.00, 
        verbose_name="Calculated Net Salary"
    )
    
    # Redundant field removed: percentage_of_basic_g (Ab iski zaroorat nahi)
    
    overtime_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    # Reuse: Linking Allowance and Deduction via 'through' models
    allowances = models.ManyToManyField(
        'Allowance', 
        through='PayGradeAllowance', 
        related_name='pay_grades'
    )
    deductions = models.ManyToManyField(
        'Deduction', 
        through='PayGradeDeduction', 
        related_name='pay_grades'
    )
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='monthly_pay_grades_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this monthly pay grade"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monthly_pay_grades_created'
    )
    
    class Meta:
        unique_together = ('parent', 'grade_name')  # Unique per company
        verbose_name = "Monthly Pay Grade"
        verbose_name_plural = "Monthly Pay Grades"
        ordering = ['grade_name']
    
    def __str__(self):
        return self.grade_name


class PayGradeAllowance(models.Model):
    """Stores the specific VALUE of an Allowance for a Pay Grade."""
    pay_grade = models.ForeignKey(MonthlyPayGrade, on_delete=models.CASCADE)
    allowance = models.ForeignKey('Allowance', on_delete=models.CASCADE) # Reuse: Allowance Model ka use
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Grade Specific Value")
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pay_grade_allowances_created'
    )
    class Meta:
        unique_together = ('pay_grade', 'allowance')

class PayGradeDeduction(models.Model):
    """Stores the specific VALUE of a Deduction for a Pay Grade."""
    pay_grade = models.ForeignKey(MonthlyPayGrade, on_delete=models.CASCADE)
    deduction = models.ForeignKey('Deduction', on_delete=models.CASCADE) # Reuse: Deduction Model ka use
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Grade Specific Value")
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pay_grade_deductions_created'
    )    
    class Meta:
        unique_together = ('pay_grade', 'deduction')


class HourlyPayGrade(models.Model):
    """Defines a pay grade structure based on an hourly rate."""
    
    pay_grade_name = models.CharField(max_length=100, verbose_name="Pay Grade Name")  # Removed unique=True for multi-tenancy
    
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        verbose_name="Hourly Rate"
    )
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='hourly_pay_grades_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this hourly pay grade"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hourly_pay_grades_created'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pay_grade_name} ({self.hourly_rate}/hr)"

    class Meta:
        unique_together = ('parent', 'pay_grade_name')  # Unique per company
        verbose_name = "Hourly Pay Grade"
        verbose_name_plural = "Hourly Pay Grades"
        ordering = ['pay_grade_name']


class PerformanceCategory(models.Model):
    category_name = models.CharField(max_length=150)  # Removed unique=True for multi-tenancy
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='performance_categories_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this performance category"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_categories_created'
    )
    
    class Meta:
        unique_together = ('parent', 'category_name')  # Unique per company
        verbose_name = "Performance Category"
        verbose_name_plural = "Performance Categories"
        ordering = ['category_name']
    
    def __str__(self):
        return self.category_name
    

class PerformanceCriteria(models.Model):
    category = models.ForeignKey(
        'company.PerformanceCategory',
        on_delete=models.CASCADE,
        related_name='criteria'
    )
    criteria_name = models.CharField(max_length=255)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_criteria_created'
    )
    
    class Meta:
        unique_together = ('category', 'criteria_name')  # Unique criteria name per category
        verbose_name = "Performance Criteria"
        verbose_name_plural = "Performance Criteria"
        ordering = ['category', 'criteria_name']
    
    def __str__(self):
        return f"{self.category.category_name}: {self.criteria_name}"
    

class EmployeePerformance(models.Model):
    # Foreign Key to Employee (User model for consistency)
    employee = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    # Kis mahine ki performance hai (Format: YYYY-MM-DD, day 1 ho sakta hai)
    review_month = models.DateField() 
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_performances_created'
    )
    # Optional: Calculated Overall Rating (Average of all criteria)
    overall_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    # Kis Admin/User ne review kiya
    reviewed_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ek employee ka ek mahine mein sirf ek review ho sakta hai
        unique_together = ('employee', 'review_month') 

    def __str__(self):
        return f"{self.employee.profile.full_name}'s Review for {self.review_month.strftime('%Y-%m')}"



class PerformanceRating(models.Model):
    # Foreign Key to the main review header
    performance_review = models.ForeignKey(
        'company.EmployeePerformance',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    # Kis Criteria ko rate kiya ja raha hai (PerformanceCriteria model se)
    criteria = models.ForeignKey(
        'company.PerformanceCriteria',
        on_delete=models.CASCADE
    )
    # Actual Rating for that specific criteria 
    rating_value = models.DecimalField(max_digits=4, decimal_places=2) 
    
    class Meta:
        # Ek review mein ek criteria ko sirf ek baar rate kiya ja sakta hai
        unique_together = ('performance_review', 'criteria')
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_ratings_created'
    )
    
    def __str__(self):
        return f"{self.criteria.criteria_name}: {self.rating_value}"
    


class JobPost(models.Model):
    """
    Model representing a single job vacancy posted by the HR team.
    """
    job_title = models.CharField(max_length=255)
    job_post = models.CharField(max_length=255, help_text="Short title or designation, e.g., 'Sr. Software Engineer'")
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=JOB_STATUS_CHOICES,
        default='DRAFT'
    )
    
    job_publish_date = models.DateField(null=True, blank=True)
    application_end_date = models.DateField() # Mandatory field
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_posts_created'
    )    

    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='job_posts'
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='job_posts_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this job post"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Post"
        verbose_name_plural = "Job Posts"
        ordering = ['-created_at'] # Latest job post pehle dikhega

    def __str__(self):
        return f"{self.job_title} ({self.get_status_display()})"
    

class TrainingType(models.Model):
    """
    Model representing different categories of training programs (e.g., Technical, Soft Skills).
    """
    training_type_name = models.CharField(max_length=255, unique=True)
    

    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.ACTIVE 
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_types_created'
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='training_types_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this training type"
    )

    class Meta:
        verbose_name = "Training Type"
        verbose_name_plural = "Training Types"
        unique_together = ('parent', 'training_type_name')
        ordering = ['training_type_name']

    def __str__(self):
        return self.training_type_name
    

class EmployeeTraining(models.Model):
    """
    Model to record specific training instances completed by an employee.
    """
    # Foreign Keys (Dropdowns from etl02.png)
    employee = models.ForeignKey(
        'users.User',  # Changed to User for consistency
        on_delete=models.CASCADE,
        related_name='trainings_attended'
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_trainings_created'
    )
    training_type = models.ForeignKey(
        'TrainingType', 
        on_delete=models.SET_NULL,
        null=True,
        related_name='training_instances'
    )
    
    # Text Fields (etl02.png)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Date Fields (etl02.png)
    from_date = models.DateField()
    to_date = models.DateField()
    
    # File Upload Field for Certificate (etl02.png)
    certificate_file = models.FileField(
        upload_to='training_certificates/',
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Training"
        verbose_name_plural = "Employee Trainings"
        unique_together = ('employee', 'subject', 'from_date') 
        ordering = ['-from_date']

    def __str__(self):
        return f"{self.employee.profile.full_name} - {self.subject}"
    

class Award(models.Model):
    """
    Model to record awards given to employees (award.png, award02.png).
    """
    # Foreign Key
    employee = models.ForeignKey(
        'users.User',  # Changed to User for consistency
        on_delete=models.CASCADE,
        related_name='awards_received'
    )
    
    # Award Name field uses Enum (TextChoices)
    award_name = models.CharField(
        max_length=50, 
        choices=AwardName.choices, # Enum se choices aayenge
        verbose_name="Award Name"
    )
    gift_item = models.CharField(max_length=255, verbose_name="Gift Item")
    award_month = models.DateField(verbose_name="Month") 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='awards_created'
    )

    class Meta:
        verbose_name = "Employee Award"
        verbose_name_plural = "Employee Awards"
        unique_together = ('employee', 'award_name', 'award_month') 
        ordering = ['-award_month']

    def __str__(self):
        # Enum value ko human-readable label mein convert karega
        return f"{self.employee.profile.full_name} - {self.get_award_name_display()} ({self.award_month.strftime('%B %Y')})"
    
class Notice(models.Model):
    """
    Model to store official notices and announcements (not01.png, not02.png).
    """
    title = models.CharField(max_length=255)
    description = models.TextField() # Rich text editor content
    
    # Status field (Published, Draft, etc.)
    status = models.CharField(
        max_length=20, 
        choices=NoticeStatus.choices, 
        default=NoticeStatus.PUBLISHED
    )
    
    publish_date = models.DateField(verbose_name="Publish Date")
    
    # Optional file attachment field
    attach_file = models.FileField(
        upload_to='notices/attachments/', 
        max_length=255, 
        null=True, 
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notices_created'
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notices_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this notice"
    )

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title
    




class LateDeductionRule(models.Model):
    """ 
    Defines the rule for salary deduction based on late attendance days.
    """
    
    late_days_threshold = models.PositiveIntegerField(
        unique=True, 
        verbose_name="Late Days Threshold",
        help_text="Number of late days (within a month) required to trigger deduction."
    )
    
    deduction_days = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Salary Deduction Days",
        help_text="Number of salary days to deduct (e.g., 1.0 for one full day)."
    )
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Status"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='late_deduction_rules_created'
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='late_deduction_rules_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this rule"
    )

    class Meta:
        ordering = ['late_days_threshold']
        verbose_name = "Late Deduction Rule"
        verbose_name_plural = "Late Deduction Rules"
        unique_together = ('parent', 'late_days_threshold')

    def __str__(self):
        return f"{self.late_days_threshold} Late Days -> {self.deduction_days} Day Cut ({self.status})"
    


class TaxRule(models.Model):

    # Tax Slab Identification
    gender = models.CharField(
        max_length=10, 
        choices=GenderChoices.choices, 
        verbose_name="Gender Rule"
    )
    
    slab_type = models.CharField(
        max_length=20, 
        choices=SlabChoices.choices, 
        default=SlabChoices.NEXT,
        verbose_name="Slab Type"
    )

    total_income_limit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Total Income Limit",
        help_text="The upper limit of the income slab (e.g., 250000.00)"
    )
    tax_rate_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Tax Rate %"
    )
    taxable_amount_fixed = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Fixed Taxable Amount for Slab"
    )
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tax_rules_created'
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='tax_rules_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this tax rule"
    )

    class Meta:
        unique_together = ('parent', 'gender', 'total_income_limit') 
        ordering = ['gender', 'total_income_limit']
        verbose_name = "Tax Rule"
        verbose_name_plural = "Tax Rules"

    def __str__(self):
        return f"Tax Rule ({self.gender}): Upto {self.total_income_limit} @ {self.tax_rate_percentage}%"
    


class PaySlip(models.Model):
    """
    Ek mahine ke liye employee ki final calculated salary ka summary record.
    """
    
    STATUS_CHOICES = (
        ('Pending', 'Pending Calculation'),
        ('Calculated', 'Ready for Payment'),
        ('Paid', 'Payment Made'),
    )

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payslips')
    payment_month = models.DateField(db_index=True) # E.g., 2025-11-01
    
    #--- Financial Summary (Adjusted Values) ---
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Payable Basic Salary (after absence cut)")
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Adjusted Gross Salary (after absence cut)")
    total_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Sum of all deductions + cuts
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total Overtime Pay added to Gross") # <-- NEW FIELD
    total_tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total Income Tax / TDS deducted") # <-- NEW FIELD
    #--- Attendance/Working Summary ---
    total_days_in_month = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    working_days = models.DecimalField(max_digits=4, decimal_places=1, default=0, help_text="Total Paid Days (Worked + Paid Leave)")
    unjustified_absence = models.DecimalField(max_digits=4, decimal_places=1, default=0, help_text="Unpaid leave/Absent days")
    late_attendance_count = models.PositiveIntegerField(default=0, help_text="Total number of late punch-ins")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_payslips')
    
    payment_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="Date when payment was made"
    )
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ('Manual', 'Manual Payment'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash')
        ],
        help_text="Payment method used"
    )
    payment_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Transaction ID or reference number"
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salary_payments_made',
        help_text="User who marked this as paid"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payslips_created'
    )
    class Meta:
        unique_together = ('employee', 'payment_month')
        ordering = ['-payment_month']

class PaySlipDetail(models.Model):
    """
    Har allowance aur deduction (including Late Cut, PF, Tax, Absence Cut) ka item-wise breakdown store karta hai.
    """
    
    TYPE_CHOICES = (
        ('Allowance', 'Allowance'),
        ('Deduction', 'Deduction'),
    )
    
    payslip = models.ForeignKey(PaySlip, on_delete=models.CASCADE, related_name='details')
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    item_name = models.CharField(max_length=100) # e.g., HRA, PF, Late Attendance Cut, Unjustified Absence Cut
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payslip_details_created'
    )
    class Meta:
        ordering = ['item_type', 'item_name']




class BonusSetting(models.Model):
    """
    Defines bonus rules for festivals (e.g., Eid bonus 50% of Basic)
    """
    festival_name = models.CharField(max_length=100, verbose_name="Festival Name")  # Removed unique=True for multi-tenancy
    percentage_of_basic = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Bonus Percentage",
        help_text="e.g., 50.00 for 50%"
    )
    
    # ✅ Admin selects: Calculate on Basic or Gross?
    calculate_on = models.CharField(
        max_length=10,
        choices=[('BASIC', 'Basic Salary'), ('GROSS', 'Gross Salary')],
        default='BASIC',
        verbose_name="Calculate Bonus On"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonus_settings_created'
    )
    
    parent = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='bonus_settings_owned',
        null=True,
        blank=True,
        help_text="Company owner who owns this bonus setting"
    )

    class Meta:
        verbose_name = "Bonus Setting"
        verbose_name_plural = "Bonus Settings"
        ordering = ['festival_name']
        unique_together = ('parent', 'festival_name')
    
    def __str__(self):
        return f"{self.festival_name} ({self.percentage_of_basic}% of {self.calculate_on})"


class EmployeeBonus(models.Model):
    """
    Records bonus given to employees
    """
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bonuses'
    )
    bonus_setting = models.ForeignKey(
        BonusSetting, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='employee_bonuses'
    )
    
    # Stored for history (snapshot at generation time)
    festival_name = models.CharField(max_length=100)
    bonus_month = models.DateField(help_text="Month for which bonus is given")
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True,help_text="Employee's basic at generation time")
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True,help_text="Employee's gross at generation time")
    
    # Bonus calculation details
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    calculated_on = models.CharField(max_length=10, choices=[('BASIC', 'Basic'), ('GROSS', 'Gross')])
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonuses_generated'
    )
    status = models.CharField(
        max_length=20,
        choices=[('Calculated', 'Calculated'), ('Paid', 'Paid')],
        default='Calculated',
        help_text="Payment status"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when payment was made"
    )
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ('Manual', 'Manual Payment'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash')
        ],
        help_text="Payment method used"
    )
    payment_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Transaction ID or reference number"
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonus_payments_made',
        help_text="User who marked this bonus as paid"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_bonuses_created'
    )
    class Meta:
        unique_together = ('employee', 'festival_name', 'bonus_month')
        ordering = ['-bonus_month', '-created_at']
    
    def __str__(self):
        return f"{self.employee.email} - {self.festival_name} - ₹{self.bonus_amount}"