from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import CharacterRecommendation, UserSimilarity, UserPreference


@admin.register(CharacterRecommendation)
class CharacterRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'character', 'score', 'reason', 'created_at', 'is_dismissed')
    list_filter = ('reason', 'is_dismissed', 'created_at')
    search_fields = ('user__username', 'character__name')
    raw_id_fields = ('user', 'character')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(UserSimilarity)
class UserSimilarityAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'similarity_score', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user1__username', 'user2__username')
    raw_id_fields = ('user1', 'user2')
    readonly_fields = ('updated_at',)


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'attribute', 'value', 'weight', 'updated_at')
    list_filter = ('attribute', 'updated_at')
    search_fields = ('user__username', 'attribute', 'value')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
