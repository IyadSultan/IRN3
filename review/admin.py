# review/admin.py

from django.contrib import admin
from .models import ReviewRequest, Review, FormResponse

@admin.register(ReviewRequest)
class ReviewRequestAdmin(admin.ModelAdmin):
    list_display = ('submission', 'requested_by', 'requested_to', 'status', 'deadline')
    list_filter = ('status',)
    search_fields = ('submission__title', 'requested_by__username', 'requested_to__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer', 'date_submitted')
    search_fields = ('submission__title', 'reviewer__username')

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'review', 'date_submitted')
    search_fields = ('form__title', 'review__reviewer__username')
