from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="RoleplayHub API",
        default_version="v1",
        description="API documentation for RoleplayHub platform",
        terms_of_service="https://www.roleplayhub.com/tos/",
        contact=openapi.Contact(email="support@roleplayhub.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Documentation
    path(
        "api/docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    # Include dashboard app
    path(
        "dashboard/", include("rpg_platform.apps.dashboard.urls", namespace="dashboard")
    ),
    # Account management
    path("accounts/", include("rpg_platform.apps.accounts.urls")),
    # Feature-specific URLs
    path("characters/", include("rpg_platform.apps.characters.urls")),
    path("messages/", include("rpg_platform.apps.messages.urls", namespace="messages")),
    path("notifications/", include("rpg_platform.apps.notifications.urls")),
    path("moderation/", include("rpg_platform.apps.moderation.urls")),
    path("recommendations/", include("rpg_platform.apps.recommendations.urls")),
    # Core app URLs
    path("core/", include("rpg_platform.apps.core.urls")),
    # Redirect authenticated users to dashboard, anonymous users to landing
    path("", RedirectView.as_view(url="/dashboard/"), name="home"),
    # Landing page for anonymous users
    path("landing/", include("rpg_platform.apps.landing.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
