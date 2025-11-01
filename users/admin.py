from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Education, Experience


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'is_active', 'is_staff')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('email', 'role', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(Experience)