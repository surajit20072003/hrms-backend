# users/permissions.py (FIXED)

from rest_framework import permissions

class HasPageAccess(permissions.BasePermission):
    """
    Custom permission to check if the user's role has the required Page access,
    by reading the 'permission_required' attribute from the View.
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        # 0. Quick check for Superuser
        if user.is_superuser:
            return True

        # 1. Get the required URL key from the View class
        required_page_key = getattr(view, 'permission_required', None)
        
        if not required_page_key:
            # Agar view mein permission_required define nahi kiya gaya, toh access deny karein (security default)
            return False 

        # 2. Basic check: User must be logged in and have a role assigned
        if not user.is_authenticated or not user.role:
            return False
            
        # 3. Check if the required page exists in the user's role pages
        return user.role.pages.filter(
            url_name=required_page_key
        ).exists()