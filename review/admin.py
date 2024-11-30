# review/admin.py

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from submission.models import Submission
from .models import ReviewRequest, Review, FormResponse

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'reviewer', 'submission', 'date_submitted']
    search_fields = ['reviewer__username', 'submission__title']
    list_filter = ['date_submitted']

@admin.register(ReviewRequest)
class ReviewRequestAdmin(admin.ModelAdmin):
    list_display = ['submission', 'requested_by', 'requested_to', 'deadline', 'status']
    search_fields = ['submission__title', 'requested_by__username', 'requested_to__username']
    list_filter = ['status', 'deadline']

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'form', 'date_submitted']
    search_fields = ['review__reviewer__username', 'form__name']
    list_filter = ['date_submitted']