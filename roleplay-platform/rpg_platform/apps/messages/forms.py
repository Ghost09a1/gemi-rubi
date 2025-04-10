from django import forms
from django.utils.translation import gettext_lazy as _

from rpg_platform.apps.characters.models import Character
from .models import (
    ChatRoom, ChatMessage, SceneBoundary,
    QuickResponse, SceneSetting, PrivateNote
)


class ChatRoomForm(forms.ModelForm):
    """Form for creating a new chat room"""
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'participants']
        widgets = {
            'participants': forms.SelectMultiple(attrs={'class': 'form-control select2'})
        }


class SceneBoundaryForm(forms.ModelForm):
    """Form for setting scene boundaries and consent preferences"""
    class Meta:
        model = SceneBoundary
        fields = ['boundaries']
        widgets = {
            'boundaries': forms.HiddenInput(),
        }

    # Common content categories for boundaries
    CONTENT_CATEGORIES = [
        ('flirting', _('Flirting')),
        ('suggestive', _('Suggestive Content')),
        ('mild_sexual', _('Mild Sexual Content')),
        ('explicit_sexual', _('Explicit Sexual Content')),
        ('romantic', _('Romantic Content')),
        ('kissing', _('Kissing/Making Out')),
        ('nudity', _('Nudity')),
        ('dominance', _('Dominance/Submission')),
        ('bondage', _('Bondage')),
        ('non_human', _('Non-human Sexual Content')),
        ('rough', _('Rough Play')),
        ('pain', _('Pain Play')),
        ('angst', _('Emotional Angst')),
        ('violence', _('Violence')),
        ('blood', _('Blood/Gore')),
        ('trauma', _('Trauma/Dark Themes')),
        ('non_consent', _('Non-consensual Themes')),
        ('drugs', _('Drug/Alcohol Use')),
        ('gambling', _('Gambling')),
        ('religious', _('Religious Themes')),
        ('political', _('Political Content')),
    ]

    # Fields for the form that will be converted to JSON
    allowed_content = forms.MultipleChoiceField(
        choices=CONTENT_CATEGORIES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Allowed Content'),
        help_text=_('Content that is allowed in this scene')
    )

    soft_limits = forms.MultipleChoiceField(
        choices=CONTENT_CATEGORIES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Soft Limits'),
        help_text=_('Content that should be approached with caution')
    )

    hard_limits = forms.MultipleChoiceField(
        choices=CONTENT_CATEGORIES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Hard Limits'),
        help_text=_('Content that is absolutely not allowed')
    )

    custom_boundaries = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        label=_('Custom Boundaries'),
        help_text=_('Any other boundaries or preferences not covered above')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If we have existing boundaries, populate the form fields
        if self.instance.pk and self.instance.boundaries:
            boundaries = self.instance.boundaries
            self.fields['allowed_content'].initial = boundaries.get('allowed', [])
            self.fields['soft_limits'].initial = boundaries.get('soft_limits', [])
            self.fields['hard_limits'].initial = boundaries.get('hard_limits', [])
            self.fields['custom_boundaries'].initial = boundaries.get('custom', '')

    def clean(self):
        cleaned_data = super().clean()

        # Make sure a content category isn't in multiple lists
        allowed = set(cleaned_data.get('allowed_content', []))
        soft = set(cleaned_data.get('soft_limits', []))
        hard = set(cleaned_data.get('hard_limits', []))

        # Check for overlap
        soft_allowed_overlap = soft.intersection(allowed)
        hard_allowed_overlap = hard.intersection(allowed)
        hard_soft_overlap = hard.intersection(soft)

        if soft_allowed_overlap:
            raise forms.ValidationError(
                _('These categories cannot be both allowed and soft limits: %(categories)s'),
                params={'categories': ', '.join(soft_allowed_overlap)}
            )

        if hard_allowed_overlap:
            raise forms.ValidationError(
                _('These categories cannot be both allowed and hard limits: %(categories)s'),
                params={'categories': ', '.join(hard_allowed_overlap)}
            )

        if hard_soft_overlap:
            raise forms.ValidationError(
                _('These categories cannot be both soft limits and hard limits: %(categories)s'),
                params={'categories': ', '.join(hard_soft_overlap)}
            )

        return cleaned_data

    def save(self, commit=True):
        # Convert form fields to JSON format
        self.instance.boundaries = {
            'allowed': self.cleaned_data.get('allowed_content', []),
            'soft_limits': self.cleaned_data.get('soft_limits', []),
            'hard_limits': self.cleaned_data.get('hard_limits', []),
            'custom': self.cleaned_data.get('custom_boundaries', '')
        }

        return super().save(commit)


class QuickResponseForm(forms.ModelForm):
    """Form for creating and editing quick responses"""
    class Meta:
        model = QuickResponse
        fields = ['name', 'response_type', 'character', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'response_type': forms.Select(attrs={'class': 'form-control'}),
            'character': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Get the user to filter characters
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['character'].queryset = Character.objects.filter(user=self.user)
            self.fields['character'].required = False
            self.fields['character'].empty_label = _('Not character-specific')


class SceneSettingForm(forms.ModelForm):
    """Form for creating and editing scene settings"""
    class Meta:
        model = SceneSetting
        fields = ['title', 'description', 'background_color', 'image_url', 'music_url', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'music_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PrivateNoteForm(forms.ModelForm):
    """Form for creating and editing private notes"""
    class Meta:
        model = PrivateNote
        fields = ['title', 'chat_room', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'chat_room': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Get the user to filter chat rooms
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['chat_room'].queryset = ChatRoom.objects.filter(participants=self.user)

            # Make room optional
            self.fields['chat_room'].required = False
            self.fields['chat_room'].empty_label = _('Not associated with any chat')


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['chat_room', 'receiver', 'character', 'message', 'message_type', 'delay_seconds', 'typing_duration_ms']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'chat_room': forms.Select(attrs={'class': 'form-control'}),
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'character': forms.Select(attrs={'class': 'form-control'}),
            'message_type': forms.Select(attrs={'class': 'form-control'}),
            'delay_seconds': forms.NumberInput(attrs={'class': 'form-control'}),
            'typing_duration_ms': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        from django.contrib.auth.models import User
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['chat_room'].queryset = ChatRoom.objects.filter(participants=self.user)
            self.fields['receiver'].queryset = User.objects.exclude(pk=self.user.pk)
            self.fields['character'].queryset = Character.objects.filter(user=self.user)
            self.fields['character'].required = False