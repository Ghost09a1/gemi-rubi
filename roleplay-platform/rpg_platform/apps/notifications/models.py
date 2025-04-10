from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

User = get_user_model()


class NotificationCategory(models.Model):
    """
    Categories for notifications to allow for better filtering
    """
    name = models.CharField(_('Category Name'), max_length=50)
    key = models.CharField(_('Category Key'), max_length=50, unique=True)
    description = models.TextField(_('Description'), blank=True)
    icon = models.CharField(_('Font Awesome Icon'), max_length=50, default='bell')
    color = models.CharField(_('Category Color'), max_length=20, default='primary')
    order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Notification Category')
        verbose_name_plural = _('Notification Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_categories(cls):
        """Define default notification categories"""
        defaults = [
            {
                'name': _('System Messages'),
                'key': 'system',
                'description': _('Important announcements and system updates'),
                'icon': 'bell',
                'color': 'primary',
                'order': 0
            },
            {
                'name': _('Messages'),
                'key': 'messages',
                'description': _('Private messages and chat notifications'),
                'icon': 'envelope',
                'color': 'info',
                'order': 1
            },
            {
                'name': _('Friends'),
                'key': 'friends',
                'description': _('Friend requests and friend activity'),
                'icon': 'user-friends',
                'color': 'success',
                'order': 2
            },
            {
                'name': _('Characters'),
                'key': 'characters',
                'description': _('Character comments, likes and mentions'),
                'icon': 'user-circle',
                'color': 'warning',
                'order': 3
            },
            {
                'name': _('Mentions'),
                'key': 'mentions',
                'description': _('When someone mentions you or your characters'),
                'icon': 'at',
                'color': 'danger',
                'order': 4
            },
            {
                'name': _('Moderation'),
                'key': 'moderation',
                'description': _('Moderation actions and reports'),
                'icon': 'shield-alt',
                'color': 'dark',
                'order': 5
            }
        ]

        return defaults

    @classmethod
    def create_defaults(cls):
        """Create default categories if they don't exist"""
        defaults = cls.get_default_categories()

        for default in defaults:
            cls.objects.get_or_create(
                key=default['key'],
                defaults={
                    'name': default['name'],
                    'description': default['description'],
                    'icon': default['icon'],
                    'color': default['color'],
                    'order': default['order']
                }
            )


class NotificationPreference(models.Model):
    """
    User preferences for notifications
    """
    DELIVERY_CHOICES = [
        ('all', _('All Notifications')),
        ('important', _('Important Only')),
        ('none', _('None')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('User')
    )
    category = models.ForeignKey(
        NotificationCategory,
        on_delete=models.CASCADE,
        related_name='user_preferences',
        verbose_name=_('Category')
    )
    in_app = models.CharField(
        _('In-App Notifications'),
        max_length=10,
        choices=DELIVERY_CHOICES,
        default='all'
    )
    email = models.CharField(
        _('Email Notifications'),
        max_length=10,
        choices=DELIVERY_CHOICES,
        default='important'
    )
    push = models.CharField(
        _('Push Notifications'),
        max_length=10,
        choices=DELIVERY_CHOICES,
        default='none'
    )
    sound = models.BooleanField(_('Play Sound'), default=True)

    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"

    @classmethod
    def get_or_create_for_user(cls, user, category=None):
        """Get or create preference for a user and category"""
        # Get all categories
        categories = NotificationCategory.objects.all()

        # If a specific category is requested
        if category:
            # Get or create preference for this category
            preference, created = cls.objects.get_or_create(
                user=user,
                category=category
            )
            return preference

        # Otherwise process all categories
        for cat in categories:
            cls.objects.get_or_create(
                user=user,
                category=cat
            )

        return cls.objects.filter(user=user)


class Notification(models.Model):
    """
    Notification model for user alerts
    """
    NOTIFICATION_TYPES = [
        ('message', _('Message')),
        ('friend_request', _('Friend Request')),
        ('friend_accept', _('Friend Request Accepted')),
        ('character_like', _('Character Like')),
        ('character_rating', _('Character Rating')),
        ('character_comment', _('Character Comment')),
        ('character_mention', _('Character Mention')),
        ('user_mention', _('User Mention')),
        ('system', _('System Notification')),
        ('moderation', _('Moderation Alert')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )
    category = models.ForeignKey(
        NotificationCategory,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Category'),
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_triggered',
        verbose_name=_('Actor'),
        null=True,
        blank=True
    )
    verb = models.CharField(_('Verb'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    url = models.CharField(_('URL'), max_length=255, blank=True)
    image_url = models.CharField(_('Image URL'), max_length=255, blank=True)
    priority = models.CharField(_('Priority'), max_length=10, choices=PRIORITY_LEVELS, default='normal')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    read = models.BooleanField(_('Read'), default=False)
    read_at = models.DateTimeField(_('Read At'), null=True, blank=True)
    is_deleted = models.BooleanField(_('Deleted'), default=False)
    extra_data = models.JSONField(_('Extra Data'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        if self.actor:
            return f"{self.actor.username} {self.verb}"
        return f"System: {self.verb}"

    def save(self, *args, **kwargs):
        """
        Override save to send WebSocket notification on create
        """
        is_new = self.pk is None

        # If category is not set, try to infer from notification_type
        if is_new and not self.category:
            self.set_category_from_type()

        # Save the object
        super().save(*args, **kwargs)

        # Send WebSocket notification for new notifications
        if is_new:
            self.send_notification()

    def set_category_from_type(self):
        """Set the category based on notification type"""
        type_to_category = {
            'message': 'messages',
            'friend_request': 'friends',
            'friend_accept': 'friends',
            'character_like': 'characters',
            'character_rating': 'characters',
            'character_comment': 'characters',
            'character_mention': 'mentions',
            'user_mention': 'mentions',
            'system': 'system',
            'moderation': 'moderation',
        }

        category_key = type_to_category.get(self.notification_type, 'system')

        try:
            self.category = NotificationCategory.objects.get(key=category_key)
        except NotificationCategory.DoesNotExist:
            # If category doesn't exist, try to create defaults
            NotificationCategory.create_defaults()
            try:
                self.category = NotificationCategory.objects.get(key=category_key)
            except NotificationCategory.DoesNotExist:
                pass

    def send_notification(self):
        """
        Send a real-time notification via WebSockets.
        Also check user preferences to see if notification should be sent.
        """
        # Check user preferences for this notification
        if not self.should_send_notification():
            return

        channel_layer = get_channel_layer()

        # Prepare notification data
        notification_data = {
            'id': self.pk,
            'type': self.notification_type,
            'category': {
                'id': self.category.id if self.category else None,
                'name': self.category.name if self.category else None,
                'key': self.category.key if self.category else None,
                'icon': self.category.icon if self.category else 'bell',
                'color': self.category.color if self.category else 'primary',
            },
            'actor': self.actor.username if self.actor else None,
            'actor_display_name': self.actor.profile.get_display_name() if self.actor and hasattr(self.actor, 'profile') else None,
            'actor_avatar': self.actor.profile.get_avatar_url() if self.actor and hasattr(self.actor, 'profile') else None,
            'verb': self.verb,
            'description': self.description,
            'action_object_id': self.action_object_id,
            'target_id': self.target_id,
            'url': self.url,
            'image_url': self.image_url,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'read': self.read,
            'extra_data': self.extra_data
        }

        # Send to the user's notification group
        async_to_sync(channel_layer.group_send)(
            f'notifications_{self.user.id}',
            {
                'type': 'new_notification',
                'notification': notification_data
            }
        )

    def should_send_notification(self):
        """Check if notification should be sent based on user preferences"""
        if not self.category:
            return True

        try:
            # Get user preference for this category
            preference = NotificationPreference.objects.get(
                user=self.user,
                category=self.category
            )

            # Check in-app notification setting
            if preference.in_app == 'none':
                return False
            elif preference.in_app == 'important' and self.priority != 'high':
                return False

            return True

        except NotificationPreference.DoesNotExist:
            # If no preference exists, create default and return True
            NotificationPreference.get_or_create_for_user(self.user, self.category)
            return True

    def mark_as_read(self):
        """Mark the notification as read and send WebSocket update"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save(update_fields=['read', 'read_at'])

            # Send WebSocket update
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{self.user.id}',
                {
                    'type': 'notification_read',
                    'notification_id': self.pk
                }
            )

    def delete_notification(self):
        """Mark notification as deleted (soft delete)"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

        # Send WebSocket update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{self.user.id}',
            {
                'type': 'notification_deleted',
                'notification_id': self.pk
            }
        )

    @classmethod
    def mark_all_as_read(cls, user, category=None):
        """Mark all unread notifications for a user as read"""
        from django.utils import timezone

        now = timezone.now()

        # Base query - unread, not deleted notifications for this user
        query = cls.objects.filter(user=user, read=False, is_deleted=False)

        # Filter by category if provided
        if category:
            query = query.filter(category=category)

        # Update all notifications
        query.update(read=True, read_at=now)

        # Get the notification IDs to send WebSocket updates
        notification_ids = list(query.values_list('id', flat=True))

        # Send WebSocket updates
        if notification_ids:
            channel_layer = get_channel_layer()

            # Send a bulk update message instead of individual messages
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'notifications_marked_read',
                    'notification_ids': notification_ids
                }
            )

    @classmethod
    def get_unread_count(cls, user, category=None):
        """Get the count of unread notifications for a user"""
        query = cls.objects.filter(user=user, read=False, is_deleted=False)

        if category:
            query = query.filter(category=category)

        return query.count()

    @classmethod
    def create_notification(cls, user, notification_type, verb, **kwargs):
        """
        Factory method to create a notification with proper defaults

        Args:
            user (User): The user to notify
            notification_type (str): Type of notification
            verb (str): Action verb
            **kwargs: Additional notification attributes

        Returns:
            Notification: The created notification instance
        """
        # Determine priority based on notification type if not provided
        if 'priority' not in kwargs:
            priority_map = {
                'friend_request': 'high',
                'message': 'high',
                'moderation': 'high',
                'user_mention': 'high',
                'character_mention': 'normal',
                'character_comment': 'normal',
                'character_rating': 'normal',
                'friend_accept': 'normal',
                'character_like': 'low',
                'system': 'normal',
            }
            kwargs['priority'] = priority_map.get(notification_type, 'normal')

        # Generate a URL if not provided
        if 'url' not in kwargs:
            url = ''

            # Target ID from kwargs
            target_id = kwargs.get('target_id')

            # Map of notification types to URL patterns
            url_patterns = {
                'message': '/messages/room/{target_id}/',
                'friend_request': '/accounts/friends/requests/',
                'friend_accept': '/accounts/friends/',
                'character_like': '/characters/{target_id}/',
                'character_rating': '/characters/{target_id}/',
                'character_comment': '/characters/{target_id}/',
                'character_mention': '/characters/{target_id}/',
                'user_mention': '/accounts/profile/{actor_username}/',
                'moderation': '/moderation/',
                'system': '/',
            }

            # Get URL pattern for this notification type
            pattern = url_patterns.get(notification_type, '')

            # Format the URL with the target_id if present
            if pattern and target_id:
                url = pattern.format(target_id=target_id)

            # Special case for user mention
            if notification_type == 'user_mention' and 'actor' in kwargs:
                actor = kwargs['actor']
                if actor and hasattr(actor, 'username'):
                    url = f'/accounts/profile/{actor.username}/'

            kwargs['url'] = url

        # Create the notification
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            verb=verb,
            **kwargs
        )
