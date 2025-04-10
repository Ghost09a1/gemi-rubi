from django.db import models
from rpg_platform.apps.accounts.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='chat_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)