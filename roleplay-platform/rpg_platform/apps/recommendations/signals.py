from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Avg, Q
from django.contrib.auth import get_user_model

from rpg_platform.apps.characters.models import CharacterRating, CharacterComment
from .models import CharacterRecommendation, UserSimilarity, UserPreference

User = get_user_model()


@receiver(post_save, sender=CharacterRating)
def update_recommendations_on_rating(sender, instance, created, **kwargs):
    """
    Update recommendations when a user rates a character
    """
    if created:
        # This is a new rating, update recommendations
        from .tasks import generate_recommendations_for_user
        generate_recommendations_for_user(instance.user.id)

        # Also update preferences based on this rating
        update_user_preferences_from_rating(instance)


@receiver(post_save, sender=CharacterComment)
def update_recommendations_on_comment(sender, instance, created, **kwargs):
    """
    Update recommendations when a user comments on a character
    """
    if created:
        # Schedule recommendation update
        from .tasks import generate_recommendations_for_user
        generate_recommendations_for_user(instance.author.id)


def update_user_preferences_from_rating(rating_instance):
    """
    Update user preferences based on a character rating
    """
    # Only consider high ratings (4-5 stars)
    if rating_instance.rating < 4:
        return

    character = rating_instance.character
    user = rating_instance.user

    # Update preference for species
    if character.species:
        UserPreference.objects.update_or_create(
            user=user,
            attribute='species',
            value=character.species,
            defaults={
                'weight': calculate_preference_weight(user, 'species', character.species)
            }
        )

    # Update preference for gender
    if character.gender:
        UserPreference.objects.update_or_create(
            user=user,
            attribute='gender',
            value=character.gender,
            defaults={
                'weight': calculate_preference_weight(user, 'gender', character.gender)
            }
        )


def calculate_preference_weight(user, attribute, value):
    """
    Calculate preference weight based on user's rating history
    """
    # Get all characters the user has rated highly (4-5 stars)
    rated_character_ids = CharacterRating.objects.filter(
        user=user,
        rating__gte=4
    ).values_list('character_id', flat=True)

    if not rated_character_ids:
        return 1.0

    # Count how many of those characters have the same attribute value
    from rpg_platform.apps.characters.models import Character

    # Build the filter based on the attribute
    if attribute == 'species':
        filter_kwargs = {'species': value}
    elif attribute == 'gender':
        filter_kwargs = {'gender': value}
    else:
        return 1.0

    matching_count = Character.objects.filter(
        id__in=rated_character_ids,
        **filter_kwargs
    ).count()

    # Calculate weight as a ratio (with min value of 1.0)
    total_rated = len(rated_character_ids)
    if total_rated == 0:
        return 1.0

    ratio = matching_count / total_rated
    # Apply a boost for highly preferred attributes
    weight = max(1.0, ratio * 3)

    return min(5.0, weight)  # Cap at 5.0
