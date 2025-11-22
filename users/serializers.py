from rest_framework import serializers
from .models import User, Profile, Education, Experience,Role,Page
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

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        # 1. User fields ko separate karein
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
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
            last_name=last_name
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


class PersonalInfoSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Profile
        fields = [
            # Personal Info
            'first_name', 'last_name', 'full_name', 'phone', 'address', 
            'date_of_birth', 'gender', 'religion', 'marital_status',
            'emergency_contact', 'photo',
            
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
    """ Serializes Role and nests the list of pages assigned to it. """
    
    # Nested field jo role ke pages (M2M field) ko serialize karega
    pages = PageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        # 'pages' field M2M relation ko represent karta hai
        fields = ['id', 'name', 'description', 'pages']
        
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
    role = RoleSerializer(read_only=True)
    profile = PersonalInfoSerializer(read_only=True)
    education = EducationSerializer(many=True, read_only=True, source='profile.education')
    experience = ExperienceSerializer(many=True, read_only=True, source='profile.experience')

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'profile', 'education', 'experience']