from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os
import django.core.validators
from django.conf import settings

User = get_user_model()


class InfoCategory(models.Model):
    """
    Categories for character information fields
    """

    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Display Order"), default=0)

    class Meta:
        verbose_name = _("Information Category")
        verbose_name_plural = _("Information Categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class InfoField(models.Model):
    """
    Predefined character information fields
    """

    category = models.ForeignKey(
        InfoCategory,
        on_delete=models.CASCADE,
        related_name="fields",
        verbose_name=_("Category"),
    )
    name = models.CharField(_("Field Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    required = models.BooleanField(_("Required"), default=False)
    order = models.PositiveIntegerField(_("Display Order"), default=0)

    class Meta:
        verbose_name = _("Information Field")
        verbose_name_plural = _("Information Fields")
        ordering = ["category", "order", "name"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class KinkCategory(models.Model):
    """
    Categories for kinks
    """

    name = models.CharField(_("Category Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Display Order"), default=0)

    class Meta:
        verbose_name = _("Kink Category")
        verbose_name_plural = _("Kink Categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Kink(models.Model):
    """
    Predefined kinks
    """

    category = models.ForeignKey(
        KinkCategory,
        on_delete=models.CASCADE,
        related_name="kinks",
        verbose_name=_("Category"),
    )
    name = models.CharField(_("Kink Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Display Order"), default=0)

    class Meta:
        verbose_name = _("Kink")
        verbose_name_plural = _("Kinks")
        ordering = ["category", "order", "name"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Character(models.Model):
    """
    Model representing a character in the roleplay platform
    """

    STATUS_CHOICES = [
        ("online", _("Online")),
        ("offline", _("Offline")),
        ("away", _("Away")),
        ("busy", _("Busy")),
        ("inactive", _("Inactive")),
        ("looking", _("Looking for RP")),
        ("private", _("Private")),
    ]

    MOOD_CHOICES = [
        ("neutral", _("Neutral")),
        ("flirty", _("Flirty")),
        ("playful", _("Playful")),
        ("passionate", _("Passionate")),
        ("dominant", _("Dominant")),
        ("submissive", _("Submissive")),
        ("shy", _("Shy")),
        ("confident", _("Confident")),
        ("curious", _("Curious")),
        ("seductive", _("Seductive")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="characters",
    )
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=50)
    species = models.CharField(max_length=100)
    height = models.CharField(max_length=50, blank=True)
    body_type = models.CharField(max_length=100, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    personality = models.TextField(blank=True)
    background = models.TextField(blank=True)
    appearance = models.TextField(blank=True)
    public = models.BooleanField(default=True)
    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="offline",
    )
    current_mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        default="neutral",
    )
    custom_status = models.CharField(max_length=200, blank=True)
    allow_random_rp = models.BooleanField(default=True)
    private_details = models.TextField(blank=True)
    show_in_lists = models.BooleanField(default=False)
    list_order = models.IntegerField(null=True, blank=True)
    list_description = models.TextField(blank=True)
    views = models.PositiveIntegerField(default=0)
    content_preferences = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("characters:detail", kwargs={"pk": self.pk})

    def can_edit(self, user):
        return user == self.user or user.is_staff

    def get_status_display(self):
        if self.custom_status:
            return self.custom_status
        return self.get_current_status_display()

    def get_mood_display(self):
        return self.get_current_mood_display()

    def has_images(self):
        """Return True if the character has images"""
        return self.images.exists()

    def get_primary_image(self):
        """Return the primary image or first image if no primary"""
        return self.images.filter(is_primary=True).first() or self.images.first()

    def get_average_rating(self):
        """Get the average rating for this character"""
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return round(sum(rating.rating for rating in ratings) / len(ratings), 1)

    def get_rating_count(self):
        """Get the number of ratings for this character"""
        return self.ratings.count()

    def get_user_rating(self, user):
        """Get the rating given by a specific user"""
        try:
            return self.ratings.get(user=user)
        except CharacterRating.DoesNotExist:
            return None

    def get_visible_comments(self, user=None):
        """Get all visible comments for this character"""
        comments = self.comments.select_related("author", "author__profile")

        # If the user is the character owner, include hidden comments
        if user and user == self.user:
            return comments

        # Otherwise filter out hidden comments
        return comments.filter(is_hidden=False)

    def can_user_comment(self, user):
        """Check if a user can comment on this character"""
        # User must be authenticated
        if not user or user.is_anonymous:
            return False

        # User must be able to see the character
        if not self.is_visible_to(user):
            return False

        return True

    def can_user_rate(self, user):
        """Check if a user can rate this character"""
        # User must be authenticated
        if not user or user.is_anonymous:
            return False

        # User can't rate their own character
        if user == self.user:
            return False

        # User must be able to see the character
        if not self.is_visible_to(user):
            return False

        return True

    def update_status(self, status, custom_message=None):
        """Update the character's status and optional custom message"""
        if status in dict(self.STATUS_CHOICES):
            self.current_status = status
            if custom_message:
                self.custom_status = custom_message
            self.save(update_fields=["current_status", "custom_status"])
            return True
        return False

    def update_mood(self, mood):
        """Update the character's mood"""
        if mood in dict(self.MOOD_CHOICES):
            self.current_mood = mood
            self.save(update_fields=["current_mood"])
            return True
        return False

    def get_mood_display_with_icon(self):
        """Returns the mood with an appropriate icon"""
        mood_icons = {
            "neutral": "😐",
            "flirty": "😏",
            "playful": "😜",
            "passionate": "😍",
            "dominant": "😈",
            "submissive": "🥺",
            "shy": "😳",
            "confident": "😎",
            "curious": "🤔",
            "seductive": "😘",
        }
        icon = mood_icons.get(self.current_mood, "")
        return f"{icon} {self.get_current_mood_display()}"

    def get_status_display_with_icon(self):
        """Returns the status with an appropriate icon"""
        status_icons = {
            "available": "🟢",
            "busy": "🔴",
            "away": "🟠",
            "looking": "🔍",
            "private": "🔒",
        }
        icon = status_icons.get(self.current_status, "")
        if self.custom_status:
            return f"{icon} {self.custom_status}"
        return f"{icon} {self.get_current_status_display()}"


class CharacterInfo(models.Model):
    """
    Character additional information fields
    """

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="info_fields",
        verbose_name=_("Character"),
    )
    field = models.ForeignKey(
        InfoField,
        on_delete=models.CASCADE,
        related_name="character_values",
        verbose_name=_("Field"),
    )
    value = models.TextField(_("Value"))

    class Meta:
        verbose_name = _("Character Information")
        verbose_name_plural = _("Character Information")
        unique_together = ("character", "field")

    def __str__(self):
        return f"{self.character.name} - {self.field.name}"


class CharacterKink(models.Model):
    """
    Character kink preferences
    """

    RATING_CHOICES = [
        ("fave", _("Favorite")),
        ("yes", _("Yes")),
        ("maybe", _("Maybe")),
        ("no", _("No")),
    ]

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="kinks",
        verbose_name=_("Character"),
    )
    kink = models.ForeignKey(
        Kink,
        on_delete=models.CASCADE,
        related_name="character_ratings",
        verbose_name=_("Kink"),
    )
    rating = models.CharField(_("Rating"), max_length=10, choices=RATING_CHOICES)

    class Meta:
        verbose_name = _("Character Kink")
        verbose_name_plural = _("Character Kinks")
        unique_together = ("character", "kink")

    def __str__(self):
        return f"{self.character.name} - {self.kink.name}: {self.rating}"


class CustomKink(models.Model):
    """
    Custom kinks created by users
    """

    RATING_CHOICES = [
        ("fave", _("Favorite")),
        ("yes", _("Yes")),
        ("maybe", _("Maybe")),
        ("no", _("No")),
    ]

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="custom_kinks",
        verbose_name=_("Character"),
    )
    name = models.CharField(_("Kink Name"), max_length=100)
    category = models.CharField(_("Category"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)
    rating = models.CharField(_("Rating"), max_length=10, choices=RATING_CHOICES)

    class Meta:
        verbose_name = _("Custom Kink")
        verbose_name_plural = _("Custom Kinks")
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.character.name} - {self.name}: {self.rating}"


class CharacterImage(models.Model):
    """
    Character images
    """

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Character"),
    )
    image = models.ImageField(_("Image"), upload_to="character_images/")
    title = models.CharField(_("Title"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)
    is_primary = models.BooleanField(_("Primary Image"), default=False)
    order = models.PositiveIntegerField(_("Display Order"), default=0)
    uploaded_at = models.DateTimeField(_("Uploaded At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Character Image")
        verbose_name_plural = _("Character Images")
        ordering = ["-is_primary", "order", "uploaded_at"]

    def __str__(self):
        return f"{self.character.name} - {self.title or 'Image'}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image
        if self.is_primary:
            CharacterImage.objects.filter(
                character=self.character, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        # If this is the first image, make it primary
        if (
            not self.pk
            and CharacterImage.objects.filter(character=self.character).count() == 0
        ):
            self.is_primary = True

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "characters:image_detail",
            kwargs={"character_pk": self.character.pk, "pk": self.pk},
        )

    def get_filename(self):
        return os.path.basename(self.image.name)

    def get_file_extension(self):
        name, extension = os.path.splitext(self.image.name)
        return extension.lower()[1:] if extension else ""

    def get_file_size(self):
        if self.image and hasattr(self.image, "size"):
            return self.image.size
        return 0

    def get_file_size_display(self):
        """Returns the file size with appropriate units (KB, MB)"""
        size = self.get_file_size()
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"


class CharacterRating(models.Model):
    """
    Ratings for a character
    """

    RATING_CHOICES = [
        (1, _("1 - Poor")),
        (2, _("2 - Fair")),
        (3, _("3 - Average")),
        (4, _("4 - Good")),
        (5, _("5 - Excellent")),
    ]

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=_("Character"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="character_ratings",
        verbose_name=_("User"),
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"),
        choices=RATING_CHOICES,
        validators=[
            django.core.validators.MinValueValidator(1),
            django.core.validators.MaxValueValidator(5),
        ],
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Character Rating")
        verbose_name_plural = _("Character Ratings")
        unique_together = ("character", "user")

    def __str__(self):
        return f"{self.character.name}: {self.rating} stars by {self.user.username}"


class CharacterComment(models.Model):
    """
    Comments left on a character's profile
    """

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Character"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="character_comments",
        verbose_name=_("Author"),
    )
    content = models.TextField(_("Content"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    is_hidden = models.BooleanField(_("Hidden"), default=False)

    class Meta:
        verbose_name = _("Character Comment")
        verbose_name_plural = _("Character Comments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.character.name}"

    def is_edited(self):
        """Check if the comment has been edited"""
        time_difference = self.updated_at - self.created_at
        return time_difference.seconds > 60  # More than a minute difference

    def hide(self):
        """Hide the comment"""
        self.is_hidden = True
        self.save(update_fields=["is_hidden"])

    def unhide(self):
        """Unhide the comment"""
        self.is_hidden = False
        self.save(update_fields=["is_hidden"])
