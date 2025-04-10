from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessagesConfig(AppConfig):
    name = 'rpg_platform.apps.messages'
    label = 'my_messages'
    verbose_name = _('Messages')