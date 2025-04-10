from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Notification, NotificationCategory, NotificationPreference


@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'order', 'icon', 'color')
    search_fields = ('name', 'key')
    list_filter = ('color',)
    ordering = ('order', 'name')

    actions = ['create_default_categories']

    def create_default_categories(self, request, queryset):
        """Action to create default categories"""
        NotificationCategory.create_defaults()
        self.message_user(request, _("Default notification categories have been created."))

    create_default_categories.short_description = _("Create default notification categories")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'in_app', 'email', 'push', 'sound')
    list_filter = ('category', 'in_app', 'email', 'push', 'sound')
    search_fields = ('user__username', 'category__name')
    raw_id_fields = ('user',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'category', 'actor', 'short_verb', 'created_at', 'read', 'is_deleted')
    list_filter = ('notification_type', 'category', 'read', 'is_deleted', 'priority', 'created_at')
    search_fields = ('user__username', 'actor__username', 'verb')
    readonly_fields = ('created_at', 'read_at')
    raw_id_fields = ('user', 'actor')
    date_hierarchy = 'created_at'

    def short_verb(self, obj):
        """Return a truncated version of the verb for display in the list"""
        max_length = 40
        if len(obj.verb) > max_length:
            return f"{obj.verb[:max_length]}..."
        return obj.verb

    short_verb.short_description = _("Verb")

    fieldsets = (
        (None, {
            'fields': ('user', 'notification_type', 'category', 'actor', 'verb', 'description')
        }),
        (_('Content'), {
            'fields': ('action_object_id', 'target_id', 'url', 'image_url', 'priority'),
        }),
        (_('Status'), {
            'fields': ('read', 'read_at', 'is_deleted', 'created_at'),
        }),
        (_('Extra Data'), {
            'fields': ('extra_data',),
            'classes': ('collapse',),
        }),
    )
