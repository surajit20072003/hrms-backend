from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Page, Role, User, Profile, SubscriptionPlan, UserSubscription
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from users.permissions import HasPageAccess
from datetime import date, timedelta

from .serializers import (
    UserProfileSerializer, 
    PersonalInfoSerializer,
    EducationSerializer,
    ExperienceSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PageSerializer, 
    RoleSerializer, 
    PageAssignmentSerializer,
    RoleListSerializer,
    SubscriptionPlanSerializer,
    SubscriptionPlanListSerializer,
    UserSubscriptionSerializer,
    PlanPageAssignmentSerializer,
)

# Helper function
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # ✅ AUTO-ASSIGN FREE PLAN to new company owner
            try:
                free_plan = SubscriptionPlan.objects.get(plan_name='Free', is_active=True)
                UserSubscription.objects.create(
                    user=user,
                    plan=free_plan,
                    status='ACTIVE',
                    end_date=None  # Free plan has no expiry
                )
            except SubscriptionPlan.DoesNotExist:
                # If Free plan doesn't exist, log warning but continue
                pass
            
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    'message': 'User registered successfully.',
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# NEW: Superadmin Create Company Owner View
# ============================================================================
class SuperadminCreateCompanyOwnerView(APIView):
    """
    POST /api/superadmin/create-company-owner/
    
    Sirf Superadmin hi company owners create kar sakta hai.
    Company owner ko email aur temporary password milega.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. Verify ki request superadmin se aa rahi hai
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can create company owners."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 2. Required fields validate karein
        email = request.data.get('email')
        password = request.data.get('password')  # Temporary password
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        company_name = request.data.get('company_name', '')
        
        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Check karein ki email already exist to nahi karta
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 4. Company Owner create karein
                user = User.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    parent=None,  # Company owner ka parent None hota hai
                    is_active=True,
                    is_staff=False,
                    is_superuser=False
                )
                user.set_password(password)
                user.save()
                
                # 5. Profile create karein
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    company_name=company_name
                )
                
                # 6. ✅ AUTO-ASSIGN FREE PLAN to new company owner
                try:
                    free_plan = SubscriptionPlan.objects.get(plan_name='Free', is_active=True)
                    UserSubscription.objects.create(
                        user=user,
                        plan=free_plan,
                        status='ACTIVE',
                        end_date=None  # Free plan has no expiry
                    )
                except SubscriptionPlan.DoesNotExist:
                    # If Free plan doesn't exist, continue without subscription
                    pass
                
                # 7. Response prepare karein with credentials
                return Response(
                    {
                        "message": "Company owner created successfully.",
                        "credentials": {
                            "email": email,
                            "password": password,  # Temporary password
                            "user_id": user.id,
                            "company_name": company_name
                        },
                        "note": "Please share these credentials securely with the company owner. They should change the password after first login."
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            return Response(
                {"error": f"Failed to create company owner: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    'message': 'Login successful.',
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Logged-in user ki poori profile details deta hai. """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """ User ki personal information ko update karta hai. """
        profile = request.user.profile
        serializer = PersonalInfoSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EducationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ Profile me nayi education add karta hai. """
        serializer = EducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExperienceCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ Profile me naya experience add karta hai. """
        serializer = ExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class PageListView(APIView):
    permission_classes = [IsAuthenticated]
    DEFAULT_ICON = 'list_alt'

    def build_tree(self, pages_map, parent_id=None):
        nodes = []
        # get children of this parent sorted by order
        children = [p for p in pages_map.values() if p.get('parent') == parent_id]
        children.sort(key=lambda x: (x.get('order', 999), x.get('name', '')))

        for child in children:
            node = {
                "id": child['id'],
                "key": child['url_name'],
                "label": child['name'],
                "icon": child.get('module_icon') or self.DEFAULT_ICON,
                "codename": child['codename'],
                # roles: if you attach allowed roles to page, include here
            }
            # recursively attach children
            subchildren = self.build_tree(pages_map, child['id'])
            if subchildren:
                node['children'] = subchildren
            nodes.append(node)

        return nodes

    def get(self, request):
        # ✅ MULTI-TENANCY: Filter pages based on subscription plan
        if request.user.is_superuser:
            pages_qs = Page.objects.all().order_by('module_order','module','order','name')
        else:
            # Get pages allowed by subscription plan
            # This uses the helper method we added to User model
            plan_pages = request.user.accessible_pages_by_plan()
            pages_qs = plan_pages.order_by('module_order','module','order','name')
            
        serializer = PageSerializer(pages_qs, many=True)
        pages = serializer.data

        # map by id for fast lookup
        pages_map = {p['id']: p for p in pages}

        # Build modules as top level: modules determined by pages where parent is None and module_order grouping
        # We want modules ordered by module_order (use first page's module_order)
        modules = {}
        for p in pages:
            module = p['module']
            if module not in modules:
                modules[module] = {
                    'module_order': p.get('module_order', 999),
                    'icon': p.get('module_icon') or self.DEFAULT_ICON
                }
            # prefer a real icon if found
            if p.get('module_icon') and p.get('module_icon') != self.DEFAULT_ICON:
                modules[module]['icon'] = p.get('module_icon')

        # Build final module list
        result = []
        for module_name, meta in sorted(modules.items(), key=lambda x: x[1]['module_order']):
            # find top-level pages for this module (pages with parent is None and page.module == module_name)
            top_pages = [p for p in pages if p['module'] == module_name and p.get('parent') in (None, '', 0)]
            # Build module children by using build_tree on each top page
            children = []
            # sort top_pages by order or name
            top_pages.sort(key=lambda x: (x.get('order', 999), x.get('name', '')))
            for tp in top_pages:
                node = {
                    "id": tp['id'],
                    "key": tp['url_name'],
                    "label": tp['name'],
                    "icon": tp.get('module_icon') or meta['icon'],
                    "codename": tp['codename'],
                }
                sub = self.build_tree(pages_map, tp['id'])
                if sub:
                    node['children'] = sub
                children.append(node)

            result.append({
                "id": meta['module_order'],  # <-- ADD THIS
                "key": f"/{module_name.lower().replace(' ', '-')}",
                "label": module_name,
                "icon": meta['icon'],
                "codename": module_name.lower().replace(" ", "_"),  # optional (future RBAC)
                "children": children
            })


        return Response(result)
    

class RoleListView(APIView):
    """ GET /api/roles/: Lists all Roles for selection dropdown. """
    permission_classes = [
        IsAuthenticated
    ]
    
    def get(self, request):
        from company.utils import filter_by_company
        
        roles = Role.objects.all().order_by('name')
        # ✅ MULTI-TENANCY: Filter roles by company
        roles = filter_by_company(roles, request.user)
        serializer = RoleSerializer(roles, many=True, context={'request': request}) 
        return Response(serializer.data)


# --- 5B & 5C: Role Page Assignment (RBAC Enforced) ---
class RolePageAssignmentView(APIView):
    """
    GET /api/roles/<id>/pages/: Gets current Page assignments.
    POST /api/roles/<id>/pages/: Updates Page assignments.
    """
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, role_id):
        """ Returns a list of Page IDs currently assigned to the Role. """
        from company.utils import filter_by_company
        
        try:
            # ✅ MULTI-TENANCY: Verify role belongs to company
            roles = Role.objects.filter(pk=role_id)
            roles = filter_by_company(roles, request.user)
            role = roles.first()
            
            if not role:
                raise Role.DoesNotExist
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Efficiently fetch IDs of assigned pages
        assigned_page_ids = role.pages.all().values_list('id', flat=True)
        
        return Response({
            "role_id": role.id,
            "role_name": role.name,
            "assigned_page_ids": list(assigned_page_ids)
        })

    def post(self, request, role_id):
        """ Replaces the existing page assignments with a new list of Page IDs. """
        from company.utils import filter_by_company
        
        try:
            # ✅ MULTI-TENANCY: Verify role belongs to company
            roles = Role.objects.filter(pk=role_id)
            roles = filter_by_company(roles, request.user)
            role = roles.first()
            
            if not role:
                raise Role.DoesNotExist
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PageAssignmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # FIX: The validated data key must be 'page_ids', not 'page_objects'
        page_objects_to_assign = serializer.validated_data.get('page_ids', [])
        
        # ✅ MULTI-TENANCY: Validate that all assigned pages are in the company's subscription plan
        if not request.user.is_superuser:
            # Get company owner (to check plan)
            company_owner = request.user.company_owner
            if company_owner:
                # Get pages allowed in the plan
                # We use accessible_pages_by_plan() on owner to get ALL plan pages
                allowed_pages = company_owner.accessible_pages_by_plan()
                
                # Check if any requested page is NOT in allowed pages
                # We compare IDs for efficiency
                allowed_page_ids = set(allowed_pages.values_list('id', flat=True))
                requested_page_ids = set(p.id for p in page_objects_to_assign)
                
                if not requested_page_ids.issubset(allowed_page_ids):
                    invalid_ids = requested_page_ids - allowed_page_ids
                    return Response(
                        {
                            "error": "You cannot assign pages that are not included in your subscription plan.",
                            "invalid_page_ids": list(invalid_ids)
                        }, 
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        with transaction.atomic():
            # 1. Update Page M2M (Menu Visibility)
            role.pages.set(page_objects_to_assign)

            # 2. Update Group Permissions (API Security) - Crucial for backend checks
            group = role.group
            if not group:
                role.save() 
                group = role.group
                
            # Filter the assigned Page objects to get only those linked to a native Permission
            native_perms_to_assign = [p.native_permission for p in page_objects_to_assign if p.native_permission]
            group.permissions.set(native_perms_to_assign)

        return Response(
            {"message": f"Permissions successfully updated for Role: {role.name}.",
             "assigned_count": len(page_objects_to_assign)}, 
            status=status.HTTP_200_OK
        )



# --- 5E: User Role Assignment/Update API (MISSING VIEW ADDED) ---
class UserRoleUpdateView(APIView):
    """
    PATCH /api/users/<user_id>/role/: To update the role of a specific user.
    """
    permission_classes = [
        IsAuthenticated
    ]
    
    def patch(self, request, user_id):
        from company.utils import filter_by_company, get_company_users
        
        # 1. ✅ MULTI-TENANCY: Verify user belongs to company
        company_users = get_company_users(request.user)
        user_to_update = get_object_or_404(company_users, pk=user_id)
        
        # 2. Check karein ki role_id request data mein hai ya nahi
        role_id = request.data.get('role_id')
        if role_id is None:
            return Response({"error": "role_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. ✅ MULTI-TENANCY: Verify role belongs to company
            if role_id:
                roles = Role.objects.filter(pk=role_id)
                roles = filter_by_company(roles, request.user)
                role = roles.first()
                
                if not role:
                    raise Role.DoesNotExist
            else:
                # Agar role_id 0 ya None hai, toh role ko None set karein
                role = None 
                
        except Role.DoesNotExist:
            return Response({"error": "Invalid Role ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 4. Role assign karein aur save karein
        with transaction.atomic():
            user_to_update.role = role
            user_to_update.save()
            
        role_name = role.name if role else 'None (Unassigned)'
        
        # 5. Response dein
        return Response({
            "message": f"Role '{role_name}' successfully assigned to user {user_to_update.email}.",
            "user_id": user_to_update.id,
            "new_role_id": role_id
        }, status=status.HTTP_200_OK)


# ============================================================================
# SUPERADMIN: SUBSCRIPTION PLAN CRUD VIEWS
# ============================================================================

class SubscriptionPlanListCreateView(APIView):
    """
    GET /api/superadmin/plans/ - List all subscription plans
    POST /api/superadmin/plans/ - Create new subscription plan
    
    Only Superadmin can access these endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all subscription plans with statistics"""
        # ✅ Only superadmin can view plans
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can view subscription plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plans = SubscriptionPlan.objects.all().order_by('price')
        serializer = SubscriptionPlanSerializer(plans, many=True)
        
        # Add statistics
        total_plans = plans.count()
        active_plans = plans.filter(is_active=True).count()
        total_value = sum(plan.price * plan.subscriptions.filter(status='ACTIVE').count() for plan in plans)
        
        return Response({
            "plans": serializer.data,
            "statistics": {
                "total_plans": total_plans,
                "active_plans": active_plans,
                "total_value": float(total_value),
            }
        })
    
    def post(self, request):
        """Create a new subscription plan"""
        # ✅ Only superadmin can create plans
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can create subscription plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Subscription plan created successfully",
                    "plan": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanDetailView(APIView):
    """
    GET /api/superadmin/plans/<id>/ - Get plan details
    PUT /api/superadmin/plans/<id>/ - Update plan
    PATCH /api/superadmin/plans/<id>/ - Partial update plan
    DELETE /api/superadmin/plans/<id>/ - Delete plan
    
    Only Superadmin can access these endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Helper method to get plan object"""
        try:
            return SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Get subscription plan details"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can view subscription plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Subscription plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SubscriptionPlanSerializer(plan)
        
        # Add subscription statistics for this plan
        active_subscriptions = plan.subscriptions.filter(status='ACTIVE').count()
        total_subscriptions = plan.subscriptions.count()
        
        return Response({
            "plan": serializer.data,
            "statistics": {
                "active_subscriptions": active_subscriptions,
                "total_subscriptions": total_subscriptions,
            }
        })
    
    def put(self, request, pk):
        """Full update of subscription plan"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can update subscription plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Subscription plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SubscriptionPlanSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Subscription plan updated successfully",
                "plan": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        """Partial update of subscription plan"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can update subscription plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Subscription plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Subscription plan updated successfully",
                "plan": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete subscription plan (only if no active subscriptions)"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can delete subscription plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plan = self.get_object(pk)
        if not plan:
            return Response(
                {"error": "Subscription plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if plan has active subscriptions
        active_subscriptions = plan.subscriptions.filter(status='ACTIVE').count()
        if active_subscriptions > 0:
            return Response(
                {
                    "error": f"Cannot delete plan with {active_subscriptions} active subscriptions. "
                             "Please cancel or migrate subscriptions first."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan_name = plan.plan_name
        plan.delete()
        
        return Response({
            "message": f"Subscription plan '{plan_name}' deleted successfully"
        }, status=status.HTTP_200_OK)


class PlanPageAssignmentView(APIView):
    """
    GET /api/superadmin/plans/<id>/pages/ - Get pages assigned to plan
    POST /api/superadmin/plans/<id>/pages/ - Assign pages to plan
    
    Only Superadmin can manage plan-page assignments.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get list of page IDs assigned to this plan"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can view plan pages"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            plan = SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"error": "Subscription plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        assigned_page_ids = plan.available_pages.all().values_list('id', flat=True)
        
        return Response({
            "plan_id": plan.id,
            "plan_name": plan.plan_name,
            "assigned_page_ids": list(assigned_page_ids),
            "total_pages": len(assigned_page_ids)
        })
    
    def post(self, request, pk):
        """Assign pages to subscription plan"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can assign pages to plans"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            plan = SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"error": "Subscription plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PlanPageAssignmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        page_objects = serializer.validated_data.get('page_ids', [])
        
        with transaction.atomic():
            # Replace existing page assignments
            plan.available_pages.set(page_objects)
        
        return Response({
            "message": f"Pages successfully assigned to plan '{plan.plan_name}'",
            "assigned_count": len(page_objects)
        }, status=status.HTTP_200_OK)


# ============================================================================
# COMPANY OWNER: SUBSCRIPTION MANAGEMENT VIEWS
# ============================================================================

class CompanyPlanListView(APIView):
    """
    GET /api/plans/ - List all active subscription plans for company owners
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # List only active plans
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
        
        # Use the lightweight serializer
        serializer = SubscriptionPlanListSerializer(plans, many=True)
        
        return Response(serializer.data)


class CompanySubscribeView(APIView):
    """
    POST /api/subscribe/ - Subscribe to a plan
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. Verify user is company owner
        if request.user.parent is not None:
            return Response(
                {"error": "Only company owners can manage subscriptions."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({"error": "plan_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Invalid or inactive plan"}, status=status.HTTP_404_NOT_FOUND)
            
        # 2. Create/Update Subscription
        with transaction.atomic():
            # Calculate end_date based on billing cycle
            if plan.price > 0:
                if plan.billing_cycle == 'MONTHLY':
                    end_date = date.today() + timedelta(days=30)
                elif plan.billing_cycle == 'YEARLY':
                    end_date = date.today() + timedelta(days=365)
                else:  # LIFETIME
                    end_date = None
            else:
                end_date = None  # Free plan has no expiry
            
            # Check if subscription exists
            subscription, created = UserSubscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'status': 'ACTIVE',
                    'end_date': end_date
                }
            )
            
            if not created:
                # Upgrade/Downgrade logic
                subscription.plan = plan
                subscription.status = 'ACTIVE'
                # Set end_date based on billing cycle
                if plan.price > 0:
                    if plan.billing_cycle == 'MONTHLY':
                        subscription.end_date = date.today() + timedelta(days=30)
                    elif plan.billing_cycle == 'YEARLY':
                        subscription.end_date = date.today() + timedelta(days=365)
                    else:  # LIFETIME
                        subscription.end_date = None
                else:
                    subscription.end_date = None  # Free plan has no expiry
                subscription.save()
                
        return Response({
            "message": f"Successfully subscribed to {plan.plan_name} plan.",
            "plan": SubscriptionPlanListSerializer(plan).data,
            "status": "ACTIVE"
        }, status=status.HTTP_200_OK)


class CompanySubscriptionDetailView(APIView):
    """
    GET /api/subscription/ - Get current subscription details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get company owner (if employee requests, show owner's plan)
        owner = request.user.company_owner
        
        if not owner:
            return Response({"error": "No company owner found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            subscription = UserSubscription.objects.get(user=owner)
            serializer = UserSubscriptionSerializer(subscription)
            return Response(serializer.data)
        except UserSubscription.DoesNotExist:
            return Response({
                "message": "No active subscription found.",
                "status": "INACTIVE"
            }, status=status.HTTP_200_OK)


# ============================================================================
# SUPERADMIN: DASHBOARD & ANALYTICS VIEWS
# ============================================================================

class SuperadminCompanyListView(APIView):
    """
    GET /api/superadmin/companies/ - List all companies with subscription details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all company owners (users with parent=None and not superuser)
        company_owners = User.objects.filter(
            parent=None, 
            is_superuser=False
        ).select_related('profile', 'subscription').order_by('-date_joined')
        
        companies_data = []
        for owner in company_owners:
            # Get employee count
            employee_count = User.objects.filter(parent=owner).count()
            
            # Get subscription details
            try:
                subscription = owner.subscription
                plan_name = subscription.plan.plan_name
                monthly_fee = float(subscription.plan.price)
                status_text = subscription.status
            except:
                plan_name = "No Plan"
                monthly_fee = 0
                status_text = "Inactive"
            
            # Safely get company name
            try:
                company_name = owner.profile.company_name if owner.profile.company_name else "N/A"
            except:
                company_name = "N/A"
            
            companies_data.append({
                "id": owner.id,
                "company_name": company_name,
                "owner_email": owner.email,
                "employees_count": employee_count,
                "subscription_plan": plan_name,
                "monthly_fee": monthly_fee,
                "status": status_text,
                "joined_date": owner.date_joined.strftime("%b %d, %Y")
            })
        
        return Response({
            "companies": companies_data,
            "total_count": len(companies_data)
        })


class SuperadminDashboardStatsView(APIView):
    """
    GET /api/superadmin/dashboard-stats/ - Get dashboard statistics
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Total companies
        total_companies = User.objects.filter(parent=None, is_superuser=False).count()
        
        # Total employees (across all companies)
        total_employees = User.objects.filter(parent__isnull=False).count()
        
        # Active subscriptions
        active_subscriptions = UserSubscription.objects.filter(status='ACTIVE').count()
        
        # Monthly revenue (sum of all active subscription plan prices)
        from django.db.models import Sum
        monthly_revenue = UserSubscription.objects.filter(
            status='ACTIVE'
        ).select_related('plan').aggregate(
            total=Sum('plan__price')
        )['total'] or 0
        
        # Plan distribution
        plan_distribution = {}
        for plan in SubscriptionPlan.objects.all():
            count = UserSubscription.objects.filter(plan=plan, status='ACTIVE').count()
            plan_distribution[plan.plan_name] = count
        
        return Response({
            "total_companies": total_companies,
            "total_employees": total_employees,
            "active_subscriptions": active_subscriptions,
            "monthly_revenue": float(monthly_revenue),
            "plan_distribution": plan_distribution
        })


class SuperadminGrowthOverviewView(APIView):
    """
    GET /api/superadmin/growth-overview/ - Get growth data for charts
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superadmin can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from datetime import datetime, timedelta
        from django.db.models.functions import TruncMonth
        from django.db.models import Count
        
        # Get data for last 12 months
        twelve_months_ago = datetime.now() - timedelta(days=365)
        
        # Group companies by month
        companies_by_month = User.objects.filter(
            parent=None,
            is_superuser=False,
            date_joined__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Prepare response data
        months = []
        companies_count = []
        cumulative_companies = 0
        
        for entry in companies_by_month:
            cumulative_companies += entry['count']
            months.append(entry['month'].strftime("%b"))
            companies_count.append(cumulative_companies)
        
        # Calculate cumulative employees (simplified - you can enhance this)
        total_employees_now = User.objects.filter(parent__isnull=False).count()
        
        return Response({
            "months": months,
            "companies": companies_count,
            "employees": [int(total_employees_now * (i+1) / len(months)) for i in range(len(months))] if months else []
        })