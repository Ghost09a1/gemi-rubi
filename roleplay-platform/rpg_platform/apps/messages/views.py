from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView,
    DeleteView, FormView, TemplateView
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, Exists, OuterRef, Count, Prefetch
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import logging

from rpg_platform.apps.characters.models import Character

from .models import (
    ChatRoom, ChatMessage, DiceRoll, SceneBoundary,
    QuickResponse, SceneSetting, PrivateNote
)
from .forms import (
    ChatMessageForm, ChatRoomForm, SceneBoundaryForm, QuickResponseForm,
    SceneSettingForm, PrivateNoteForm
)

# Setup logger
logger = logging.getLogger(__name__)

# Chat Room Views
class ChatRoomListView(LoginRequiredMixin, ListView):
    """
    Display a list of chat rooms that the user is a participant in
    """
    model = ChatRoom
    template_name = "messages/chatroom_list.html"
    context_object_name = "rooms"

    def get_queryset(self):
        # Get all chat rooms where the user is a participant
        return ChatRoom.objects.filter(participants=self.request.user).order_by('-last_message_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user's characters for the create room form
        context["characters"] = Character.objects.filter(user=self.request.user)
        return context

class ChatRoomCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new chat room
    """
    model = ChatRoom
    form_class = ChatRoomForm
    template_name = "messages/chatroom_form.html"

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs
        except Exception as e:
            logger.error(f"Error in ChatRoomCreateView.get_form_kwargs: {str(e)}")
            return super().get_form_kwargs()

    def form_valid(self, form):
        try:
            # Set the creator
            form.instance.creator = self.request.user

            # Check for chat room limits (optional)
            user_room_count = ChatRoom.objects.filter(creator=self.request.user).count()
            max_rooms = 50  # Consider moving to settings

            if user_room_count >= max_rooms:
                messages.warning(self.request, _("You have reached your maximum chat room limit."))
                logger.warning(f"User {self.request.user.username} attempted to create a room beyond their limit")
                return self.form_invalid(form)

            # Continue with creating the room
            response = super().form_valid(form)

            # Add the creator as a participant
            self.object.participants.add(self.request.user)

            # Validate participants before adding them
            if form.cleaned_data.get('participants'):
                for user in form.cleaned_data['participants']:
                    # Verify user is not blocked
                    # You might need to implement a check against a Blocked model
                    self.object.participants.add(user)

            # Add system message about room creation
            ChatMessage.objects.create(
                chat_room=self.object,
                sender=self.request.user,
                message=_("Chat room created"),
                is_system_message=True
            )

            messages.success(self.request, _("Chat room created successfully!"))
            logger.info(f"User {self.request.user.username} created chat room ID {self.object.pk} - {self.object.name}")

            return response
        except Exception as e:
            logger.error(f"Error in ChatRoomCreateView.form_valid: {str(e)}")
            messages.error(self.request, _("An error occurred while creating the chat room. Please try again."))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors in the form."))
        logger.warning(f"Chat room creation form invalid for user {self.request.user.username}. Errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('messages:room_detail', kwargs={'pk': self.object.pk})

class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = "messages/chatroom_detail.html"
    context_object_name = "room"

    def get_queryset(self):
        """Ensure users can only access rooms they are participants in"""
        return ChatRoom.objects.filter(participants=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Additional security check before processing the request"""
        try:
            # Get the room object
            room = self.get_object()

            # Check if user is blocked from this room (if you implement room blocking)
            # if room.is_user_blocked(request.user):
            #     messages.error(request, _("You cannot access this chat room."))
            #     return redirect('messages:room_list')

            # Record room visit for analytics (optional)
            # RoomVisit.objects.create(user=request.user, room=room)

            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ChatRoomDetailView.dispatch: {str(e)}")
            messages.error(request, _("An error occurred while accessing the chat room."))
            return redirect('messages:room_list')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)

            # Add user characters for the dropdown
            context["characters"] = Character.objects.filter(user=self.request.user)

            # Get scene boundary information if it exists
            room = self.get_object()

            try:
                context["scene_boundary"] = SceneBoundary.objects.get(chat_room=room)

                # Check if current user has agreed to boundaries
                if context["scene_boundary"].agreed_users.filter(id=self.request.user.id).exists():
                    context["has_agreed"] = True
                else:
                    context["has_agreed"] = False
            except SceneBoundary.DoesNotExist:
                context["scene_boundary"] = None

            # Get user's quick responses
            context["quick_responses"] = QuickResponse.objects.filter(user=self.request.user)

            # Get user's private notes for this room
            context["private_notes"] = PrivateNote.objects.filter(
                user=self.request.user,
                chat_room=room
            ).order_by('-created_at')

            # Get recent messages for initial display
            context["recent_messages"] = ChatMessage.objects.filter(
                chat_room=room
            ).select_related('sender', 'character').order_by('-timestamp')[:50]

            return context
        except Exception as e:
            logger.error(f"Error in ChatRoomDetailView.get_context_data: {str(e)}")
            context = super().get_context_data(**kwargs)
            messages.error(self.request, _("An error occurred while loading chat room data."))
            return context

class ChatRoomDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a chat room
    """
    model = ChatRoom
    template_name = "messages/chatroom_confirm_delete.html"
    success_url = reverse_lazy('messages:room_list')

    def get_queryset(self):
        # Users can only delete rooms they created
        return ChatRoom.objects.filter(creator=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _("Chat room deleted successfully."))
        return response

# New views for the added features

class SceneBoundaryView(LoginRequiredMixin, UpdateView):
    model = SceneBoundary
    form_class = SceneBoundaryForm
    template_name = 'messages/scene_boundary_form.html'

    def get_object(self):
        chat_room = get_object_or_404(ChatRoom, pk=self.kwargs['room_id'], participants=self.request.user)
        obj, created = SceneBoundary.objects.get_or_create(chat_room=chat_room)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = self.object.chat_room
        return context

    def get_success_url(self):
        # Mark boundaries as not agreed upon when they change
        self.object.all_participants_agreed = False
        self.object.last_reviewed = timezone.now()
        self.object.save(update_fields=['all_participants_agreed', 'last_reviewed'])

        # Mark the room as having established boundaries
        self.object.chat_room.has_established_boundaries = True
        self.object.chat_room.save(update_fields=['has_established_boundaries'])

        # Create system message about updated boundaries
        ChatMessage.objects.create(
            chat_room=self.object.chat_room,
            sender=self.request.user,
            receiver=self.request.user,  # In group chats, this is a placeholder
            message=_("Scene boundaries have been updated. All participants should review them."),
            is_system_message=True
        )

        return reverse('messages:room_detail', kwargs={'pk': self.object.chat_room.pk})


class SceneBoundaryAgreementView(LoginRequiredMixin, TemplateView):
    """
    View for agreeing to established scene boundaries
    """
    template_name = 'messages/scene_boundary_agreement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs.get('room_id')
        context['room'] = get_object_or_404(ChatRoom, pk=room_id, participants=self.request.user)

        try:
            context['scene_boundary'] = SceneBoundary.objects.get(chat_room_id=room_id)
        except SceneBoundary.DoesNotExist:
            # Redirect if no boundaries exist
            messages.error(self.request, _("No boundaries have been set for this chat room."))
            return context

        return context

    def post(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id')
        try:
            boundaries = SceneBoundary.objects.get(chat_room_id=room_id)

            # Mark that this user has agreed to the boundaries
            boundaries.agreed_participants.add(request.user)

            # Check if all participants have agreed
            all_participants = set(boundaries.chat_room.participants.all())
            agreed_participants = set(boundaries.agreed_participants.all())

            if all_participants.issubset(agreed_participants):
                boundaries.all_participants_agreed = True
                boundaries.save(update_fields=['all_participants_agreed'])

                # Create system message that all have agreed
                ChatMessage.objects.create(
                    chat_room=boundaries.chat_room,
                    sender=request.user,
                    message=_("All participants have agreed to the scene boundaries."),
                    is_system_message=True
                )
            else:
                # Create system message that this user has agreed
                ChatMessage.objects.create(
                    chat_room=boundaries.chat_room,
                    sender=request.user,
                    message=_("{username} has agreed to the scene boundaries.").format(
                        username=request.user.username
                    ),
                    is_system_message=True
                )

            messages.success(request, _("You have agreed to the scene boundaries."))
            return redirect('messages:room_detail', pk=room_id)

        except SceneBoundary.DoesNotExist:
            messages.error(request, _("No boundaries have been set for this chat room."))
            return redirect('messages:room_detail', pk=room_id)

class SceneSettingListView(LoginRequiredMixin, ListView):
    """
    Display list of scene settings that the user has created or are public
    """
    model = SceneSetting
    template_name = 'messages/scene_setting_list.html'
    context_object_name = 'scene_settings'

    def get_queryset(self):
        # Get public settings and user's private settings
        return SceneSetting.objects.filter(
            Q(is_public=True) | Q(user=self.request.user)
        ).order_by('-use_count', 'title')


class QuickResponseListView(LoginRequiredMixin, ListView):
    model = QuickResponse
    template_name = 'messages/quick_response_list.html'
    context_object_name = 'quick_responses'

    def get_queryset(self):
        return QuickResponse.objects.filter(user=self.request.user).order_by('response_type', '-use_count')


class QuickResponseCreateView(LoginRequiredMixin, CreateView):
    model = QuickResponse
    form_class = QuickResponseForm
    template_name = 'messages/quick_response_form.html'
    success_url = reverse_lazy('messages:quick_response_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class QuickResponseUpdateView(LoginRequiredMixin, UpdateView):
    model = QuickResponse
    form_class = QuickResponseForm
    template_name = 'messages/quick_response_form.html'
    success_url = reverse_lazy('messages:quick_response_list')

    def get_queryset(self):
        return QuickResponse.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class QuickResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = QuickResponse
    template_name = 'messages/quick_response_confirm_delete.html'
    success_url = reverse_lazy('messages:quick_response_list')

    def get_queryset(self):
        return QuickResponse.objects.filter(user=self.request.user)


class SceneSettingCreateView(LoginRequiredMixin, CreateView):
    model = SceneSetting
    form_class = SceneSettingForm
    template_name = 'messages/scene_setting_form.html'
    success_url = reverse_lazy('messages:scene_setting_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SceneSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = SceneSetting
    form_class = SceneSettingForm
    template_name = 'messages/scene_setting_form.html'
    success_url = reverse_lazy('messages:scene_setting_list')

    def get_queryset(self):
        return SceneSetting.objects.filter(user=self.request.user)


class SceneSettingDeleteView(LoginRequiredMixin, DeleteView):
    model = SceneSetting
    template_name = 'messages/scene_setting_confirm_delete.html'
    success_url = reverse_lazy('messages:scene_setting_list')

    def get_queryset(self):
        return SceneSetting.objects.filter(user=self.request.user)


class PrivateNoteListView(LoginRequiredMixin, ListView):
    model = PrivateNote
    template_name = 'messages/private_note_list.html'
    context_object_name = 'private_notes'

    def get_queryset(self):
        # Filter by chat room if provided
        room_id = self.kwargs.get('room_id')
        if room_id:
            return PrivateNote.objects.filter(user=self.request.user, chat_room_id=room_id)
        return PrivateNote.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add chat room if provided
        room_id = self.kwargs.get('room_id')
        if room_id:
            context['room'] = get_object_or_404(ChatRoom, pk=room_id, participants=self.request.user)
        return context


class PrivateNoteCreateView(LoginRequiredMixin, CreateView):
    model = PrivateNote
    form_class = PrivateNoteForm
    template_name = 'messages/private_note_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        room_id = self.kwargs.get('room_id')
        if room_id:
            initial['chat_room'] = room_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs.get('room_id')
        if room_id:
            context['room'] = get_object_or_404(ChatRoom, pk=room_id, participants=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.chat_room:
            return reverse('messages:private_note_list_room', kwargs={'room_id': self.object.chat_room.pk})
        return reverse('messages:private_note_list')


class PrivateNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = PrivateNote
    form_class = PrivateNoteForm
    template_name = 'messages/private_note_form.html'

    def get_queryset(self):
        return PrivateNote.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.chat_room:
            context['room'] = self.object.chat_room
        return context

    def get_success_url(self):
        if self.object.chat_room:
            return reverse('messages:private_note_list_room', kwargs={'room_id': self.object.chat_room.pk})
        return reverse('messages:private_note_list')


class PrivateNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = PrivateNote
    template_name = 'messages/private_note_confirm_delete.html'

    def get_queryset(self):
        return PrivateNote.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.chat_room:
            context['room'] = self.object.chat_room
        return context

    def get_success_url(self):
        if self.object.chat_room:
            return reverse('messages:private_note_list_room', kwargs={'room_id': self.object.chat_room.pk})
        return reverse('messages:private_note_list')


# API views for AJAX functionality
def apply_scene_setting(request, room_id, setting_id):
    """Apply a scene setting to a chat room via AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=403)

    try:
        room = ChatRoom.objects.get(pk=room_id, participants=request.user)
        setting = SceneSetting.objects.get(pk=setting_id)

        # Only apply if public or owned by the user
        if setting.is_public or setting.user == request.user:
            setting.apply_to_room(room)

            # Create a system message about the scene change
            ChatMessage.objects.create(
                chat_room=room,
                sender=request.user,
                receiver=request.user,  # In group chats, this is a placeholder
                message=_(f"Scene changed to: {setting.title}"),
                is_system_message=True
            )

            return JsonResponse({
                'status': 'success',
                'message': _('Scene setting applied successfully'),
                'scene': {
                    'description': room.scene_description,
                    'background_color': room.scene_background_color,
                    'image_url': room.scene_image_url,
                    'music_url': room.scene_music_url,
                }
            })
        else:
            return JsonResponse({'status': 'error', 'message': _('Permission denied')}, status=403)

    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Chat room not found')}, status=404)
    except SceneSetting.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Scene setting not found')}, status=404)


def update_scene_status(request, room_id):
    """Update scene status (active, paused, etc.) via AJAX"""
    if not request.user.is_authenticated or request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=403)

    try:
        room = ChatRoom.objects.get(pk=room_id, participants=request.user)
        status = request.POST.get('status')

        if status and status in dict(ChatRoom.SCENE_STATUS_CHOICES):
            room.scene_status = status
            room.save(update_fields=['scene_status'])

            # Create a system message about the status change
            status_display = dict(ChatRoom.SCENE_STATUS_CHOICES)[status]
            ChatMessage.objects.create(
                chat_room=room,
                sender=request.user,
                receiver=request.user,  # In group chats, this is a placeholder
                message=_(f"Scene status changed to: {status_display}"),
                is_system_message=True
            )

            return JsonResponse({
                'status': 'success',
                'message': _('Scene status updated'),
                'scene_status': status,
                'status_display': status_display
            })
        else:
            return JsonResponse({'status': 'error', 'message': _('Invalid status')}, status=400)

    except ChatRoom.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Chat room not found')}, status=404)


def use_quick_response(request, response_id):
    """Get quick response content and increment usage counter via AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=403)

    try:
        response = QuickResponse.objects.get(pk=response_id, user=request.user)
        response.increment_usage()

        return JsonResponse({
            'status': 'success',
            'content': response.content,
            'response_type': response.response_type,
            'response_type_display': response.get_response_type_display()
        })

    except QuickResponse.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Quick response not found')}, status=404)

@login_required
def chat_messages_api(request, room_id):
    """API endpoint to get messages for a chat room"""
    try:
        # Verify user is a participant in this room
        room = get_object_or_404(ChatRoom, pk=room_id, participants=request.user)

        # Get last_message_id from request for pagination
        last_message_id = request.GET.get('last_id')

        # Base query for messages in this room
        query = ChatMessage.objects.filter(chat_room=room)

        # If last_id provided, get only newer messages
        if last_message_id and last_message_id.isdigit():
            query = query.filter(id__gt=int(last_message_id))

        # Get the messages
        messages = query.order_by('timestamp')[:50]  # Limit to 50 messages per request

        # Format the messages for JSON response
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender': msg.sender.username,
                'sender_id': msg.sender.id,
                'character': msg.character.name if msg.character else None,
                'character_id': msg.character.id if msg.character else None,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'is_system_message': msg.is_system_message,
                'dice_roll': {
                    'dice': msg.dice_roll.dice_type,
                    'result': msg.dice_roll.result
                } if hasattr(msg, 'dice_roll') and msg.dice_roll else None
            })

        return JsonResponse({
            'messages': messages_data,
            'room_id': room.id,
            'room_title': room.title
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def send_message_api(request, room_id):
    """API endpoint to send a message to a chat room"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        # Verify user is a participant in this room
        room = get_object_or_404(ChatRoom, pk=room_id, participants=request.user)

        # Parse the request body
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        character_id = data.get('character_id')

        if not message_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Create the new message
        message = ChatMessage(
            chat_room=room,
            sender=request.user,
            message=message_text
        )

        # Set character if provided
        if character_id:
            try:
                character = Character.objects.get(pk=character_id, user=request.user)
                message.character = character
            except Character.DoesNotExist:
                pass

        message.save()

        # Update room last_message_time
        room.last_message_time = timezone.now()
        room.save(update_fields=['last_message_time'])

        # Return the created message
        return JsonResponse({
            'id': message.id,
            'sender': message.sender.username,
            'sender_id': message.sender.id,
            'character': message.character.name if message.character else None,
            'character_id': message.character.id if message.character else None,
            'message': message.message,
            'timestamp': message.timestamp.isoformat(),
            'is_system_message': message.is_system_message
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def mark_message_read_api(request, message_id):
    """API endpoint to mark a message as read"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        # Get the message
        message = get_object_or_404(ChatMessage, pk=message_id)

        # Verify user is a participant in the chat room
        if request.user not in message.chat_room.participants.all():
            return HttpResponseForbidden()

        # Mark as read by this user
        # This depends on your data model, but assuming there's a ManyToMany field for read_by
        if hasattr(message, 'read_by'):
            message.read_by.add(request.user)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def user_characters_api(request):
    """API endpoint to get the current user's characters"""
    try:
        characters = Character.objects.filter(user=request.user, public=True)

        characters_data = [
            {
                'id': char.id,
                'name': char.name,
                'gender': char.gender,
                'species': char.species,
                'image_url': char.get_primary_image().image.url if char.has_images() else None
            }
            for char in characters
        ]

        return JsonResponse({'characters': characters_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


class ChatMessageCreateView(LoginRequiredMixin, CreateView):
    model = ChatMessage
    form_class = ChatMessageForm
    template_name = 'messages/chatmessage_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('messages:room_detail', kwargs={'pk': self.object.chat_room.pk})
