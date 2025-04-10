# Signal handlers for character-related events
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from rpg_platform.apps.characters.models import Character, CharacterImage
