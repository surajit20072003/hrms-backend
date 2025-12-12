from django.urls import path
from .views import *

urlpatterns = [
    # ============================================================================
    # AUTHENTICATION & REGISTRATION
    # ============================================================================
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    
    # ============================================================================
    # SUPERADMIN ENDPOINTS
    # ============================================================================
    path('superadmin/create-company-owner/', SuperadminCreateCompanyOwnerView.as_view(), name='superadmin-create-company-owner'),
    path('superadmin/companies/', SuperadminCompanyListView.as_view(), name='superadmin-companies'),
    path('superadmin/dashboard-stats/', SuperadminDashboardStatsView.as_view(), name='superadmin-dashboard-stats'),
    path('superadmin/growth-overview/', SuperadminGrowthOverviewView.as_view(), name='superadmin-growth-overview'),
    
    # ============================================================================
    # USER PROFILE MANAGEMENT
    # ============================================================================
    # Apni profile dekhne (GET) aur update (PATCH) karne ke liye
    path('profile/me/', UserProfileView.as_view(), name='my-profile'),
    
    # Nayi education add karne ke liye (POST)
    path('profile/education/', EducationCreateView.as_view(), name='add-education'),

    # Naya experience add karne ke liye (POST)
    path('profile/experience/', ExperienceCreateView.as_view(), name='add-experience'),

    # ============================================================================
    # PAGE & ROLE MANAGEMENT
    # ============================================================================
    # All pages listing
    path('pages/', PageListView.as_view(), name='page-list'),
    
    # Role Listing for Dropdown
    path('roles/', RoleListView.as_view(), name='role-list'), 
    
    # Role Page Assignment (GET assigned, POST update)
    path('roles/<int:role_id>/pages/', RolePageAssignmentView.as_view(), name='role-page-assignment'),
    
    # User Role Assignment/Update
    path('users/<int:user_id>/role/', UserRoleUpdateView.as_view(), name='user-role-update'),
    
    # ============================================================================
    # SUBSCRIPTION PLAN MANAGEMENT (Superadmin Only)
    # ============================================================================
    # Plan CRUD Operations
    path('superadmin/plans/', SubscriptionPlanListCreateView.as_view(), name='superadmin-plan-list-create'),
    path('superadmin/plans/<int:pk>/', SubscriptionPlanDetailView.as_view(), name='superadmin-plan-detail'),
    
    # Plan-Page Assignment
    path('superadmin/plans/<int:pk>/pages/', PlanPageAssignmentView.as_view(), name='superadmin-plan-pages'),
    
    # ============================================================================
    # COMPANY OWNER SUBSCRIPTION ENDPOINTS
    # ============================================================================
    path('plans/', CompanyPlanListView.as_view(), name='company-plan-list'),
    path('subscribe/', CompanySubscribeView.as_view(), name='company-subscribe'),
    path('subscription/', CompanySubscriptionDetailView.as_view(), name='company-subscription-detail'),
]