from django.views.generic.edit import CreateView
from rpg_platform.apps.messages.models import ChatMessage

class ChatMessageCreateView(CreateView):
    model = ChatMessage
    fields = '__all__'
    template_name = 'messages/chatmessage_form.html'