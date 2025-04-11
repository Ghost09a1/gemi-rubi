from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rpg_platform.utils.routers import VersionedRouter
from . import views
from .api import NotificationViewSet, NotificationCategoryViewSet

# Create a versioned router
router = VersionedRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(
    r"categories", NotificationCategoryViewSet, basename="notification-category"
)

urlpatterns = [
    # API URLs
    path("api/", include(router.urls)),
    # Template-based views
    path("", views.NotificationCenterView.as_view(), name="notification_center"),
    path("list/", views.NotificationListView.as_view(), name="notification_list"),
    path(
        "preferences/",
        views.NotificationPreferenceView.as_view(),
        name="notification_preferences",
    ),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path("mark-read/<int:pk>/", views.mark_read, name="mark_read"),
    path("delete/<int:pk>/", views.delete_notification, name="delete_notification"),
]
