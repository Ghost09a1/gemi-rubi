from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Q, F, Sum, Value, Case, When
from django.db import transaction
import logging
import math

from rpg_platform.apps.characters.models import Character, CharacterRating, CharacterComment
from .models import CharacterRecommendation, UserSimilarity, UserPreference

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_recommendations_for_user(user_id):
    """
    Generate character recommendations for a user.

    This is the main entry point for recommendation generation. It combines
    multiple recommendation strategies and saves the results to the database.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User ID {user_id} not found when generating recommendations")
        return

    logger.info(f"Generating recommendations for user {user.username}")

    # Clear existing non-dismissed recommendations
    CharacterRecommendation.objects.filter(
        user=user,
        is_dismissed=False
    ).delete()

    # Get characters this user has already rated or commented on
    interacted_character_ids = set(list(
        CharacterRating.objects.filter(user=user).values_list('character_id', flat=True)
    ) + list(
        CharacterComment.objects.filter(author=user).values_list('character_id', flat=True)
    ))

    # Get characters this user owns
    own_character_ids = set(
        Character.objects.filter(user=user).values_list('id', flat=True)
    )

    # Combine all characters to exclude from recommendations
    excluded_character_ids = interacted_character_ids.union(own_character_ids)

    # Only recommend public characters
    base_queryset = Character.objects.filter(is_public=True).exclude(id__in=excluded_character_ids)

    # Generate recommendations using different strategies
    recommendations = []

    # Strategy 1: Similar to rated characters
    similar_recs = recommend_similar_to_rated(user, base_queryset)
    recommendations.extend(similar_recs)

    # Strategy 2: Popular in the community
    popular_recs = recommend_popular_characters(user, base_queryset)
    recommendations.extend(popular_recs)

    # Strategy 3: Recommended by similar users
    similar_user_recs = recommend_from_similar_users(user, base_queryset)
    recommendations.extend(similar_user_recs)

    # Strategy 4: Recently active characters
    recent_recs = recommend_recently_active(user, base_queryset)
    recommendations.extend(recent_recs)

    # Save all recommendations to the database
    with transaction.atomic():
        CharacterRecommendation.objects.bulk_create(recommendations)

    logger.info(f"Generated {len(recommendations)} recommendations for user {user.username}")


def recommend_similar_to_rated(user, queryset, max_results=5):
    """Recommend characters similar to those the user has rated highly"""
    # Find characters the user has rated 4-5 stars
    highly_rated = CharacterRating.objects.filter(
        user=user,
        rating__gte=4
    ).select_related('character')

    if not highly_rated.exists():
        return []

    # Get user's preferences
    user_preferences = UserPreference.objects.filter(user=user)

    preferences_by_attr = {}
    for pref in user_preferences:
        if pref.attribute not in preferences_by_attr:
            preferences_by_attr[pref.attribute] = []
        preferences_by_attr[pref.attribute].append({
            'value': pref.value,
            'weight': pref.weight
        })

    recommendations = []

    # Get characters that match preferences
    for character in queryset[:50]:  # Limit to prevent performance issues
        score = 0

        # Score based on species preference
        if 'species' in preferences_by_attr and character.species:
            for pref in preferences_by_attr['species']:
                if pref['value'].lower() == character.species.lower():
                    score += pref['weight']

        # Score based on gender preference
        if 'gender' in preferences_by_attr and character.gender:
            for pref in preferences_by_attr['gender']:
                if pref['value'] == character.gender:
                    score += pref['weight']

        # Only include if there's a meaningful match
        if score > 0:
            recommendations.append(
                CharacterRecommendation(
                    user=user,
                    character=character,
                    score=min(5.0, score),  # Cap at 5.0
                    reason='similar_rating'
                )
            )

    # Sort by score and limit results
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations[:max_results]


def recommend_popular_characters(user, queryset, max_results=3):
    """Recommend popular characters from the community"""
    # Find characters with high ratings and many comments
    popular_characters = queryset.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings'),
        comment_count=Count('comments')
    ).filter(
        avg_rating__gte=4,
        rating_count__gte=3
    ).order_by('-avg_rating', '-rating_count', '-comment_count')[:max_results]

    recommendations = []

    for character in popular_characters:
        # Score based on average rating and number of ratings
        score = min(5.0, (character.avg_rating * 0.8) + (min(1.0, character.rating_count / 10) * 0.2 * 5))

        recommendations.append(
            CharacterRecommendation(
                user=user,
                character=character,
                score=score,
                reason='popular'
            )
        )

    return recommendations


def recommend_from_similar_users(user, queryset, max_results=5):
    """Recommend characters that similar users have rated highly"""
    # Find similar users
    similar_users = UserSimilarity.objects.filter(
        user1=user,
        similarity_score__gte=0.5
    ).order_by('-similarity_score')[:10]

    if not similar_users.exists():
        # Calculate similarities first if none exist
        calculate_user_similarities(user)
        similar_users = UserSimilarity.objects.filter(
            user1=user,
            similarity_score__gte=0.5
        ).order_by('-similarity_score')[:10]

    similar_user_ids = [sim.user2_id for sim in similar_users]

    if not similar_user_ids:
        return []

    # Get characters that similar users have rated highly
    highly_rated_characters = CharacterRating.objects.filter(
        user_id__in=similar_user_ids,
        rating__gte=4
    ).values('character_id').annotate(
        avg_rating=Avg('rating'),
        count=Count('character_id')
    ).filter(count__gte=2).order_by('-avg_rating', '-count')

    recommendations = []

    for item in highly_rated_characters:
        try:
            character = queryset.get(id=item['character_id'])

            # Score based on average rating and similarity of users
            score = min(5.0, item['avg_rating'] * 0.8 + (item['count'] / 5) * 0.2 * 5)

            recommendations.append(
                CharacterRecommendation(
                    user=user,
                    character=character,
                    score=score,
                    reason='friend_rated'
                )
            )

            if len(recommendations) >= max_results:
                break

        except Character.DoesNotExist:
            continue

    return recommendations


def recommend_recently_active(user, queryset, max_results=3):
    """Recommend recently active characters"""
    # Get recently updated characters
    recent_characters = queryset.order_by('-updated_at')[:max_results]

    recommendations = []

    for character in recent_characters:
        recommendations.append(
            CharacterRecommendation(
                user=user,
                character=character,
                score=3.0,  # Fixed score for recency
                reason='recently_active'
            )
        )

    return recommendations


def calculate_user_similarities(user):
    """Calculate similarity between a user and other users based on ratings"""
    # Get all users who have rated at least 3 characters
    active_users = User.objects.annotate(
        rating_count=Count('character_ratings')
    ).filter(
        rating_count__gte=3
    ).exclude(
        id=user.id
    )[:50]  # Limit to prevent performance issues

    # Get this user's ratings
    user_ratings = {
        r.character_id: r.rating
        for r in CharacterRating.objects.filter(user=user)
    }

    if not user_ratings:
        return

    similarities = []

    for other_user in active_users:
        # Get other user's ratings
        other_ratings = {
            r.character_id: r.rating
            for r in CharacterRating.objects.filter(user=other_user)
        }

        # Find common rated characters
        common_characters = set(user_ratings.keys()) & set(other_ratings.keys())

        if len(common_characters) < 2:
            continue  # Not enough common ratings

        # Calculate cosine similarity
        dot_product = sum(user_ratings[cid] * other_ratings[cid] for cid in common_characters)
        magnitude1 = math.sqrt(sum(rating ** 2 for rating in user_ratings.values()))
        magnitude2 = math.sqrt(sum(rating ** 2 for rating in other_ratings.values()))

        similarity = dot_product / (magnitude1 * magnitude2) if magnitude1 * magnitude2 > 0 else 0

        # Add weight for number of common ratings
        similarity_adj = similarity * (min(1, len(common_characters) / 10) * 0.5 + 0.5)

        similarities.append(
            UserSimilarity(
                user1=user,
                user2=other_user,
                similarity_score=min(1.0, similarity_adj)
            )
        )

    # Save all similarities
    with transaction.atomic():
        # Delete existing similarities
        UserSimilarity.objects.filter(user1=user).delete()

        # Create new ones
        UserSimilarity.objects.bulk_create(similarities)

    return similarities
