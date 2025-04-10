import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""

    async def connect(self):
        """Connect to the WebSocket and join the user's notification group"""
        self.user = self.scope['user']

        # Check if user is authenticated
        if self.user.is_anonymous:
            await self.close()
            return

        # Set the group name for this user
        self.notification_group_name = f'notifications_{self.user.id}'

        # Join the group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

        # Send initial data to the client
        await self.send_initial_data()

    async def disconnect(self, close_code):
        """Leave the notification group on disconnect"""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type', '')

        # Handle different client message types
        if message_type == 'mark_all_read':
            # Mark all notifications as read
            category_id = data.get('category_id')
            await self.mark_all_as_read(category_id)

            # Send updated counts
            await self.send_notification_counts()

        elif message_type == 'mark_read':
            # Mark a specific notification as read
            notification_id = data.get('notification_id')
            if notification_id:
                await self.mark_notification_read(notification_id)

                # Send updated counts
                await self.send_notification_counts()

        elif message_type == 'delete_notification':
            # Delete a specific notification
            notification_id = data.get('notification_id')
            if notification_id:
                await self.delete_notification(notification_id)

                # Send updated counts
                await self.send_notification_counts()

        elif message_type == 'get_notifications':
            # Fetch notifications for a specific category
            category_id = data.get('category_id')
            page = data.get('page', 1)
            limit = data.get('limit', 10)

            # Fetch and send notifications
            await self.send_notifications(category_id, page, limit)

        elif message_type == 'get_notification_counts':
            # Send updated counts
            await self.send_notification_counts()

    async def new_notification(self, event):
        """Send notification to WebSocket when a new notification is created"""
        # Forward the notification data to the client
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

        # Also send the updated unread count
        await self.send_notification_counts()

    async def notification_read(self, event):
        """Send notification read update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification_read',
            'notification_id': event['notification_id']
        }))

        # Also send the updated unread count
        await self.send_notification_counts()

    async def notifications_marked_read(self, event):
        """Send notification when multiple notifications are marked as read"""
        await self.send(text_data=json.dumps({
            'type': 'notifications_marked_read',
            'notification_ids': event['notification_ids']
        }))

        # Also send the updated unread count
        await self.send_notification_counts()

    async def notification_deleted(self, event):
        """Send notification when a notification is deleted"""
        await self.send(text_data=json.dumps({
            'type': 'notification_deleted',
            'notification_id': event['notification_id']
        }))

        # Also send the updated unread count
        await self.send_notification_counts()

    async def send_initial_data(self):
        """Send initial data when client connects"""
        # Send notification counts
        await self.send_notification_counts()

        # Send categories with notification counts
        categories = await self.get_categories_with_counts()
        await self.send(text_data=json.dumps({
            'type': 'categories',
            'categories': categories
        }))

        # Send recent notifications
        await self.send_notifications(None, 1, 5)

    async def send_notification_counts(self):
        """Send counts of unread notifications to the client"""
        # Get total unread count
        total_count = await self.get_unread_count()

        # Get counts by category
        category_counts = await self.get_unread_counts_by_category()

        # Send the counts to the client
        await self.send(text_data=json.dumps({
            'type': 'notification_counts',
            'total_count': total_count,
            'category_counts': category_counts
        }))

    async def send_notifications(self, category_id, page, limit):
        """Send notifications to the client, optionally filtered by category"""
        notifications = await self.get_notifications(category_id, page, limit)

        await self.send(text_data=json.dumps({
            'type': 'notifications_list',
            'notifications': notifications['results'],
            'page': page,
            'has_more': notifications['has_more'],
            'total_pages': notifications['total_pages'],
            'total_count': notifications['total_count'],
            'category_id': category_id
        }))

    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread notifications for the user"""
        from .models import Notification
        return Notification.get_unread_count(self.user)

    @database_sync_to_async
    def get_unread_counts_by_category(self):
        """Get counts of unread notifications by category"""
        from .models import Notification, NotificationCategory

        # Get all categories
        categories = NotificationCategory.objects.all()

        counts = {}
        for category in categories:
            counts[category.id] = Notification.get_unread_count(self.user, category)

        return counts

    @database_sync_to_async
    def get_categories_with_counts(self):
        """Get notification categories with their unread counts"""
        from .models import NotificationCategory, Notification

        # Ensure default categories exist
        NotificationCategory.create_defaults()

        categories = NotificationCategory.objects.all().order_by('order', 'name')

        results = []
        for category in categories:
            count = Notification.get_unread_count(self.user, category)

            results.append({
                'id': category.id,
                'name': category.name,
                'key': category.key,
                'description': category.description,
                'icon': category.icon,
                'color': category.color,
                'unread_count': count
            })

        return results

    @database_sync_to_async
    def mark_all_as_read(self, category_id=None):
        """Mark all notifications as read"""
        from .models import Notification, NotificationCategory

        # If category ID is provided, only mark that category as read
        if category_id:
            try:
                category = NotificationCategory.objects.get(id=category_id)
                Notification.mark_all_as_read(self.user, category)
            except NotificationCategory.DoesNotExist:
                pass
        else:
            # Mark all notifications as read
            Notification.mark_all_as_read(self.user)

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read"""
        from .models import Notification

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def delete_notification(self, notification_id):
        """Delete a specific notification"""
        from .models import Notification

        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.delete_notification()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def get_notifications(self, category_id=None, page=1, limit=10):
        """Get notifications with pagination, optionally filtered by category"""
        from .models import Notification
        from django.core.paginator import Paginator

        # Start with non-deleted notifications for this user
        query = Notification.objects.filter(
            user=self.user,
            is_deleted=False
        ).select_related('actor', 'category').order_by('-created_at')

        # Filter by category if provided
        if category_id:
            query = query.filter(category_id=category_id)

        # Paginate the results
        paginator = Paginator(query, limit)
        current_page = paginator.get_page(page)

        # Convert notification objects to dict for JSON serialization
        results = []
        for notification in current_page.object_list:
            # Get actor data if available
            actor_data = None
            if notification.actor:
                actor_data = {
                    'id': notification.actor.id,
                    'username': notification.actor.username,
                    'display_name': notification.actor.profile.get_display_name() if hasattr(notification.actor, 'profile') else notification.actor.username,
                    'avatar': notification.actor.profile.get_avatar_url() if hasattr(notification.actor, 'profile') else None
                }

            # Get category data if available
            category_data = None
            if notification.category:
                category_data = {
                    'id': notification.category.id,
                    'name': notification.category.name,
                    'key': notification.category.key,
                    'icon': notification.category.icon,
                    'color': notification.category.color
                }

            # Create notification dict
            results.append({
                'id': notification.id,
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

        return {
            'results': results,
            'has_more': current_page.has_next(),
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        }
