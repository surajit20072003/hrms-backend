
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission # Import Permission
from .managers import UserManager

# Assuming these imports are available in your structure:
# from company.models import Department, Designation, Branch, WorkShift, MonthlyPayGrade, HourlyPayGrade
from company.models import Department,Designation,Branch,WorkShift 
# Assuming Enums are correctly defined elsewhere:
# from .enums import JobStatus, Status 
# (Retaining existing imports for context)
from .enums import JobStatus, Status
from company.models import WorkShift


# --- NEW: Page Model for Granular Access Control ---
class Page(models.Model):
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=50)
    module_icon = models.CharField(max_length=50, default='list_alt')
    codename = models.CharField(max_length=100, unique=True)
    url_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    native_permission = models.OneToOneField(Permission, on_delete=models.SET_NULL, null=True, blank=True)

    # NEW
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    module_order = models.PositiveIntegerField(default=999)
    order = models.PositiveIntegerField(default=999)

    class Meta:
        verbose_name = "Page Access"
        verbose_name_plural = "Page Accesses"
        ordering = ['module_order', 'module', 'order', 'name']


# --- Role Model (UPDATED) ---
class Role(models.Model):
    """
    Holds dynamic roles that can be created by the Admin from the frontend.
    It links to a Django Group for robust permission management.
    """
    name = models.CharField(max_length=50, verbose_name="Role Name")
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='roles_created',
        null=True,
        blank=True,
        help_text="Company owner who owns this role (not necessarily who created it)"
    )
    created_by = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='roles_defined'
    )

    # Linking to Django's native permission Group for granular access control
    group = models.OneToOneField(
        Group, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='custom_role'
    ) 
    
    # NEW: Many-to-Many link to the new Page model for menu access control
    pages = models.ManyToManyField(
        Page, 
        blank=True, 
        related_name='roles',
        verbose_name="Assigned Pages/Features"
    )

    class Meta:
        verbose_name = "Dynamic Role"
        verbose_name_plural = "Dynamic Roles"
        unique_together = ('parent', 'name')
        ordering = ['name']

    def save(self, *args, **kwargs):
        """
        ✅ MULTI-TENANCY: Create unique Group per company
        Group name format: Role_{parent_id}_{role_name}
        """
        if not self.group:
            # Include parent ID to make group name unique per company
            parent_id = self.parent.id if self.parent else 'global'
            group_name = f"Role_{parent_id}_{self.name}"
            group, created = Group.objects.get_or_create(name=group_name)
            self.group = group
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# --- User Model (No changes needed, but included for completeness) ---
class User(AbstractUser):

    username = None  # remove username field
    email = models.EmailField(unique=True)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Company owner for this user. NULL for company owners and superusers."
    )

    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
        related_name='users'
    )

    # ✅ Django's built-in permission fields (Kept)
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Logic to automatically add user to the corresponding Django Group (for permissions)
        if self.role and self.role.group:
            # Clear existing groups to ensure only the primary role group is active
            self.groups.clear() 
            self.groups.add(self.role.group)
        
        # Super Admin logic (Tier 1)
        if self.is_superuser:
            self.is_staff = True # Superuser should always have staff access
    @property
    def company_owner(self):
        """
        Get the company owner for this user.
        
        Returns:
            - self if user is company owner (parent=None and not superuser)
            - parent if user is employee (parent is set)
            - None if user is superuser
        
        Why needed:
            When Admin creates employee/role, we need to know which company owner
            to assign. This property finds the owner regardless of who is logged in.
        
        Example:
            # Company owner
            owner.company_owner  # Returns owner itself
            
            # Admin employee
            admin.company_owner  # Returns owner (admin.parent)
            
            # Manager employee
            manager.company_owner  # Returns owner (manager.parent)
        """
        if self.parent is None and not self.is_superuser:
            return self  # User IS the company owner
        elif self.parent:
            return self.parent  # User is employee, return their owner
        return None  # Superuser has no company


    @property
    def accessible_pages(self):
        """
        Returns all pages accessible to this user.
        Superusers get all pages, regular users get pages from their role.
        """
        if self.is_superuser:
            return Page.objects.all()
        elif self.role:
            return self.role.pages.all()
        return Page.objects.none()
    
    @property
    def is_super_admin(self):
        # Tier 1: Highest access
        return self.is_superuser

    @property
    def is_primary_admin(self):
        return self.is_staff and self.role and self.role.name == "Admin"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profiles',
        null=True,
        blank=True,
        help_text="Company owner (same as user.parent)"
    )
    
    # --- Shared Personal Information Fields ---
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    face_encoding = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="128-D Face Encoding"
    )

    # --- Employee-Specific Fields (Using string references for company models) ---
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Fingerprint/Emp No.")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)
    
    # Corrected string references for PayGrades
    monthly_pay_grade = models.ForeignKey(
        'company.MonthlyPayGrade',  
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees'
    )
    hourly_pay_grade = models.ForeignKey( 
        'company.HourlyPayGrade', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='hourly_employees'
    )
    emergency_contact = models.CharField(max_length=20, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, null=True, blank=True)
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


# --- Education Model (No changes needed) ---
class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    institute = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    board = models.CharField(max_length=255, verbose_name="Board / University")
    result = models.CharField(max_length=50, null=True, blank=True)
    gpa = models.FloatField(verbose_name="GPA / CGPA", null=True, blank=True)
    passing_year = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='education_created'
    )

    def __str__(self):
        return f"{self.degree} from {self.institute}"

# --- Experience Model (No changes needed) ---
class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience')
    organization = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)
    skill = models.TextField(null=True, blank=True)
    responsibility = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='experience_created'
    )

    def __str__(self):
        return f"{self.designation} at {self.organization}"



# --- Account Details Model ---
class AccountDetails(models.Model):
    """Bank account details for employee salary payments"""
    
    ACCOUNT_TYPE_CHOICES = [
        ('Savings', 'Savings Account'),
        ('Current', 'Current Account'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='account_details')
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=11, help_text="Bank IFSC Code")
    branch_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='Savings')
    is_primary = models.BooleanField(default=False, help_text="Primary account for salary payment")
    created_by = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='account_details_created'
    )

    class Meta:
        verbose_name = "Account Detail"
        verbose_name_plural = "Account Details"
        ordering = ['-is_primary']

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank_name} ({self.account_number[-4:]})"