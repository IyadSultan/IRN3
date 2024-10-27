# messaging/urls.py
from django.urls import path
from . import views
from .views import UserAutocomplete

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('view/<int:message_id>/', views.view_message, name='view_message'),
    path('archive/', views.archive_messages, name='archive_messages'),
    path('delete/', views.delete_messages, name='delete_messages'),
    path('compose/', views.compose_message, name='compose_message'),
    path('reply/<int:pk>/', views.reply_message, name='reply_message'),
    path('search/', views.search_messages, name='search_messages'),
    path('user-autocomplete/', UserAutocomplete.as_view(), name='user-autocomplete'),
    path('archived/', views.archived_messages, name='archived_messages'),
]
