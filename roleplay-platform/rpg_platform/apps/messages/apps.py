from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rpg_platform.apps.messages'
    verbose_name = _('Messages')
    label = 'chat_messages'  # Added unique label to avoid conflict with Django's built-in messages

    def ready(self):
        import rpg_platform.apps.messages.signals  # noqa
