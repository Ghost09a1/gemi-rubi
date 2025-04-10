from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CharacterRecommendation(models.Model):
    """
    Character recommendations for users based on various signals
    """
    REASON_CHOICES = [
        ('similar_rating', _('Similar to Characters You Rated Highly')),
        ('similar_comment', _('Similar to Characters You Commented On')),
        ('friend_rated', _('Rated Highly by Your Friends')),
        ('popular', _('Popular in the Community')),
        ('similar_tags', _('Similar Tags to Your Interests')),
        ('recently_active', _('Recently Active Character')),
        ('new_character', _('New Character You Might Like')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='character_recommendations',
        verbose_name=_('User')
    )
    character = models.ForeignKey(
        'characters.Character',
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name=_('Character')
    )
    score = models.FloatField(
        _('Recommendation Score'),
        help_text=_('Higher score indicates stronger recommendation')
    )
    reason = models.CharField(
        _('Recommendation Reason'),
        max_length=50,
        choices=REASON_CHOICES
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_dismissed = models.BooleanField(_('Dismissed'), default=False)

    class Meta:
        verbose_name = _('Character Recommendation')
        verbose_name_plural = _('Character Recommendations')
        ordering = ['-score']
        unique_together = ('user', 'character')
        indexes = [
            models.Index(fields=['user', 'is_dismissed']),
            models.Index(fields=['character']),
            models.Index(fields=['score']),
        ]

    def __str__(self):
        return f"Recommendation of {self.character.name} for {self.user.username}"


class UserSimilarity(models.Model):
    """
    Stores similarity scores between users based on ratings and preferences
    """
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='similarities_as_user1',
        verbose_name=_('User 1')
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='similarities_as_user2',
        verbose_name=_('User 2')
    )
    similarity_score = models.FloatField(
        _('Similarity Score'),
        help_text=_('How similar the users\' tastes are (0-1)')
    )
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('User Similarity')
        verbose_name_plural = _('User Similarities')
        unique_together = (('user1', 'user2'),)
        indexes = [
            models.Index(fields=['user1', 'similarity_score']),
            models.Index(fields=['user2', 'similarity_score']),
        ]

    def __str__(self):
        return f"Similarity between {self.user1.username} and {self.user2.username}: {self.similarity_score:.2f}"


class UserPreference(models.Model):
    """
    Stores user preferences for different character attributes
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='character_preferences',
        verbose_name=_('User')
    )
    attribute = models.CharField(
        _('Attribute'),
        max_length=100,
        help_text=_('Character attribute (e.g., species, gender, etc.)')
    )
    value = models.CharField(
        _('Value'),
        max_length=100
    )
    weight = models.FloatField(
        _('Preference Weight'),
        default=1.0,
        help_text=_('How strongly this preference influences recommendations')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('User Preference')
        verbose_name_plural = _('User Preferences')
        unique_together = ('user', 'attribute', 'value')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['attribute', 'value']),
        ]

    def __str__(self):
        return f"{self.user.username}'s preference for {self.attribute}: {self.value} ({self.weight})"
