"""
Utility functions for the RPG Platform.
This module provides helper functions for common operations used throughout the platform.
"""
import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()
logger = logging.getLogger(__name__)

def get_user_limit(user, limit_type):
    """
    Get the limit for a specific feature based on user type.

    Args:
        user: The user to check
        limit_type: String identifying the limit type (e.g., 'characters', 'rooms')

    Returns:
        int: The maximum number allowed for this user
    """
    # Default limits
    default_limits = {
        'characters': 10,
        'chatrooms': 50,
        'images_per_character': 10,
        'friends': 100,
        'custom_kinks': 20,
    }

    # Premium user limits (if you implement a premium system)
    premium_limits = {
        'characters': 30,
        'chatrooms': 200,
        'images_per_character': 30,
        'friends': 500,
        'custom_kinks': 50,
    }

    # Admin limits
    admin_limits = {
        'characters': 100,
        'chatrooms': 500,
        'images_per_character': 100,
        'friends': 1000,
        'custom_kinks': 100,
    }

    # Check user type and return appropriate limit
    if user.is_superuser or user.is_staff:
        return admin_limits.get(limit_type, default_limits.get(limit_type, 10))

    # In the future, you could check for premium status
    # if user.profile.is_premium:
    #     return premium_limits.get(limit_type, default_limits.get(limit_type, 10))

    return default_limits.get(limit_type, 10)

def check_user_limit(user, limit_type, current_count):
    """
    Check if a user has reached their limit for a specific feature.

    Args:
        user: The user to check
        limit_type: String identifying the limit type
        current_count: Current count of items

    Returns:
        tuple: (reached_limit, limit_value)
    """
    limit = get_user_limit(user, limit_type)
    return current_count >= limit, limit

def is_user_blocked(user, target_user):
    """
    Check if a user is blocked by another user.

    Args:
        user: The user who might be blocked
        target_user: The user who might have blocked

    Returns:
        bool: True if blocked, False if not blocked
    """
    # This is a stub - replace with your actual blocked user implementation
    # For example:
    # return BlockedUser.objects.filter(blocker=target_user, blocked=user).exists()
    return False

def get_user_friends(user):
    """
    Get all friends of a user.

    Args:
        user: The user to get friends for

    Returns:
        QuerySet: User objects that are friends with the given user
    """
    # This is a stub - replace with your actual friendship implementation
    # For example:
    # friend_relations = Friendship.objects.filter(Q(user1=user) | Q(user2=user))
    # friend_ids = []
    # for relation in friend_relations:
    #     friend = relation.user1 if relation.user2 == user else relation.user2
    #     friend_ids.append(friend.id)
    # return User.objects.filter(id__in=friend_ids)
    return User.objects.none()

def log_user_activity(user, activity_type, ip_address=None, related_object=None, data=None):
    """
    Log user activity for auditing and analytics.

    Args:
        user: The user performing the activity
        activity_type: String describing the activity
        ip_address: Optional IP address of the user
        related_object: Optional related object
        data: Optional additional data
    """
    try:
        # This is a stub - replace with your actual activity logging implementation
        # For example:
        # UserActivity.objects.create(
        #     user=user,
        #     activity_type=activity_type,
        #     ip_address=ip_address,
        #     content_object=related_object,
        #     data=data or {}
        # )

        # Just log the activity for now
        logger.info(f"User {user.username} performed {activity_type}")
    except Exception as e:
        logger.error(f"Failed to log user activity: {str(e)}")

def handle_exception(request, e, default_message=_("An error occurred. Please try again.")):
    """
    Standard exception handler for views

    Args:
        request: The HTTP request
        e: The exception that was raised
        default_message: Message to show to the user

    Returns:
        None, but adds a message to the request
    """
    logger.error(f"Exception in view: {str(e)}")
    messages.error(request, default_message)
