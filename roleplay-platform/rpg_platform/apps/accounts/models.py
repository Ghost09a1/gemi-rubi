from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
import os
import json
from datetime import date

# Define custom User model that extends Django's AbstractUser
class User(AbstractUser):
    """
    Custom user model for the roleplay platform
    """
    bio = models.TextField(_('Bio'), blank=True)

    def __str__(self):
        return self.username

def avatar_upload_path(instance, filename):
    """Define upload path for user avatars"""
    ext = filename.split('.')[-1]
    return f'avatars/{instance.user.username}/{instance.user.username}.{ext}'


class Profile(models.Model):
    """
    User profile with additional information and preferences
    """
    THEME_CHOICES = [
        ('light', _('Light')),
        ('dark', _('Dark')),
        ('auto', _('System Default')),
    ]

    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('es', _('Spanish')),
        ('de', _('German')),
    ]

    PRIVACY_LEVEL_CHOICES = [
        ('public', _('Public - Anyone can view')),
        ('registered', _('Registered - Only registered users can view')),
        ('friends', _('Friends Only - Only friends can view')),
        ('private', _('Private - Only you can view')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    display_name = models.CharField(_('Display Name'), max_length=100, blank=True)
    bio = models.TextField(_('Bio'), blank=True)
    location = models.CharField(_('Location'), max_length=100, blank=True)
    avatar = models.ImageField(
        _('Avatar'),
        upload_to=avatar_upload_path,
        blank=True,
        null=True
    )

    # Preferences
    theme = models.CharField(
        _('Theme'),
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )
    language = models.CharField(
        _('Language'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en'
    )

    # Privacy settings
    profile_privacy = models.CharField(
        _('Profile Privacy'),
        max_length=10,
        choices=PRIVACY_LEVEL_CHOICES,
        default='public'
    )
    activity_privacy = models.CharField(
        _('Activity Privacy'),
        max_length=10,
        choices=PRIVACY_LEVEL_CHOICES,
        default='registered'
    )
    online_status = models.BooleanField(
        _('Show Online Status'),
        default=True
    )

    # Chat privacy settings
    chat_privacy = models.CharField(
        _('Chat Privacy'),
        max_length=10,
        choices=PRIVACY_LEVEL_CHOICES,
        default='friends'
    )
    allow_strangers_chat = models.BooleanField(
        _('Allow Chat from Strangers'),
        default=False,
        help_text=_('Allow users who are not your friends to start conversations with you')
    )
    show_character_status = models.BooleanField(
        _('Show Character Status'),
        default=True,
        help_text=_('Show which character you are currently using in chats')
    )
    chat_notifications = models.BooleanField(
        _('Chat Notifications'),
        default=True
    )

    # Interface preferences
    show_nsfw_content = models.BooleanField(
        _('Show NSFW Content'),
        default=False
    )
    compact_layout = models.BooleanField(
        _('Use Compact Layout'),
        default=False
    )

    # Communication preferences
    email_notifications = models.BooleanField(
        _('Email Notifications'),
        default=True
    )
    friend_requests = models.BooleanField(
        _('Allow Friend Requests'),
        default=True
    )
    private_messages = models.BooleanField(
        _('Allow Private Messages'),
        default=True
    )

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    last_active = models.DateTimeField(_('Last Active'), blank=True, null=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return self.user.username

    def get_display_name(self):
        """Return the display name or username"""
        return self.display_name or self.user.username

    def get_absolute_url(self):
        """URL for the profile"""
        return reverse('accounts:profile_detail', kwargs={'username': self.user.username})

    def get_avatar_url(self):
        """Return avatar URL or default"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return settings.STATIC_URL + 'accounts/img/default-avatar.png'


class SocialLink(models.Model):
    """
    Social media links for users
    """
    PLATFORM_CHOICES = [
        ('website', _('Website')),
        ('twitter', _('Twitter')),
        ('instagram', _('Instagram')),
        ('deviantart', _('DeviantArt')),
        ('furaffinity', _('FurAffinity')),
        ('discord', _('Discord')),
        ('other', _('Other')),
    ]

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='social_links',
        verbose_name=_('Profile')
    )
    platform = models.CharField(
        _('Platform'),
        max_length=20,
        choices=PLATFORM_CHOICES
    )
    url = models.URLField(_('URL'), blank=True)
    username = models.CharField(_('Username/Handle'), max_length=100, blank=True)
    display_name = models.CharField(_('Display Name'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')
        ordering = ['platform']

    def __str__(self):
        return f"{self.profile.user.username} - {self.get_platform_display()}"

    def get_link(self):
        """Return the full URL for the social link"""
        if self.url:
            return self.url

        # Generate URLs based on platform and username
        if self.platform == 'twitter' and self.username:
            return f'https://twitter.com/{self.username}'
        elif self.platform == 'instagram' and self.username:
            return f'https://instagram.com/{self.username}'
        elif self.platform == 'deviantart' and self.username:
            return f'https://{self.username}.deviantart.com'
        elif self.platform == 'furaffinity' and self.username:
            return f'https://www.furaffinity.net/user/{self.username}'

        return ""


class BlockedUser(models.Model):
    """
    Users that have been blocked by a user
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocking',
        verbose_name=_('User')
    )
    blocked_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_by',
        verbose_name=_('Blocked User')
    )
    reason = models.TextField(_('Reason'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Blocked User')
        verbose_name_plural = _('Blocked Users')
        unique_together = ('user', 'blocked_user')

    def __str__(self):
        return f"{self.user.username} blocked {self.blocked_user.username}"


class FriendRequest(models.Model):
    """
    Friend request from one user to another
    """
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
        verbose_name=_('From User')
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
        verbose_name=_('To User')
    )
    message = models.TextField(_('Message'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Friend Request')
        verbose_name_plural = _('Friend Requests')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"

    def accept(self):
        """Accept the friend request and create friendship"""
        Friendship.objects.create(
            user=self.from_user,
            friend=self.to_user
        )
        Friendship.objects.create(
            user=self.to_user,
            friend=self.from_user
        )
        self.delete()

    def reject(self):
        """Reject the friend request"""
        self.delete()


class Friendship(models.Model):
    """
    Friendship between two users (bidirectional)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendships',
        verbose_name=_('User')
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name=_('Friend')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Friendship')
        verbose_name_plural = _('Friendships')
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} ↔ {self.friend.username}"


class UserActivity(models.Model):
    """
    Model to track user activities for the activity feed
    """
    ACTIVITY_TYPES = [
        ('character_create', _('Created Character')),
        ('character_update', _('Updated Character')),
        ('character_delete', _('Deleted Character')),
        ('comment', _('Commented on Character')),
        ('rating', _('Rated Character')),
        ('friendship', _('Friendship')),
        ('message', _('Chat Message')),
        ('login', _('Login')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('User')
    )
    activity_type = models.CharField(
        _('Activity Type'),
        max_length=30,
        choices=ACTIVITY_TYPES
    )
    content_type = models.CharField(
        _('Content Type'),
        max_length=100,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        _('Object ID'),
        null=True,
        blank=True
    )
    extra_data = models.JSONField(
        _('Extra Data'),
        default=dict,
        blank=True
    )
    public = models.BooleanField(
        _('Public'),
        default=True,
        help_text=_('Whether this activity is visible to other users')
    )
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

    @classmethod
    def log_activity(cls, user, activity_type, content_type=None, object_id=None, extra_data=None, public=True):
        """
        Create a new activity log
        """
        if extra_data is None:
            extra_data = {}

        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            content_type=content_type or '',
            object_id=object_id,
            extra_data=extra_data,
            public=public
        )

    def get_extra_data(self, key, default=None):
        """
        Get a specific value from the extra_data JSON field
        """
        if isinstance(self.extra_data, str):
            try:
                data = json.loads(self.extra_data)
                return data.get(key, default)
            except json.JSONDecodeError:
                return default
        return self.extra_data.get(key, default)


class DatingProfile(models.Model):
    """
    Dating profile extension for users, containing matchmaking information
    """
    GENDER_IDENTITY_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('non_binary', _('Non-Binary')),
        ('genderfluid', _('Genderfluid')),
        ('transgender', _('Transgender')),
        ('other', _('Other')),
        ('prefer_not_to_say', _('Prefer not to say')),
    ]

    LOOKING_FOR_CHOICES = [
        ('roleplay_partner', _('Roleplay Partner')),
        ('friend', _('Friend')),
        ('chat_buddy', _('Chat Buddy')),
        ('relationship', _('Relationship')),
        ('casual', _('Casual Dating')),
        ('not_looking', _('Not actively looking')),
    ]

    ROLEPLAY_EXPERIENCE_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('experienced', _('Experienced')),
        ('advanced', _('Advanced')),
        ('professional', _('Professional/Published')),
    ]

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='dating_profile',
        verbose_name=_('User Profile')
    )

    # Basic information
    headline = models.CharField(_('Headline'), max_length=100, blank=True,
                            help_text=_('A catchy headline for your dating profile'))
    summary = models.TextField(_('About Me'), blank=True,
                           help_text=_('Tell potential matches about yourself'))
    birth_date = models.DateField(_('Birth Date'), null=True, blank=True)
    gender_identity = models.CharField(_('Gender Identity'), max_length=20,
                                   choices=GENDER_IDENTITY_CHOICES, blank=True)
    looking_for = models.CharField(_('Looking For'), max_length=20,
                               choices=LOOKING_FOR_CHOICES, default='roleplay_partner')

    # Roleplay preferences
    roleplay_experience = models.CharField(_('Roleplay Experience'), max_length=20,
                                       choices=ROLEPLAY_EXPERIENCE_CHOICES, blank=True)
    writing_style = models.TextField(_('Writing Style'), blank=True,
                                 help_text=_('Describe your writing style, length preferences, etc.'))
    post_frequency = models.CharField(_('Post Frequency'), max_length=100, blank=True,
                                 help_text=_('How often do you usually post? E.g., "Daily", "Few times a week"'))

    # Matching preferences
    min_age_preference = models.PositiveSmallIntegerField(_('Minimum Age Preference'), default=18)
    max_age_preference = models.PositiveSmallIntegerField(_('Maximum Age Preference'), default=99)
    gender_preference = models.JSONField(_('Gender Preference'), default=list, blank=True,
                                    help_text=_('List of gender identities you are interested in'))

    # Additional details
    languages = models.JSONField(_('Languages'), default=list, blank=True,
                            help_text=_('Languages you speak or write in'))
    favorite_genres = models.JSONField(_('Favorite Genres'), default=list, blank=True,
                                  help_text=_('Your favorite roleplay genres'))

    # Privacy and visibility
    is_visible = models.BooleanField(_('Visible in Search'), default=True,
                                help_text=_('Whether your dating profile is visible in search results'))
    show_online_status = models.BooleanField(_('Show Online Status'), default=True)
    verified = models.BooleanField(_('Verified Profile'), default=False)

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Dating Profile')
        verbose_name_plural = _('Dating Profiles')

    def __str__(self):
        return f"{self.profile.user.username}'s Dating Profile"

    def get_absolute_url(self):
        return reverse('accounts:dating_profile_detail', kwargs={'username': self.profile.user.username})

    def get_age(self):
        """Calculate age from birth date"""
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def is_match_candidate(self, other_profile):
        """Check if another profile meets basic matching criteria"""
        if not other_profile.is_visible:
            return False

        # Check for blocks in either direction
        user = self.profile.user
        other_user = other_profile.profile.user
        if BlockedUser.objects.filter(user=user, blocked_user=other_user).exists():
            return False
        if BlockedUser.objects.filter(user=other_user, blocked_user=user).exists():
            return False

        # Check age preferences if birth date is available
        other_age = other_profile.get_age()
        if other_age is not None:
            if other_age < self.min_age_preference or other_age > self.max_age_preference:
                return False

        # Check gender preferences if specified
        if self.gender_preference and other_profile.gender_identity:
            if other_profile.gender_identity not in self.gender_preference:
                return False

        return True

    def get_match_score(self, other_profile):
        """Calculate a match score with another profile based on compatibility"""
        score = 0

        # Check interest overlap
        my_interests = set(Interest.objects.filter(dating_profile=self).values_list('interest_type', flat=True))
        other_interests = set(Interest.objects.filter(dating_profile=other_profile).values_list('interest_type', flat=True))
        common_interests = my_interests.intersection(other_interests)

        # More common interests = higher score
        score += len(common_interests) * 5

        # Check genre preferences
        my_genres = set(self.favorite_genres)
        other_genres = set(other_profile.favorite_genres)
        common_genres = my_genres.intersection(other_genres)

        score += len(common_genres) * 3

        # Check roleplay experience compatibility
        experience_levels = dict(self.ROLEPLAY_EXPERIENCE_CHOICES)
        experience_weights = {
            'beginner': 1,
            'intermediate': 2,
            'experienced': 3,
            'advanced': 4,
            'professional': 5
        }

        my_experience = experience_weights.get(self.roleplay_experience, 0)
        other_experience = experience_weights.get(other_profile.roleplay_experience, 0)

        # Similar experience levels get higher scores
        experience_diff = abs(my_experience - other_experience)
        if experience_diff == 0:
            score += 10
        elif experience_diff == 1:
            score += 5

        # Add points for matching "looking for" criteria
        if self.looking_for == other_profile.looking_for:
            score += 15

        return score


class Interest(models.Model):
    """
    User interests for matching in the dating system
    """
    INTEREST_TYPES = [
        ('fantasy', _('Fantasy')),
        ('sci_fi', _('Science Fiction')),
        ('romance', _('Romance')),
        ('action', _('Action/Adventure')),
        ('horror', _('Horror')),
        ('mystery', _('Mystery')),
        ('slice_of_life', _('Slice of Life')),
        ('historical', _('Historical')),
        ('superhero', _('Superhero')),
        ('anime', _('Anime/Manga')),
        ('fanfiction', _('Fanfiction')),
        ('original', _('Original Fiction')),
        ('tabletop', _('Tabletop RPG')),
        ('freeform', _('Freeform')),
        ('paragraph', _('Paragraph Style')),
        ('multi_para', _('Multi-Paragraph')),
        ('novella', _('Novella Style')),
        ('casual', _('Casual')),
        ('serious', _('Serious')),
        ('nsfw', _('NSFW/Adult')),
        ('lgbtq', _('LGBTQ+ Themes')),
        ('combat', _('Combat Focused')),
        ('character_dev', _('Character Development')),
        ('world_building', _('World Building')),
        ('slice_of_life', _('Slice of Life')),
    ]

    dating_profile = models.ForeignKey(
        DatingProfile,
        on_delete=models.CASCADE,
        related_name='interests',
        verbose_name=_('Dating Profile')
    )
    interest_type = models.CharField(
        _('Interest Type'),
        max_length=30,
        choices=INTEREST_TYPES
    )
    level = models.PositiveSmallIntegerField(
        _('Interest Level'),
        default=5,
        help_text=_('How interested are you in this topic (1-10)')
    )

    class Meta:
        verbose_name = _('Interest')
        verbose_name_plural = _('Interests')
        unique_together = ('dating_profile', 'interest_type')

    def __str__(self):
        return f"{self.dating_profile.profile.user.username} - {self.get_interest_type_display()}"


class DatingLike(models.Model):
    """
    User likes/interests in the dating system
    """
    from_profile = models.ForeignKey(
        DatingProfile,
        on_delete=models.CASCADE,
        related_name='sent_likes',
        verbose_name=_('From Profile')
    )
    to_profile = models.ForeignKey(
        DatingProfile,
        on_delete=models.CASCADE,
        related_name='received_likes',
        verbose_name=_('To Profile')
    )
    message = models.TextField(_('Message'), blank=True,
                          help_text=_('Optional message to send with the like'))
    is_super_like = models.BooleanField(_('Super Like'), default=False,
                                   help_text=_('Super likes are highlighted and prioritized'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Dating Like')
        verbose_name_plural = _('Dating Likes')
        unique_together = ('from_profile', 'to_profile')

    def __str__(self):
        return f"{self.from_profile.profile.user.username} → {self.to_profile.profile.user.username}"

    def create_match_if_mutual(self):
        """Check if there's a mutual like and create a match if there is"""
        # Check if the other person has already liked this profile
        mutual_like = DatingLike.objects.filter(
            from_profile=self.to_profile,
            to_profile=self.from_profile
        ).first()

        if mutual_like:
            # Create a match
            match = Match.objects.create(
                profile1=self.from_profile,
                profile2=self.to_profile,
                initial_like1=self,
                initial_like2=mutual_like
            )

            # Notify both users
            # This would trigger a notification in a real system
            return match

        return None


class Match(models.Model):
    """
    Mutual matches between dating profiles
    """
    profile1 = models.ForeignKey(
        DatingProfile,
        on_delete=models.CASCADE,
        related_name='matches_as_profile1',
        verbose_name=_('Profile 1')
    )
    profile2 = models.ForeignKey(
        DatingProfile,
        on_delete=models.CASCADE,
        related_name='matches_as_profile2',
        verbose_name=_('Profile 2')
    )
    initial_like1 = models.ForeignKey(
        DatingLike,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Initial Like from Profile 1'),
        null=True
    )
    initial_like2 = models.ForeignKey(
        DatingLike,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Initial Like from Profile 2'),
        null=True
    )
    matched_at = models.DateTimeField(_('Matched At'), auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Match')
        verbose_name_plural = _('Matches')
        unique_together = ('profile1', 'profile2')

    def __str__(self):
        return f"Match: {self.profile1.profile.user.username} ↔ {self.profile2.profile.user.username}"

    def get_match_score(self):
        """Get the compatibility score for this match"""
        return self.profile1.get_match_score(self.profile2)

    def unmatch(self):
        """End this match"""
        self.is_active = False
        self.save()

    def get_other_profile(self, profile):
        """Get the other profile in this match"""
        if self.profile1 == profile:
            return self.profile2
        return self.profile1
