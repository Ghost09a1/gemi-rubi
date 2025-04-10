from django.db import models
from rpg_platform.apps.accounts.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Update the updated_at field each time a message is added."""
        super().save(*args, **kwargs)

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='chat_messages', on_delete=models.CASCADE, )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.chat_room.save()

    def save(self, *args, **kwargs):
        self.chat_room.save()
        super().save(*args, **kwargs)