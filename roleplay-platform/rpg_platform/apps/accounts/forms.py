from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import (
    Profile, SocialLink, BlockedUser,
    DatingProfile, Interest, DatingLike, Match
)

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration"""
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        help_text=_("Required. Enter a valid email address."),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom form for user login"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class ProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = Profile
        fields = ('display_name', 'bio', 'location', 'avatar')
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


class PreferencesForm(forms.ModelForm):
    """Form for updating user preferences"""
    class Meta:
        model = Profile
        fields = ('theme', 'language', 'compact_layout', 'show_nsfw_content')
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'compact_layout': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_nsfw_content': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PrivacyForm(forms.ModelForm):
    """Form for updating privacy settings"""
    class Meta:
        model = Profile
        fields = ('profile_privacy', 'activity_privacy', 'online_status')
        widgets = {
            'profile_privacy': forms.Select(attrs={'class': 'form-control'}),
            'activity_privacy': forms.Select(attrs={'class': 'form-control'}),
            'online_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CommunicationForm(forms.ModelForm):
    """Form for updating communication preferences"""
    class Meta:
        model = Profile
        fields = ('email_notifications', 'friend_requests', 'private_messages',
                 'chat_privacy', 'allow_strangers_chat', 'show_character_status',
                 'chat_notifications')
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'friend_requests': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'private_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chat_privacy': forms.Select(attrs={'class': 'form-control'}),
            'allow_strangers_chat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_character_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chat_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SocialLinkForm(forms.ModelForm):
    """Form for social media links"""
    class Meta:
        model = SocialLink
        fields = ('platform', 'url', 'username', 'display_name')
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BlockedUserForm(forms.ModelForm):
    """Form for blocking users"""
    blocked_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label=_("User to block"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = BlockedUser
        fields = ('blocked_user', 'reason')
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude already blocked users and the user themselves
        self.fields['blocked_user'].queryset = User.objects.exclude(
            id__in=BlockedUser.objects.filter(user=user).values_list('blocked_user_id', flat=True)
        ).exclude(id=user.id)


# Dating app forms

class DatingProfileForm(forms.ModelForm):
    """Form for creating and updating dating profiles"""
    class Meta:
        model = DatingProfile
        fields = ('headline', 'summary', 'birth_date', 'gender_identity', 'looking_for',
                 'roleplay_experience', 'writing_style', 'post_frequency',
                 'min_age_preference', 'max_age_preference', 'gender_preference',
                 'languages', 'favorite_genres', 'is_visible', 'show_online_status')
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender_identity': forms.Select(attrs={'class': 'form-control'}),
            'looking_for': forms.Select(attrs={'class': 'form-control'}),
            'roleplay_experience': forms.Select(attrs={'class': 'form-control'}),
            'writing_style': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'post_frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'min_age_preference': forms.NumberInput(attrs={'class': 'form-control', 'min': 18}),
            'max_age_preference': forms.NumberInput(attrs={'class': 'form-control', 'min': 18}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_online_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'birth_date': _('Your age will be shown to other users, not your birth date.'),
            'min_age_preference': _('Minimum age you want to match with (18+)'),
            'max_age_preference': _('Maximum age you want to match with'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For multi-select fields (using JSONField)
        self.fields['gender_preference'] = forms.MultipleChoiceField(
            choices=DatingProfile.GENDER_IDENTITY_CHOICES,
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            help_text=_('Select the gender identities you are interested in')
        )

        # Languages multi-select field
        LANGUAGE_CHOICES = [
            ('en', _('English')),
            ('es', _('Spanish')),
            ('fr', _('French')),
            ('de', _('German')),
            ('it', _('Italian')),
            ('pt', _('Portuguese')),
            ('ru', _('Russian')),
            ('ja', _('Japanese')),
            ('zh', _('Chinese')),
            ('ko', _('Korean')),
            ('ar', _('Arabic')),
            ('hi', _('Hindi')),
            ('other', _('Other')),
        ]
        self.fields['languages'] = forms.MultipleChoiceField(
            choices=LANGUAGE_CHOICES,
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            help_text=_('Languages you speak or write in')
        )

        # Genre multi-select field
        GENRE_CHOICES = [
            ('fantasy', _('Fantasy')),
            ('sci_fi', _('Science Fiction')),
            ('modern', _('Modern')),
            ('historical', _('Historical')),
            ('supernatural', _('Supernatural')),
            ('horror', _('Horror')),
            ('mystery', _('Mystery')),
            ('romance', _('Romance')),
            ('action', _('Action/Adventure')),
            ('comedy', _('Comedy')),
            ('drama', _('Drama')),
            ('slice_of_life', _('Slice of Life')),
            ('post_apocalyptic', _('Post-Apocalyptic')),
            ('cyberpunk', _('Cyberpunk')),
            ('steampunk', _('Steampunk')),
            ('western', _('Western')),
            ('anime', _('Anime-inspired')),
            ('fanfiction', _('Fanfiction')),
            ('superhero', _('Superhero')),
            ('erotic', _('Erotic/NSFW')),
        ]
        self.fields['favorite_genres'] = forms.MultipleChoiceField(
            choices=GENRE_CHOICES,
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            help_text=_('Your favorite roleplay genres')
        )

        # Initialize values from instance if available
        if self.instance and self.instance.pk:
            # Convert JSON fields to appropriate form field values
            if self.instance.gender_preference:
                self.fields['gender_preference'].initial = self.instance.gender_preference
            if self.instance.languages:
                self.fields['languages'].initial = self.instance.languages
            if self.instance.favorite_genres:
                self.fields['favorite_genres'].initial = self.instance.favorite_genres

    def clean(self):
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age_preference')
        max_age = cleaned_data.get('max_age_preference')

        # Validate age range
        if min_age and max_age and min_age > max_age:
            raise forms.ValidationError(
                _('Minimum age preference must be less than or equal to maximum age preference.')
            )

        # Ensure minimum age is at least 18
        if min_age and min_age < 18:
            self.add_error('min_age_preference', _('Minimum age preference must be at least 18.'))

        return cleaned_data


class InterestForm(forms.ModelForm):
    """Form for adding interests to a dating profile"""
    class Meta:
        model = Interest
        fields = ('interest_type', 'level')
        widgets = {
            'interest_type': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }


class InterestFormSet(forms.BaseModelFormSet):
    """Formset for managing multiple interests"""
    def __init__(self, *args, **kwargs):
        self.dating_profile = kwargs.pop('dating_profile', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['dating_profile'] = self.dating_profile
        return super()._construct_form(i, **kwargs)


class DatingLikeForm(forms.ModelForm):
    """Form for liking another profile"""
    class Meta:
        model = DatingLike
        fields = ('message', 'is_super_like')
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_super_like': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DatingSearchForm(forms.Form):
    """Form for searching dating profiles"""
    keyword = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Search by username or headline')})
    )

    gender_identity = forms.MultipleChoiceField(
        label=_("Gender Identity"),
        choices=DatingProfile.GENDER_IDENTITY_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    looking_for = forms.MultipleChoiceField(
        label=_("Looking For"),
        choices=DatingProfile.LOOKING_FOR_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    roleplay_experience = forms.MultipleChoiceField(
        label=_("Roleplay Experience"),
        choices=DatingProfile.ROLEPLAY_EXPERIENCE_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    age_min = forms.IntegerField(
        label=_("Minimum Age"),
        required=False,
        min_value=18,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    age_max = forms.IntegerField(
        label=_("Maximum Age"),
        required=False,
        min_value=18,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    interests = forms.MultipleChoiceField(
        label=_("Interests"),
        choices=Interest.INTEREST_TYPES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    online_now = forms.BooleanField(
        label=_("Online Now"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    verified_only = forms.BooleanField(
        label=_("Verified Profiles Only"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    sort_by = forms.ChoiceField(
        label=_("Sort By"),
        choices=[
            ('match_score', _('Match Score')),
            ('last_active', _('Recently Active')),
            ('recently_joined', _('Recently Joined')),
            ('alphabetical', _('Alphabetical')),
        ],
        required=False,
        initial='match_score',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FriendRequestForm(forms.Form):
    """Form for sending a friend request with a message"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label=_("Message (optional)"),
        help_text=_("Add a personal message to your friend request.")
    )
