from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from .models import Report, ModeratorAction, ModerationLog, ModeratorApplication


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'content_summary', 'report_type', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'report_type', 'created_at')
    search_fields = ('reporter__username', 'description')
    actions = ['mark_as_investigating', 'mark_as_resolved', 'mark_as_rejected']
    readonly_fields = ('reporter', 'content_type', 'object_id', 'created_at', 'updated_at')

    def content_summary(self, obj):
        """
        Generate a summary of the reported content
        """
        if obj.content_object:
            return f"{obj.content_type.model}: {str(obj.content_object)[:50]}"
        return "Unknown content"
    content_summary.short_description = _('Reported Content')

    def mark_as_investigating(self, request, queryset):
        """
        Mark selected reports as under investigation
        """
        queryset.update(
            status='investigating',
            assigned_to=request.user,
            updated_at=timezone.now()
        )
        self.message_user(request, _("Selected reports marked as under investigation"))
    mark_as_investigating.short_description = _("Mark as under investigation")

    def mark_as_resolved(self, request, queryset):
        """
        Mark selected reports as resolved
        """
        queryset.update(
            status='resolved',
            assigned_to=request.user,
            updated_at=timezone.now(),
            resolved_at=timezone.now()
        )
        self.message_user(request, _("Selected reports marked as resolved"))
    mark_as_resolved.short_description = _("Mark as resolved")

    def mark_as_rejected(self, request, queryset):
        """
        Mark selected reports as rejected
        """
        queryset.update(
            status='rejected',
            assigned_to=request.user,
            updated_at=timezone.now(),
            resolved_at=timezone.now()
        )
        self.message_user(request, _("Selected reports marked as rejected"))
    mark_as_rejected.short_description = _("Reject reports")


@admin.register(ModeratorAction)
class ModeratorActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_type', 'user', 'moderator', 'is_active', 'expires_at', 'created_at')
    list_filter = ('action_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'moderator__username', 'reason')
    readonly_fields = ('created_at',)
    actions = ['deactivate_actions', 'activate_actions']

    def deactivate_actions(self, request, queryset):
        """
        Deactivate selected moderator actions
        """
        queryset.update(is_active=False)
        self.message_user(request, _("Selected actions have been deactivated"))
    deactivate_actions.short_description = _("Deactivate selected actions")

    def activate_actions(self, request, queryset):
        """
        Activate selected moderator actions
        """
        queryset.update(is_active=True)
        self.message_user(request, _("Selected actions have been activated"))
    activate_actions.short_description = _("Activate selected actions")


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor', 'action', 'content_type', 'object_id', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('actor__username', 'action', 'ip_address')
    readonly_fields = ('actor', 'action', 'ip_address', 'content_type', 'object_id', 'created_at', 'additional_data')


@admin.register(ModeratorApplication)
class ModeratorApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'reviewer', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'reason', 'experience')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        """
        Approve selected moderator applications
        """
        queryset.update(
            status='approved',
            reviewer=request.user,
            updated_at=timezone.now()
        )

        # Get the users from the approved applications
        users = queryset.values_list('user', flat=True)

        # Add the users to the moderators group
        group, created = Group.objects.get_or_create(name='Moderators')
        for user_id in users:
            try:
                user = User.objects.get(id=user_id)
                user.groups.add(group)

                # Log the action
                ModerationLog.objects.create(
                    actor=request.user,
                    action=f"Approved moderator application for {user.username}",
                    content_type=ContentType.objects.get_for_model(user),
                    object_id=user.id
                )
            except User.DoesNotExist:
                pass

        self.message_user(request, _("Selected applications have been approved"))
    approve_applications.short_description = _("Approve selected applications")

    def reject_applications(self, request, queryset):
        """
        Reject selected moderator applications
        """
        queryset.update(
            status='rejected',
            reviewer=request.user,
            updated_at=timezone.now()
        )
        self.message_user(request, _("Selected applications have been rejected"))
    reject_applications.short_description = _("Reject selected applications")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.status != 'pending':
            form.base_fields['reviewer_notes'].required = True
        return form
