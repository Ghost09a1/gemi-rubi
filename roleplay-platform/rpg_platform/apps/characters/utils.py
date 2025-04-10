from django.db.models import Count, Avg, Q, F, ExpressionWrapper, FloatField
from django.contrib.auth import get_user_model
from collections import Counter

from .models import Character, CharacterKink, CharacterRating, CharacterComment, Kink

User = get_user_model()


def recommend_characters_for_user(user, limit=10):
    """
    Recommend characters for a user based on their ratings, interactions,
    and preferences.

    Algorithm takes into account:
    1. Characters with similar kinks to ones the user has rated highly
    2. Characters from users whose characters the user has rated highly
    3. Collaborative filtering - characters liked by users with similar tastes
    4. Popular characters the user hasn't interacted with yet

    Returns a QuerySet of recommended Character objects.
    """
    if not user.is_authenticated:
        # For anonymous users, just return popular characters
        return get_popular_characters(limit=limit)

    # Get characters the user has already interacted with
    rated_character_ids = CharacterRating.objects.filter(user=user).values_list('character_id', flat=True)
    commented_character_ids = CharacterComment.objects.filter(author=user).values_list('character_id', flat=True)
    user_character_ids = Character.objects.filter(user=user).values_list('id', flat=True)

    # Combine all ids of characters the user has interacted with
    interacted_character_ids = set(rated_character_ids) | set(commented_character_ids) | set(user_character_ids)

    # 1. Find kinks that the user seems to like based on their ratings
    user_ratings = CharacterRating.objects.filter(user=user, rating__gte=4)
    highly_rated_character_ids = user_ratings.values_list('character_id', flat=True)

    if highly_rated_character_ids:
        # Get kinks from characters the user rated highly
        liked_kinks = CharacterKink.objects.filter(
            character_id__in=highly_rated_character_ids,
            rating__in=['yes', 'fave']
        ).values_list('kink_id', flat=True)

        # Count frequency of each kink
        kink_counter = Counter(liked_kinks)
        favored_kink_ids = [kink_id for kink_id, _ in kink_counter.most_common(20)]

        # Find characters that have these kinks
        kink_based_character_ids = CharacterKink.objects.filter(
            kink_id__in=favored_kink_ids,
            rating__in=['yes', 'fave'],
            character__public=True
        ).exclude(
            character_id__in=interacted_character_ids
        ).values_list('character_id', flat=True)

        # Convert to set for faster lookups
        kink_based_character_ids = set(kink_based_character_ids)
    else:
        kink_based_character_ids = set()

    # 2. Find characters from creators the user seems to like
    if highly_rated_character_ids:
        liked_creators = Character.objects.filter(
            id__in=highly_rated_character_ids
        ).values_list('user_id', flat=True)

        # Count frequency of each creator
        creator_counter = Counter(liked_creators)
        favored_creator_ids = [creator_id for creator_id, _ in creator_counter.most_common(10)]

        # Find other characters from these creators
        creator_based_character_ids = Character.objects.filter(
            user_id__in=favored_creator_ids,
            public=True
        ).exclude(
            id__in=interacted_character_ids
        ).values_list('id', flat=True)

        creator_based_character_ids = set(creator_based_character_ids)
    else:
        creator_based_character_ids = set()

    # 3. Collaborative filtering - find users with similar tastes
    if rated_character_ids:
        # Find users who rated the same characters that the user rated highly
        similar_users = CharacterRating.objects.filter(
            character_id__in=highly_rated_character_ids,
            rating__gte=4
        ).exclude(
            user=user
        ).values_list('user_id', flat=True)

        # Get characters that these similar users rated highly
        collab_based_character_ids = CharacterRating.objects.filter(
            user_id__in=similar_users,
            rating__gte=4,
            character__public=True
        ).exclude(
            character_id__in=interacted_character_ids
        ).values_list('character_id', flat=True)

        collab_based_character_ids = set(collab_based_character_ids)
    else:
        collab_based_character_ids = set()

    # 4. Popular characters the user hasn't interacted with
    # Calculate a character popularity score based on ratings and comments
    popular_character_ids = set(get_popular_characters().exclude(
        id__in=interacted_character_ids
    ).values_list('id', flat=True)[:50])

    # Combine recommendation sources with different weights
    final_character_ids = set()

    # Add collaborative filtering recommendations with highest priority
    final_character_ids.update(collab_based_character_ids)

    # Add kink-based recommendations next
    final_character_ids.update(kink_based_character_ids)

    # Add creator-based recommendations
    final_character_ids.update(creator_based_character_ids)

    # Fill in with popular characters if needed
    remaining_slots = limit - len(final_character_ids)
    if remaining_slots > 0 and popular_character_ids:
        # Add popular characters not already in the recommendations
        additional_popular = list(popular_character_ids - final_character_ids)[:remaining_slots]
        final_character_ids.update(additional_popular)

    # Convert back to a QuerySet with proper ordering
    if final_character_ids:
        # Convert set to list for use in WHERE IN
        character_ids_list = list(final_character_ids)

        # Create custom ordering to preserve our priority
        from django.db.models.expressions import Case, When
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(character_ids_list)])

        # Return the characters with our custom ordering
        return Character.objects.filter(id__in=character_ids_list).order_by(preserved_order)[:limit]

    # Fallback to popular characters if we couldn't make good recommendations
    return get_popular_characters(exclude_ids=interacted_character_ids, limit=limit)


def get_popular_characters(exclude_ids=None, limit=10):
    """
    Get popular characters based on ratings and comment count
    """
    queryset = Character.objects.filter(public=True)

    if exclude_ids:
        queryset = queryset.exclude(id__in=exclude_ids)

    # Annotate with average rating and comment count
    queryset = queryset.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings'),
        comment_count=Count('comments')
    )

    # Calculate a popularity score: rating_count * avg_rating + comment_count
    queryset = queryset.annotate(
        popularity_score=ExpressionWrapper(
            (F('avg_rating') * F('rating_count')) + F('comment_count'),
            output_field=FloatField()
        )
    )

    # Filter out characters with no ratings (null avg_rating)
    queryset = queryset.filter(rating_count__gt=0)

    # Order by popularity score
    return queryset.order_by('-popularity_score')[:limit]


def recommend_characters_by_kinks(kink_ids, exclude_ids=None, limit=10):
    """
    Recommend characters that match the given kink IDs
    """
    queryset = Character.objects.filter(
        characterkink__kink_id__in=kink_ids,
        characterkink__rating__in=['yes', 'fave'],
        public=True
    )

    if exclude_ids:
        queryset = queryset.exclude(id__in=exclude_ids)

    # Annotate with the count of matching kinks
    queryset = queryset.annotate(
        matching_kink_count=Count('characterkink', filter=Q(
            characterkink__kink_id__in=kink_ids,
            characterkink__rating__in=['yes', 'fave']
        ))
    )

    # Also annotate with average rating and total rating count
    queryset = queryset.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings')
    )

    # Order by matching kink count (descending) and then average rating (descending)
    return queryset.order_by('-matching_kink_count', '-avg_rating')[:limit]
