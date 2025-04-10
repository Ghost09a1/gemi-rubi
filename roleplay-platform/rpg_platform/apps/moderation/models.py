from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Report(models.Model):
    """
    Report model for users to report content violations
    """
    REPORT_TYPES = [
        ('spam', _('Spam')),
        ('inappropriate', _('Inappropriate Content')),
        ('harassment', _('Harassment')),
        ('other', _('Other')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('investigating', _('Under Investigation')),
        ('resolved', _('Resolved')),
        ('rejected', _('Rejected')),
    ]

    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reports_filed',
        verbose_name=_('Reporter'),
        null=True
    )

    # Generic foreign key to the reported content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    report_type = models.CharField(
        _('Report Type'),
        max_length=20,
        choices=REPORT_TYPES
    )
    description = models.TextField(_('Description'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    # For moderator assignment and resolution
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_reports',
        verbose_name=_('Assigned Moderator'),
        null=True,
        blank=True
    )
    resolution_note = models.TextField(_('Resolution Note'), blank=True)
    resolved_at = models.DateTimeField(_('Resolved At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} by {self.reporter} - {self.get_report_type_display()}"


class ModeratorAction(models.Model):
    """
    Record of actions taken by moderators
    """
    ACTION_TYPES = [
        ('warn', _('Warning')),
        ('suspend', _('Suspension')),
        ('ban', _('Ban')),
        ('delete', _('Content Deletion')),
        ('other', _('Other Action')),
    ]

    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='moderation_actions',
        verbose_name=_('Moderator'),
        null=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_mod_actions',
        verbose_name=_('User')
    )
    action_type = models.CharField(
        _('Action Type'),
        max_length=20,
        choices=ACTION_TYPES
    )
    reason = models.TextField(_('Reason'))

    # Generic foreign key to the related content (if applicable)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # For suspensions and bans
    duration_days = models.PositiveIntegerField(
        _('Duration (Days)'),
        null=True,
        blank=True,
        help_text=_('Leave empty for permanent')
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expires At'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    # Related report if this action was taken in response to a report
    report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        related_name='actions',
        verbose_name=_('Related Report'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Moderator Action')
        verbose_name_plural = _('Moderator Actions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_type_display()} for {self.user.username} by {self.moderator.username if self.moderator else 'System'}"


class ModerationLog(models.Model):
    """
    Log of all moderation actions for auditing
    """
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='moderation_logs',
        verbose_name=_('Actor'),
        null=True
    )
    action = models.TextField(_('Action'))
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)

    # Generic foreign key to the related content
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    additional_data = models.JSONField(_('Additional Data'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Moderation Log')
        verbose_name_plural = _('Moderation Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor.username if self.actor else 'System'}: {self.action} at {self.created_at}"


class ModeratorApplication(models.Model):
    """
    Application to become a moderator
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='moderator_applications',
        verbose_name=_('User')
    )
    reason = models.TextField(_('Reason for Application'))
    experience = models.TextField(_('Moderation Experience'))
    availability = models.TextField(_('Availability'), help_text=_('Hours per week you can dedicate'))

    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reviewed_applications',
        verbose_name=_('Reviewer'),
        null=True,
        blank=True
    )
    reviewer_notes = models.TextField(_('Reviewer Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Moderator Application')
        verbose_name_plural = _('Moderator Applications')
        ordering = ['-created_at']

    def __str__(self):
        return f"Application from {self.user.username} - {self.get_status_display()}"
