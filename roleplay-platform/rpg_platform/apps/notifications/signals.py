from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from rpg_platform.apps.accounts.models import FriendRequest
from rpg_platform.apps.notifications.models import Notification

User = get_user_model()


@receiver(post_save, sender=FriendRequest)
def create_friend_request_notification(sender, instance, created, **kwargs):
    """
    Create a notification when a new friend request is received
    """
    if created:
        Notification.objects.create(
            user=instance.to_user,
            notification_type='friend_request',
            actor=instance.from_user,
            verb='sent you a friend request',
            action_object_id=instance.id
        )
