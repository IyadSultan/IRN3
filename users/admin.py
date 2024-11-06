# users/admin.py

from django.contrib import admin
from django.contrib.auth.models import Group
from .models import (
    UserProfile,
    Document,
    Role,
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'role', 'is_approved')
    list_filter = ('is_approved', 'role')
    actions = ['approve_users']
    filter_horizontal = ('groups',)

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'issue_date', 'expiry_date')
    list_filter = ('document_type',)
    search_fields = ('user__username', 'user__email')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)



