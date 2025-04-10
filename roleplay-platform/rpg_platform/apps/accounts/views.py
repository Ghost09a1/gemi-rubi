from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView,
    DeleteView, FormView, TemplateView, RedirectView
)
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model, login, authenticate
from django.db.models import Q, Count, Exists, OuterRef, F, Prefetch
from django.utils import timezone
from django.forms import inlineformset_factory
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView

from .models import (
    Profile, SocialLink, BlockedUser, FriendRequest, Friendship, UserActivity,
    DatingProfile, Interest, DatingLike, Match
)
from .forms import (
    ProfileForm, PreferencesForm, PrivacyForm, CommunicationForm,
    SocialLinkForm, BlockedUserForm, DatingProfileForm, InterestForm,
    DatingLikeForm, DatingSearchForm, FriendRequestForm
)

User = get_user_model()

# Authentication Views
class RegisterView(CreateView):
    """User registration view"""
    model = User
    template_name = 'accounts/register.html'
    fields = ['username', 'email', 'password']
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Create user with hashed password
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Profile is automatically created by the post_save signal
        # No need to create it explicitly here

        messages.success(self.request, _("Your account has been created. You can now log in."))
        return super().form_valid(form)

class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:home')

    def form_valid(self, form):
        messages.success(self.request, _("You have successfully logged in."))
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = 'landing:home'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _("You have been logged out."))
        return super().dispatch(request, *args, **kwargs)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Custom password change view"""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile_update')

    def form_valid(self, form):
        messages.success(self.request, _("Your password has been changed."))
        return super().form_valid(form)

# Profile management views
class ProfileDetailView(DetailView):
    """View user profile"""
    model = Profile
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(
            Profile.objects.select_related('user').prefetch_related('social_links'),
            user__username=username
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        user = self.request.user

        # Check if the current user is friends with the profile user
        if user.is_authenticated:
            try:
                context['is_friend'] = Friendship.objects.filter(
                    (Q(user=user) & Q(friend=profile.user)) |
                    (Q(user=profile.user) & Q(friend=user))
                ).exists()

                # Check for pending friend requests
                context['outgoing_request'] = FriendRequest.objects.filter(
                    from_user=user, to_user=profile.user
                ).exists()

                context['incoming_request'] = FriendRequest.objects.filter(
                    from_user=profile.user, to_user=user
                ).exists()

                # Check if blocked
                context['is_blocked'] = BlockedUser.objects.filter(
                    user=user, blocked_user=profile.user
                ).exists()

                context['is_blocking'] = BlockedUser.objects.filter(
                    user=profile.user, blocked_user=user
                ).exists()
            except Exception as e:
                # Log error and provide fallback values
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error checking relationship status: {str(e)}")
                context['is_friend'] = False
                context['outgoing_request'] = False
                context['incoming_request'] = False
                context['is_blocked'] = False
                context['is_blocking'] = False

        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile"""
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile_detail')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _("Your profile has been updated."))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accounts:profile_detail', kwargs={'username': self.request.user.username})

class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """Main settings view"""
    template_name = 'accounts/account_settings.html'

class UserPreferencesView(LoginRequiredMixin, UpdateView):
    """Update user preferences"""
    model = Profile
    form_class = PreferencesForm
    template_name = 'accounts/preferences_form.html'
    success_url = reverse_lazy('accounts:account_settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _("Your preferences have been updated."))
        return super().form_valid(form)

class PrivacySettingsView(LoginRequiredMixin, UpdateView):
    """Update privacy settings"""
    model = Profile
    form_class = PrivacyForm
    template_name = 'accounts/privacy_form.html'
    success_url = reverse_lazy('accounts:account_settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _("Your privacy settings have been updated."))
        return super().form_valid(form)

class CommunicationSettingsView(LoginRequiredMixin, UpdateView):
    """Update communication settings"""
    model = Profile
    form_class = CommunicationForm
    template_name = 'accounts/communication_form.html'
    success_url = reverse_lazy('accounts:account_settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _("Your communication settings have been updated."))
        return super().form_valid(form)

# Social link management
class SocialLinkCreateView(LoginRequiredMixin, CreateView):
    """Add a social media link"""
    model = SocialLink
    form_class = SocialLinkForm
    template_name = 'accounts/social_link_form.html'
    success_url = reverse_lazy('accounts:profile_update')

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        messages.success(self.request, _("Social link added successfully."))
        return super().form_valid(form)

class SocialLinkUpdateView(LoginRequiredMixin, UpdateView):
    """Update a social media link"""
    model = SocialLink
    form_class = SocialLinkForm
    template_name = 'accounts/social_link_form.html'
    success_url = reverse_lazy('accounts:profile_update')

    def get_queryset(self):
        return SocialLink.objects.filter(profile=self.request.user.profile)

    def form_valid(self, form):
        messages.success(self.request, _("Social link updated successfully."))
        return super().form_valid(form)

class SocialLinkDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a social media link"""
    model = SocialLink
    template_name = 'accounts/social_link_confirm_delete.html'
    success_url = reverse_lazy('accounts:profile_update')

    def get_queryset(self):
        return SocialLink.objects.filter(profile=self.request.user.profile)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Social link deleted successfully."))
        return super().delete(request, *args, **kwargs)

# User blocking
class BlockedUserListView(LoginRequiredMixin, ListView):
    """View blocked users"""
    model = BlockedUser
    template_name = 'accounts/blocked_users.html'
    context_object_name = 'blocked_users'

    def get_queryset(self):
        return BlockedUser.objects.filter(user=self.request.user).select_related('blocked_user')

class BlockUserView(LoginRequiredMixin, CreateView):
    """Block a user"""
    model = BlockedUser
    form_class = BlockedUserForm
    template_name = 'accounts/block_user_form.html'
    success_url = reverse_lazy('accounts:blocked_users')

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Check if already blocked
        if BlockedUser.objects.filter(
            user=self.request.user,
            blocked_user=form.cleaned_data['blocked_user']
        ).exists():
            messages.info(self.request, _("This user is already blocked."))
            return redirect('accounts:blocked_users')

        # Handle case where username is provided instead of user object
        username = self.kwargs.get('username')
        if username:
            blocked_user = get_object_or_404(User, username=username)
            form.instance.blocked_user = blocked_user

        messages.success(self.request, _("User blocked successfully."))
        return super().form_valid(form)

class UnblockUserView(LoginRequiredMixin, DeleteView):
    """Unblock a user"""
    model = BlockedUser
    template_name = 'accounts/unblock_user_confirm.html'
    success_url = reverse_lazy('accounts:blocked_users')

    def get_queryset(self):
        return BlockedUser.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("User unblocked successfully."))
        return super().delete(request, *args, **kwargs)

# Friend management
class FriendListView(LoginRequiredMixin, ListView):
    """View friends list"""
    model = Friendship
    template_name = 'accounts/friends/friend_list.html'
    context_object_name = 'friendships'

    def get_queryset(self):
        try:
            return Friendship.objects.filter(
                Q(user=self.request.user) | Q(friend=self.request.user)
            ).select_related('user', 'friend')
        except Exception as e:
            # Log error and provide fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving friendships: {str(e)}")
            return Friendship.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Process the friendships to get a clean list of friend users
        friends = []
        for friendship in context['friendships']:
            friend_user = friendship.friend if friendship.user == user else friendship.user
            friends.append(friend_user)

        context['friends'] = friends
        return context

class FriendRequestListView(LoginRequiredMixin, ListView):
    """View friend requests"""
    model = FriendRequest
    template_name = 'accounts/friends/friend_request_list.html'
    context_object_name = 'friend_requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Separate incoming and outgoing requests
        context['incoming_requests'] = FriendRequest.objects.filter(
            to_user=user, status='pending'
        ).select_related('from_user')

        context['outgoing_requests'] = FriendRequest.objects.filter(
            from_user=user, status='pending'
        ).select_related('to_user')

        return context

class SendFriendRequestView(LoginRequiredMixin, RedirectView):
    """Send a friend request"""
    pattern_name = 'accounts:profile_detail'

    def get_redirect_url(self, *args, **kwargs):
        username = self.kwargs.get('username')
        to_user = get_object_or_404(User, username=username)

        # Can't friend yourself
        if to_user == self.request.user:
            messages.error(self.request, _("You cannot send a friend request to yourself."))
            return reverse('accounts:profile_detail', kwargs={'username': username})

        # Check if already friends
        try:
            already_friends = Friendship.objects.filter(
                (Q(user=self.request.user) & Q(friend=to_user)) |
                (Q(user=to_user) & Q(friend=self.request.user))
            ).exists()
        except Exception as e:
            # Log error and provide fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking friendship status: {str(e)}")
            already_friends = False

        if already_friends:
            messages.info(self.request, _("You are already friends with this user."))
            return reverse('accounts:profile_detail', kwargs={'username': username})

        # Check for blocks
        if BlockedUser.objects.filter(
            (Q(user=self.request.user) & Q(blocked_user=to_user)) |
            (Q(user=to_user) & Q(blocked_user=self.request.user))
        ).exists():
            messages.error(self.request, _("Cannot send friend request due to blocking."))
            return reverse('accounts:profile_detail', kwargs={'username': username})

        # Check for existing requests
        existing_request = FriendRequest.objects.filter(
            from_user=self.request.user, to_user=to_user, status='pending'
        ).first()

        if existing_request:
            messages.info(self.request, _("You already sent a friend request to this user."))
            return reverse('accounts:profile_detail', kwargs={'username': username})

        # Check for incoming request from this user
        incoming_request = FriendRequest.objects.filter(
            from_user=to_user, to_user=self.request.user, status='pending'
        ).first()

        if incoming_request:
            # Auto-accept the incoming request
            incoming_request.accept()
            messages.success(self.request, _("You are now friends with {}.").format(to_user.username))
            return reverse('accounts:profile_detail', kwargs={'username': username})

        # Create new request
        FriendRequest.objects.create(from_user=self.request.user, to_user=to_user)
        messages.success(self.request, _("Friend request sent to {}.").format(to_user.username))

        return reverse('accounts:profile_detail', kwargs={'username': username})

class SendFriendRequestWithMessageView(LoginRequiredMixin, FormView):
    """Send a friend request with a message"""
    template_name = 'accounts/friends/friend_request_form.html'
    form_class = FriendRequestForm  # You'll need to create this form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        context['to_user'] = get_object_or_404(User, username=username)
        return context

    def form_valid(self, form):
        username = self.kwargs.get('username')
        to_user = get_object_or_404(User, username=username)

        # All the same checks as in SendFriendRequestView
        # ...

        # Create request with message
        FriendRequest.objects.create(
            from_user=self.request.user,
            to_user=to_user,
            message=form.cleaned_data['message']
        )

        messages.success(self.request, _("Friend request sent to {}.").format(to_user.username))
        return redirect('accounts:profile_detail', username=username)

class AcceptFriendRequestView(LoginRequiredMixin, RedirectView):
    """Accept a friend request"""
    pattern_name = 'accounts:friend_request_list'

    def get_redirect_url(self, *args, **kwargs):
        request_id = self.kwargs.get('pk')
        friend_request = get_object_or_404(
            FriendRequest,
            id=request_id,
            to_user=self.request.user,
            status='pending'
        )

        friend_request.accept()
        messages.success(
            self.request,
            _("You are now friends with {}.").format(friend_request.from_user.username)
        )

        return reverse('accounts:friend_request_list')

class AcceptFriendRequestFromUserView(LoginRequiredMixin, RedirectView):
    """Accept a friend request from a specific user"""
    pattern_name = 'accounts:profile_detail'

    def get_redirect_url(self, *args, **kwargs):
        username = self.kwargs.get('username')
        from_user = get_object_or_404(User, username=username)

        friend_request = get_object_or_404(
            FriendRequest,
            from_user=from_user,
            to_user=self.request.user,
            status='pending'
        )

        friend_request.accept()
        messages.success(
            self.request,
            _("You are now friends with {}.").format(from_user.username)
        )

        return reverse('accounts:profile_detail', kwargs={'username': username})

class RejectFriendRequestView(LoginRequiredMixin, RedirectView):
    """Reject a friend request"""
    pattern_name = 'accounts:friend_request_list'

    def get_redirect_url(self, *args, **kwargs):
        request_id = self.kwargs.get('pk')
        friend_request = get_object_or_404(
            FriendRequest,
            id=request_id,
            to_user=self.request.user,
            status='pending'
        )

        friend_request.reject()
        messages.info(
            self.request,
            _("Friend request from {} rejected.").format(friend_request.from_user.username)
        )

        return reverse('accounts:friend_request_list')

class CancelFriendRequestView(LoginRequiredMixin, RedirectView):
    """Cancel a sent friend request"""
    pattern_name = 'accounts:friend_request_list'

    def get_redirect_url(self, *args, **kwargs):
        request_id = self.kwargs.get('pk')
        friend_request = get_object_or_404(
            FriendRequest,
            id=request_id,
            from_user=self.request.user,
            status='pending'
        )

        friend_request.cancel()
        messages.info(
            self.request,
            _("Friend request to {} cancelled.").format(friend_request.to_user.username)
        )

        return reverse('accounts:friend_request_list')

class RemoveFriendView(LoginRequiredMixin, RedirectView):
    """Remove a friend"""
    pattern_name = 'accounts:friend_list'

    def get_redirect_url(self, *args, **kwargs):
        friend_id = self.kwargs.get('pk')
        friend = get_object_or_404(User, id=friend_id)

        try:
            friendship = get_object_or_404(
                Friendship,
                (Q(user=self.request.user) & Q(friend=friend)) |
                (Q(user=friend) & Q(friend=self.request.user))
            )
        except Exception as e:
            # Log error and provide fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving friendship: {str(e)}")
            messages.error(self.request, _("An error occurred while removing this friend."))
            return redirect('accounts:friend_list')

        friendship.delete()
        messages.info(self.request, _("You are no longer friends with {}.").format(friend.username))

        return reverse('accounts:friend_list')

class UserSearchView(LoginRequiredMixin, ListView):
    """Search for users"""
    model = User
    template_name = 'accounts/friends/user_search.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return User.objects.filter(
                Q(username__icontains=query) |
                Q(profile__display_name__icontains=query)
            ).exclude(id=self.request.user.id)
        return User.objects.none()

class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard"""
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Recent activities
        context['activities'] = UserActivity.objects.filter(
            user=user
        ).order_by('-timestamp')[:10]

        # Pending friend requests
        context['pending_requests'] = FriendRequest.objects.filter(
            to_user=user, status='pending'
        ).count()

        # Unread notifications count
        from rpg_platform.apps.notifications.models import Notification
        context['unread_notifications'] = Notification.objects.filter(
            user=user, read=False
        ).count()

        # Characters
        from rpg_platform.apps.characters.models import Character
        context['characters'] = Character.objects.filter(user=user)[:5]

        # Active chats
        from rpg_platform.apps.messages.models import ChatRoom
        context['chatrooms'] = ChatRoom.objects.filter(
            participants=user
        ).order_by('-last_message_time')[:5]

        return context

class ActivityListView(LoginRequiredMixin, ListView):
    """View activity history"""
    model = UserActivity
    template_name = 'accounts/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        return UserActivity.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')

class BlockedUsersListView(LoginRequiredMixin, ListView):
    """List blocked users"""
    model = BlockedUser
    template_name = 'accounts/blocked_users.html'
    context_object_name = 'blocked_users'

    def get_queryset(self):
        return BlockedUser.objects.filter(
            user=self.request.user
        ).select_related('blocked_user')

# Existing views...

# Dating profile views

class DatingProfileCreateView(LoginRequiredMixin, CreateView):
    """Create a new dating profile"""
    model = DatingProfile
    form_class = DatingProfileForm
    template_name = 'accounts/dating/profile_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user already has a dating profile
        if hasattr(request.user.profile, 'dating_profile'):
            messages.info(request, _("You already have a dating profile."))
            return redirect('accounts:dating_profile_detail', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        response = super().form_valid(form)

        # Log activity
        UserActivity.log_activity(
            user=self.request.user,
            activity_type='dating_profile_create',
            content_type='dating_profile',
            object_id=form.instance.id,
            public=form.instance.is_visible
        )

        messages.success(self.request, _("Dating profile created successfully."))
        return response

    def get_success_url(self):
        return reverse('accounts:dating_profile_detail', kwargs={'username': self.request.user.username})


class DatingProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing dating profile"""
    model = DatingProfile
    form_class = DatingProfileForm
    template_name = 'accounts/dating/profile_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(DatingProfile, profile__user__username=self.kwargs['username'])

    def dispatch(self, request, *args, **kwargs):
        # Only the owner can edit their dating profile
        profile = self.get_object()
        if profile.profile.user != request.user:
            messages.error(request, _("You can only edit your own dating profile."))
            return redirect('accounts:dating_profile_detail', username=profile.profile.user.username)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        # Log activity
        UserActivity.log_activity(
            user=self.request.user,
            activity_type='dating_profile_update',
            content_type='dating_profile',
            object_id=form.instance.id,
            public=form.instance.is_visible
        )

        messages.success(self.request, _("Dating profile updated successfully."))
        return response

    def get_success_url(self):
        return reverse('accounts:dating_profile_detail', kwargs={'username': self.request.user.username})


class DatingProfileDetailView(DetailView):
    """View a dating profile"""
    model = DatingProfile
    template_name = 'accounts/dating/profile_detail.html'
    context_object_name = 'dating_profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(
            DatingProfile.objects.select_related('profile__user')
            .prefetch_related('interests'),
            profile__user__username=username
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        user = self.request.user

        # Check if the current user has liked this profile
        if user.is_authenticated:
            try:
                user_dating_profile = user.profile.dating_profile
                context['has_liked'] = DatingLike.objects.filter(
                    from_profile=user_dating_profile,
                    to_profile=profile
                ).exists()

                # Check if they are matched
                context['is_matched'] = Match.objects.filter(
                    (Q(profile1=user_dating_profile) & Q(profile2=profile)) |
                    (Q(profile1=profile) & Q(profile2=user_dating_profile)),
                    is_active=True
                ).exists()

                # Calculate match score if the user has a dating profile
                if hasattr(user.profile, 'dating_profile'):
                    context['match_score'] = user.profile.dating_profile.get_match_score(profile)
            except DatingProfile.DoesNotExist:
                # User doesn't have a dating profile
                pass

        # Get common interests
        context['interests'] = profile.interests.all()

        # Determine if this is the owner's view
        context['is_owner'] = user.is_authenticated and profile.profile.user == user

        # Privacy check - if not public and not the owner, may need to restrict
        if not profile.is_visible and not context['is_owner']:
            # Implement privacy logic
            # (e.g., check if they're friends, block certain sections, etc.)
            pass

        return context

    def dispatch(self, request, *args, **kwargs):
        profile = self.get_object()

        # Check privacy settings
        if not profile.is_visible and (not request.user.is_authenticated or profile.profile.user != request.user):
            messages.error(request, _("This dating profile is not publicly visible."))
            return redirect('accounts:browse_dating_profiles')

        # Check for blocks
        if request.user.is_authenticated:
            user_blocked = BlockedUser.objects.filter(
                user=profile.profile.user,
                blocked_user=request.user
            ).exists()

            user_blocking = BlockedUser.objects.filter(
                user=request.user,
                blocked_user=profile.profile.user
            ).exists()

            if user_blocked or user_blocking:
                messages.error(request, _("This profile is not available."))
                return redirect('accounts:browse_dating_profiles')

        return super().dispatch(request, *args, **kwargs)


class ManageInterestsView(LoginRequiredMixin, TemplateView):
    """Manage interests for a dating profile"""
    template_name = 'accounts/dating/manage_interests.html'

    def get_dating_profile(self):
        return get_object_or_404(DatingProfile, profile__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dating_profile = self.get_dating_profile()

        # Get existing interests
        context['interests'] = Interest.objects.filter(dating_profile=dating_profile)

        # Form for adding new interests
        context['form'] = InterestForm()

        # Available interests not yet selected
        current_interests = context['interests'].values_list('interest_type', flat=True)
        context['available_interests'] = [
            (value, label) for value, label in Interest.INTEREST_TYPES
            if value not in current_interests
        ]

        return context

    def post(self, request, *args, **kwargs):
        dating_profile = self.get_dating_profile()
        form = InterestForm(request.POST)

        if form.is_valid():
            interest = form.save(commit=False)
            interest.dating_profile = dating_profile

            # Check if this interest type already exists
            if not Interest.objects.filter(
                dating_profile=dating_profile,
                interest_type=interest.interest_type
            ).exists():
                interest.save()
                messages.success(request, _("Interest added successfully."))
            else:
                messages.error(request, _("You already have this interest."))

        return redirect('accounts:manage_interests')


@login_required
def delete_interest(request, pk):
    """Delete an interest"""
    interest = get_object_or_404(Interest, pk=pk)

    # Verify ownership
    if interest.dating_profile.profile.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this interest.")

    interest.delete()
    messages.success(request, _("Interest removed successfully."))
    return redirect('accounts:manage_interests')


class BrowseDatingProfilesView(ListView):
    """Browse dating profiles"""
    model = DatingProfile
    template_name = 'accounts/dating/browse_profiles.html'
    context_object_name = 'profiles'
    paginate_by = 12

    def get_queryset(self):
        queryset = DatingProfile.objects.filter(is_visible=True).select_related('profile__user')

        # Get user's dating profile for score calculation
        user = self.request.user
        if user.is_authenticated and hasattr(user.profile, 'dating_profile'):
            user_profile = user.profile.dating_profile

            # Filter out users the current user has blocked or been blocked by
            blocked_users = BlockedUser.objects.filter(
                Q(user=user) | Q(blocked_user=user)
            ).values_list('user_id', 'blocked_user_id')

            blocked_ids = set()
            for block_user_id, blocked_user_id in blocked_users:
                blocked_ids.add(block_user_id)
                blocked_ids.add(blocked_user_id)

            queryset = queryset.exclude(profile__user__id__in=blocked_ids)

            # Exclude the user's own profile
            queryset = queryset.exclude(profile__user=user)

        # Apply filters from search form
        form = self.get_form()
        if form.is_valid():
            # Keyword search
            keyword = form.cleaned_data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(profile__user__username__icontains=keyword) |
                    Q(headline__icontains=keyword) |
                    Q(summary__icontains=keyword)
                )

            # Gender identity filter
            gender_identity = form.cleaned_data.get('gender_identity')
            if gender_identity:
                queryset = queryset.filter(gender_identity__in=gender_identity)

            # Looking for filter
            looking_for = form.cleaned_data.get('looking_for')
            if looking_for:
                queryset = queryset.filter(looking_for__in=looking_for)

            # Roleplay experience filter
            roleplay_experience = form.cleaned_data.get('roleplay_experience')
            if roleplay_experience:
                queryset = queryset.filter(roleplay_experience__in=roleplay_experience)

            # Age range filter
            age_min = form.cleaned_data.get('age_min')
            age_max = form.cleaned_data.get('age_max')

            if age_min or age_max:
                # This is a simplified version - in a real app you'd need
                # to calculate age from birth_date dynamically
                today = timezone.now().date()
                if age_min:
                    max_birth_date = today.replace(year=today.year - age_min)
                    queryset = queryset.filter(birth_date__lte=max_birth_date)

                if age_max:
                    min_birth_date = today.replace(year=today.year - age_max - 1)
                    queryset = queryset.filter(birth_date__gte=min_birth_date)

            # Interests filter
            interests = form.cleaned_data.get('interests')
            if interests:
                queryset = queryset.filter(interests__interest_type__in=interests).distinct()

            # Online now filter
            if form.cleaned_data.get('online_now'):
                # Define what "online now" means - e.g., active in the last 15 minutes
                recent_time = timezone.now() - timezone.timedelta(minutes=15)
                queryset = queryset.filter(profile__last_active__gte=recent_time)

            # Verified only filter
            if form.cleaned_data.get('verified_only'):
                queryset = queryset.filter(verified=True)

            # Sorting
            sort_by = form.cleaned_data.get('sort_by')
            if sort_by:
                if sort_by == 'last_active':
                    queryset = queryset.order_by('-profile__last_active')
                elif sort_by == 'recently_joined':
                    queryset = queryset.order_by('-created_at')
                elif sort_by == 'alphabetical':
                    queryset = queryset.order_by('profile__user__username')
                # Match score sorting is handled below

        # Custom sorting by match score if user is logged in
        if user.is_authenticated and hasattr(user.profile, 'dating_profile') and self.get_form().cleaned_data.get('sort_by') == 'match_score':
            # This is a simplified approach - in a real app, you'd likely
            # calculate this in the database or cache scores
            profiles = list(queryset)
            for profile in profiles:
                if profile.profile.user != user:
                    profile.match_score = user.profile.dating_profile.get_match_score(profile)
                else:
                    profile.match_score = 0

            # Sort by match score
            profiles.sort(key=lambda p: p.match_score, reverse=True)
            return profiles

        return queryset

    def get_form(self):
        return DatingSearchForm(self.request.GET or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()

        # Add match scores if user is logged in
        user = self.request.user
        if user.is_authenticated and hasattr(user.profile, 'dating_profile'):
            user_profile = user.profile.dating_profile

            # If not already calculated in get_queryset
            if self.get_form().cleaned_data.get('sort_by') != 'match_score':
                for profile in context['profiles']:
                    if profile.profile.user != user:
                        profile.match_score = user_profile.get_match_score(profile)

            # Add liked profiles info
            liked_profile_ids = DatingLike.objects.filter(
                from_profile=user_profile
            ).values_list('to_profile_id', flat=True)
            context['liked_profile_ids'] = set(liked_profile_ids)

            # Add matched profiles info
            matched_profiles = Match.objects.filter(
                (Q(profile1=user_profile) | Q(profile2=user_profile)),
                is_active=True
            )
            matched_profile_ids = set()

            for match in matched_profiles:
                if match.profile1_id == user_profile.id:
                    matched_profile_ids.add(match.profile2_id)
                else:
                    matched_profile_ids.add(match.profile1_id)

            context['matched_profile_ids'] = matched_profile_ids

        return context


@login_required
@require_POST
def like_profile(request, username):
    """Like another user's dating profile"""
    # Get the target profile
    target_profile = get_object_or_404(
        DatingProfile,
        profile__user__username=username
    )

    # Get the current user's profile
    try:
        from_profile = request.user.profile.dating_profile
    except DatingProfile.DoesNotExist:
        messages.error(request, _("You need to create a dating profile before liking others."))
        return redirect('accounts:dating_profile_create')

    # Can't like your own profile
    if target_profile.profile.user == request.user:
        messages.error(request, _("You cannot like your own profile."))
        return redirect('accounts:dating_profile_detail', username=username)

    # Check if already liked
    existing_like = DatingLike.objects.filter(
        from_profile=from_profile,
        to_profile=target_profile
    ).first()

    if existing_like:
        messages.info(request, _("You have already liked this profile."))
        return redirect('accounts:dating_profile_detail', username=username)

    # Get optional message and super like status
    message = request.POST.get('message', '')
    is_super_like = request.POST.get('is_super_like', False) == 'on'

    # Create the like
    like = DatingLike.objects.create(
        from_profile=from_profile,
        to_profile=target_profile,
        message=message,
        is_super_like=is_super_like
    )

    # Check for mutual likes and create a match if needed
    match = like.create_match_if_mutual()

    if match:
        messages.success(
            request,
            _("It's a match! You and {} liked each other.").format(target_profile.profile.user.username)
        )

        # Log activity for both users
        UserActivity.log_activity(
            user=request.user,
            activity_type='dating_match',
            content_type='match',
            object_id=match.id,
            extra_data={'matched_with': target_profile.profile.user.username}
        )

        UserActivity.log_activity(
            user=target_profile.profile.user,
            activity_type='dating_match',
            content_type='match',
            object_id=match.id,
            extra_data={'matched_with': request.user.username}
        )

        # Redirect to matches page
        return redirect('accounts:view_matches')
    else:
        messages.success(request, _("You liked {}'s profile.").format(target_profile.profile.user.username))

        # Log activity
        UserActivity.log_activity(
            user=request.user,
            activity_type='dating_like',
            content_type='dating_like',
            object_id=like.id,
            extra_data={'liked_profile': target_profile.profile.user.username},
            public=False  # Keep likes private until there's a match
        )

        # Redirect back to the profile
        return redirect('accounts:dating_profile_detail', username=username)


@login_required
def unlike_profile(request, username):
    """Remove a like from another user's profile"""
    target_profile = get_object_or_404(
        DatingProfile,
        profile__user__username=username
    )

    try:
        from_profile = request.user.profile.dating_profile
    except DatingProfile.DoesNotExist:
        messages.error(request, _("You don't have a dating profile."))
        return redirect('accounts:dating_profile_detail', username=username)

    # Find and delete the like
    like = DatingLike.objects.filter(
        from_profile=from_profile,
        to_profile=target_profile
    ).first()

    if like:
        # Check if there's a match and deactivate it
        match = Match.objects.filter(
            (Q(profile1=from_profile) & Q(profile2=target_profile)) |
            (Q(profile1=target_profile) & Q(profile2=from_profile)),
            is_active=True
        ).first()

        if match:
            match.unmatch()
            messages.info(request, _("You've unmatched with {}.").format(target_profile.profile.user.username))
        else:
            messages.info(request, _("You've unliked {}'s profile.").format(target_profile.profile.user.username))

        # Delete the like
        like.delete()
    else:
        messages.info(request, _("You haven't liked this profile."))

    return redirect('accounts:dating_profile_detail', username=username)


class MatchesListView(LoginRequiredMixin, ListView):
    """View user's matches"""
    model = Match
    template_name = 'accounts/dating/matches.html'
    context_object_name = 'matches'

    def get_queryset(self):
        try:
            dating_profile = self.request.user.profile.dating_profile
        except DatingProfile.DoesNotExist:
            return Match.objects.none()

        # Get active matches where the user is either profile1 or profile2
        queryset = Match.objects.filter(
            (Q(profile1=dating_profile) | Q(profile2=dating_profile)),
            is_active=True
        ).select_related('profile1__profile__user', 'profile2__profile__user')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Process matches to make them easier to use in template
        processed_matches = []

        try:
            user_profile = self.request.user.profile.dating_profile

            for match in context['matches']:
                # Get the other profile in this match
                if match.profile1 == user_profile:
                    other_profile = match.profile2
                    initial_message = match.initial_like2.message if match.initial_like2 else ''
                else:
                    other_profile = match.profile1
                    initial_message = match.initial_like1.message if match.initial_like1 else ''

                processed_matches.append({
                    'match': match,
                    'other_profile': other_profile,
                    'match_score': user_profile.get_match_score(other_profile),
                    'matched_at': match.matched_at,
                    'initial_message': initial_message
                })

            # Sort by match score
            processed_matches.sort(key=lambda m: m['match_score'], reverse=True)

        except DatingProfile.DoesNotExist:
            pass

        context['processed_matches'] = processed_matches
        return context


@login_required
def unmatch(request, match_id):
    """End a match with another user"""
    match = get_object_or_404(Match, pk=match_id)

    # Verify that the user is part of this match
    try:
        user_profile = request.user.profile.dating_profile
    except DatingProfile.DoesNotExist:
        messages.error(request, _("You don't have a dating profile."))
        return redirect('accounts:view_matches')

    if match.profile1 != user_profile and match.profile2 != user_profile:
        messages.error(request, _("This is not your match."))
        return redirect('accounts:view_matches')

    # Get the other profile
    other_profile = match.get_other_profile(user_profile)

    # End the match
    match.unmatch()

    # Delete the like from this user
    DatingLike.objects.filter(
        from_profile=user_profile,
        to_profile=other_profile
    ).delete()

    messages.success(request, _("You've unmatched with {}.").format(
        other_profile.profile.user.username
    ))

    return redirect('accounts:view_matches')


@login_required
def received_likes(request):
    """View profiles that have liked the user"""
    try:
        dating_profile = request.user.profile.dating_profile
    except DatingProfile.DoesNotExist:
        messages.error(request, _("You need to create a dating profile first."))
        return redirect('accounts:dating_profile_create')

    # Get likes received
    likes = DatingLike.objects.filter(
        to_profile=dating_profile
    ).select_related('from_profile__profile__user')

    # Filter out profiles that are already matched
    matched_profiles = Match.objects.filter(
        (Q(profile1=dating_profile) | Q(profile2=dating_profile)),
        is_active=True
    )

    matched_profile_ids = set()
    for match in matched_profiles:
        if match.profile1 == dating_profile:
            matched_profile_ids.add(match.profile2_id)
        else:
            matched_profile_ids.add(match.profile1_id)

    # Exclude likes from matched profiles
    likes = likes.exclude(from_profile_id__in=matched_profile_ids)

    return render(request, 'accounts/dating/received_likes.html', {
        'likes': likes,
    })
