from django.urls import path
from .views import *

urlpatterns = [
    # Apni profile dekhne (GET) aur update (PATCH) karne ke liye
    path('profile/me/', UserProfileView.as_view(), name='my-profile'),
    
    # Nayi education add karne ke liye (POST)
    path('profile/education/', EducationCreateView.as_view(), name='add-education'),

    # Naya experience add karne ke liye (POST)
    path('profile/experience/', ExperienceCreateView.as_view(), name='add-experience'),

    path('signup/', RegisterView.as_view(), name='signup'),
    
    path('login/', LoginView.as_view(), name='login'),

    path('pages/', PageListView.as_view(), name='page-list'),
    
    # 2. Role Listing for Dropdown
    path('roles/', RoleListView.as_view(), name='role-list'), 
    
    # 3. Role Page Assignment (GET assigned, POST update)
    path('roles/<int:role_id>/pages/', RolePageAssignmentView.as_view(), name='role-page-assignment'),
    

]