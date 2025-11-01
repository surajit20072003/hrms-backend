from django.urls import path
from .views import UserProfileView, EducationCreateView, ExperienceCreateView

urlpatterns = [
    # Apni profile dekhne (GET) aur update (PATCH) karne ke liye
    path('profile/me/', UserProfileView.as_view(), name='my-profile'),
    
    # Nayi education add karne ke liye (POST)
    path('profile/education/', EducationCreateView.as_view(), name='add-education'),

    # Naya experience add karne ke liye (POST)
    path('profile/experience/', ExperienceCreateView.as_view(), name='add-experience'),
]