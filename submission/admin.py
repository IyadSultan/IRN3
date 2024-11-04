# submission/admin.py

from django.contrib import admin
from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('temporary_id', 'title', 'primary_investigator', 'irb_number', 'status', 'date_created', 'is_locked')
    search_fields = ('title', 'primary_investigator__username', 'irb_number')
    list_filter = ('status', 'study_type', 'is_locked')
    ordering = ('-date_created',)
    fields = ('title', 'study_type', 'primary_investigator', 'irb_number', 'status', 'date_created', 'last_modified', 'is_locked')
    readonly_fields = ('date_created', 'last_modified')

from django.contrib import admin
from .models import CoInvestigator

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

from django.contrib import admin
from .models import SystemSettings  # Add this import

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance of settings
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False