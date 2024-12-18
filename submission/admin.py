# submission/admin.py

from django.contrib import admin
from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
    StatusChoice,
    SystemSettings,
)
from .models import PermissionChangeLog



@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('temporary_id', 'title', 'primary_investigator', 'khcc_number', 'status', 'date_created', 'is_locked')
    search_fields = ('title', 'primary_investigator__username', 'khcc_number')
    list_filter = ('status', 'study_type', 'is_locked')
    ordering = ('-date_created',)
    fields = ('title', 'study_type', 'primary_investigator', 'khcc_number', 'status', 'date_created', 'last_modified', 'is_locked')
    readonly_fields = ('date_created', 'last_modified')

@admin.register(CoInvestigator)
class CoInvestigatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'submission', 'get_roles', 'can_edit', 'can_submit', 'can_view_communications']
    list_filter = ['can_edit', 'can_submit', 'can_view_communications']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    
    def get_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])
    get_roles.short_description = 'Roles'

@admin.register(ResearchAssistant)
class ResearchAssistantAdmin(admin.ModelAdmin):
    list_display = ('user', 'submission', 'can_submit', 'can_edit')
    list_filter = ('can_submit', 'can_edit', 'can_view_communications')
    search_fields = ('user__username', 'submission__title')

@admin.register(FormDataEntry)
class FormDataEntryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'form', 'field_name', 'date_saved', 'version')
    list_filter = ('form', 'version')
    search_fields = ('submission__title', 'field_name', 'value')
    readonly_fields = ('date_saved',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'filename', 'uploaded_by', 'uploaded_at')
    search_fields = ('submission__title', 'file', 'uploaded_by__username')
    list_filter = ('uploaded_at',)

@admin.register(VersionHistory)
class VersionHistoryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'version', 'status', 'date')
    search_fields = ('submission__title',)
    list_filter = ('status', 'date')

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(StatusChoice)
class StatusChoiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'label', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('code', 'label')
    ordering = ('order',)




@admin.register(PermissionChangeLog)
class PermissionChangeLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'permission_type', 'new_value', 'changed_by', 'change_date')
    list_filter = ('role', 'permission_type', 'change_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 
                    'changed_by__username', 'changed_by__first_name', 'changed_by__last_name')
    date_hierarchy = 'change_date'