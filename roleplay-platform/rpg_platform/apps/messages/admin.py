from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    ChatRoom, ChatMessage, DiceRoll, SceneBoundary,
    QuickResponse, SceneSetting, PrivateNote
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'room_type', 'created_at', 'is_active', 'participants_list', 'scene_status')
    list_filter = ('room_type', 'is_active', 'created_at', 'scene_status')
    search_fields = ('name', 'participants__username')
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'participants', 'is_active')
        }),
        (_('Scene Settings'), {
            'fields': ('scene_description', 'scene_background_color', 'scene_image_url',
                       'scene_music_url', 'scene_intensity', 'scene_status')
        }),
        (_('Immersion Settings'), {
            'fields': ('typing_effect_enabled', 'message_timing_enabled')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def participants_list(self, obj):
        return ", ".join([p.username for p in obj.participants.all()[:5]])
    participants_list.short_description = _('Participants')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_room', 'sender', 'receiver', 'character', 'short_message', 'message_type', 'created_at', 'read')
    list_filter = ('read', 'created_at', 'is_system_message', 'is_ooc', 'message_type')
    search_fields = ('message', 'sender__username', 'receiver__username')
    raw_id_fields = ('chat_room', 'sender', 'receiver', 'character')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('chat_room', 'sender', 'receiver', 'character', 'message', 'read')
        }),
        (_('Message Properties'), {
            'fields': ('message_type', 'is_system_message', 'is_ooc', 'delay_seconds', 'typing_duration_ms')
        }),
        (_('Metadata'), {
            'fields': ('created_at',)
        }),
    )

    def short_message(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    short_message.short_description = _('Message')


@admin.register(DiceRoll)
class DiceRollAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_room', 'user', 'character', 'formula', 'total', 'created_at', 'is_private')
    list_filter = ('is_private', 'created_at')
    search_fields = ('formula', 'user__username')
    raw_id_fields = ('chat_room', 'user', 'character')
    readonly_fields = ('created_at', 'result_display')

    def result_display(self, obj):
        if not obj.result:
            return _('No results')

        rolls = obj.get_individual_results()
        modifiers = obj.result.get('modifiers', 0) if isinstance(obj.result, dict) else 0

        rolls_display = ", ".join([f"d{r['sides']}: {r['value']}" for r in rolls])
        modifier_display = f" {modifiers:+d}" if modifiers != 0 else ""

        return f"{rolls_display}{modifier_display} = {obj.total}"
    result_display.short_description = _('Roll Results')


@admin.register(SceneBoundary)
class SceneBoundaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_room', 'all_participants_agreed', 'created_at', 'updated_at', 'last_reviewed')
    list_filter = ('all_participants_agreed', 'created_at')
    search_fields = ('chat_room__name',)
    raw_id_fields = ('chat_room',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuickResponse)
class QuickResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'character', 'response_type', 'use_count', 'created_at')
    list_filter = ('response_type', 'created_at')
    search_fields = ('name', 'content', 'user__username')
    raw_id_fields = ('user', 'character')
    readonly_fields = ('created_at', 'updated_at', 'use_count')


@admin.register(SceneSetting)
class SceneSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'is_public', 'use_count', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at', 'use_count')


@admin.register(PrivateNote)
class PrivateNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'chat_room', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content', 'user__username')
    raw_id_fields = ('user', 'chat_room')
    readonly_fields = ('created_at', 'updated_at')
