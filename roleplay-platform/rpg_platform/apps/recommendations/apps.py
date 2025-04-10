from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rpg_platform.apps.recommendations'
    verbose_name = _('Recommendations')

    def ready(self):
        import rpg_platform.apps.recommendations.signals
