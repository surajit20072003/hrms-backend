from django.db import models
from django.conf import settings
from users.enums import DayOfWeek,LeaveStatus
from decimal import Decimal

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Designation(models.Model):
    name = models.CharField(max_length=100)
    # Har designation ko ek department se joda gaya hai
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')

    def __str__(self):
        return self.name
    
class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)

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

    # Promoted details
    promoted_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='promoted_employees')
    promoted_designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, related_name='promoted_employees')
    promoted_pay_grade = models.CharField(max_length=100, null=True, blank=True)
    promoted_salary = models.CharField(max_length=50)
    
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Promotion for {self.employee.email} on {self.promotion_date}"

class Holiday(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Christmas, Diwali")
    def __str__(self): return self.name

# Model for "Public Holiday" (Naam ko date assign karega)
class PublicHoliday(models.Model):
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    comment = models.TextField(null=True, blank=True)
    def __str__(self): return f"{self.holiday.name} ({self.start_date})"

# Baaki models waise hi rahenge
class WeeklyHoliday(models.Model):
    day = models.CharField(max_length=10, choices=DayOfWeek.choices, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.day

class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    number_of_days = models.PositiveIntegerField()
    def __str__(self): return self.name

class EarnLeaveRule(models.Model):
    for_month = models.PositiveIntegerField(default=1)
    day_of_earn_leave = models.FloatField(default=1.0)
    
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

    class Meta:
        # Ensures an employee has only one balance record per leave type
        unique_together = ('employee', 'leave_type')

    def __str__(self):
        return f"{self.employee.email} - {self.leave_type.name}: {self.available_balance}/{self.entitlement}"
    





class WorkShift(models.Model):
    """Stores different work shifts defined by the company."""
    shift_name = models.CharField(max_length=100, unique=True, verbose_name="Work Shift Name")
    start_time = models.TimeField(verbose_name="Start Time") # e.g., 09:00:00
    end_time = models.TimeField(verbose_name="End Time")     # e.g., 18:00:00
    
    # Time after which arrival is considered late
    late_count_time = models.TimeField(verbose_name="Late Count Time", null=True, blank=True) # e.g., 09:15:00

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shift_name

    class Meta:
        verbose_name = "Work Shift"
        verbose_name_plural = "Work Shifts"
        ordering = ['start_time']



class Attendance(models.Model):
    """Records attendance records."""
    employee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField()
    punch_in_time = models.DateTimeField(null=True, blank=True)
    punch_out_time = models.DateTimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)
    total_work_duration = models.DurationField(null=True, blank=True)
    overtime_duration = models.DurationField(null=True, blank=True)
    late_duration = models.DurationField(null=True, blank=True)


    class Meta:
        unique_together = ('employee', 'attendance_date')
        ordering = ['-attendance_date']




class Allowance(models.Model):
    """Stores different types of allowances (e.g., House Rent, Medical)."""

    class AllowanceType(models.TextChoices):
        PERCENTAGE = 'Percentage', 'Percentage of Basic'
        FIXED = 'Fixed', 'Fixed Amount'

    allowance_name = models.CharField(max_length=100, unique=True, verbose_name="Allowance Name")
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.allowance_name

    class Meta:
        verbose_name = "Allowance"
        verbose_name_plural = "Allowances"
        ordering = ['allowance_name']


class Deduction(models.Model):
    """Stores different types of deductions (e.g., Provident Fund, Income Tax)."""

    class DeductionType(models.TextChoices):
        PERCENTAGE = 'Percentage', 'Percentage of Basic'
        FIXED = 'Fixed', 'Fixed Amount'

    deduction_name = models.CharField(max_length=100, unique=True, verbose_name="Deduction Name")
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.deduction_name

    class Meta:
        verbose_name = "Deduction"
        verbose_name_plural = "Deductions"
        ordering = ['deduction_name']





class MonthlyPayGrade(models.Model):
    grade_name = models.CharField(max_length=100, unique=True, verbose_name="Grade Name")
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    percentage_of_basic_g = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
    
    def __str__(self):
        return self.grade_name


class PayGradeAllowance(models.Model):
    """Stores the specific VALUE of an Allowance for a Pay Grade."""
    pay_grade = models.ForeignKey(MonthlyPayGrade, on_delete=models.CASCADE)
    allowance = models.ForeignKey('Allowance', on_delete=models.CASCADE) # Reuse: Allowance Model ka use
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Grade Specific Value")
    
    class Meta:
        unique_together = ('pay_grade', 'allowance')

class PayGradeDeduction(models.Model):
    """Stores the specific VALUE of a Deduction for a Pay Grade."""
    pay_grade = models.ForeignKey(MonthlyPayGrade, on_delete=models.CASCADE)
    deduction = models.ForeignKey('Deduction', on_delete=models.CASCADE) # Reuse: Deduction Model ka use
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Grade Specific Value")
    
    class Meta:
        unique_together = ('pay_grade', 'deduction')


class HourlyPayGrade(models.Model):
    """Defines a pay grade structure based on an hourly rate."""
    
    pay_grade_name = models.CharField(max_length=100, unique=True, verbose_name="Pay Grade Name")
    
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        verbose_name="Hourly Rate"
    )
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pay_grade_name} ({self.hourly_rate}/hr)"

    class Meta:
        verbose_name = "Hourly Pay Grade"
        ordering = ['pay_grade_name']


class PerformanceCategory(models.Model):
    category_name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return f"{self.category.category_name}: {self.criteria_name}"
    

class EmployeePerformance(models.Model):
    # Foreign Key to Employee (Aapke users/models.py se)
    employee = models.ForeignKey(
        'users.Profile', 
        on_delete=models.CASCADE,
        related_name='performance_reviews'
    )
    # Kis mahine ki performance hai (Format: YYYY-MM-DD, day 1 ho sakta hai)
    review_month = models.DateField() 
    remarks = models.TextField(blank=True, null=True)
    
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
        return f"{self.employee.full_name}'s Review for {self.review_month.strftime('%Y-%m')}"



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
    
    def __str__(self):
        return f"{self.criteria.criteria_name}: {self.rating_value}"