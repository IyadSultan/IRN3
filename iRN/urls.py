# user_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url='/users/login/', permanent=False), name='login_redirect'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('submission/', include('submission.urls', namespace='submission')),
    path('review/', include('review.urls', namespace='review')),
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
