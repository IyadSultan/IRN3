# users/admin.py

from django.contrib import admin
from .models import UserProfile, Document, SystemSettings

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'role', 'is_approved')
    list_filter = ('is_approved', 'role')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'issue_date', 'expiry_date')
    list_filter = ('document_type',)

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance of settings
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib import admin
from .models import Role, UserProfile  # Add Role to your imports

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

# Keep your existing UserProfile admin registration