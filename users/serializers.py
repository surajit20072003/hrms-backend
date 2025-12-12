from rest_framework import serializers
from .models import User, Profile, Education, Experience, Role, Page, AccountDetails, SubscriptionPlan, UserSubscription
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

# ==========================
# User Serializer
# ==========================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_name = serializers.CharField(required=False, allow_blank=True, max_length=200)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'company_name']

    def create(self, validated_data):
        # 1. User fields ko separate karein
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        company_name = validated_data.pop('company_name', '')  # NEW
        email = validated_data.get('email')
        user = User.objects.create(
            email=email, 
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        Profile.objects.create(
            user=user, 
            first_name=first_name,
            last_name=last_name,
            company_name=company_name  # NEW
        )
        
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs


# ==========================
# Logout Serializer
# ==========================
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is invalid or expired.'
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['profile']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ['profile']
class AccountDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetails
        exclude = ['profile']


class PersonalInfoSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Profile
        fields = [
            # Personal Info
            'first_name', 'last_name', 'full_name', 'phone', 'address', 
            'date_of_birth', 'gender', 'religion', 'marital_status',
            'emergency_contact', 'photo', 'company_name',  # Added company_name
            
            # Employment Info (IDs for updates, read-only for display)
            'employee_id', 'date_of_joining', 'date_of_leaving',
            'status', 'job_status', 
            
            # Foreign Key IDs (Read/Write for updates, requires corresponding fields in Profile model)
            'department', 
            'designation', 
            'branch', 
            'supervisor', 
            'work_shift',
            'monthly_pay_grade', 
            'hourly_pay_grade',
        ]
        # full_name is a property, so mark it read_only
        read_only_fields = ['full_name', 'employee_id', 'date_of_leaving', 'date_of_joining'] 




class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

# --- 4A: Page Serializer ---
class PageSerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(source='parent_id', read_only=True)
    native_permission_codename = serializers.CharField(source='native_permission.codename', read_only=True, allow_null=True)

    class Meta:
        model = Page
        fields = ['id','name','module','codename','url_name','module_icon','parent','module_order','order','native_permission_codename']


class RoleSerializer(serializers.ModelSerializer):
    pages = serializers.SerializerMethodField()

    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'pages', 'parent', 'users_count']
        read_only_fields = ['id', 'parent', 'users_count']

    def get_users_count(self, obj):
        return obj.users.count()

    def get_pages(self, obj):
        pages = obj.pages.all().order_by('module_order','module','order','name')
        serializer = PageSerializer(pages, many=True)
        pages_data = serializer.data

        # Convert list -> dict for quick lookup
        pages_map = {p['id']: p for p in pages_data}

        def build_tree(parent_id=None):
            nodes = []
            children = [p for p in pages_map.values() if p.get('parent') == parent_id]
            children.sort(key=lambda x: (x.get('order', 999), x.get('name', '')))

            for child in children:
                node = {
                    "id": child['id'],
                    "label": child['name'],
                    "key": child['url_name'],
                    "icon": child.get('module_icon'),
                    "codename": child['codename']
                }
                sub = build_tree(child['id'])
                if sub:
                    node["children"] = sub
                nodes.append(node)

            return nodes

        # Group by module like PageListView
        modules = {}
        for p in pages_data:
            mod = p['module']
            if mod not in modules:
                modules[mod] = {
                    "id": p['module_order'],
                    "label": mod,
                    "icon": p.get('module_icon'),
                    "children": []
                }

        result = []
        for mod, meta in modules.items():
            top = [p for p in pages_data if p['module'] == mod and not p.get('parent')]
            top.sort(key=lambda x: (x.get('order', 999), x.get('name', '')))

            for tp in top:
                node = {
                    "id": tp['id'],
                    "label": tp['name'],
                    "key": tp['url_name'],
                    "icon": tp.get('module_icon'),
                    "codename": tp['codename'],
                    "children": build_tree(tp['id'])
                }
                meta["children"].append(node)

            result.append(meta)

        return result

    def validate_name(self, value):
        """
        ✅ MULTI-TENANCY: Check role name uniqueness within company only
        """
        user = self.context['request'].user
        
        # Determine company owner
        if user.parent is None and not user.is_superuser:
            company_owner = user
        elif user.parent:
            company_owner = user.parent
        else:
            company_owner = None

        # Check uniqueness
        if self.instance:
            if Role.objects.filter(parent=company_owner, name__iexact=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(f"Role '{value}' already exists in your company")
        else:
            if Role.objects.filter(parent=company_owner, name__iexact=value).exists():
                raise serializers.ValidationError(f"Role '{value}' already exists in your company")
        
        return value
    
    def create(self, validated_data):
        """
        ✅ MULTI-TENANCY: Auto-set parent to company owner and created_by
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create role")
        
        user = request.user
        
        # Determine company owner
        if user.parent is None and not user.is_superuser:
            company_owner = user
        elif user.parent:
            company_owner = user.parent
        else:
            company_owner = None
            
        validated_data['parent'] = company_owner
        validated_data['created_by'] = user  # ✅ Set created_by for filter_by_company
        
        return super().create(validated_data)

        
# --- 4C: Page Assignment Serializer (For POST/PATCH Input) ---
class PageAssignmentSerializer(serializers.Serializer):
    """ 
    Serializer to validate and process the list of Page IDs assigned to a Role.
    Used for POST /api/roles/<id>/pages/
    """
    # Validates that the list contains valid Page Primary Keys (PKs)
    page_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Page.objects.all(), 
            # The source name 'page_objects' is a custom name to hold the validated Page objects
            #source='page_objects' 
        ),
        write_only=True,
        required=True,
        allow_empty=True, 
        help_text="A list of Page IDs that should be assigned to the role."
    )

class UserProfileSerializer(serializers.ModelSerializer):
    profile = PersonalInfoSerializer(read_only=True)
    education = EducationSerializer(many=True, read_only=True, source='profile.education')
    experience = ExperienceSerializer(many=True, read_only=True, source='profile.experience')
    account_details = AccountDetailsSerializer(many=True, read_only=True, source='profile.account_details')
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'profile', 'education', 'experience', 'account_details']

    def get_role(self, obj):
        # 1. If user has a real role (Employee), return it
        if obj.role:
            return RoleSerializer(obj.role).data
            
        # 2. If user is Company Owner (No Role) OR Superuser, return Virtual Role
        if (obj.parent is None and not obj.is_superuser) or obj.is_superuser:
            # Determine pages based on user type
            if obj.is_superuser:
                pages_qs = Page.objects.all().order_by('module_order','module','order','name')
                role_name = "Super Admin"
                role_desc = "Administrator with full access"
            else:
                # Company Owner
                pages_qs = obj.accessible_pages_by_plan().order_by('module_order','module','order','name')
                role_name = "Company Owner"
                role_desc = "Owner of the company"
            
            # --- Tree Building Logic (Same as RoleSerializer) ---
            serializer = PageSerializer(pages_qs, many=True)
            pages_data = serializer.data
            pages_map = {p['id']: p for p in pages_data}

            def build_tree(parent_id=None):
                nodes = []
                children = [p for p in pages_map.values() if p.get('parent') == parent_id]
                children.sort(key=lambda x: (x.get('order', 999), x.get('name', '')))

                for child in children:
                    node = {
                        "id": child['id'],
                        "label": child['name'],
                        "key": child['url_name'],
                        "icon": child.get('module_icon'),
                        "codename": child['codename']
                    }
                    sub = build_tree(child['id'])
                    if sub:
                        node["children"] = sub
                    nodes.append(node)
                return nodes

            modules = {}
            for p in pages_data:
                mod = p['module']
                if mod not in modules:
                    modules[mod] = {
                        "id": p['module_order'],
                        "label": mod,
                        "icon": p.get('module_icon'),
                        "children": []
                    }

            tree_pages = []
            for mod, meta in modules.items():
                top = [p for p in pages_data if p['module'] == mod and not p.get('parent')]
                top.sort(key=lambda x: (x.get('order', 999), x.get('name', '')))

                for tp in top:
                    node = {
                        "id": tp['id'],
                        "label": tp['name'],
                        "key": tp['url_name'],
                        "icon": tp.get('module_icon'),
                        "codename": tp['codename'],
                        "children": build_tree(tp['id'])
                    }
                    meta["children"].append(node)
                tree_pages.append(meta)
            # ----------------------------------------------------

            return {
                "id": None,
                "name": role_name,
                "description": role_desc,
                "pages": tree_pages,
                "parent": None,
                "users_count": 1
            }
            
        return None


# ============================================================================
# SUBSCRIPTION PLAN SERIALIZERS (For Superadmin CRUD)
# ============================================================================

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for Subscription Plan CRUD operations.
    Used by Superadmin to create/update/delete plans.
    """
    features_count = serializers.SerializerMethodField(read_only=True)
    available_pages = PageSerializer(many=True, read_only=True)
    available_page_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Page.objects.all(),
        write_only=True,
        required=False,
        source='available_pages'
    )
    is_unlimited_employees = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'plan_name',
            'description',
            'price',
            'max_employees',
            'is_unlimited_employees',
            'available_pages',
            'available_page_ids',
            'features_count',
            'billing_cycle',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'features_count', 'is_unlimited_employees']
    
    def get_features_count(self, obj):
        """Returns the number of pages/features in this plan"""
        return obj.features_count
    
    def validate_plan_name(self, value):
        """Ensure plan name is unique"""
        if self.instance:
            # Update case - exclude current instance
            if SubscriptionPlan.objects.filter(plan_name__iexact=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(f"Plan '{value}' already exists")
        else:
            # Create case
            if SubscriptionPlan.objects.filter(plan_name__iexact=value).exists():
                raise serializers.ValidationError(f"Plan '{value}' already exists")
        return value
    
    def validate_price(self, value):
        """Ensure price is not negative"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_max_employees(self, value):
        """Validate max employees limit"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Max employees must be at least 1 or leave blank for unlimited")
        return value


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing plans (without full page details).
    Used in dropdown selections and list views.
    """
    features_count = serializers.SerializerMethodField()
    is_unlimited_employees = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'plan_name',
            'description',
            'price',
            'max_employees',
            'is_unlimited_employees',
            'features_count',
            'billing_cycle',
            'is_active',
        ]
    
    def get_features_count(self, obj):
        return obj.features_count


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for User Subscription details.
    Shows which plan a company owner has subscribed to.
    """
    plan_details = SubscriptionPlanListSerializer(source='plan', read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        write_only=True,
        source='plan'
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'user',
            'user_email',
            'plan',
            'plan_id',
            'plan_details',
            'start_date',
            'end_date',
            'status',
            'days_remaining',
            'is_active',
            'last_payment_date',
            'next_billing_date',
            'razorpay_subscription_id',
            'razorpay_customer_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'start_date', 'created_at', 
            'updated_at', 'days_remaining', 'is_active'
        ]
    
    def validate(self, attrs):
        """Ensure user doesn't already have an active subscription"""
        user = attrs.get('user') or (self.instance.user if self.instance else None)
        
        if not self.instance:  # Create case
            if hasattr(user, 'subscription'):
                raise serializers.ValidationError("User already has a subscription")
        
        return attrs


class PlanPageAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning pages to a subscription plan.
    Used by Superadmin to update which pages are available in a plan.
    """
    page_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Page.objects.all()),
        write_only=True,
        required=True,
        allow_empty=True,
        help_text="List of Page IDs to assign to this plan"
    )