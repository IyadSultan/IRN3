# messaging/urls.py
from django.urls import path
from . import views
from .views import UserAutocomplete

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('view/<int:message_id>/', views.view_message, name='view_message'),
    path('compose/', views.compose_message, name='compose_message'),
    path('reply/<int:message_id>/', views.reply, name='reply'),
    path('reply-all/<int:message_id>/', views.reply_all, name='reply_all'),
    path('forward/<int:message_id>/', views.forward, name='forward'),
    # path('archive/<int:message_id>/', views.archive_message, name='archive_message'),
    path('archive/', views.archive_message, name='archive_message'),
    path('search/', views.search_messages, name='search_messages'),
    path('user-autocomplete/', UserAutocomplete.as_view(), name='user-autocomplete'),
    path('archived/', views.archived_messages, name='archived_messages'),
    path('threads/', views.threads_inbox, name='threads_inbox'),
]
