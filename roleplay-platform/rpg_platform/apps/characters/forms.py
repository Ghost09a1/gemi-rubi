from django import forms
from django.utils.translation import gettext_lazy as _
import os
from django.forms.widgets import Input

from rpg_platform.apps.characters.models import (
    Character,
    CharacterInfo,
    CharacterKink,
    CustomKink,
    CharacterImage,
    InfoField,
    Kink,
    CharacterRating,
    CharacterComment,
)


class CharacterForm(forms.ModelForm):
    """
    Form for creating and editing a character
    """
    class Meta:
        model = Character
        fields = [
            'name', 'gender', 'species', 'height', 'body_type',
            'age', 'personality', 'background', 'appearance',
            'public', 'current_status', 'current_mood', 'custom_status',
            'allow_random_rp', 'private_details'
        ]
        widgets = {
            'personality': forms.Textarea(attrs={'rows': 5}),
            'background': forms.Textarea(attrs={'rows': 5}),
            'appearance': forms.Textarea(attrs={'rows': 5}),
            'private_details': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text for fields
        self.fields['gender'].help_text = _("Character's gender identity")
        self.fields['species'].help_text = _("Human, elf, dragon, etc.")
        self.fields['public'].help_text = _("If checked, this character will be visible to other users")
        self.fields['allow_random_rp'].help_text = _("Allow others to invite this character to roleplay")

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.Select) or \
               isinstance(field.widget, forms.Textarea) or \
               isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})


class CharacterInfoForm(forms.ModelForm):
    """
    Form for adding/editing character information fields
    """
    class Meta:
        model = CharacterInfo
        fields = ['field', 'value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.Select) or \
               isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})


class CharacterKinkForm(forms.ModelForm):
    """
    Form for setting kink preferences
    """
    class Meta:
        model = CharacterKink
        fields = ['kink', 'rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.Select) or \
               isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})


class CustomKinkForm(forms.ModelForm):
    """
    Form for adding custom kinks
    """
    class Meta:
        model = CustomKink
        fields = ['name', 'category', 'description', 'rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.Select) or \
               isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})


class CharacterImageForm(forms.ModelForm):
    """
    Form for uploading character images
    """
    class Meta:
        model = CharacterImage
        fields = ['image', 'title', 'description', 'is_primary', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.Select) or \
               isinstance(field.widget, forms.Textarea) or \
               isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (limit to 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Image size must be no more than 5MB."))

            # Check file extension
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = image.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(_(
                    "Unsupported file format. Allowed formats: %(formats)s"
                ) % {'formats': ', '.join(allowed_extensions)})

        return image


class RawMultipleFileInput(Input):
    """
    A custom widget that renders a file input that supports multiple files
    Django's built-in ClearableFileInput doesn't fully support the multiple attribute
    """
    input_type = 'file'

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

    def value_from_datadict(self, data, files, name):
        """Return a list of files."""
        if files and name in files:
            return files.getlist(name)
        return None


class MultipleImageUploadForm(forms.Form):
    """
    Form for uploading multiple character images at once
    """
    images = forms.FileField(
        widget=RawMultipleFileInput(attrs={'class': 'form-control'}),
        label=_("Select Images"),
        required=False  # We'll handle validation in clean_images
    )

    def clean_images(self):
        # Get files list from request.FILES
        if self.files:
            files = self.files.getlist('images')
            if not files:
                raise forms.ValidationError(_("No files selected."))

            # Check file count (limit to 10 per upload)
            if len(files) > 10:
                raise forms.ValidationError(_("You can upload up to 10 images at a time."))

            for image in files:
                # Check file size (limit to 5MB)
                if image.size > 5 * 1024 * 1024:
                    raise forms.ValidationError(_("Image '%(name)s' is too large. Maximum size is 5MB.") % {'name': image.name})

                # Check file extension
                ext = os.path.splitext(image.name)[1].lower()
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                if ext not in allowed_extensions:
                    raise forms.ValidationError(_("Unsupported file format. Allowed formats: %(formats)s") % {'formats': ', '.join(allowed_extensions)})

            return files
        return []


class KinkBulkForm(forms.Form):
    """
    Form for bulk editing kinks
    """
    def __init__(self, *args, **kwargs):
        character = kwargs.pop('character', None)
        super().__init__(*args, **kwargs)

        if character:
            # Get all kinks with their categories
            kinks = Kink.objects.select_related('category').order_by('category__order', 'category__name', 'order', 'name')

            # Get existing ratings for this character
            existing_ratings = {}
            for char_kink in CharacterKink.objects.filter(character=character):
                existing_ratings[char_kink.kink_id] = char_kink.rating

            # Group kinks by category
            categories = {}
            for kink in kinks:
                if kink.category.name not in categories:
                    categories[kink.category.name] = []
                categories[kink.category.name].append(kink)

            # Create a field for each kink
            for category_name, category_kinks in categories.items():
                for kink in category_kinks:
                    field_name = f'kink_{kink.id}'
                    choices = [
                        ('', _('Not Set')),
                        ('fave', _('Favorite')),
                        ('yes', _('Yes')),
                        ('maybe', _('Maybe')),
                        ('no', _('No')),
                    ]
                    self.fields[field_name] = forms.ChoiceField(
                        label=kink.name,
                        choices=choices,
                        required=False,
                        initial=existing_ratings.get(kink.id, ''),
                        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
                    )

                    # Add data attributes for filtering and sorting
                    self.fields[field_name].widget.attrs.update({
                        'data-category': category_name,
                        'data-kink-id': kink.id,
                    })


class CharacterSearchForm(forms.Form):
    """
    Form for searching characters with various filters
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Search character name, species, etc...')})
    )

    gender = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Filter by gender')})
    )

    min_age = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Min age')})
    )

    max_age = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Max age')})
    )

    species = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Filter by species')})
    )

    has_images = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    kinks = forms.ModelMultipleChoiceField(
        queryset=Kink.objects.all().order_by('category__name', 'name'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    kink_rating = forms.ChoiceField(
        choices=[('', '---')] + list(CharacterKink.RATING_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    sort_by = forms.ChoiceField(
        choices=[
            ('name', _('Name (A-Z)')),
            ('-name', _('Name (Z-A)')),
            ('created_at', _('Oldest First')),
            ('-created_at', _('Newest First')),
            ('gender', _('Gender')),
            ('species', _('Species')),
            ('age', _('Age')),
        ],
        required=False,
        initial='name',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')

        if min_age is not None and max_age is not None and min_age > max_age:
            raise forms.ValidationError(_("Minimum age cannot be greater than maximum age."))

        return cleaned_data


class CharacterCommentForm(forms.ModelForm):
    """Form for adding or editing a comment on a character"""
    class Meta:
        model = CharacterComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Leave a comment about this character...'),
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = False


class CharacterReplyForm(forms.ModelForm):
    """Form for adding a reply to a comment on a character"""
    class Meta:
        model = CharacterComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': _('Add your reply...'),
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = False


class CharacterRatingForm(forms.ModelForm):
    """Form for rating a character"""
    class Meta:
        model = CharacterRating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].label = _('Rate this character')
        self.fields['rating'].help_text = _('Click to rate')
