

from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from company.models import Department,Designation,Branch
from .enums import JobStatus, Status
from company.models import WorkShift
# --- User Model ---
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EMPLOYEE = "EMPLOYEE", "Employee"

    username = None  # remove username field
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    # ✅ Django's built-in permission fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # ✅ Configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE
    


# --- Profile Model (Personal Information) ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # --- Shared Personal Information Fields ---
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)

    # --- Employee-Specific Fields ---
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Fingerprint/Emp No.")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)
    monthly_pay_grade = models.ForeignKey(
        'company.MonthlyPayGrade',  
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees'
    )
    hourly_pay_grade = models.ForeignKey( 
        'company.HourlyPayGrade', # Use the imported model name
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='hourly_employees'
    )
    emergency_contact = models.CharField(max_length=20, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, null=True, blank=True)
    # ADDED new job_status field using Enum
    job_status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PERMANENT, null=True, blank=True)
    
    work_shift = models.ForeignKey(
        WorkShift, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees'
    )
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


# --- Education Model ---
class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    institute = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    board = models.CharField(max_length=255, verbose_name="Board / University")
    result = models.CharField(max_length=50, null=True, blank=True)
    gpa = models.FloatField(verbose_name="GPA / CGPA", null=True, blank=True)
    passing_year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.degree} from {self.institute}"

# --- Experience Model ---
class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience')
    organization = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)
    skill = models.TextField(null=True, blank=True)
    responsibility = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.designation} at {self.organization}"