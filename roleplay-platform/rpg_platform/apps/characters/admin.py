from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rpg_platform.apps.characters.models import (
    InfoCategory,
    InfoField,
    KinkCategory,
    Kink,
    Character,
    CharacterInfo,
    CharacterKink,
    CustomKink,
    CharacterImage,
    CharacterRating,
    CharacterComment,
)


class InfoFieldInline(admin.TabularInline):
    model = InfoField
    extra = 1


@admin.register(InfoCategory)
class InfoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    inlines = [InfoFieldInline]


@admin.register(InfoField)
class InfoFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'required', 'order')
    list_filter = ('category', 'required')
    search_fields = ('name', 'description')


class KinkInline(admin.TabularInline):
    model = Kink
    extra = 1


@admin.register(KinkCategory)
class KinkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    inlines = [KinkInline]


@admin.register(Kink)
class KinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('name', 'description')


class CharacterInfoInline(admin.TabularInline):
    model = CharacterInfo
    extra = 1


class CharacterKinkInline(admin.TabularInline):
    model = CharacterKink
    extra = 1


class CustomKinkInline(admin.TabularInline):
    model = CustomKink
    extra = 1


class CharacterImageInline(admin.TabularInline):
    model = CharacterImage
    extra = 1


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'gender', 'species', 'created_at', 'public')
    list_filter = ('gender', 'public', 'created_at')
    search_fields = ('name', 'user__username', 'species')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'public')
        }),
        (_('Basic Information'), {
            'fields': ('gender', 'species', 'height', 'body_type', 'age')
        }),
        (_('Description'), {
            'fields': ('personality', 'background', 'appearance')
        }),
        (_('Status Information'), {
            'fields': ('current_status', 'current_mood', 'custom_status', 'allow_random_rp')
        }),
        (_('Private Information'), {
            'fields': ('private_details',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'views'),
            'classes': ('collapse',)
        }),
    )
    inlines = [
        CharacterInfoInline,
        CharacterImageInline,
        CharacterKinkInline,
        CustomKinkInline,
    ]


@admin.register(CharacterInfo)
class CharacterInfoAdmin(admin.ModelAdmin):
    list_display = ('character', 'field', 'value')
    list_filter = ('character', 'field')
    search_fields = ('character__name', 'field__name', 'value')


@admin.register(CharacterKink)
class CharacterKinkAdmin(admin.ModelAdmin):
    list_display = ('character', 'kink', 'rating')
    list_filter = ('character', 'kink', 'rating')
    search_fields = ('character__name', 'kink__name')


@admin.register(CustomKink)
class CustomKinkAdmin(admin.ModelAdmin):
    list_display = ('character', 'name', 'category', 'rating')
    list_filter = ('character', 'rating', 'category')
    search_fields = ('character__name', 'name', 'description')


@admin.register(CharacterImage)
class CharacterImageAdmin(admin.ModelAdmin):
    list_display = ('character', 'title', 'is_primary', 'order')
    list_filter = ('character', 'is_primary')
    search_fields = ('character__name', 'title', 'description')


@admin.register(CharacterRating)
class CharacterRatingAdmin(admin.ModelAdmin):
    list_display = ('character', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('character__name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CharacterComment)
class CharacterCommentAdmin(admin.ModelAdmin):
    list_display = ('character', 'author', 'short_content', 'is_reply', 'is_hidden', 'created_at')
    list_filter = ('is_hidden', 'created_at')
    search_fields = ('character__name', 'author__username', 'content')
    actions = ['hide_comments', 'unhide_comments']
    readonly_fields = ('created_at', 'updated_at')

    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = _('Content')

    def is_reply(self, obj):
        return hasattr(obj, 'parent') and obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = _('Is Reply')

    def hide_comments(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, _(f"{updated} comment(s) have been hidden."))
    hide_comments.short_description = _("Hide selected comments")

    def unhide_comments(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request, _(f"{updated} comment(s) have been unhidden."))
    unhide_comments.short_description = _("Unhide selected comments")
