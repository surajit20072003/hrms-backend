from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Page, Role, User # User model import kiya for UserRoleUpdateView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404 # get_object_or_404 import kiya
from users.permissions import HasPageAccess # Custom permission import kiya

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
    RoleListSerializer # <-- Ab yeh sahi se use hoga
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
    """ GET /api/pages/: Lists all available Page/Feature items, grouped by module. """
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        pages = Page.objects.all()
        serializer = PageSerializer(pages, many=True)
        
        # Group pages by module for the frontend UI structure
        grouped_data = {}
        for item in serializer.data:
            module = item['module']
            if module not in grouped_data:
                grouped_data[module] = []
            
            # Remove the 'module' key from the inner page object
            page_data = {k: v for k, v in item.items() if k != 'module'}
            grouped_data[module].append(page_data)
            
        return Response(grouped_data)

class RoleListView(APIView):
    """ GET /api/roles/: Lists all Roles for selection dropdown. """
    permission_classes = [
        IsAuthenticated
    ]
    
    def get(self, request):
        roles = Role.objects.all()
        # FIX: RoleListSerializer is now used for simple list display
        serializer = RoleSerializer(roles, many=True) 
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
        try:
            role = Role.objects.get(pk=role_id)
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
        
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PageAssignmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # FIX: The validated data key must be 'page_ids', not 'page_objects'
        page_objects_to_assign = serializer.validated_data.get('page_ids', [])
        
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

# --- 5D: User Menu API ---
class UserMenuAPIView(APIView):
    """ GET /api/user/menus/: Returns the allowed pages for the current user, grouped by module. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.is_superuser:
            allowed_pages = Page.objects.all().order_by('module', 'name')
        elif user.role:
            allowed_pages = user.role.pages.all().order_by('module', 'name')
        else:
            return Response({'menu': {}}, status=status.HTTP_200_OK)

        serializer = PageSerializer(allowed_pages, many=True)
        
        menu_structure = {}
        for item in serializer.data:
            module = item['module']
            
            # Prepare page data for frontend menu item
            page_data = {
                'id': item['id'],
                'name': item['name'],
                'url': item['url_name'], # Use the route path
                'codename': item['codename'],
            }
            
            if module not in menu_structure:
                menu_structure[module] = []
                
            menu_structure[module].append(page_data)

        return Response({
            'user_role': user.role.name if user.role else 'Superuser',
            'menu': menu_structure
        })

# --- 5E: User Role Assignment/Update API (MISSING VIEW ADDED) ---
class UserRoleUpdateView(APIView):
    """
    PATCH /api/users/<user_id>/role/: To update the role of a specific user.
    """
    permission_classes = [
        IsAuthenticated
    ]
    
    def patch(self, request, user_id):
        # 1. Target User ko fetch karein
        user_to_update = get_object_or_404(User, pk=user_id)
        
        # 2. Check karein ki role_id request data mein hai ya nahi
        role_id = request.data.get('role_id')
        if role_id is None:
            return Response({"error": "role_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. Role object ko fetch karein
            if role_id:
                # Agar role_id diya gaya hai, toh Role object dhundho
                role = Role.objects.get(pk=role_id)
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