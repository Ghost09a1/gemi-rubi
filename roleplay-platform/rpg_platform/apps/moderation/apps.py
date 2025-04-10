from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ModerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rpg_platform.apps.moderation'
    verbose_name = _('Moderation')

    def ready(self):
        import rpg_platform.apps.moderation.signals  # noqa
