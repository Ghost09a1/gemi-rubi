from django.db.models.signals import post_save
from django.dispatch import receiver

from rpg_platform.apps.messages.models import ChatMessage, ChatRoom
from rpg_platform.apps.notifications.models import Notification
from rpg_platform.apps.accounts.models import UserActivity


@receiver(post_save, sender=ChatMessage)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Create a notification when a new chat message is received
    """
    if created and instance.receiver != instance.sender:
        # Don't notify for self-messages
        Notification.objects.create(
            user=instance.receiver,
            notification_type='message',
            actor=instance.sender,
            target_id=instance.chat_room.id,
            verb='sent you a message',
            action_object_id=instance.id
        )


@receiver(post_save, sender=ChatMessage)
def update_chatroom_last_message_time(sender, instance, created, **kwargs):
    """
    Update the last_message_time field in the ChatRoom model when a new message is created
    """
    if created:
        chat_room = instance.chat_room
        chat_room.last_message_time = instance.created_at
        chat_room.save(update_fields=['last_message_time'])


@receiver(post_save, sender=ChatRoom)
def initialize_chatroom_last_message_time(sender, instance, created, **kwargs):
    """
    Initialize the last_message_time field to the created_at time when a ChatRoom is created
    """
    if created and not instance.last_message_time:
        instance.last_message_time = instance.created_at
        instance.save(update_fields=['last_message_time'])


@receiver(post_save, sender=ChatRoom)
def log_chatroom_creation(sender, instance, created, **kwargs):
    """
    Log when a new chat room is created
    """
    if created:
        # Get first participant as creator (since there's no explicit creator field)
        try:
            creator = instance.participants.first()
            if not creator:
                return  # No participants yet

            # Get list of participants (excluding the creator)
            participants = [user.username for user in instance.participants.all()
                            if user != creator]

            # Log activity for the creator
            UserActivity.log_activity(
                user=creator,
                activity_type='message',
                content_type='chatroom',
                object_id=instance.id,
                extra_data={
                    'participants': participants,
                    'room_name': instance.name or '',
                    'room_type': instance.room_type
                }
            )
        except Exception as e:
            # Log error but don't interrupt the process
            print(f"Error logging chat room creation: {e}")
