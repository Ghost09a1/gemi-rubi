from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from rpg_platform.apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Password reset
    path('password-reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password-reset/complete/'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Profile
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/password/', views.CustomPasswordChangeView.as_view(), name='password_change'),

    # Account settings
    path('settings/', views.AccountSettingsView.as_view(), name='account_settings'),
    path('settings/preferences/', views.UserPreferencesView.as_view(), name='user_preferences'),
    path('settings/privacy/', views.PrivacySettingsView.as_view(), name='privacy_settings'),
    path('settings/communication/', views.CommunicationSettingsView.as_view(), name='communication_settings'),

    # Social links
    path('social-links/add/', views.SocialLinkCreateView.as_view(), name='social_link_add'),
    path('social-links/<int:pk>/edit/', views.SocialLinkUpdateView.as_view(), name='social_link_edit'),
    path('social-links/<int:pk>/delete/', views.SocialLinkDeleteView.as_view(), name='social_link_delete'),

    # User blocking
    path('blocked-users/', views.BlockedUserListView.as_view(), name='blocked_users'),
    path('block-user/', views.BlockUserView.as_view(), name='block_user'),
    path('unblock-user/<int:pk>/', views.UnblockUserView.as_view(), name='unblock_user'),

    # Friend management URLs
    path('friends/', views.FriendListView.as_view(), name='friend_list'),
    path('friends/requests/', views.FriendRequestListView.as_view(), name='friend_request_list'),
    path('friends/requests/<int:pk>/accept/', views.AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('friends/requests/<int:pk>/reject/', views.RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('friends/requests/<int:pk>/cancel/', views.CancelFriendRequestView.as_view(), name='cancel_friend_request'),
    path('friends/<int:pk>/remove/', views.RemoveFriendView.as_view(), name='remove_friend'),
    path('friends/add/<str:username>/', views.SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friends/add/<str:username>/message/', views.SendFriendRequestWithMessageView.as_view(), name='send_friend_request_with_message'),
    path('friends/search/', views.UserSearchView.as_view(), name='user_search'),
    path('friends/accept/<str:username>/', views.AcceptFriendRequestFromUserView.as_view(), name='accept_friend_request_from_user'),

    # Block management URLs
    path('blocks/', views.BlockedUsersListView.as_view(), name='blocked_users'),
    path('blocks/<int:pk>/unblock/', views.UnblockUserView.as_view(), name='unblock_user'),
    path('blocks/add/<str:username>/', views.BlockUserView.as_view(), name='block_user'),

    # Dashboard URL
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Activity Feed URL
    path('activities/', views.ActivityListView.as_view(), name='activity_list'),

    # Dating Profiles
    path('dating/create/', views.DatingProfileCreateView.as_view(), name='dating_profile_create'),
    path('dating/profiles/<str:username>/', views.DatingProfileDetailView.as_view(), name='dating_profile_detail'),
    path('dating/profiles/<str:username>/edit/', views.DatingProfileUpdateView.as_view(), name='dating_profile_update'),

    # Interests Management
    path('dating/interests/', views.ManageInterestsView.as_view(), name='manage_interests'),
    path('dating/interests/<int:pk>/delete/', views.delete_interest, name='delete_interest'),

    # Browsing and Matching
    path('dating/browse/', views.BrowseDatingProfilesView.as_view(), name='browse_dating_profiles'),
    path('dating/matches/', views.MatchesListView.as_view(), name='view_matches'),
    path('dating/likes/', views.received_likes, name='received_likes'),

    # Actions
    path('dating/like/<str:username>/', views.like_profile, name='like_profile'),
    path('dating/unlike/<str:username>/', views.unlike_profile, name='unlike_profile'),
    path('dating/unmatch/<int:match_id>/', views.unmatch, name='unmatch'),
]
