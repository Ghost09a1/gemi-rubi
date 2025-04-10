from django.urls import path
from rpg_platform.apps.messages.views import ChatMessageCreateView

app_name = 'my_messages'

urlpatterns = [
    path('create/', ChatMessageCreateView.as_view(), name='chatmessage_create'),
]