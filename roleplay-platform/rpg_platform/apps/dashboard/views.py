from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.utils import OperationalError, ProgrammingError
import logging

# Import models from other apps
from rpg_platform.apps.characters.models import Character
from rpg_platform.apps.messages.models import ChatRoom
from rpg_platform.apps.accounts.models import Friendship, FriendRequest, UserActivity
from rpg_platform.apps.notifications.models import Notification
from rpg_platform.apps.recommendations.models import CharacterRecommendation

# Set up logger
logger = logging.getLogger(__name__)

@login_required
def home(request):
    """
    Main dashboard/home page view that shows an aggregated view of
    all platform features and user activity.
    """
    user = request.user
    context = {}

    # Character stats - with error handling
    try:
        context['character_count'] = Character.objects.filter(user=user).count()
        context['characters'] = Character.objects.filter(user=user).select_related('user').order_by('-updated_at')[:4]
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Error retrieving character data: {str(e)}")
        context['character_count'] = 0
        context['characters'] = []

    # Chat stats - with error handling
    try:
        context['chatroom_count'] = ChatRoom.objects.filter(participants=user).count()
        context['chat_rooms'] = ChatRoom.objects.filter(participants=user).prefetch_related('participants').order_by('-updated_at')[:5]
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Error retrieving chat room data: {str(e)}")
        context['chatroom_count'] = 0
        context['chat_rooms'] = []

    # Friend stats - with error handling - Updated to use correct field names and remove status filter
    try:
        # Get friendships where the user is either the 'user' or the 'friend'
        context['friend_count'] = Friendship.objects.filter(
            Q(user=user) | Q(friend=user)
        ).count()

        # Get friend requests - removed status field since it doesn't exist in the model
        context['friend_requests'] = FriendRequest.objects.filter(
            to_user=user
        ).select_related('from_user', 'to_user')[:3]
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Error retrieving friendship data: {str(e)}")
        context['friend_count'] = 0
        context['friend_requests'] = []

    # Notification stats - with error handling
    try:
        context['notification_count'] = Notification.objects.filter(user=user, read=False).count()
        context['notifications'] = Notification.objects.filter(user=user).select_related('actor', 'category').order_by('-created_at')[:5]
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Error retrieving notification data: {str(e)}")
        context['notification_count'] = 0
        context['notifications'] = []

    # Activity stats - with error handling - Updated to use correct field names
    try:
        # Get friends IDs
        friend_ids = Friendship.objects.filter(
            Q(user=user)
        ).values_list('friend', flat=True)

        # Also include friendships where user is the 'friend'
        friend_ids_reverse = Friendship.objects.filter(
            Q(friend=user)
        ).values_list('user', flat=True)

        # Combine both sets of friend IDs
        all_friend_ids = list(friend_ids) + list(friend_ids_reverse)

        # Get activities from user and their friends
        context['activities'] = UserActivity.objects.filter(
            Q(user=user) | Q(user__id__in=all_friend_ids)
        ).select_related('user').order_by('-created_at')[:8]
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Error retrieving activity data: {str(e)}")
        context['activities'] = []

    # Recommendations - with error handling
    try:
        context['recommendations'] = CharacterRecommendation.objects.filter(user=user, is_dismissed=False).select_related('character')[:3]
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Error retrieving recommendation data: {str(e)}")
        context['recommendations'] = []

    return render(request, 'dashboard/home.html', context)
