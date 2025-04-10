from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import gettext_lazy as _

from rpg_platform.apps.accounts.models import Profile, Friendship, FriendRequest, UserActivity
from rpg_platform.apps.characters.models import Character, CharacterComment, CharacterRating
from rpg_platform.apps.messages.models import ChatRoom

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for newly created users"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=FriendRequest)
def notify_friend_request(sender, instance, created, **kwargs):
    """Notify user of new friend request"""
    if created:
        from rpg_platform.apps.notifications.models import Notification

        # Create notification for the recipient
        Notification.objects.create(
            user=instance.to_user,
            notification_type='friend_request',
            actor=instance.from_user,
            verb=_('sent you a friend request'),
            action_object_id=instance.pk
        )

@receiver(post_save, sender=Friendship)
def log_friendship(sender, instance, created, **kwargs):
    """Log when users become friends"""
    if created:
        UserActivity.log_activity(
            user=instance.user,
            activity_type='friendship',
            object_id=instance.friend.id,
            extra_data={
                'friend_username': instance.friend.username,
                'friend_id': instance.friend.id
            }
        )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log when a user logs in"""
    UserActivity.log_activity(
        user=user,
        activity_type='login',
        extra_data={
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        },
        public=False  # Login activities are private
    )

@receiver(post_save, sender=Character)
def log_character_activity(sender, instance, created, **kwargs):
    """Log character creation/updates"""
    if created:
        UserActivity.log_activity(
            user=instance.user,
            activity_type='character_create',
            content_type='character',
            object_id=instance.id,
            extra_data={
                'character_name': instance.name,
                'character_gender': instance.gender,
                'character_species': instance.species
            }
        )
    else:
        UserActivity.log_activity(
            user=instance.user,
            activity_type='character_update',
            content_type='character',
            object_id=instance.id,
            extra_data={
                'character_name': instance.name
            }
        )

@receiver(post_delete, sender=Character)
def log_character_deletion(sender, instance, **kwargs):
    """Log character deletion"""
    UserActivity.log_activity(
        user=instance.user,
        activity_type='character_delete',
        content_type='character',
        extra_data={
            'character_name': instance.name
        }
    )

@receiver(post_save, sender=CharacterComment)
def log_character_comment(sender, instance, created, **kwargs):
    """Log when a user comments on a character"""
    if created:  # Only log new comments
        UserActivity.log_activity(
            user=instance.author,
            activity_type='comment',
            content_type='character',
            object_id=instance.character.id,
            extra_data={
                'character_name': instance.character.name,
                'character_owner': instance.character.user.username,
                'comment_snippet': instance.content[:100] + ('...' if len(instance.content) > 100 else '')
            }
        )

@receiver(post_save, sender=CharacterRating)
def log_character_rating(sender, instance, created, **kwargs):
    """Log when a user rates a character"""
    if created:  # Only log new ratings
        UserActivity.log_activity(
            user=instance.user,
            activity_type='rating',
            content_type='character',
            object_id=instance.character.id,
            extra_data={
                'character_name': instance.character.name,
                'character_owner': instance.character.user.username,
                'rating': instance.rating
            }
        )

@receiver(post_save, sender=ChatRoom)
def log_new_chat(sender, instance, created, **kwargs):
    """Log when a user starts a new chat"""
    if created:
        # Get the user who created the chat (the first participant in many cases)
        first_user = instance.participants.first()
        if first_user:
            # Get other participants
            other_participants = list(instance.participants.exclude(id=first_user.id).values_list('username', flat=True))

            UserActivity.log_activity(
                user=first_user,
                activity_type='message',
                object_id=instance.id,
                participants=other_participants,
                room_name=instance.name
            )
