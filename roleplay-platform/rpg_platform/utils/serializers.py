from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        """
        Add custom validation logic here
        """
        return super().validate(data)

    def to_representation(self, instance):
        """
        Customize the representation of the instance
        """
        data = super().to_representation(instance)

        # Add common fields
        data["id"] = instance.id

        # Add user-specific fields if available
        if hasattr(instance, "user"):
            data["user"] = {
                "id": instance.user.id,
                "username": instance.user.username,
                "display_name": (
                    instance.user.profile.get_display_name()
                    if hasattr(instance.user, "profile")
                    else instance.user.username
                ),
                "avatar": (
                    instance.user.profile.get_avatar_url()
                    if hasattr(instance.user, "profile")
                    else None
                ),
            }

        return data


class PaginatedSerializer(serializers.Serializer):
    """
    Base serializer for paginated responses
    """

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()
