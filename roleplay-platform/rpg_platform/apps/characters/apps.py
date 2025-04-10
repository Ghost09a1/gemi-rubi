from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CharactersConfig(AppConfig):
    name = 'rpg_platform.apps.characters'
    verbose_name = _('Characters')

    def ready(self):
        import rpg_platform.apps.characters.signals  # noqa
