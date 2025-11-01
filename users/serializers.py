from rest_framework import serializers
from .models import User, Profile, Education, Experience

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
            'full_name', 'phone', 'address', 'date_of_joining', 'date_of_birth',
            'gender', 'religion', 'marital_status'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    profile = PersonalInfoSerializer(read_only=True)
    education = EducationSerializer(many=True, read_only=True, source='profile.education')
    experience = ExperienceSerializer(many=True, read_only=True, source='profile.experience')

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'profile', 'education', 'experience']