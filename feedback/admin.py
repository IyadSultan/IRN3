# feedback/admin.py

from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['subject', 'category', 'user', 'created_at', 'is_resolved']
    list_filter = ['category', 'is_resolved', 'created_at']
    search_fields = ['subject', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_resolved.short_description = "Mark selected feedback as resolved"
    
    actions = ['mark_resolved']