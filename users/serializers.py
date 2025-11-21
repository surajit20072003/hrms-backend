from rest_framework import serializers
from .models import User, Profile, Education, Experience,Role
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

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


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
        
# ==========================
# UserProfileSerializer (Remains the same, aggregates data)
# ==========================
class UserProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    profile = PersonalInfoSerializer(read_only=True)
    education = EducationSerializer(many=True, read_only=True, source='profile.education')
    experience = ExperienceSerializer(many=True, read_only=True, source='profile.experience')

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'profile', 'education', 'experience']