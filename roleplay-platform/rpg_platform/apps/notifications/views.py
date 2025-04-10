from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.generic import ListView, View, TemplateView
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count, Q
from django.utils import timezone
import logging

from .models import Notification, NotificationCategory, NotificationPreference

# Setup logger
logger = logging.getLogger(__name__)


class NotificationCenterView(LoginRequiredMixin, TemplateView):
    """
    Main view for the notification center
    """
    template_name = 'notifications/notification_center.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get categories with counts
        categories = []
        all_categories = NotificationCategory.objects.all().order_by('order', 'name')

        for category in all_categories:
            count = Notification.get_unread_count(self.request.user, category)
            categories.append({
                'id': category.id,
                'name': category.name,
                'key': category.key,
                'icon': category.icon,
                'color': category.color,
                'unread_count': count
            })

        context['categories'] = categories

        # Total unread count
        context['unread_count'] = Notification.get_unread_count(self.request.user)

        # Get active category if provided
        active_category = self.request.GET.get('category')
        if active_category:
            try:
                context['active_category'] = NotificationCategory.objects.get(key=active_category)
            except NotificationCategory.DoesNotExist:
                pass

        return context


class NotificationListView(LoginRequiredMixin, ListView):
    """
    Display all notifications for the current user
    """
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        """Get notifications filtered by various parameters"""
        try:
            # Base queryset - current user, not deleted
            queryset = Notification.objects.filter(
                user=self.request.user,
                is_deleted=False
            ).select_related('actor', 'category')

            # Apply filters
            category = self.request.GET.get('category')
            notification_type = self.request.GET.get('type')
            read = self.request.GET.get('read')
            priority = self.request.GET.get('priority')
            search = self.request.GET.get('search')

            # Filter by category
            if category:
                try:
                    category_obj = NotificationCategory.objects.get(key=category)
                    queryset = queryset.filter(category=category_obj)
                except NotificationCategory.DoesNotExist:
                    logger.warning(f"User {self.request.user.username} attempted to filter by non-existent category: {category}")
                    messages.warning(self.request, _("The selected category does not exist."))

            # Filter by notification type
            if notification_type:
                queryset = queryset.filter(notification_type=notification_type)

            # Filter by read status
            if read == 'read':
                queryset = queryset.filter(read=True)
            elif read == 'unread':
                queryset = queryset.filter(read=False)

            # Filter by priority
            if priority:
                queryset = queryset.filter(priority=priority)

            # Search in message content
            if search:
                queryset = queryset.filter(
                    Q(description__icontains=search) |
                    Q(verb__icontains=search)
                )

            return queryset.order_by('-created_at')
        except Exception as e:
            logger.error(f"Error in NotificationListView.get_queryset: {str(e)}")
            messages.error(self.request, _("An error occurred while retrieving notifications. Please try again."))
            return Notification.objects.none()

    def get_context_data(self, **kwargs):
        """Add additional context data for the template"""
        try:
            context = super().get_context_data(**kwargs)

            # Add filter values to context
            context['current_category'] = self.request.GET.get('category', '')
            context['current_type'] = self.request.GET.get('type', '')
            context['current_read'] = self.request.GET.get('read', '')
            context['current_priority'] = self.request.GET.get('priority', '')
            context['search_query'] = self.request.GET.get('search', '')

            # Add available categories for filter dropdown
            context['categories'] = NotificationCategory.objects.all().order_by('order', 'name')

            # Add notification types for filter dropdown
            context['notification_types'] = dict(Notification.NOTIFICATION_TYPES)

            # Add priority levels for filter dropdown
            context['priority_levels'] = dict(Notification.PRIORITY_LEVELS)

            return context
        except Exception as e:
            logger.error(f"Error in NotificationListView.get_context_data: {str(e)}")
            messages.error(self.request, _("An error occurred while preparing the notification list. Please try again."))
            return super().get_context_data(**kwargs)


class NotificationPreferenceView(LoginRequiredMixin, View):
    """
    View for managing notification preferences
    """
    template_name = 'notifications/preferences.html'

    def get(self, request):
        # Ensure we have preferences for all categories
        NotificationCategory.create_defaults()
        NotificationPreference.get_or_create_for_user(request.user)

        # Get preferences grouped by category
        preferences = NotificationPreference.objects.filter(
            user=request.user
        ).select_related('category').order_by('category__order')

        return render(request, self.template_name, {
            'preferences': preferences
        })

    def post(self, request):
        # Process form submission to update preferences
        category_id = request.POST.get('category_id')
        in_app = request.POST.get('in_app')
        email = request.POST.get('email')
        push = request.POST.get('push')
        sound = request.POST.get('sound', '') == 'on'

        if category_id and in_app and email and push:
            try:
                # Get preference
                preference = NotificationPreference.objects.get(
                    user=request.user,
                    category_id=category_id
                )

                # Update settings
                preference.in_app = in_app
                preference.email = email
                preference.push = push
                preference.sound = sound
                preference.save()

                messages.success(request, _("Notification preferences updated."))
            except NotificationPreference.DoesNotExist:
                messages.error(request, _("Notification category not found."))

        return redirect('notifications:preferences')


@login_required
@require_POST
def mark_all_read(request):
    """
    Mark all notifications as read for the current user
    """
    category_id = request.POST.get('category_id')

    if category_id:
        try:
            category = NotificationCategory.objects.get(id=category_id)
            Notification.mark_all_as_read(request.user, category)
            messages.success(request, _('All notifications in this category marked as read'))
        except NotificationCategory.DoesNotExist:
            messages.error(request, _('Category not found'))
    else:
        Notification.mark_all_as_read(request.user)
        messages.success(request, _('All notifications marked as read'))

    # Check if request wants JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    # Otherwise redirect back to notifications list
    return redirect('notifications:notification_list')


@login_required
@require_POST
def mark_read(request, pk):
    """
    Mark a specific notification as read
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()

    # Check if request wants JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Otherwise redirect back to notifications list
    return redirect('notifications:notification_list')


@login_required
@require_POST
def delete_notification(request, pk):
    """
    Delete a notification
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete_notification()

    messages.success(request, _('Notification deleted'))

    # Check if request wants JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    # Otherwise redirect back to notifications list
    return redirect('notifications:notification_list')


@login_required
@require_GET
def unread_count_api(request):
    """
    API endpoint to get the number of unread notifications
    """
    count = Notification.get_unread_count(request.user)

    # Get category counts if requested
    include_categories = request.GET.get('include_categories', 'false').lower() == 'true'

    response = {'count': count}

    if include_categories:
        categories = NotificationCategory.objects.all()
        category_counts = {}

        for category in categories:
            category_counts[category.key] = Notification.get_unread_count(request.user, category)

        response['categories'] = category_counts

    return JsonResponse(response)


@login_required
@require_GET
def recent_notifications_api(request):
    """
    API endpoint to get recent notifications
    """
    # Get parameters
    limit = int(request.GET.get('limit', 5))
    include_read = request.GET.get('include_read', 'false').lower() == 'true'
    category = request.GET.get('category')

    # Build query
    query = Notification.objects.filter(
        user=request.user,
        is_deleted=False
    )

    # Filter by read status if needed
    if not include_read:
        query = query.filter(read=False)

    # Filter by category if provided
    if category:
        try:
            category_obj = NotificationCategory.objects.get(key=category)
            query = query.filter(category=category_obj)
        except NotificationCategory.DoesNotExist:
            pass

    # Get notifications
    notifications = query.select_related('actor', 'category').order_by('-created_at')[:limit]

    # Format for JSON
    notifications_data = []
    for notification in notifications:
        actor_data = None
        if notification.actor:
            actor_data = {
                'id': notification.actor.id,
                'username': notification.actor.username,
                'display_name': notification.actor.profile.get_display_name() if hasattr(notification.actor, 'profile') else notification.actor.username,
                'avatar': notification.actor.profile.get_avatar_url() if hasattr(notification.actor, 'profile') else None
            }

        category_data = None
        if notification.category:
            category_data = {
                'id': notification.category.id,
                'key': notification.category.key,
                'name': notification.category.name,
                'icon': notification.category.icon,
                'color': notification.category.color
            }

        notifications_data.append({
            'id': notification.pk,
            'type': notification.notification_type,
            'category': category_data,
            'actor': actor_data,
            'verb': notification.verb,
            'description': notification.description,
            'action_object_id': notification.action_object_id,
            'target_id': notification.target_id,
            'url': notification.url,
            'image_url': notification.image_url,
            'priority': notification.priority,
            'created_at': notification.created_at.isoformat(),
            'read': notification.read,
            'read_at': notification.read_at.isoformat() if notification.read_at else None,
            'extra_data': notification.extra_data
        })

    # Get total unread count
    unread_count = Notification.get_unread_count(request.user)

    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'total_count': query.count()
    })


class NotificationsAPIView(LoginRequiredMixin, View):
    """
    API view for notifications
    """
    def get(self, request):
        """Get notifications for the current user"""
        # Get parameters
        limit = int(request.GET.get('limit', 10))
        page = int(request.GET.get('page', 1))
        include_read = request.GET.get('include_read', 'true').lower() == 'true'
        category_id = request.GET.get('category_id')
        notification_type = request.GET.get('type')

        # Start with base query - not deleted
        query = Notification.objects.filter(
            user=request.user,
            is_deleted=False
        ).select_related('actor', 'category')

        # Apply filters
        if not include_read:
            query = query.filter(read=False)

        if category_id:
            query = query.filter(category_id=category_id)

        if notification_type:
            query = query.filter(notification_type=notification_type)

        # Order by created_at (newest first)
        query = query.order_by('-created_at')

        # Paginate
        from django.core.paginator import Paginator
        paginator = Paginator(query, limit)
        page_obj = paginator.get_page(page)

        # Format notifications for JSON response
        notifications_data = []
        for notification in page_obj.object_list:
            actor_data = None
            if notification.actor:
                actor_data = {
                    'id': notification.actor.id,
                    'username': notification.actor.username,
                    'display_name': notification.actor.profile.get_display_name() if hasattr(notification.actor, 'profile') else notification.actor.username,
                    'avatar': notification.actor.profile.get_avatar_url() if hasattr(notification.actor, 'profile') else None
                }

            category_data = None
            if notification.category:
                category_data = {
                    'id': notification.category.id,
                    'key': notification.category.key,
                    'name': notification.category.name,
                    'icon': notification.category.icon,
                    'color': notification.category.color
                }

            notifications_data.append({
                'id': notification.pk,
                'type': notification.notification_type,
                'category': category_data,
                'actor': actor_data,
                'verb': notification.verb,
                'description': notification.description,
                'action_object_id': notification.action_object_id,
                'target_id': notification.target_id,
                'url': notification.url,
                'image_url': notification.image_url,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat(),
                'read': notification.read,
                'read_at': notification.read_at.isoformat() if notification.read_at else None
            })

        return JsonResponse({
            'notifications': notifications_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        })


class MarkNotificationReadView(LoginRequiredMixin, View):
    """
    View for marking a notification as read
    """
    def post(self, request):
        """Mark a notification as read"""
        notification_id = request.GET.get('id')

        if notification_id:
            try:
                notification = Notification.objects.get(pk=notification_id, user=request.user)
                notification.mark_as_read()
                return JsonResponse({'success': True})
            except Notification.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Notification not found'})
        else:
            # Mark all as read
            Notification.mark_all_as_read(request.user)
            return JsonResponse({'success': True})


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """
    View for marking all notifications as read
    """
    def post(self, request):
        """Mark all notifications as read"""
        category_id = request.GET.get('category_id')

        if category_id:
            try:
                category = NotificationCategory.objects.get(id=category_id)
                Notification.mark_all_as_read(request.user, category)
            except NotificationCategory.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Category not found'})
        else:
            Notification.mark_all_as_read(request.user)

        return JsonResponse({'success': True})


class DeleteNotificationView(LoginRequiredMixin, View):
    """
    View for deleting a notification
    """
    def post(self, request, pk):
        """Delete a notification"""
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete_notification()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})


class CategoriesAPIView(LoginRequiredMixin, View):
    """
    API view for notification categories
    """
    def get(self, request):
        """Get all notification categories with unread counts"""
        # Ensure default categories exist
        NotificationCategory.create_defaults()

        # Get all categories
        categories = NotificationCategory.objects.all().order_by('order', 'name')

        # Format for JSON response
        categories_data = []
        for category in categories:
            unread_count = Notification.get_unread_count(request.user, category)

            categories_data.append({
                'id': category.id,
                'key': category.key,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'color': category.color,
                'unread_count': unread_count
            })

        return JsonResponse({
            'categories': categories_data
        })
