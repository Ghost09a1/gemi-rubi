from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from .models import Report, ModeratorApplication, ModeratorAction


class ReportForm(forms.ModelForm):
    """
    Form for users to report content
    """
    class Meta:
        model = Report
        fields = ['report_type', 'description']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Please describe why you are reporting this content...')
            })
        }


class ModeratorApplicationForm(forms.ModelForm):
    """
    Form for users to apply to become moderators
    """
    accept_guidelines = forms.BooleanField(
        label=_('I accept the moderator guidelines and code of conduct'),
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = ModeratorApplication
        fields = ['reason', 'experience', 'availability']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Why do you want to be a moderator?')
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Describe any relevant moderation experience')
            }),
            'availability': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('How many hours per week can you dedicate to moderation?')
            })
        }


class ModeratorActionForm(forms.ModelForm):
    """
    Form for moderators to take action on users
    """
    class Meta:
        model = ModeratorAction
        fields = ['action_type', 'reason', 'duration_days']
        widgets = {
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Reason for this action')
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': _('Number of days (leave empty for permanent)')
            })
        }


class ReportReviewForm(forms.ModelForm):
    """
    Form for moderators to review and resolve reports
    """
    class Meta:
        model = Report
        fields = ['status', 'resolution_note']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Provide details on how this report was handled')
            })
        }


class ContentReportForm(forms.Form):
    """
    Form for reporting specific content with content type and object ID hidden
    """
    report_type = forms.ChoiceField(
        choices=Report.REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Please describe why you are reporting this content...')
        })
    )

    # Hidden fields
    content_type_id = forms.IntegerField(widget=forms.HiddenInput())
    object_id = forms.IntegerField(widget=forms.HiddenInput())


class ModeratorNoteForm(forms.Form):
    """
    Form for moderators to add notes to user profiles, characters, or other content
    """
    note = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Add moderation note...')
        })
    )

    # Optional fields
    is_private = forms.BooleanField(
        label=_('Visible to moderators only'),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    is_warning = forms.BooleanField(
        label=_('Flag as warning'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
