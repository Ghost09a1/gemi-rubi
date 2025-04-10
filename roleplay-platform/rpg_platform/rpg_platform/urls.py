from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from rpg_platform.apps.messages.views import ChatMessageCreateView  # ✅


app_name = 'messages'

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('create/', ChatMessageCreateView.as_view(), name='chatmessage_create'),

    # Include dashboard app
    path('dashboard/', include('rpg_platform.apps.dashboard.urls')),

    # Account management
    path('accounts/', include('rpg_platform.apps.accounts.urls')),

    # Feature-specific URLs
    path('characters/', include('rpg_platform.apps.characters.urls')),
    path('messages/', include('rpg_platform.apps.messages.urls')),
    path('notifications/', include('rpg_platform.apps.notifications.urls')),
    path('moderation/', include('rpg_platform.apps.moderation.urls')),
    path('recommendations/', include('rpg_platform.apps.recommendations.urls')),

    # Redirect authenticated users to dashboard, anonymous users to landing
    path('', RedirectView.as_view(url='/dashboard/'), name='home'),

    # Landing page for anonymous users
    path('landing/', include('rpg_platform.apps.landing.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
