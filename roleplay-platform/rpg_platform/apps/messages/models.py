from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import json

from rpg_platform.apps.characters.models import Character

User = get_user_model()


class ChatRoom(models.Model):
    """
    Chat room model for private conversations between users
    """
    ROOM_TYPES = [
        ('private', _('Private')),
        ('group', _('Group')),
    ]

    name = models.CharField(_('Room Name'), max_length=100, blank=True)
    room_type = models.CharField(_('Room Type'), max_length=10, choices=ROOM_TYPES, default='private')
    participants = models.ManyToManyField(
        User,
        related_name='chat_rooms',
        verbose_name=_('Participants')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Active'), default=True)
    last_message_time = models.DateTimeField(_('Last Message Time'), null=True, blank=True)

    # New fields for roleplay features
    scene_description = models.TextField(_('Scene Description'), blank=True,
                                         help_text=_('Setting and atmosphere for the current scene'))
    scene_background_color = models.CharField(_('Scene Background Color'), max_length=20, blank=True, default='')
    scene_image_url = models.URLField(_('Scene Background Image'), blank=True)
    scene_music_url = models.URLField(_('Scene Background Music'), blank=True)
    scene_intensity = models.PositiveSmallIntegerField(_('Scene Intensity'), default=1,
                                                      help_text=_('Intensity level from 1-5'))
    # Scene status for pause/break functionality
    SCENE_STATUS_CHOICES = [
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('ooc', _('Out of Character')),
        ('break', _('Taking a Break')),
    ]
    scene_status = models.CharField(_('Scene Status'), max_length=20, choices=SCENE_STATUS_CHOICES, default='active')

    # Immersion settings
    typing_effect_enabled = models.BooleanField(_('Enable Typing Effect'), default=False)
    message_timing_enabled = models.BooleanField(_('Enable Message Timing'), default=False)

    # Consent and boundaries
    has_established_boundaries = models.BooleanField(_('Has Established Boundaries'), default=False)

    class Meta:
        verbose_name = _('Chat Room')
        verbose_name_plural = _('Chat Rooms')
        ordering = ['-updated_at']

    def __str__(self):
        if self.name:
            return self.name
        return f"Chat {self.id} ({', '.join([p.username for p in self.participants.all()[:3]])})"

    def get_absolute_url(self):
        return reverse('messages:room_detail', kwargs={'pk': self.pk})

    def get_last_message(self):
        """Return the last message in the chat room"""
        return self.messages.order_by('-created_at').first()

    def mark_as_read(self, user):
        """Mark all unread messages in this room as read for the user"""
        self.messages.filter(receiver=user, read=False).update(read=True)

    def update_scene(self, description=None, background_color=None, image_url=None, music_url=None, intensity=None):
        """Update scene settings"""
        update_fields = []

        if description is not None:
            self.scene_description = description
            update_fields.append('scene_description')

        if background_color is not None:
            self.scene_background_color = background_color
            update_fields.append('scene_background_color')

        if image_url is not None:
            self.scene_image_url = image_url
            update_fields.append('scene_image_url')

        if music_url is not None:
            self.scene_music_url = music_url
            update_fields.append('scene_music_url')

        if intensity is not None and 1 <= intensity <= 5:
            self.scene_intensity = intensity
            update_fields.append('scene_intensity')

        if update_fields:
            self.save(update_fields=update_fields)

    def update_scene_status(self, status):
        """Update the scene status (active, paused, etc.)"""
        if status in dict(self.SCENE_STATUS_CHOICES):
            self.scene_status = status
            self.save(update_fields=['scene_status'])
            return True
        return False


class ChatMessage(models.Model):
    """
    Individual chat message within a chat room
    """
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Chat Room')
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Sender')
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('Receiver')
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        related_name='chat_messages',
        verbose_name=_('Character'),
        null=True,
        blank=True
    )
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    read = models.BooleanField(_('Read'), default=False)

    # New fields for message features
    is_system_message = models.BooleanField(_('System Message'), default=False)
    is_ooc = models.BooleanField(_('Out of Character'), default=False)
    message_type = models.CharField(_('Message Type'), max_length=20, default='regular',
                              choices=[
                                  ('regular', _('Regular')),
                                  ('whisper', _('Whisper')),
                                  ('action', _('Action')),
                                  ('thought', _('Thought')),
                                  ('narration', _('Narration')),
                              ])
    # For timed messages
    delay_seconds = models.PositiveSmallIntegerField(_('Delay Seconds'), default=0)

    # For typing effect
    typing_duration_ms = models.PositiveIntegerField(_('Typing Duration (ms)'), default=0)

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['created_at']

    def __str__(self):
        if self.character:
            return f"{self.character.name}: {self.message[:30]}..."
        return f"{self.sender.username}: {self.message[:30]}..."

    def mark_as_read(self):
        """Mark the message as read"""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])


class DiceRoll(models.Model):
    """
    Stores dice roll history for tabletop roleplay
    """
    DICE_TYPES = [
        ('d4', 'D4'),
        ('d6', 'D6'),
        ('d8', 'D8'),
        ('d10', 'D10'),
        ('d12', 'D12'),
        ('d20', 'D20'),
        ('d100', 'D100'),
        ('custom', 'Custom'),
    ]

    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='dice_rolls',
        verbose_name=_('Chat Room')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dice_rolls',
        verbose_name=_('User')
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        related_name='dice_rolls',
        verbose_name=_('Character'),
        null=True,
        blank=True
    )
    formula = models.CharField(_('Dice Formula'), max_length=100,
                              help_text=_('Format like "2d6+3" or "d20"'))
    result = models.JSONField(_('Result'),
                             help_text=_('JSON containing the dice roll results'))
    total = models.IntegerField(_('Total Result'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_private = models.BooleanField(_('Private Roll'), default=False,
                                    help_text=_('If true, only visible to GM and roller'))

    class Meta:
        verbose_name = _('Dice Roll')
        verbose_name_plural = _('Dice Rolls')
        ordering = ['-created_at']

    def __str__(self):
        character_name = self.character.name if self.character else self.user.username
        return f"{character_name}: {self.formula} = {self.total}"

    def get_individual_results(self):
        """Returns the individual dice results as a list"""
        if isinstance(self.result, str):
            return json.loads(self.result).get('rolls', [])
        return self.result.get('rolls', [])

    def get_roll_details(self):
        """Returns a dictionary with roll details for display"""
        if isinstance(self.result, str):
            result_data = json.loads(self.result)
        else:
            result_data = self.result

        return {
            'rolls': result_data.get('rolls', []),
            'modifiers': result_data.get('modifiers', 0),
            'formula': self.formula,
            'total': self.total
        }


class SceneBoundary(models.Model):
    """
    Stores content boundaries and consent preferences for a chat room
    """
    chat_room = models.OneToOneField(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='boundaries',
        verbose_name=_('Chat Room')
    )

    # Consent boundaries using JSON field for flexibility
    boundaries = models.JSONField(
        _('Boundaries'),
        default=dict,
        help_text=_('Content boundaries and consent preferences')
    )

    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    last_reviewed = models.DateTimeField(_('Last Reviewed'), null=True, blank=True)
    all_participants_agreed = models.BooleanField(_('All Participants Agreed'), default=False)

    class Meta:
        verbose_name = _('Scene Boundary')
        verbose_name_plural = _('Scene Boundaries')

    def __str__(self):
        return f"Boundaries for {self.chat_room}"

    def get_allowed_content(self):
        """Returns a list of allowed content categories"""
        return self.boundaries.get('allowed', [])

    def get_soft_limits(self):
        """Returns a list of soft limits (proceed with caution)"""
        return self.boundaries.get('soft_limits', [])

    def get_hard_limits(self):
        """Returns a list of hard limits (absolutely not)"""
        return self.boundaries.get('hard_limits', [])

    def is_content_allowed(self, content_type):
        """Check if a specific content type is allowed"""
        if content_type in self.get_hard_limits():
            return False
        return content_type in self.get_allowed_content()


class QuickResponse(models.Model):
    """
    Stores quick responses for writing assistance
    """
    RESPONSE_TYPES = [
        ('action', _('Action')),
        ('expression', _('Expression')),
        ('emotion', _('Emotion')),
        ('pose', _('Pose')),
        ('scene', _('Scene Description')),
        ('location', _('Location Description')),
        ('custom', _('Custom')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quick_responses',
        verbose_name=_('User')
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        related_name='quick_responses',
        verbose_name=_('Character'),
        null=True,
        blank=True,
        help_text=_('If set, this response is specific to this character')
    )
    response_type = models.CharField(_('Response Type'), max_length=20, choices=RESPONSE_TYPES)
    name = models.CharField(_('Name'), max_length=50, help_text=_('Short name for this response'))
    content = models.TextField(_('Content'), help_text=_('The actual text of this quick response'))

    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    use_count = models.PositiveIntegerField(_('Use Count'), default=0)

    class Meta:
        verbose_name = _('Quick Response')
        verbose_name_plural = _('Quick Responses')
        ordering = ['-use_count', 'name']

    def __str__(self):
        if self.character:
            return f"{self.character.name} - {self.name}"
        return f"{self.user.username} - {self.name}"

    def increment_usage(self):
        """Increment the usage counter"""
        self.use_count += 1
        self.save(update_fields=['use_count'])


class SceneSetting(models.Model):
    """
    Reusable scene settings templates
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scene_settings',
        verbose_name=_('User')
    )
    title = models.CharField(_('Title'), max_length=100)
    description = models.TextField(_('Description'))
    background_color = models.CharField(_('Background Color'), max_length=20, blank=True)
    image_url = models.URLField(_('Background Image URL'), blank=True)
    music_url = models.URLField(_('Background Music URL'), blank=True)
    is_public = models.BooleanField(_('Public'), default=False,
                                  help_text=_('If true, other users can use this scene setting'))

    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    use_count = models.PositiveIntegerField(_('Use Count'), default=0)

    class Meta:
        verbose_name = _('Scene Setting')
        verbose_name_plural = _('Scene Settings')
        ordering = ['-use_count', 'title']

    def __str__(self):
        return f"{self.title} by {self.user.username}"

    def apply_to_room(self, chat_room):
        """Apply this scene setting to a chat room"""
        chat_room.scene_description = self.description
        chat_room.scene_background_color = self.background_color
        chat_room.scene_image_url = self.image_url
        chat_room.scene_music_url = self.music_url
        chat_room.save(update_fields=[
            'scene_description',
            'scene_background_color',
            'scene_image_url',
            'scene_music_url'
        ])

        # Increment usage counter
        self.use_count += 1
        self.save(update_fields=['use_count'])

        return True


class PrivateNote(models.Model):
    """
    Personal notes visible only to the author
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='private_notes',
        verbose_name=_('User')
    )
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='private_notes',
        verbose_name=_('Chat Room')
    )
    title = models.CharField(_('Title'), max_length=100)
    content = models.TextField(_('Content'))

    # Metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Private Note')
        verbose_name_plural = _('Private Notes')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"
