from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Avg, F, DateTimeField, ExpressionWrapper
from django.utils import timezone
from django.db import transaction
import json
import datetime
from django.db.models.functions import TruncDay, TruncMonth, TruncHour
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from rpg_platform.apps.characters.models import Character, CharacterComment, CharacterRating, CharacterImage, CharacterKink
from rpg_platform.apps.accounts.models import Profile, UserActivity, BlockedUser
from rpg_platform.apps.notifications.models import Notification
from .models import Report, ModerationLog, ModeratorAction, ModeratorApplication
from .forms import ReportForm, ModeratorNoteForm, ModeratorApplicationForm, ContentReportForm, ModeratorActionForm

User = get_user_model()


class ModeratorRequiredMixin(UserPassesTestMixin):
    """Mixin that tests if the user is a moderator"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class ModerationDashboardView(ModeratorRequiredMixin, TemplateView):
    """View for the moderation dashboard home page"""
    template_name = 'moderation/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get stats for the dashboard
        context['total_users'] = User.objects.count()
        context['active_users'] = UserActivity.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).values('user').distinct().count()

        context['total_characters'] = Character.objects.count()
        context['public_characters'] = Character.objects.filter(public=True).count()

        # Get total comments and ratings
        context['total_comments'] = CharacterComment.objects.count()
        context['total_ratings'] = CharacterRating.objects.count()

        # Get reports
        context['pending_reports'] = Report.objects.filter(status='pending').count()
        context['total_reports'] = Report.objects.count()

        # Recent reports
        context['recent_reports'] = Report.objects.order_by('-created_at')[:5]

        # Recent blocked users
        context['recent_blocks'] = BlockedUser.objects.order_by('-created_at')[:5]

        # Recent user activity
        context['recent_activity'] = UserActivity.objects.select_related(
            'user', 'user__profile'
        ).order_by('-created_at')[:10]

        # Get user metrics
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

        context['new_users_30d'] = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()

        context['active_users_30d'] = UserActivity.objects.filter(
            created_at__gte=thirty_days_ago
        ).values('user').distinct().count()

        # Character stats by privacy
        privacy_stats = Character.objects.values('public').annotate(
            count=Count('id')
        ).order_by('public')

        privacy_labels = {True: 'Public', False: 'Private'}
        context['privacy_data'] = json.dumps({
            'labels': [privacy_labels[entry['public']] for entry in privacy_stats],
            'data': [entry['count'] for entry in privacy_stats]
        })

        return context


class UserListView(ModeratorRequiredMixin, ListView):
    """View for listing users with moderation controls"""
    model = User
    template_name = 'moderation/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.select_related('profile').all()

        # Apply filters
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(profile__display_name__icontains=query)
            )

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'staff':
            queryset = queryset.filter(is_staff=True)

        # Filter by privacy
        privacy_status = self.request.GET.get('privacy_status')
        if privacy_status:
            if privacy_status == 'public':
                queryset = queryset.filter(public=True)
            elif privacy_status == 'private':
                queryset = queryset.filter(public=False)

        # Annotate with stats
        queryset = queryset.annotate(
            character_count=Count('characters', distinct=True),
            comment_count=Count('character_comments', distinct=True),
            rating_count=Count('character_ratings', distinct=True),
            report_count=Count('reports_filed', distinct=True),
            reported_count=Count('reports_received', distinct=True)
        )

        # Order by
        order_by = self.request.GET.get('order_by', '-date_joined')
        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['order_by'] = self.request.GET.get('order_by', '-date_joined')
        context['privacy_filter'] = self.request.GET.get('privacy_status', '')
        return context


class UserDetailView(ModeratorRequiredMixin, DetailView):
    """View for detailed user information with moderation actions"""
    model = User
    template_name = 'moderation/user_detail.html'
    context_object_name = 'user_obj'  # Use user_obj to avoid conflicts with request.user

    def get_object(self, queryset=None):
        """Get user by username instead of pk"""
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Get user activity
        context['recent_activity'] = UserActivity.objects.filter(
            user=user
        ).select_related('character').order_by('-created_at')[:20]

        # Get user characters
        context['characters'] = Character.objects.filter(
            user=user
        ).order_by('-created_at')

        # Get moderation history
        context['moderation_actions'] = ModeratorAction.objects.filter(
            user=user
        ).select_related('moderator').order_by('-created_at')

        # Check for suspension status
        active_suspension = ModeratorAction.objects.filter(
            user=user,
            action_type='suspend',
            is_active=True
        ).first()

        context['active_suspension'] = active_suspension

        # Get groups for assignment
        context['groups'] = Group.objects.all()

        return context


class CharacterListView(ModeratorRequiredMixin, ListView):
    """View for listing characters with moderation controls"""
    model = Character
    template_name = 'moderation/character_list.html'
    context_object_name = 'characters'
    paginate_by = 20

    def get_queryset(self):
        queryset = Character.objects.select_related('user', 'user__profile')

        # Apply filters
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(user__username__icontains=query)
            )

        # Filter by privacy
        privacy_status = self.request.GET.get('privacy_status')
        if privacy_status:
            if privacy_status == 'public':
                queryset = queryset.filter(public=True)
            elif privacy_status == 'private':
                queryset = queryset.filter(public=False)

        # Annotate with stats
        queryset = queryset.annotate(
            comment_count=Count('comments', distinct=True),
            rating_count=Count('ratings', distinct=True),
            avg_rating=Avg('ratings__rating'),
            report_count=Count('reports', distinct=True)
        )

        # Order by
        order_by = self.request.GET.get('order_by', '-created_at')
        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['order_by'] = self.request.GET.get('order_by', '-created_at')
        context['privacy_filter'] = self.request.GET.get('privacy_status', '')
        return context


class CharacterDetailView(ModeratorRequiredMixin, DetailView):
    """View for detailed character information with moderation actions"""
    model = Character
    template_name = 'moderation/character_detail.html'
    context_object_name = 'character'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.object

        # Get character's comments
        context['comments'] = CharacterComment.objects.filter(
            character=character
        ).select_related('author', 'author__profile').order_by('-created_at')

        # Get character's ratings
        context['ratings'] = CharacterRating.objects.filter(
            character=character
        ).select_related('user', 'user__profile').order_by('-created_at')

        # Get reports for this character
        context['reports'] = Report.objects.filter(
            reported_character=character
        ).select_related('reporter', 'reported_user').order_by('-created_at')

        # Get moderation logs for this character
        context['moderation_logs'] = ModerationLog.objects.filter(
            character=character
        ).select_related('moderator').order_by('-created_at')

        return context


class ReportListView(ModeratorRequiredMixin, ListView):
    """View for listing and filtering reports"""
    model = Report
    template_name = 'moderation/report_list.html'
    paginate_by = 15

    def get_queryset(self):
        queryset = Report.objects.all().select_related(
            'reporter', 'assigned_to', 'content_type'
        )

        # Apply filters
        status = self.request.GET.get('status')
        report_type = self.request.GET.get('type')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort', '-created_at')

        if status:
            queryset = queryset.filter(status=status)

        if report_type:
            queryset = queryset.filter(report_type=report_type)

        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(reporter__username__icontains=search) |
                Q(assigned_to__username__icontains=search)
            )

        # Apply sorting
        if sort not in ['created_at', '-created_at', 'status', 'report_type']:
            sort = '-created_at'

        return queryset.order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add stats for different report statuses
        context['pending_count'] = Report.objects.filter(status='pending').count()
        context['investigating_count'] = Report.objects.filter(status='investigating').count()
        context['resolved_count'] = Report.objects.filter(status='resolved').count()
        context['rejected_count'] = Report.objects.filter(status='rejected').count()

        # Add template tag for URL parameters in pagination
        context['url_replace'] = self.url_replace

        return context

    def url_replace(self, **kwargs):
        """
        Template tag for replacing URL parameters in pagination
        while preserving existing parameters
        """
        query_dict = self.request.GET.copy()

        for key, value in kwargs.items():
            query_dict[key] = value

        return query_dict.urlencode()


class ReportDetailView(ModeratorRequiredMixin, DetailView):
    """View for displaying details of a report"""
    model = Report
    template_name = 'moderation/report_detail.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get staff users for the assign to dropdown
        context['moderators'] = User.objects.filter(is_staff=True).order_by('username')

        # Get actions related to this report
        report = self.get_object()
        context['report_actions'] = ModeratorAction.objects.filter(
            report=report
        ).select_related('moderator', 'user').order_by('-created_at')

        return context

    def post(self, request, *args, **kwargs):
        """Handle POST requests for moderator actions"""
        self.object = self.get_object()

        # Check the action requested
        action = request.POST.get('action')

        if action == 'add_note':
            form = ModeratorNoteForm(request.POST)
            if form.is_valid():
                # Create a moderator log entry
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=self.object.reported_user,
                    character=self.object.reported_character,
                    comment=self.object.reported_comment,
                    report=self.object,
                    action='note',
                    note=form.cleaned_data['note']
                )
                messages.success(request, _("Note added successfully."))
            else:
                messages.error(request, _("There was an error adding the note."))

        elif action == 'approve':
            with transaction.atomic():
                # Mark report as approved
                self.object.status = 'approved'
                self.object.moderator = request.user
                self.object.moderated_at = timezone.now()
                self.object.save()

                # Create a moderator log entry
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=self.object.reported_user,
                    character=self.object.reported_character,
                    comment=self.object.reported_comment,
                    report=self.object,
                    action='approve_report'
                )

            messages.success(request, _("Report approved."))

        elif action == 'reject':
            with transaction.atomic():
                # Mark report as rejected
                self.object.status = 'rejected'
                self.object.moderator = request.user
                self.object.moderated_at = timezone.now()
                self.object.save()

                # Create a moderator log entry
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=self.object.reported_user,
                    character=self.object.reported_character,
                    comment=self.object.reported_comment,
                    report=self.object,
                    action='reject_report'
                )

            messages.success(request, _("Report rejected."))

        return redirect('moderation:report_detail', pk=self.object.pk)


class ReportUpdateView(ModeratorRequiredMixin, UpdateView):
    """View for updating a report status"""
    model = Report
    fields = ['status', 'assigned_to', 'resolution_note']

    def form_valid(self, form):
        report = form.instance
        old_status = Report.objects.get(pk=report.pk).status

        # If status is changing to resolved, set resolved_at
        if report.status == 'resolved' and old_status != 'resolved':
            report.resolved_at = timezone.now()

        # Log the action
        if old_status != report.status:
            ModerationLog.objects.create(
                moderator=self.request.user,
                action=f"Changed report #{report.pk} status from {old_status} to {report.status}",
                content_object=report,
                ip_address=self.request.META.get('REMOTE_ADDR'),
            )

            # Notify the reporter if the report is resolved/rejected
            if report.status in ['resolved', 'rejected'] and report.reporter:
                status_display = 'resolved' if report.status == 'resolved' else 'rejected'
                Notification.create_notification(
                    user=report.reporter,
                    notification_type='moderation',
                    verb=f"Your report was {status_display}",
                    description=report.resolution_note,
                    actor=self.request.user,
                    url=f"/moderation/reports/{report.pk}/",
                    priority='normal',
                )

        messages.success(self.request, _("Report updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('moderation:report_detail', kwargs={'pk': self.object.pk})


class ModerationLogListView(ModeratorRequiredMixin, ListView):
    """View for listing moderation logs with filtering options"""
    model = ModerationLog
    template_name = 'moderation/log_list.html'
    context_object_name = 'logs'
    paginate_by = 25

    def get_queryset(self):
        queryset = ModerationLog.objects.all().select_related('actor', 'content_type')

        # Apply filters
        actor_id = self.request.GET.get('actor')
        period = self.request.GET.get('period')
        search = self.request.GET.get('search')

        # Filter by actor (moderator)
        if actor_id:
            try:
                actor_id = int(actor_id)
                queryset = queryset.filter(actor_id=actor_id)
            except (ValueError, TypeError):
                pass

        # Filter by time period
        if period:
            now = timezone.now()
            if period == 'today':
                # Today's logs
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(created_at__gte=today)
            elif period == 'week':
                # This week's logs
                week_start = now - timezone.timedelta(days=now.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(created_at__gte=week_start)
            elif period == 'month':
                # This month's logs
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                queryset = queryset.filter(created_at__gte=month_start)

        # Search in action text
        if search:
            queryset = queryset.filter(action__icontains=search)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get moderators for the filter dropdown
        context['moderators'] = User.objects.filter(is_staff=True).order_by('username')

        # Add template tag for URL parameters in pagination
        context['url_replace'] = self.get_url_replace_function()

        return context

    def get_url_replace_function(self):
        """Create a function for replacing URL parameters in pagination"""
        def url_replace(**kwargs):
            query_dict = self.request.GET.copy()
            for key, value in kwargs.items():
                query_dict[key] = value
            return query_dict.urlencode()
        return url_replace


class AdminActionView(ModeratorRequiredMixin, View):
    """View for handling administrative actions"""

    def post(self, request, *args, **kwargs):
        """Process administrative actions"""
        action = request.POST.get('action')
        target_type = request.POST.get('target_type')
        target_id = request.POST.get('target_id')
        reason = request.POST.get('reason', '')

        # Validate inputs
        if not action or not target_type or not target_id:
            messages.error(request, _("Invalid request parameters."))
            return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))

        # Process action based on target type
        if target_type == 'user':
            return self._process_user_action(request, action, target_id, reason)
        elif target_type == 'character':
            return self._process_character_action(request, action, target_id, reason)
        elif target_type == 'comment':
            return self._process_comment_action(request, action, target_id, reason)

        messages.error(request, _("Invalid target type."))
        return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))

    def _process_user_action(self, request, action, user_id, reason):
        """Process actions targeted at users"""
        try:
            user = User.objects.get(id=user_id)

            if action == 'disable':
                # Disable user account
                user.is_active = False
                user.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=user,
                    action='disable_user',
                    note=reason
                )

                messages.success(request, _("User account disabled successfully."))

            elif action == 'enable':
                # Enable user account
                user.is_active = True
                user.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=user,
                    action='enable_user',
                    note=reason
                )

                messages.success(request, _("User account enabled successfully."))

            elif action == 'promote_mod':
                # Make user a moderator
                user.is_staff = True
                user.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=user,
                    action='promote_moderator',
                    note=reason
                )

                messages.success(request, _("User promoted to moderator successfully."))

            elif action == 'demote_mod':
                # Remove moderator status
                user.is_staff = False
                user.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=user,
                    action='demote_moderator',
                    note=reason
                )

                messages.success(request, _("User demoted from moderator successfully."))

            else:
                messages.error(request, _("Invalid action for user."))

        except User.DoesNotExist:
            messages.error(request, _("User not found."))

        # Redirect back to referrer
        return redirect(request.META.get('HTTP_REFERER', 'moderation:user_list'))

    def _process_character_action(self, request, action, character_id, reason):
        """Process actions targeted at characters"""
        try:
            character = Character.objects.get(id=character_id)

            if action == 'hide':
                # Change character privacy to private
                character.public = False
                character.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=character.user,
                    character=character,
                    action='hide_character',
                    note=reason
                )

                # Notify the character owner
                Notification.objects.create(
                    user=character.user,
                    notification_type='system',
                    verb=_("Your character '{name}' has been hidden by a moderator. Reason: {reason}").format(
                        name=character.name,
                        reason=reason if reason else _("Not specified")
                    ),
                    action_object_id=character.id
                )

                messages.success(request, _("Character hidden successfully."))

            elif action == 'unhide':
                # Make character public again
                character.public = True
                character.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=character.user,
                    character=character,
                    action='unhide_character',
                    note=reason
                )

                # Notify the character owner
                Notification.objects.create(
                    user=character.user,
                    notification_type='system',
                    verb=_("Your character '{name}' has been made public again by a moderator.").format(
                        name=character.name
                    ),
                    action_object_id=character.id
                )

                messages.success(request, _("Character made public successfully."))

            elif action == 'delete':
                # Store character info for logging
                character_name = character.name
                character_owner = character.user

                # Delete the character
                character.delete()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=character_owner,
                    action='delete_character',
                    note=f"Deleted character '{character_name}'. Reason: {reason}"
                )

                # Notify the character owner
                Notification.objects.create(
                    user=character_owner,
                    notification_type='system',
                    verb=_("Your character '{name}' has been deleted by a moderator. Reason: {reason}").format(
                        name=character_name,
                        reason=reason if reason else _("Not specified")
                    )
                )

                messages.success(request, _("Character deleted successfully."))

                # Redirect to user list after deletion
                return redirect('moderation:character_list')

            else:
                messages.error(request, _("Invalid action for character."))

        except Character.DoesNotExist:
            messages.error(request, _("Character not found."))

        # Redirect back to referrer
        return redirect(request.META.get('HTTP_REFERER', 'moderation:character_list'))

    def _process_comment_action(self, request, action, comment_id, reason):
        """Process actions targeted at comments"""
        try:
            comment = CharacterComment.objects.get(id=comment_id)

            if action == 'hide':
                # Hide the comment
                comment.is_hidden = True
                comment.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=comment.author,
                    character=comment.character,
                    comment=comment,
                    action='hide_comment',
                    note=reason
                )

                # Notify the comment author
                Notification.objects.create(
                    user=comment.author,
                    notification_type='system',
                    verb=_("Your comment on '{name}' has been hidden by a moderator. Reason: {reason}").format(
                        name=comment.character.name,
                        reason=reason if reason else _("Not specified")
                    ),
                    action_object_id=comment.character.id,
                    target_id=comment.id
                )

                messages.success(request, _("Comment hidden successfully."))

            elif action == 'unhide':
                # Unhide the comment
                comment.is_hidden = False
                comment.save()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=comment.author,
                    character=comment.character,
                    comment=comment,
                    action='unhide_comment',
                    note=reason
                )

                # Notify the comment author
                Notification.objects.create(
                    user=comment.author,
                    notification_type='system',
                    verb=_("Your comment on '{name}' has been made visible again by a moderator.").format(
                        name=comment.character.name
                    ),
                    action_object_id=comment.character.id,
                    target_id=comment.id
                )

                messages.success(request, _("Comment made visible successfully."))

            elif action == 'delete':
                # Store comment info for logging
                comment_author = comment.author
                character = comment.character

                # Delete the comment
                comment.delete()

                # Log the action
                ModerationLog.objects.create(
                    moderator=request.user,
                    user=comment_author,
                    character=character,
                    action='delete_comment',
                    note=f"Deleted comment on character '{character.name}'. Reason: {reason}"
                )

                # Notify the comment author
                Notification.objects.create(
                    user=comment_author,
                    notification_type='system',
                    verb=_("Your comment on '{name}' has been deleted by a moderator. Reason: {reason}").format(
                        name=character.name,
                        reason=reason if reason else _("Not specified")
                    ),
                    action_object_id=character.id
                )

                messages.success(request, _("Comment deleted successfully."))

            else:
                messages.error(request, _("Invalid action for comment."))

        except CharacterComment.DoesNotExist:
            messages.error(request, _("Comment not found."))

        # Redirect back to referrer
        return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))


class UserManagementView(ModeratorRequiredMixin, ListView):
    """View for listing users with management controls"""
    model = User
    template_name = 'moderation/user_management.html'
    paginate_by = 20
    context_object_name = 'users'

    def get_queryset(self):
        queryset = User.objects.select_related('profile').order_by('-date_joined')

        # Apply filters
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')
        status = self.request.GET.get('status')
        sort_by = self.request.GET.get('sort', '-date_joined')

        # Search filter
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(profile__display_name__icontains=search)
            )

        # Role filter
        if role == 'staff':
            queryset = queryset.filter(is_staff=True)
        elif role == 'superuser':
            queryset = queryset.filter(is_superuser=True)
        elif role == 'regular':
            queryset = queryset.filter(is_staff=False, is_superuser=False)

        # Status filter
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        # Sort options
        valid_sort_fields = ['username', '-username', 'date_joined', '-date_joined',
                           'last_login', '-last_login']

        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-date_joined')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['role'] = self.request.GET.get('role', '')
        context['status'] = self.request.GET.get('status', '')
        context['sort'] = self.request.GET.get('sort', '-date_joined')

        # Get user statistics
        context['total_users'] = User.objects.count()
        context['staff_users'] = User.objects.filter(is_staff=True).count()
        context['inactive_users'] = User.objects.filter(is_active=False).count()

        # Recently active users
        recent_activity = UserActivity.objects.values('user').annotate(
            last_active=Max('created_at')
        ).order_by('-last_active')[:50]

        recently_active_ids = [item['user'] for item in recent_activity]
        context['recently_active'] = recently_active_ids

        # Groups for assignment
        context['groups'] = Group.objects.all()

        return context


class AdvancedSearchView(ModeratorRequiredMixin, TemplateView):
    """Advanced search tool for finding characters and users with complex filters"""
    template_name = 'moderation/advanced_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get search parameters
        search_type = self.request.GET.get('type', 'character')
        search_term = self.request.GET.get('q', '')
        search_field = self.request.GET.get('field', 'name')

        # Set search results to empty by default
        context['character_results'] = []
        context['user_results'] = []
        context['character_count'] = 0
        context['user_count'] = 0
        context['search_performed'] = False

        # Return early if no search term
        if not search_term:
            return context

        context['search_performed'] = True
        context['search_type'] = search_type
        context['search_term'] = search_term
        context['search_field'] = search_field

        # Perform search based on type
        if search_type == 'character':
            self.search_characters(context, search_term, search_field)
        elif search_type == 'user':
            self.search_users(context, search_term, search_field)
        elif search_type == 'both':
            self.search_characters(context, search_term, search_field)
            self.search_users(context, search_term, search_field)

        return context

    def search_characters(self, context, search_term, search_field):
        """Search for characters based on different fields"""
        query = Q()

        # Build query based on selected field
        if search_field == 'name':
            query |= Q(name__icontains=search_term)
        elif search_field == 'description':
            query |= Q(description__icontains=search_term)
        elif search_field == 'kinks':
            # Search in kinks
            kink_ids = CharacterKink.objects.filter(
                Q(kink__name__icontains=search_term) |
                Q(custom_kink__icontains=search_term)
            ).values_list('character_id', flat=True)
            query |= Q(id__in=kink_ids)
        elif search_field == 'any':
            # Search in all text fields
            query |= Q(name__icontains=search_term)
            query |= Q(description__icontains=search_term)
            query |= Q(backstory__icontains=search_term)

            # Include kinks
            kink_ids = CharacterKink.objects.filter(
                Q(kink__name__icontains=search_term) |
                Q(custom_kink__icontains=search_term)
            ).values_list('character_id', flat=True)
            query |= Q(id__in=kink_ids)

            # Include comments
            comment_char_ids = CharacterComment.objects.filter(
                content__icontains=search_term
            ).values_list('character_id', flat=True)
            query |= Q(id__in=comment_char_ids)

        # Apply privacy filter
        privacy_status = self.request.GET.get('privacy_status', '')
        if privacy_status:
            if privacy_status == 'public':
                query &= Q(public=True)
            elif privacy_status == 'private':
                query &= Q(public=False)

        # Apply date filter
        date_filter = self.request.GET.get('date_filter', '')
        if date_filter:
            if date_filter == 'today':
                query &= Q(created_at__gte=timezone.now().replace(hour=0, minute=0, second=0))
            elif date_filter == 'week':
                query &= Q(created_at__gte=timezone.now() - timezone.timedelta(days=7))
            elif date_filter == 'month':
                query &= Q(created_at__gte=timezone.now() - timezone.timedelta(days=30))
            elif date_filter == 'year':
                query &= Q(created_at__gte=timezone.now() - timezone.timedelta(days=365))

        # Apply user filter
        user_filter = self.request.GET.get('user', '')
        if user_filter:
            query &= Q(user__username__iexact=user_filter)

        # Execute query with proper ordering
        sort_by = self.request.GET.get('sort', '-created_at')

        # Get paginated results
        per_page = int(self.request.GET.get('per_page', 12))
        page = int(self.request.GET.get('page', 1))

        all_results = Character.objects.filter(query).select_related('user').order_by(sort_by)
        context['character_count'] = all_results.count()

        # Manual pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        results = all_results[start_idx:end_idx]

        # Enhance with additional info
        enhanced_results = []
        for character in results:
            # Get main image if available
            main_image = character.get_main_image()
            image_url = main_image.image.url if main_image else None

            # Count comments
            comment_count = CharacterComment.objects.filter(character=character).count()

            enhanced_results.append({
                'character': character,
                'image_url': image_url,
                'comment_count': comment_count
            })

        context['character_results'] = enhanced_results
        context['page'] = page
        context['total_pages'] = (context['character_count'] + per_page - 1) // per_page
        context['has_prev'] = page > 1
        context['has_next'] = page < context['total_pages']
        context['per_page'] = per_page

    def search_users(self, context, search_term, search_field):
        """Search for users based on different fields"""
        query = Q()

        # Build query based on selected field
        if search_field == 'username':
            query |= Q(username__icontains=search_term)
        elif search_field == 'email':
            query |= Q(email__icontains=search_term)
        elif search_field == 'display_name':
            query |= Q(profile__display_name__icontains=search_term)
        elif search_field == 'any':
            query |= Q(username__icontains=search_term)
            query |= Q(email__icontains=search_term)
            query |= Q(profile__display_name__icontains=search_term)
            query |= Q(profile__bio__icontains=search_term)

        # Apply role filter
        role_filter = self.request.GET.get('role', '')
        if role_filter == 'staff':
            query &= Q(is_staff=True)
        elif role_filter == 'superuser':
            query &= Q(is_superuser=True)
        elif role_filter == 'regular':
            query &= Q(is_staff=False, is_superuser=False)

        # Apply status filter
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            query &= Q(is_active=True)
        elif status_filter == 'inactive':
            query &= Q(is_active=False)

        # Apply date filter
        date_filter = self.request.GET.get('date_filter', '')
        if date_filter:
            if date_filter == 'today':
                query &= Q(date_joined__gte=timezone.now().replace(hour=0, minute=0, second=0))
            elif date_filter == 'week':
                query &= Q(date_joined__gte=timezone.now() - timezone.timedelta(days=7))
            elif date_filter == 'month':
                query &= Q(date_joined__gte=timezone.now() - timezone.timedelta(days=30))
            elif date_filter == 'year':
                query &= Q(date_joined__gte=timezone.now() - timezone.timedelta(days=365))

        # Execute query with proper ordering
        sort_by = self.request.GET.get('sort', '-date_joined')

        # Get paginated results
        per_page = int(self.request.GET.get('per_page', 12))
        page = int(self.request.GET.get('page', 1))

        all_results = User.objects.filter(query).select_related('profile').order_by(sort_by)
        context['user_count'] = all_results.count()

        # Manual pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        results = all_results[start_idx:end_idx]

        # Enhance with additional info
        enhanced_results = []
        for user in results:
            # Count characters
            character_count = Character.objects.filter(user=user).count()

            # Check for recent activity
            recent_activity = UserActivity.objects.filter(
                user=user
            ).order_by('-created_at').first()

            last_active = recent_activity.created_at if recent_activity else None

            enhanced_results.append({
                'user': user,
                'character_count': character_count,
                'last_active': last_active
            })

        context['user_results'] = enhanced_results
        context['page'] = page
        context['total_pages'] = (context['user_count'] + per_page - 1) // per_page
        context['has_prev'] = page > 1
        context['has_next'] = page < context['total_pages']
        context['per_page'] = per_page


@login_required
@require_POST
def update_user_role(request, username):
    """Update user's staff/admin status"""
    if not request.user.is_staff:
        raise PermissionDenied("You don't have permission to modify user roles")

    user = get_object_or_404(User, username=username)

    # Only superusers can change other superusers
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, _("You don't have permission to modify superuser accounts"))
        return redirect('moderation:user_detail', username=username)

    # Get form data
    is_staff = request.POST.get('is_staff') == 'on'
    is_active = request.POST.get('is_active') == 'on'

    # Update groups
    group_ids = request.POST.getlist('groups')
    groups = Group.objects.filter(id__in=group_ids)

    # Clear existing groups and add selected ones
    user.groups.clear()
    for group in groups:
        user.groups.add(group)

    # Update user status
    user.is_staff = is_staff
    user.is_active = is_active
    user.save()

    # Log the action
    action_description = f"Updated user roles and permissions for {username}"
    ModerationLog.objects.create(
        actor=request.user,
        action=action_description,
        content_object=user,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, _("User roles updated successfully"))
    return redirect('moderation:user_detail', username=username)


@login_required
@require_POST
def suspend_user(request, username):
    """Temporarily suspend a user account"""
    if not request.user.is_staff:
        raise PermissionDenied("You don't have permission to suspend users")

    user = get_object_or_404(User, username=username)

    # Only superusers can suspend other superusers or staff
    if (user.is_superuser or user.is_staff) and not request.user.is_superuser:
        messages.error(request, _("You don't have permission to suspend staff or admin accounts"))
        return redirect('moderation:user_detail', username=username)

    # Get form data
    duration_days = request.POST.get('duration_days')
    reason = request.POST.get('reason')

    if not reason:
        messages.error(request, _("You must provide a reason for suspension"))
        return redirect('moderation:user_detail', username=username)

    # Calculate expiration date
    try:
        duration_days = int(duration_days)
        if duration_days <= 0:
            messages.error(request, _("Duration must be a positive number"))
            return redirect('moderation:user_detail', username=username)

        expires_at = timezone.now() + timezone.timedelta(days=duration_days)
    except (ValueError, TypeError):
        expires_at = None  # Permanent suspension

    # Create suspension record
    ModeratorAction.objects.create(
        moderator=request.user,
        user=user,
        action_type='suspend',
        reason=reason,
        duration_days=duration_days if duration_days > 0 else None,
        expires_at=expires_at,
        is_active=True
    )

    # Deactivate user account
    user.is_active = False
    user.save()

    # Notify the user
    Notification.create_notification(
        user=user,
        notification_type='moderation',
        verb=_("Your account has been suspended"),
        description=reason,
        actor=request.user,
        priority='high'
    )

    messages.success(request, _("User has been suspended"))
    return redirect('moderation:user_detail', username=username)


@login_required
@require_POST
def unsuspend_user(request, username):
    """Unsuspend a previously suspended user account"""
    if not request.user.is_staff:
        raise PermissionDenied("You don't have permission to unsuspend users")

    user = get_object_or_404(User, username=username)

    # Only superusers can unsuspend other staff/admin
    if (user.is_staff or user.is_superuser) and not request.user.is_superuser:
        messages.error(request, _("You don't have permission to modify staff or admin accounts"))
        return redirect('moderation:user_detail', username=username)

    # Find active suspension/ban actions and mark them inactive
    actions = ModeratorAction.objects.filter(
        user=user,
        action_type__in=['suspend', 'ban'],
        is_active=True
    )

    if actions.exists():
        actions.update(is_active=False)

        # Reactivate the user account
        user.is_active = True
        user.save()

        # Create a notification for the user
        Notification.objects.create(
            user=user,
            title=_('Account Reinstated'),
            message=_('Your account has been reinstated and you can now access the platform again.'),
            notification_type='success',
            is_system=True
        )

        # Log the action
        ModerationLog.objects.create(
            actor=request.user,
            action=f'Unsuspended user {username}',
            content_object=user,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, _(f'User {username} has been unsuspended'))
    else:
        messages.info(request, _(f'User {username} is not currently suspended'))

    return redirect('moderation:user_detail', username=username)


class UserActivityStatsView(ModeratorRequiredMixin, TemplateView):
    """View for displaying user activity statistics and analytics"""
    template_name = 'moderation/user_activity_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Time range filter
        time_range = self.request.GET.get('time_range', 'week')

        if time_range == 'day':
            start_date = timezone.now() - timezone.timedelta(days=1)
            trunc_function = TruncHour
            date_format = '%H:00'
        elif time_range == 'month':
            start_date = timezone.now() - timezone.timedelta(days=30)
            trunc_function = TruncDay
            date_format = '%b %d'
        elif time_range == 'year':
            start_date = timezone.now() - timezone.timedelta(days=365)
            trunc_function = TruncMonth
            date_format = '%b %Y'
        else:  # week (default)
            start_date = timezone.now() - timezone.timedelta(days=7)
            trunc_function = TruncDay
            date_format = '%a'

        # Get user signups over time
        user_signups = User.objects.filter(
            date_joined__gte=start_date
        ).annotate(
            date=trunc_function('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Format dates for chart labels
        signup_dates = [entry['date'].strftime(date_format) for entry in user_signups]
        signup_counts = [entry['count'] for entry in user_signups]

        # Get user activity over time
        user_activity = UserActivity.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=trunc_function('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Format dates for chart labels
        activity_dates = [entry['date'].strftime(date_format) for entry in user_activity]
        activity_counts = [entry['count'] for entry in user_activity]

        # Activity by type
        activity_by_type = UserActivity.objects.filter(
            created_at__gte=start_date
        ).values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Most active users
        most_active_users = UserActivity.objects.filter(
            created_at__gte=start_date
        ).values('user__username').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Get character creation stats
        character_creation = Character.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=trunc_function('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Format dates for chart labels
        character_dates = [entry['date'].strftime(date_format) for entry in character_creation]
        character_counts = [entry['count'] for entry in character_creation]

        # Character stats by privacy
        visibility_stats = Character.objects.values('public').annotate(
            count=Count('id')
        ).order_by('-count')

        # Comment and rating stats
        comments_count = CharacterComment.objects.filter(
            created_at__gte=start_date
        ).count()

        ratings_count = CharacterRating.objects.filter(
            created_at__gte=start_date
        ).count()

        # Average rating
        avg_rating = CharacterRating.objects.filter(
            created_at__gte=start_date
        ).aggregate(avg=Avg('rating'))['avg'] or 0

        # Prepare all data for charts
        context['time_range'] = time_range
        context['signup_data'] = json.dumps({
            'labels': signup_dates,
            'data': signup_counts
        }, cls=DjangoJSONEncoder)

        context['activity_data'] = json.dumps({
            'labels': activity_dates,
            'data': activity_counts
        }, cls=DjangoJSONEncoder)

        context['character_data'] = json.dumps({
            'labels': character_dates,
            'data': character_counts
        }, cls=DjangoJSONEncoder)

        context['activity_by_type'] = json.dumps({
            'labels': [entry['activity_type'] for entry in activity_by_type],
            'data': [entry['count'] for entry in activity_by_type]
        }, cls=DjangoJSONEncoder)

        context['visibility_data'] = json.dumps({
            'labels': [entry['public'] for entry in visibility_stats],
            'data': [entry['count'] for entry in visibility_stats]
        }, cls=DjangoJSONEncoder)

        context['most_active_users'] = most_active_users
        context['comments_count'] = comments_count
        context['ratings_count'] = ratings_count
        context['avg_rating'] = round(avg_rating, 1)

        # Summary stats
        context['total_users'] = User.objects.count()
        context['new_users'] = User.objects.filter(date_joined__gte=start_date).count()
        context['active_users'] = UserActivity.objects.filter(
            created_at__gte=start_date
        ).values('user').distinct().count()

        context['total_characters'] = Character.objects.count()
        context['new_characters'] = Character.objects.filter(created_at__gte=start_date).count()

        return context


class ModeratorActionListView(ModeratorRequiredMixin, ListView):
    """View for listing moderator actions with filtering options"""
    model = ModeratorAction
    template_name = 'moderation/action_list.html'
    context_object_name = 'actions'
    paginate_by = 25

    def get_queryset(self):
        queryset = ModeratorAction.objects.all().select_related(
            'moderator', 'user'
        ).order_by('-created_at')

        # Filter by action type if specified
        action_type = self.request.GET.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        # Filter by user if specified
        username = self.request.GET.get('username')
        if username:
            queryset = queryset.filter(user__username__icontains=username)

        # Filter by moderator if specified
        mod_username = self.request.GET.get('moderator')
        if mod_username:
            queryset = queryset.filter(moderator__username__icontains=mod_username)

        # Filter by date range if specified
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            try:
                date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__gte=date_from)
            except ValueError:
                pass

        if date_to:
            try:
                date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                # Add a day to include the end date
                date_to = date_to + datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lt=date_to)
            except ValueError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_types'] = dict(ModeratorAction.ACTION_TYPES)
        context['filter_form'] = self.request.GET
        return context


class ModeratorActionDetailView(ModeratorRequiredMixin, DetailView):
    """View for showing details of a moderator action"""
    model = ModeratorAction
    template_name = 'moderation/action_detail.html'
    context_object_name = 'action'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related actions for this user
        context['related_actions'] = ModeratorAction.objects.filter(
            user=self.object.user
        ).exclude(pk=self.object.pk).order_by('-created_at')[:5]
        return context


class ModeratorApplicationCreateView(LoginRequiredMixin, CreateView):
    """View for users to apply to become moderators"""
    model = ModeratorApplication
    form_class = ModeratorApplicationForm
    template_name = 'moderation/application_form.html'
    success_url = reverse_lazy('accounts:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Apply to be a Moderator')
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Your application has been submitted and will be reviewed soon.'))
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # Check if user already has a pending application
        if ModeratorApplication.objects.filter(user=request.user, status='pending').exists():
            messages.info(request, _('You already have a pending application.'))
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)

class ModeratorApplicationListView(ModeratorRequiredMixin, ListView):
    """View for listing moderator applications"""
    model = ModeratorApplication
    template_name = 'moderation/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        # Filter by status if specified
        status = self.request.GET.get('status')
        if status and status in dict(ModeratorApplication.STATUS_CHOICES):
            return ModeratorApplication.objects.filter(status=status).select_related('user', 'reviewer')
        return ModeratorApplication.objects.all().select_related('user', 'reviewer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = dict(ModeratorApplication.STATUS_CHOICES)
        context['current_status'] = self.request.GET.get('status', '')
        return context

class ModeratorApplicationDetailView(ModeratorRequiredMixin, DetailView):
    """View for showing details of a moderator application"""
    model = ModeratorApplication
    template_name = 'moderation/application_detail.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user details
        user = self.object.user
        context['user_joined'] = user.date_joined
        context['user_activity'] = UserActivity.objects.filter(user=user).count()
        context['user_characters'] = Character.objects.filter(user=user).count()
        return context

class ModeratorApplicationUpdateView(ModeratorRequiredMixin, UpdateView):
    """View for reviewing and updating moderator applications"""
    model = ModeratorApplication
    fields = ['status', 'reviewer_notes']
    template_name = 'moderation/application_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Review Application')
        context['is_review'] = True
        return context

    def form_valid(self, form):
        form.instance.reviewer = self.request.user

        if form.instance.status == 'approved':
            # Grant moderator privileges
            user = form.instance.user
            moderator_group = Group.objects.get(name='Moderators')
            user.groups.add(moderator_group)
            user.save()

            # Send notification
            Notification.objects.create(
                user=user,
                title=_('Application Approved'),
                message=_('Your application to become a moderator has been approved. You now have access to the moderation dashboard.'),
                notification_type='success'
            )

        elif form.instance.status == 'rejected':
            # Send notification
            Notification.objects.create(
                user=form.instance.user,
                title=_('Application Declined'),
                message=_('Your application to become a moderator has been declined. See the feedback for details.'),
                notification_type='info'
            )

        messages.success(self.request, _('Application updated successfully.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('moderation:application_list')


@login_required
def create_moderator_action(request, username):
    """Create a new moderation action for a user"""
    if not request.user.is_staff:
        raise PermissionDenied("You don't have permission to perform moderation actions")

    user = get_object_or_404(User, username=username)

    # Only superusers can moderate other staff/admin
    if (user.is_staff or user.is_superuser) and not request.user.is_superuser:
        messages.error(request, _("You don't have permission to moderate staff or admin accounts"))
        return redirect('moderation:user_detail', username=username)

    if request.method == 'POST':
        form = ModeratorActionForm(request.POST)

        if form.is_valid():
            action = form.save(commit=False)
            action.moderator = request.user
            action.user = user

            # Set expiration date for temporary actions
            if action.action_type in ['suspend', 'ban'] and action.duration_days:
                action.expires_at = timezone.now() + datetime.timedelta(days=action.duration_days)

            # Handle content-specific actions
            content_type = request.POST.get('content_type')
            object_id = request.POST.get('object_id')

            if content_type and object_id and object_id.isdigit():
                try:
                    ct = ContentType.objects.get(id=content_type)
                    action.content_type = ct
                    action.object_id = int(object_id)
                except (ContentType.DoesNotExist, ValueError):
                    pass

            # Save the action
            action.save()

            # Process specific action types
            if action.action_type == 'suspend':
                # Disable the user account temporarily
                user.is_active = False
                user.save()

                # Create a notification for the user
                Notification.objects.create(
                    user=user,
                    title=_('Account Suspended'),
                    message=_(f'Your account has been suspended for {action.duration_days} days. Reason: {action.reason}'),
                    notification_type='warning',
                    is_system=True
                )

                messages.success(request, _(f'User {username} has been suspended for {action.duration_days} days'))

            elif action.action_type == 'ban':
                # Disable the user account permanently
                user.is_active = False
                user.save()

                message = _('Your account has been banned permanently')
                if action.duration_days:
                    message = _(f'Your account has been banned for {action.duration_days} days')

                # Create a notification for the user
                Notification.objects.create(
                    user=user,
                    title=_('Account Banned'),
                    message=f'{message}. Reason: {action.reason}',
                    notification_type='danger',
                    is_system=True
                )

                messages.success(request, _(f'User {username} has been banned'))

            elif action.action_type == 'warn':
                # Create a notification for the user
                Notification.objects.create(
                    user=user,
                    title=_('Warning'),
                    message=_(f'You have received a warning from the moderation team. Reason: {action.reason}'),
                    notification_type='warning',
                    is_system=True
                )

                messages.success(request, _(f'Warning has been sent to {username}'))

            # Log the action
            ModerationLog.objects.create(
                actor=request.user,
                action=f'Created {action.get_action_type_display()} for {username}',
                content_object=action,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return redirect('moderation:user_detail', username=username)

    else:
        form = ModeratorActionForm()

    # Get report if specified
    report_id = request.GET.get('report')
    report = None
    if report_id and report_id.isdigit():
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            pass

    return render(request, 'moderation/action_form.html', {
        'form': form,
        'user_obj': user,
        'report': report,
        'title': _('Create Moderation Action')
    })

@login_required
def report_content(request, model_name, object_id):
    """View for users to report content"""
    # Map model names to actual ContentType objects
    model_map = {
        'character': 'characters.character',
        'comment': 'characters.charactercomment',
        'message': 'messages.chatmessage',
        'user': 'auth.user',
    }

    if model_name not in model_map:
        raise Http404(_("Invalid content type"))

    try:
        content_type = ContentType.objects.get(app_label=model_map[model_name].split('.')[0],
                                             model=model_map[model_name].split('.')[1])
        obj = content_type.get_object_for_this_type(pk=object_id)
    except (ContentType.DoesNotExist, Exception):
        raise Http404(_("Content not found"))

    # Check if content is already reported by this user
    if Report.objects.filter(reporter=request.user,
                            content_type=content_type,
                            object_id=object_id,
                            status__in=['pending', 'investigating']).exists():
        messages.info(request, _("You have already reported this content"))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        form = ContentReportForm(request.POST)

        if form.is_valid():
            report = Report(
                reporter=request.user,
                content_type=content_type,
                object_id=object_id,
                report_type=form.cleaned_data['report_type'],
                description=form.cleaned_data['description'],
                status='pending'
            )
            report.save()

            # Log the report creation
            ModerationLog.objects.create(
                actor=request.user,
                action=f'Reported {model_name} #{object_id} as {report.get_report_type_display()}',
                content_object=report
            )

            messages.success(request, _("Your report has been submitted"))
            return redirect(request.META.get('HTTP_REFERER', '/'))

    else:
        form = ContentReportForm(initial={
            'content_type_id': content_type.id,
            'object_id': object_id
        })

    return render(request, 'moderation/report_form.html', {
        'form': form,
        'content_type': model_name,
        'object_id': object_id,
        'object': obj
    })
