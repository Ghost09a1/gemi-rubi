from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    name = 'rpg_platform.apps.accounts'
    label = 'accounts'
    verbose_name = _('Accounts')

    def ready(self):
        import rpg_platform.apps.accounts.signals  # noqa
