from rest_framework import viewsets, filters
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rpg_platform.utils.api_views import BaseAPIView
from rpg_platform.utils.serializers import BaseModelSerializer
from rpg_platform.utils.permissions import IsOwnerOrReadOnly
from .models import Notification, NotificationCategory


class NotificationSerializer(BaseModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "verb",
            "description",
            "action_object_id",
            "target_id",
            "url",
            "image_url",
            "priority",
            "created_at",
            "read",
            "read_at",
            "actor",
            "category",
        ]
        read_only_fields = ["created_at", "read_at"]


class NotificationCategorySerializer(BaseModelSerializer):
    class Meta:
        model = NotificationCategory
        fields = ["id", "key", "name", "description", "icon", "color", "order"]
        read_only_fields = ["key", "order"]


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for notifications
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["notification_type", "category", "read"]
    search_fields = ["description", "verb"]
    ordering_fields = ["created_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Return notifications for the current user
        """
        return self.queryset.filter(
            user=self.request.user, is_deleted=False
        ).select_related("actor", "category")


    def perform_create(self, serializer):
        """
        Set the user when creating a notification
        """
        serializer.save(user=self.request.user)


class NotificationCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for notification categories
    """

    serializer_class = NotificationCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    queryset = NotificationCategory.objects.all().order_by("order", "name")
