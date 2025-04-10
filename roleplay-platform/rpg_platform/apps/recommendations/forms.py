from django import forms
from django.utils.translation import gettext_lazy as _

from rpg_platform.apps.characters.models import Character
from .models import UserPreference


class UserPreferenceForm(forms.ModelForm):
    """Form for creating and editing user preferences"""
    class Meta:
        model = UserPreference
        fields = ['attribute', 'value', 'weight']
        widgets = {
            'attribute': forms.Select(choices=[
                ('species', _('Species')),
                ('gender', _('Gender')),
                ('tag', _('Tag')),
                ('kink', _('Kink')),
            ]),
            'weight': forms.NumberInput(attrs={
                'min': '0.1',
                'max': '5.0',
                'step': '0.1'
            })
        }
        help_texts = {
            'attribute': _('The type of character attribute you prefer'),
            'value': _('The specific value of this attribute (e.g., "Human" for species)'),
            'weight': _('How strongly this preference influences recommendations (0.1-5.0)')
        }

    def clean_weight(self):
        """Ensure weight is between 0.1 and 5.0"""
        weight = self.cleaned_data.get('weight')
        if weight is not None:
            if weight < 0.1:
                raise forms.ValidationError(_('Weight must be at least 0.1'))
            if weight > 5.0:
                raise forms.ValidationError(_('Weight cannot be greater than 5.0'))
        return weight


class RegenerateRecommendationsForm(forms.Form):
    """Form for regenerating character recommendations"""
    include_dismissed = forms.BooleanField(
        label=_('Include previously dismissed recommendations'),
        required=False,
        initial=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class RecommendationFilterForm(forms.Form):
    """Form for filtering character recommendations"""
    reason = forms.ChoiceField(
        label=_('Recommendation Type'),
        required=False,
        choices=[('', _('All Types'))]
    )

    min_score = forms.FloatField(
        label=_('Minimum Score'),
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'step': '0.5',
            'min': '0',
            'max': '5'
        })
    )

    species = forms.CharField(
        label=_('Species Contains'),
        required=False
    )

    gender = forms.ChoiceField(
        label=_('Gender'),
        required=False,
        choices=[('', _('Any'))]
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add recommendation reasons from model
        from .models import CharacterRecommendation
        reason_choices = [('', _('All Types'))] + list(CharacterRecommendation.REASON_CHOICES)
        self.fields['reason'].choices = reason_choices

        # Add gender choices from Character model
        from rpg_platform.apps.characters.models import Character
        gender_choices = [('', _('Any'))] + list(Character.GENDER_CHOICES)
        self.fields['gender'].choices = gender_choices
