from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from rpg_platform.apps.accounts.models import User
from .models import ChatRoom, ChatMessage

# List view for chat rooms
class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'messages/chatroom_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

# Detail view for a chat room
class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'messages/chatroom_detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = ChatMessage.objects.filter(chat_room=self.object).order_by('created_at')
        return context

# New style detail view for a chat room
class ChatRoomDetailNewView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'messages/chatroom_detail_new.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = ChatMessage.objects.filter(chat_room=self.object).order_by('created_at')
        return context

# Create a new message in a chat room
@login_required
def send_message(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = ChatMessage.objects.create(
                sender=request.user,
                chat_room=room,
                message=content
            )
            # Return JSON response for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': message.id,
                        'sender': message.sender.username,
                        'content': message.message,
                        'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            return redirect('messages:room_detail', pk=pk)

    # Handle GET request or form errors
    return redirect('messages:room_detail', pk=pk)

# Create a new chat message (form-based)
@method_decorator(login_required, name='dispatch')
class ChatMessageCreateView(CreateView):
    model = ChatMessage
    fields = ['message', 'chat_room']
    template_name = 'messages/chatmessage_form.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('messages:room_detail', kwargs={'pk': self.object.chat_room.pk})

# Create a new chat room
@method_decorator(login_required, name='dispatch')
class ChatRoomCreateView(CreateView):
    model = ChatRoom
    fields = ['name', 'room_type']
    template_name = 'messages/chatroom_form.html'
    success_url = reverse_lazy('messages:room_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add the creator as a participant
        self.object.participants.add(self.request.user)
        return response

# Update a chat room
@method_decorator(login_required, name='dispatch')
class ChatRoomUpdateView(UpdateView):
    model = ChatRoom
    fields = ['name', 'room_type']
    template_name = 'messages/chatroom_form.html'

    def get_success_url(self):
        return reverse('messages:room_detail', kwargs={'pk': self.object.pk})

# Delete a chat room
@method_decorator(login_required, name='dispatch')
class ChatRoomDeleteView(DeleteView):
    model = ChatRoom
    template_name = 'messages/chatroom_confirm_delete.html'
    success_url = reverse_lazy('messages:room_list')

# Create a private chat room with a specific user
@login_required
def create_private_room(request, username):
    """
    Create or get a private chat room with the specified user.
    If a room already exists between the users, redirect to that room.
    """
    try:
        # Get target user or 404
        other_user = get_object_or_404(User, username=username)

        # Don't allow chats with yourself
        if other_user == request.user:
            messages.error(request, _("You cannot create a chat room with yourself."))
            return redirect('dashboard:home')

        # Check if a private room already exists between these users
        existing_rooms = ChatRoom.objects.filter(
            room_type='private',
            participants=request.user
        ).filter(
            participants=other_user
        ).distinct()

        if existing_rooms.exists():
            # Return the first existing room
            return redirect('messages:room_detail', pk=existing_rooms.first().pk)

        # Create a new private room
        new_room = ChatRoom.objects.create(
            name=f"Chat with {other_user.username}",
            room_type='private'
        )

        # Add both users as participants
        new_room.participants.add(request.user, other_user)

        # Success message
        messages.success(request, _(f"Chat room with {other_user.username} created successfully."))

        # Redirect to the new room
        return redirect('messages:room_detail', pk=new_room.pk)

    except Exception as e:
        messages.error(request, _(f"Error creating chat room: {str(e)}"))
        return redirect('dashboard:home')

# Scene settings views
class SceneSettingListView(LoginRequiredMixin, ListView):
    model = ChatRoom  # Replace with actual model if you have one
    template_name = 'messages/scene_setting_list.html'
    context_object_name = 'settings'

class SceneSettingCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/scene_setting_form.html'
    fields = ['name']
    success_url = reverse_lazy('messages:scene_setting_list')

class SceneSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/scene_setting_form.html'
    fields = ['name']
    success_url = reverse_lazy('messages:scene_setting_list')

class SceneSettingDeleteView(LoginRequiredMixin, DeleteView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/scene_setting_confirm_delete.html'
    success_url = reverse_lazy('messages:scene_setting_list')

# Scene boundary views
class SceneBoundaryAgreementView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'messages/scene_boundary_agreement.html'
    context_object_name = 'room'

class SceneBoundaryFormView(LoginRequiredMixin, UpdateView):
    model = ChatRoom
    template_name = 'messages/scene_boundary_form.html'
    fields = ['scene_description', 'scene_background_color']

    def get_success_url(self):
        return reverse('messages:room_detail', kwargs={'pk': self.object.pk})

# Quick responses views
class QuickResponseListView(LoginRequiredMixin, ListView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/quick_response_list.html'
    context_object_name = 'responses'

class QuickResponseCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/quick_response_form.html'
    fields = ['name']
    success_url = reverse_lazy('messages:quick_response_list')

class QuickResponseUpdateView(LoginRequiredMixin, UpdateView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/quick_response_form.html'
    fields = ['name']
    success_url = reverse_lazy('messages:quick_response_list')

class QuickResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/quick_response_confirm_delete.html'
    success_url = reverse_lazy('messages:quick_response_list')

# Private notes views
class PrivateNoteListView(LoginRequiredMixin, ListView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/private_note_list.html'
    context_object_name = 'notes'

class PrivateNoteCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/private_note_form.html'
    fields = ['name']
    success_url = reverse_lazy('messages:private_note_list')

class PrivateNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/private_note_form.html'
    fields = ['name']
    success_url = reverse_lazy('messages:private_note_list')

class PrivateNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = ChatRoom  # Replace with actual model
    template_name = 'messages/private_note_confirm_delete.html'
    success_url = reverse_lazy('messages:private_note_list')
