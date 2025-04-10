from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rpg_platform.apps.accounts.models import (
    Profile, SocialLink, BlockedUser,
    FriendRequest, Friendship, UserActivity,
    DatingProfile, Interest, DatingLike, Match
)

User = get_user_model()


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1


class InterestInline(admin.TabularInline):
    model = Interest
    extra = 1
    max_num = 20


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_display_name', 'location', 'theme', 'language', 'created_at')
    list_filter = ('theme', 'language', 'show_nsfw_content', 'friend_requests')
    search_fields = ('user__username', 'user__email', 'display_name', 'location')
    readonly_fields = ('created_at', 'updated_at', 'last_active')
    inlines = [SocialLinkInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'display_name', 'bio', 'location', 'avatar')
        }),
        (_('Preferences'), {
            'fields': ('theme', 'language', 'compact_layout', 'show_nsfw_content')
        }),
        (_('Privacy'), {
            'fields': ('profile_privacy', 'activity_privacy', 'online_status')
        }),
        (_('Communication'), {
            'fields': ('email_notifications', 'friend_requests', 'private_messages')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )


class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('profile', 'platform', 'username', 'display_name')
    list_filter = ('platform',)
    search_fields = ('profile__user__username', 'username', 'display_name')


class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'blocked_user', 'created_at')
    search_fields = ('user__username', 'blocked_user__username', 'reason')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('from_user__username', 'to_user__username', 'message')
    raw_id_fields = ('from_user', 'to_user')
    readonly_fields = ('created_at',)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'friend', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'friend__username')
    raw_id_fields = ('user', 'friend')
    readonly_fields = ('created_at',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin for user activities"""
    list_display = ('user', 'activity_type', 'content_type', 'object_id', 'created_at', 'public')
    list_filter = ('activity_type', 'content_type', 'public', 'created_at')
    search_fields = ('user__username', 'content_type')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': ('user', 'activity_type', 'content_type', 'object_id', 'public')
        }),
        (_('Data'), {
            'fields': ('extra_data',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
        }),
    )


@admin.register(DatingProfile)
class DatingProfileAdmin(admin.ModelAdmin):
    """Admin for dating profiles"""
    list_display = ('id', 'profile', 'headline', 'gender_identity', 'looking_for',
                   'roleplay_experience', 'is_visible', 'verified', 'created_at')
    list_filter = ('looking_for', 'roleplay_experience', 'gender_identity',
                   'is_visible', 'verified', 'created_at')
    search_fields = ('profile__user__username', 'headline', 'summary')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('profile',)
    inlines = [InterestInline]

    fieldsets = (
        (None, {
            'fields': ('profile', 'headline', 'summary', 'is_visible', 'verified')
        }),
        (_('Personal Information'), {
            'fields': ('birth_date', 'gender_identity', 'looking_for')
        }),
        (_('Roleplay Preferences'), {
            'fields': ('roleplay_experience', 'writing_style', 'post_frequency',
                      'favorite_genres', 'languages')
        }),
        (_('Matching Preferences'), {
            'fields': ('min_age_preference', 'max_age_preference', 'gender_preference')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    """Admin for interests"""
    list_display = ('id', 'dating_profile', 'interest_type', 'level')
    list_filter = ('interest_type', 'level')
    search_fields = ('dating_profile__profile__user__username', 'interest_type')
    raw_id_fields = ('dating_profile',)


@admin.register(DatingLike)
class DatingLikeAdmin(admin.ModelAdmin):
    """Admin for dating likes"""
    list_display = ('id', 'from_profile', 'to_profile', 'is_super_like', 'created_at')
    list_filter = ('is_super_like', 'created_at')
    search_fields = ('from_profile__profile__user__username', 'to_profile__profile__user__username')
    raw_id_fields = ('from_profile', 'to_profile')
    readonly_fields = ('created_at',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Admin for matches"""
    list_display = ('id', 'profile1', 'profile2', 'matched_at', 'is_active')
    list_filter = ('is_active', 'matched_at')
    search_fields = ('profile1__profile__user__username', 'profile2__profile__user__username')
    raw_id_fields = ('profile1', 'profile2', 'initial_like1', 'initial_like2')
    readonly_fields = ('matched_at',)

    actions = ['mark_as_inactive']

    def mark_as_inactive(self, request, queryset):
        """Mark selected matches as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} matches marked as inactive."))
    mark_as_inactive.short_description = _("Mark selected matches as inactive")


admin.site.register(Profile, ProfileAdmin)
admin.site.register(SocialLink, SocialLinkAdmin)
admin.site.register(BlockedUser, BlockedUserAdmin)
