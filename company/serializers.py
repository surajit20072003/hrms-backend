from rest_framework import serializers
from .models import Department,Designation,Branch,Warning ,Termination,Promotion,Holiday,WeeklyHoliday,LeaveType,EarnLeaveRule,PublicHoliday,LeaveApplication,LeaveBalance,WorkShift, \
Allowance,Deduction,MonthlyPayGrade,PayGradeAllowance,PayGradeDeduction,HourlyPayGrade,PerformanceCategory,PerformanceCriteria,PerformanceRating,EmployeePerformance,JobPost,TrainingType,\
EmployeeTraining,Award,Notice,LateDeductionRule,TaxRule
from users.models import User, Profile, Education, Experience
from users.enums import JobStatus,LeaveStatus,SlabChoices
from django.db.models import Sum
from decimal import Decimal
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__' 

class DesignationSerializer(serializers.ModelSerializer):
    # Response me department ka naam bhi dikhayenge
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Designation
        # 'id' aur 'name' read/write hain, 'department' sirf write ke liye hai
        fields = ['id', 'name', 'department', 'department_name']
        extra_kwargs = {
            'department': {'write_only': True}
        }

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institute', 'degree', 'board', 'result', 'gpa', 'passing_year']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'organization', 'designation', 'duration', 'skill', 'responsibility']


# This is the main serializer for an Admin to create a new Employee
class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new User and their related Profile object.
    It handles nested fields like email, password, and role for User creation.
    """
    # Fields for creating the User object
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, required=True)
    
    work_shift = serializers.PrimaryKeyRelatedField(
        queryset=WorkShift.objects.all(), 
        allow_null=True, 
        required=False
    )
    monthly_pay_grade = serializers.PrimaryKeyRelatedField(
        queryset=MonthlyPayGrade.objects.all(), 
        allow_null=True, 
        required=False
    )
    hourly_pay_grade = serializers.PrimaryKeyRelatedField(
        queryset=HourlyPayGrade.objects.all(), 
        allow_null=True, 
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'email', 'password', 'role', 'first_name', 'last_name', 'phone', 'address',
            'date_of_birth', 'gender', 'religion', 'marital_status', 'photo',
            'employee_id', 'department', 'designation', 'branch', 'supervisor',
            'date_of_joining', 'date_of_leaving', 'status', 'monthly_pay_grade',
            'hourly_pay_grade', 'emergency_contact', 'work_shift'
        ]

    def create(self, validated_data):
        # Step 0: Separate User data (pop writes only fields)
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        role = validated_data.pop('role')
        
        # Other user data
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')

        # Step 1: Create the User object
        user_obj = User.objects.create_user(
            email=email, 
            password=password, 
            role=role,
            first_name=first_name,
            last_name=last_name
        )

        # Step 2: Create the Profile object (validated_data now contains all Profile fields, 
        # including the WorkShift object due to PrimaryKeyRelatedField)
        profile = Profile.objects.create(user=user_obj, **validated_data)
        
        return profile


class EmployeeListSerializer(serializers.ModelSerializer):
    # Get related fields from other models
    name = serializers.SerializerMethodField()
    role = serializers.CharField(source='user.role', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    designation = serializers.CharField(source='designation.name', read_only=True, allow_null=True)
    pay_grade = serializers.SerializerMethodField()
    # We need the user's primary key (ID) for detail/edit/delete actions
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user_id',
            'photo',
            'name',
            'role',
            'department',
            'designation',
            'phone',
            'employee_id', # This is Fingerprint/Emp No.
            'pay_grade',
            'date_of_joining',
            'status',
            'job_status',
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_pay_grade(self, obj):
        if obj.monthly_pay_grade:
            return f"{obj.monthly_pay_grade} (Monthly)"
        if obj.hourly_pay_grade:
            return f"{obj.hourly_pay_grade} (Hourly)"
        return "N/A"

# Assuming necessary imports: WorkShift, MonthlyPayGrade, HourlyPayGrade

class EmployeeDetailSerializer(serializers.ModelSerializer):
    # --- User Data (Display/Update) ---
    email = serializers.EmailField(source='user.email')
    role = serializers.CharField(source='user.role', read_only=True)
    
    # --- Nested Read-Only Data (Assuming these exist) ---
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    
    # --- Pay Grade & Work Shift (Explicit Definition for Input/Output) ---
    
    # Work Shift Handling (Input: ID, Output: ID + Name)
    work_shift = serializers.PrimaryKeyRelatedField( 
        queryset=WorkShift.objects.all(), 
        allow_null=True, 
        required=False
    )
    work_shift_name = serializers.CharField(source='work_shift.name', read_only=True)

    # Monthly Pay Grade Handling (Input: ID, Output: ID + Name)
    monthly_pay_grade = serializers.PrimaryKeyRelatedField(
        queryset=MonthlyPayGrade.objects.all(), 
        allow_null=True, 
        required=False
    )
    monthly_pay_grade_name = serializers.CharField(source='monthly_pay_grade.grade_name', read_only=True)

    # Hourly Pay Grade Handling (Input: ID, Output: ID + Rate)
    hourly_pay_grade = serializers.PrimaryKeyRelatedField(
        queryset=HourlyPayGrade.objects.all(), 
        allow_null=True, 
        required=False
    )
    # Assuming 'hourly_rate' is a better display field than 'grade_name' for HourlyPayGrade
    hourly_pay_grade_rate = serializers.CharField(source='hourly_pay_grade.hourly_rate', read_only=True)


    class Meta:
        model = Profile
        # We still use '__all__' but the explicit fields defined above override the default behavior.
        # We must ensure to exclude 'user' as before.
        fields = '__all__' 
        exclude = ['user']
        

    def update(self, instance, validated_data):
        # 1. Handle User update 
        user_data = validated_data.pop('user', {})
        user = instance.user
        user.email = user_data.get('email', user.email)
        user.save()
        
        # 2. Handle Profile update (This includes saving the new FK objects: 
        # work_shift, monthly_pay_grade, hourly_pay_grade)
        updated_instance = super().update(instance, validated_data) 

        return updated_instance

class WarningSerializer(serializers.ModelSerializer):
    # For displaying names instead of IDs in GET requests
    employee_name = serializers.CharField(source='warning_to.profile.full_name', read_only=True)
    warning_by_name = serializers.CharField(source='warning_by.profile.full_name', read_only=True)

    class Meta:
        model = Warning
        fields = [
            'id', 
            'warning_to',         # Used for creating (takes user ID)
            'employee_name',      # Used for displaying
            'warning_by',         # Used for creating (takes user ID)
            'warning_by_name',    # Used for displaying
            'warning_type', 
            'subject', 
            'warning_date', 
            'description'
        ]
        # Make these fields write-only so they are only used for input
        extra_kwargs = {
            'warning_to': {'write_only': True},
            'warning_by': {'write_only': True},
        }
class TerminationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='terminate_to.profile.full_name', read_only=True, allow_null=True)
    terminated_by_name = serializers.CharField(source='terminate_by.profile.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Termination
        fields = [
            'id',
            'terminate_to',
            'employee_name',
            'terminate_by',
            'terminated_by_name',
            'termination_type',
            'termination_date',
            'notice_date',
            'subject',
            'description'
        ]
        extra_kwargs = {
            'terminate_to': {'write_only': True},
            'terminate_by': {'write_only': True},
        }
class PromotionSerializer(serializers.ModelSerializer):
    # For displaying names and other details in GET requests (read-only)
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True, allow_null=True)
    promoted_department_name = serializers.CharField(source='promoted_department.name', read_only=True, allow_null=True)
    promoted_designation_name = serializers.CharField(source='promoted_designation.name', read_only=True, allow_null=True)

    class Meta:
        model = Promotion
        fields = [
            'id',
            'employee',                 # For writing (takes user ID)
            'employee_name',            # For reading
            'promotion_date',
            'current_department_name',
            'current_designation_name',
            'current_pay_grade',
            'current_salary',
            'promoted_department',      # For writing (takes department ID)
            'promoted_department_name', # For reading
            'promoted_designation',     # For writing (takes designation ID)
            'promoted_designation_name',# For reading
            'promoted_pay_grade',
            'promoted_salary',
            'description'
        ]
        # These fields are used for input (creating/updating) but not shown in the output list
        extra_kwargs = {
            'employee': {'write_only': True},
            'promoted_department': {'write_only': True},
            'promoted_designation': {'write_only': True},
        }



class EmployeeJobStatusSerializer(serializers.ModelSerializer):
    # This field will only accept valid choices from your JobStatus enum
    job_status = serializers.ChoiceField(choices=JobStatus.choices)

    class Meta:
        model = Profile
        fields = ['job_status']


class HolidaySerializer(serializers.ModelSerializer):
    """ Serializer for the Holiday names master list. """
    class Meta:
        model = Holiday
        fields = '__all__'

class PublicHolidaySerializer(serializers.ModelSerializer):
    """ Serializer for assigning dates to a holiday. """
    # For displaying the holiday name in GET responses
    name = serializers.CharField(source='holiday.name', read_only=True)

    class Meta:
        model = PublicHoliday
        fields = ['id', 'holiday', 'name', 'start_date', 'end_date', 'comment']
        extra_kwargs = {
            # For creation (POST), we only need the holiday ID
            'holiday': {'write_only': True}
        }

class WeeklyHolidaySerializer(serializers.ModelSerializer):
    """ Serializer for weekly holidays. """
    class Meta:
        model = WeeklyHoliday
        fields = '__all__'

class LeaveTypeSerializer(serializers.ModelSerializer):
    """ Serializer for different types of leave. """
    class Meta:
        model = LeaveType
        fields = '__all__'

class EarnLeaveRuleSerializer(serializers.ModelSerializer):
    """ Serializer for the earn leave configuration rule. """
    class Meta:
        model = EarnLeaveRule
        fields = '__all__'

class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    number_of_days = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = LeaveApplication
        fields = [
            'leave_type', 
            'from_date', 
            'to_date', 
            'purpose',
            'number_of_days' # Calculated field
        ]
        
    def validate(self, data):
        employee = self.context['request'].user
        leave_type = data['leave_type']
        from_date = data['from_date']
        to_date = data['to_date']
        
        # --- 1. Date Validation & Calculation ---
        if from_date > to_date:
            raise serializers.ValidationError({"from_date": "From Date cannot be after To Date."})
            
        time_difference = to_date - from_date
        requested_days = time_difference.days + 1
        
        data['number_of_days'] = float(requested_days) 
        
        if requested_days <= 0:
             raise serializers.ValidationError({"number_of_days": "Calculated number of days must be greater than zero."})
             
        
        try:
            balance_record = LeaveBalance.objects.get(employee=employee, leave_type=leave_type)
            available_balance = balance_record.available_balance
        except LeaveBalance.DoesNotExist:
            available_balance = 0.0 # Agar record nahi hai, toh balance zero
            
        if requested_days > available_balance:
            raise serializers.ValidationError({
                "from_date": (f"Requested leave of {requested_days} days exceeds your current available balance "
                                   f"({round(available_balance, 1)} days for {leave_type.name}).")
            })
        
        return data


class LeaveApplicationListSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.profile.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    approved_by_name = serializers.CharField(source='approved_by.profile.full_name', read_only=True, allow_null=True)
    rejected_by_name = serializers.CharField(source='rejected_by.profile.full_name', read_only=True, allow_null=True)
    
    request_duration = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'employee_name', 'leave_type_name', 'from_date', 'to_date',
            'application_date', 'request_duration', 'number_of_days', 'status',
            'approved_by_name', 'approved_date', 'rejected_by_name', 'reject_date',
            'rejection_reason', 'purpose'
        ]
        
    def get_request_duration(self, obj):
        try:
            from_date_str = obj.from_date.strftime("%d/%m/%Y")
            to_date_str = obj.to_date.strftime("%d/%m/%Y")
            return f"{from_date_str} to {to_date_str}"
        except AttributeError:
            return "N/A"
        

class LeaveReportSerializer(serializers.Serializer):
    """ Used for filtering reports by date range and employee. """
    employee_id = serializers.IntegerField(required=False, allow_null=True)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, data):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({"from_date": "From Date cannot be after To Date."})
        return data
    

class WorkShiftSerializer(serializers.ModelSerializer):
    """Serializer for creating, listing, and updating work shifts."""
    class Meta:
        model = WorkShift
        fields = ['id', 'shift_name', 'start_time', 'end_time', 'late_count_time']

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Simple validation: Start time must be before End time (assuming no midnight cross-over for simplicity)
        if start_time and end_time and start_time >= end_time:
            pass 
        return data
    

class ManualAttendanceFilterSerializer(serializers.Serializer):
    """ Used to filter employees by department and date for GET request. """
    department_id = serializers.IntegerField(required=True)
    target_date = serializers.DateField(required=True)
    
class ManualAttendanceInputSerializer(serializers.Serializer):
    """ Used to update attendance for a single employee via PATCH request. """
    employee_id = serializers.IntegerField(required=True)
    target_date = serializers.DateField(required=True)
    punch_in_time = serializers.DateTimeField(required=False, allow_null=True)
    punch_out_time = serializers.DateTimeField(required=False, allow_null=True)
    is_late = serializers.BooleanField(required=False)
    is_present = serializers.BooleanField(required=False)

class AttendanceReportFilterSerializer(serializers.Serializer):
    """ Used to filter reports by date range and optionally employee_id. """
    employee_id = serializers.IntegerField(required=False, allow_null=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    
class DailyAttendanceFilterSerializer(serializers.Serializer):
    """ Specific filter for Daily Report (only date needed). """
    target_date = serializers.DateField(required=True)

class MonthlySummaryFilterSerializer(serializers.Serializer):
    """ Specific filter for Attendance Summary Report (only month needed). (lr04.png) """
    # Month format: YYYY-MM
    month = serializers.CharField(max_length=7, required=True)

class EmployeeProfileUpdateSerializer(serializers.ModelSerializer):
    work_shift_id = serializers.IntegerField(required=False, allow_null=True) 

    class Meta:
        model = Profile
        # Add 'work_shift_id' to your fields list
        fields = ['full_name', 'designation', 'department', 'work_shift_id', 'employee_id']




class AllowanceSerializer(serializers.ModelSerializer):
    """Serializer for Allowance List, Create, Retrieve, Update, and Delete."""
    
    # Read-only field to display the full Allowance Type name
    allowance_type_display = serializers.CharField(
        source='get_allowance_type_display', 
        read_only=True
    )

    class Meta:
        model = Allowance
        fields = [
            'id', 'allowance_name', 'allowance_type', 'allowance_type_display',
            'percentage_of_basic', 'limit_per_month', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation to ensure data consistency based on allowance type.
        """
        # If type is Fixed, percentage_of_basic must represent the fixed value
        if data.get('allowance_type') == Allowance.AllowanceType.FIXED:
            
            pass
        elif data.get('allowance_type') == Allowance.AllowanceType.PERCENTAGE:
            percentage = data.get('percentage_of_basic')
            if percentage is not None and (percentage <= 0 or percentage > 100):
                raise serializers.ValidationError(
                    {"percentage_of_basic": "Percentage must be between 0.01 and 100."}
                )

        return data
    


class DeductionSerializer(serializers.ModelSerializer):
    """Serializer for Deduction List, Create, Retrieve, Update, and Delete."""
    
    # Read-only field to display the full Deduction Type name
    deduction_type_display = serializers.CharField(
        source='get_deduction_type_display', 
        read_only=True
    )

    class Meta:
        model = Deduction
        fields = [
            'id', 'deduction_name', 'deduction_type', 'deduction_type_display',
            'percentage_of_basic', 'limit_per_month', 'is_tax_exempt',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Custom validation for percentage field."""
        deduction_type = data.get('deduction_type')
        percentage = data.get('percentage_of_basic')
        
        if deduction_type == Deduction.DeductionType.PERCENTAGE:
            if percentage is not None and (percentage < 0 or percentage > 100):
                raise serializers.ValidationError(
                    {"percentage_of_basic": "Percentage must be between 0 and 100."}
                )
        return data
    

class PayGradeAllowanceSerializer(serializers.ModelSerializer):
    """
    Handles Allowance ID input (write) and displays Allowance Name/Value (read).
    The 'value' is read-only because it is calculated/fetched in the parent serializer.
    """
    allowance_name = serializers.CharField(source='allowance.allowance_name', read_only=True)
    
    class Meta:
        model = PayGradeAllowance
        # 'value' field is NOT in extra_kwargs as write_only, it will be handled by the parent serializer
        fields = ['allowance', 'allowance_name', 'value']
        extra_kwargs = {
            'allowance': {'write_only': True},
            'value': {'read_only': True} # Read-only, as we set it internally
        } 

class PayGradeDeductionSerializer(serializers.ModelSerializer):
    """Handles Deduction ID input (write) and displays Deduction Name/Value (read)."""
    deduction_name = serializers.CharField(source='deduction.deduction_name', read_only=True)
    
    class Meta:
        model = PayGradeDeduction
        fields = ['deduction', 'deduction_name', 'value']
        extra_kwargs = {
            'deduction': {'write_only': True},
            'value': {'read_only': True}
        } 

# --- 2. MonthlyPayGradeSerializer Fix: Logic to Fetch Default Values ---

class MonthlyPayGradeSerializer(serializers.ModelSerializer):
    
    # Read nested data 
    allowance_details = PayGradeAllowanceSerializer(source='paygradeallowance_set', many=True, read_only=True)
    deduction_details = PayGradeDeductionSerializer(source='paygradededuction_set', many=True, read_only=True)
    
    # Write nested data (Input will only contain [{"allowance": ID}, ...])
    # The 'value' field is not expected in the input.
    allowances_to_add = PayGradeAllowanceSerializer(many=True, write_only=True, required=False)
    deductions_to_add = PayGradeDeductionSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = MonthlyPayGrade
        fields = [
            'id', 'grade_name', 'gross_salary', 'percentage_of_basic_g', 
            'basic_salary', 'overtime_rate', 'is_active', 
            'allowance_details', 'deduction_details', 
            'allowances_to_add', 'deductions_to_add'
        ]
        read_only_fields = ['id', 'basic_salary']

    def calculate_basic_salary(self, gross_salary, percentage):
        if percentage > 0 and gross_salary > 0:
            return (gross_salary * percentage) / Decimal(100)
        return Decimal(0.00)

    # --- Helper function for M2M creation/update ---
    def _create_update_m2m(self, pay_grade_instance, allowances_data, deductions_data, is_update=False):
        
        # 1. Handle Allowances
        if allowances_data is not None:
            if is_update:
                pay_grade_instance.paygradeallowance_set.all().delete()
                
            for item in allowances_data:
                # item['allowance'] is the actual Allowance object due to FK validation
                allowance_obj = item['allowance']
                
                # Logic: Fetch the default value from the Allowance object
                if allowance_obj.allowance_type == Allowance.AllowanceType.PERCENTAGE:
                    default_value = allowance_obj.percentage_of_basic
                else: # Fixed Type
                    default_value = allowance_obj.limit_per_month
                
                PayGradeAllowance.objects.create(
                    pay_grade=pay_grade_instance, 
                    allowance=allowance_obj, 
                    value=default_value # Inject the default value
                )

        # 2. Handle Deductions (Similar logic)
        if deductions_data is not None:
            if is_update:
                pay_grade_instance.paygradededuction_set.all().delete()
                
            for item in deductions_data:
                deduction_obj = item['deduction']
                
                # Logic: Fetch the default value from the Deduction object
                if deduction_obj.deduction_type == Deduction.DeductionType.PERCENTAGE:
                    default_value = deduction_obj.percentage_of_basic
                else: # Fixed Type
                    default_value = deduction_obj.limit_per_month
                    
                PayGradeDeduction.objects.create(
                    pay_grade=pay_grade_instance, 
                    deduction=deduction_obj, 
                    value=default_value # Inject the default value
                )


    def create(self, validated_data):
        allowances_data = validated_data.pop('allowances_to_add', [])
        deductions_data = validated_data.pop('deductions_to_add', [])
        
        # Calculate and set basic salary
        gross_salary = validated_data.get('gross_salary', Decimal(0))
        percentage = validated_data.get('percentage_of_basic_g', Decimal(0))
        validated_data['basic_salary'] = self.calculate_basic_salary(gross_salary, percentage)
        
        pay_grade = MonthlyPayGrade.objects.create(**validated_data)
        
        # Create nested M2M records using the helper function
        self._create_update_m2m(pay_grade, allowances_data, deductions_data, is_update=False)
            
        return pay_grade
    
    def update(self, instance, validated_data):
        allowances_data = validated_data.pop('allowances_to_add', None)
        deductions_data = validated_data.pop('deductions_to_add', None)

        # 1. Calculate Basic Salary before updating the main instance
        gross_salary = validated_data.get('gross_salary', instance.gross_salary)
        percentage = validated_data.get('percentage_of_basic_g', instance.percentage_of_basic_g)
        validated_data['basic_salary'] = self.calculate_basic_salary(gross_salary, percentage)
        
        # 2. Update the main MonthlyPayGrade instance fields 
        instance = super().update(instance, validated_data)

        # 3. Update nested M2M tables (PayGradeAllowance & PayGradeDeduction)
        self._create_update_m2m(instance, allowances_data, deductions_data, is_update=True)
                
        return instance
    
class HourlyPayGradeSerializer(serializers.ModelSerializer):
    """Serializer for Hourly Pay Grade CRUD."""
    
    class Meta:
        model = HourlyPayGrade
        fields = ['id', 'pay_grade_name', 'hourly_rate', 'is_active']
        read_only_fields = ['id']




class PerformanceCategorySerializer(serializers.ModelSerializer):
    """Serializer for minimal Performance Category CRUD operations."""
    
    class Meta:
        model = PerformanceCategory
        fields = ['id', 'category_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class PerformanceCriteriaSerializer(serializers.ModelSerializer):
    """Serializer for Performance Criteria CRUD operations."""
    
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    
    class Meta:
        model = PerformanceCriteria
        fields = [
            'id', 'category', 'category_name', 'criteria_name', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PerformanceRatingSerializer(serializers.ModelSerializer):
    """Handles the detail (criteria ID and rating value)."""
    # Read-only fields to display the criteria name
    criteria_name = serializers.CharField(source='criteria.criteria_name', read_only=True)
    
    class Meta:
        model = PerformanceRating
        fields = ['criteria', 'criteria_name', 'rating_value']


class EmployeePerformanceSerializer(serializers.ModelSerializer):
    # Nested Write Field: POST/PUT/PATCH input ke liye ratings ki list
    ratings_to_add = PerformanceRatingSerializer(many=True, write_only=True)
    
    # Nested Read Field: GET output ke liye ratings ki list
    ratings = PerformanceRatingSerializer( many=True, read_only=True)
    
    # Read-only fields to display employee and reviewer names
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewed_by.username', read_only=True)

    class Meta:
        model = EmployeePerformance
        fields = [
            'id', 'employee', 'employee_name', 'review_month', 'remarks', 
            'overall_rating', 'reviewed_by', 'reviewer_name', 'created_at',
            'ratings', 'ratings_to_add'
        ]
        read_only_fields = ['id', 'overall_rating', 'reviewed_by', 'created_at']

    # --- CREATE Method (Nested Saving Logic) ---
    def create(self, validated_data):
        ratings_data = validated_data.pop('ratings_to_add')
        
        # Current user ko 'reviewed_by' set karein
        validated_data['reviewed_by'] = self.context['request'].user
        
        # 1. EmployeePerformance (Header) instance create karein
        performance_review = EmployeePerformance.objects.create(**validated_data)
        
        # 2. PerformanceRating (Detail) records create karein
        ratings_list = []
        total_rating = Decimal('0.00')
        for rating_item in ratings_data:
            ratings_list.append(
                PerformanceRating(
                    performance_review=performance_review, 
                    **rating_item
                )
            )
            total_rating += rating_item['rating_value']
            
        PerformanceRating.objects.bulk_create(ratings_list)
        
        # 3. Overall rating calculate aur save karein
        if ratings_list:
            average_rating = total_rating / len(ratings_list)
            performance_review.overall_rating = average_rating
            performance_review.save(update_fields=['overall_rating'])
            
        return performance_review

    # --- UPDATE Method (Nested Update Logic - Full replacement) ---
    def update(self, instance, validated_data):
        ratings_data = validated_data.pop('ratings_to_add', None)
        
        # Header fields update karein
        instance = super().update(instance, validated_data)
        
        # Ratings update karein (Purane delete karke naye create karna)
        if ratings_data is not None:
            instance.ratings.all().delete()
            ratings_list = []
            total_rating = Decimal('0.00')
            
            for rating_item in ratings_data:
                ratings_list.append(
                    PerformanceRating(
                        performance_review=instance, 
                        **rating_item
                    )
                )
                total_rating += rating_item['rating_value']

            PerformanceRating.objects.bulk_create(ratings_list)

            # Recalculate and save overall_rating
            if ratings_list:
                instance.overall_rating = total_rating / len(ratings_list)
                instance.save(update_fields=['overall_rating'])
        
        return instance
    

class PerformanceSummarySerializer(serializers.ModelSerializer):
    """
    Serializer to display simple summary data for the Performance Summary Report.
    """
    # Employee name property se
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    ratings_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeePerformance
        fields = [
            'id', 'employee', 'employee_name', 'review_month', 'overall_rating', 
            'remarks', 'ratings_detail'
        ]
        
    def get_ratings_detail(self, obj):
        """
        Criteria, Category aur unki ratings ko list karta hai.
        """
        # Optimized query: Fetch criteria and nested category
        ratings = obj.ratings.all().select_related('criteria__category')
        
        detail_data = [
            {
                'category_name': rating.criteria.category.category_name,
                'criteria_name': rating.criteria.criteria_name,
                'rating_value': rating.rating_value
            } 
            for rating in ratings
        ]
        return detail_data
    

class JobPostSerializer(serializers.ModelSerializer):
    """
    Serializer for Job Post CRUD operations.
    """
    # 'published_by' field ko read-only rakhte hain, aur yeh field current user se set hoga
    published_by_name = serializers.CharField(source='published_by.full_name', read_only=True)
    
    class Meta:
        model = JobPost
        fields = [
            'id', 'job_title', 'job_post', 'description', 
            'status', 'job_publish_date', 'application_end_date',
            'published_by', 'published_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'published_by', 'published_by_name', 'created_at']


class TrainingTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for Training Type CRUD operations.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TrainingType
        fields = ['id', 'training_type_name', 'status', 'status_display', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmployeeTrainingSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee Training CRUD operations.
    Handles nested reading of FK names and file uploads.
    """
    
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    training_type_name = serializers.CharField(source='training_type.training_type_name', read_only=True)
    
    certificate_file = serializers.FileField(use_url=True, allow_null=True, required=False)
    class Meta:
        model = EmployeeTraining
        fields = [
            'id',
            'employee', 'training_type','employee_name', 'training_type_name',
            'subject', 'from_date', 'to_date', 'description', 
            'certificate_file', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AwardSerializer(serializers.ModelSerializer):
    """
    Serializer for Award CRUD operations using Enum for Award Name.
    """
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    display_award_name = serializers.CharField(source='get_award_name_display', read_only=True)
    display_month = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Award
        fields = [
            'id', 
            'award_name', 
            'employee', 'award_month', 'gift_item',
            'employee_name', 'display_award_name', 'display_month'
        ]
        read_only_fields = ['id']

    def get_display_month(self, obj):
        # Date ko Month YYYY format mein convert karna
        return obj.award_month.strftime('%B %Y')



class NoticeSerializer(serializers.ModelSerializer):
    """
    Serializer for Notice CRUD operations.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    attach_file = serializers.FileField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'description', 'publish_date', 
            'status', 
            'status_display',
            'attach_file', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LateDeductionRuleSerializer(serializers.ModelSerializer):
    """ 
    Serializer is simple because the 'status' field is already a CharField 
    with choices matching the frontend strings.
    """
    class Meta:
        model = LateDeductionRule
        fields = [
            'id', 
            'late_days_threshold', 
            'deduction_days',      
            'status'               # 'status' field ab seedhe model se aata hai
        ]
        read_only_fields = ['id']



class TaxRuleSerializer(serializers.ModelSerializer):
    """ 
    Serializer for Tax Rule Setup, including auto-calculation of 
    Taxable Amount based on the previous slab limit. 
    """
    
    class Meta:
        model = TaxRule
        fields = [
            'id',
            'gender',
            'slab_type',
            'total_income_limit',
            'tax_rate_percentage',
            'taxable_amount_fixed',
            'is_active',
        ]
        read_only_fields = ['id']

    def calculate_fixed_tax(self, gender, current_limit, tax_rate_percent):
        """ 
        Calculates the fixed taxable amount for the current slab by querying the previous slab's limit.
        """
        
        # 1. Previous Slab ki limit dhoondhna
        # Filter: Same gender, aur income limit current limit se kam ho.
        previous_rules = TaxRule.objects.filter(
            gender=gender,
            total_income_limit__lt=current_limit
        ).order_by('-total_income_limit')
        
        previous_limit = Decimal('0.00')
        if previous_rules.exists():
            # Pichle sabse bade rule ki limit. Agar 'First' slab hai, to yeh 0 rahega.
            previous_limit = previous_rules.first().total_income_limit
        
        # 2. Calculation
        taxable_income_in_slab = current_limit - previous_limit
        
        # Fixed Tax = (Income in Slab * Tax Rate) / 100
        fixed_tax = (taxable_income_in_slab * tax_rate_percent) / 100
        return fixed_tax

    def save_taxable_amount(self, validated_data):
        """ Calculates Taxable Amount before saving/updating. """
        
        current_limit = validated_data.get('total_income_limit')
        tax_rate = validated_data.get('tax_rate_percentage')
        gender = validated_data.get('gender')
        slab_type = validated_data.get('slab_type')
        
        # 'Remaining Total Income' slab ke liye, fixed tax 0 hoga.
        if slab_type == SlabChoices.REMAINING:
             validated_data['taxable_amount_fixed'] = 0.00
        else:
            # Fixed tax calculate karein
            calculated_tax = self.calculate_fixed_tax(gender, current_limit, tax_rate)
            validated_data['taxable_amount_fixed'] = calculated_tax
            
        return validated_data

    def create(self, validated_data):
        """ Create method ko override kiya taaki calculation ho sake. """
        validated_data = self.save_taxable_amount(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """ Update method ko override kiya taaki calculation ho sake. """
        validated_data = self.save_taxable_amount(validated_data)
        return super().update(instance, validated_data)