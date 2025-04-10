from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rpg_platform.apps.notifications'
    verbose_name = _('Notifications')

    def ready(self):
        import rpg_platform.apps.notifications.signals  # noqa
