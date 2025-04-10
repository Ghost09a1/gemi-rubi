from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from rpg_platform.apps.messages.models import ChatRoom, ChatMessage
from rpg_platform.apps.accounts.models import User
from .models import ChatRoom
from django.urls import reverse_lazy

# ✅ Show all rooms user is in
@login_required
def room_list(request):
    rooms = ChatRoom.objects.filter(participants=request.user)
    return render(request, 'messages/room_list.html', {'chat_rooms': rooms})

# ✅ Show single chat room detail
@login_required
def room_detail(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk, participants=request.user)
    messages = room.chat_messages.all().order_by('timestamp')
    return render(request, 'messages/room_detail.html', {
        'room': room,
        'messages': messages
    })

# ✅ Already present - just decorator added
@method_decorator(login_required, name='dispatch')
class ChatMessageCreateView(CreateView):
    model = ChatMessage
    fields = '__all__'
    template_name = 'messages/chatmessage_form.html'

@method_decorator(login_required, name='dispatch')
class ChatRoomCreateView(CreateView):
    model = ChatRoom
    fields = ['name', 'description', 'participants']
    template_name = 'messages/chatroom_form.html'
    success_url = reverse_lazy('messages:room_list')  # 👈 Redirect after creation