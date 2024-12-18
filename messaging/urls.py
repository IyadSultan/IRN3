from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('sent/archive/', views.archive_sent_messages, name='archive_sent_messages'),
    path('compose/', views.compose_message, name='compose_message'),
    path('message/<int:message_id>/', views.view_message, name='view_message'),
    path('reply/<int:message_id>/', views.reply, name='reply'),
    path('reply-all/<int:message_id>/', views.reply_all, name='reply_all'),
    path('forward/<int:message_id>/', views.forward, name='forward'),
    path('search/', views.search_messages, name='search_messages'),
    path('archive/', views.archive_message, name='archive_message'),
    path('delete/', views.delete_messages, name='delete_messages'),
    path('archived/', views.archived_messages, name='archived_messages'),
    path('threads/', views.threads_inbox, name='threads_inbox'),
    path('user-autocomplete/', views.user_autocomplete, name='user_autocomplete'),
    path('submission-autocomplete/', views.submission_autocomplete, name='submission_autocomplete'),
    path('dismiss-notification/', views.dismiss_notification, name='dismiss_notification'),
    path('update-read-status/', views.update_read_status, name='update_read_status'),
]