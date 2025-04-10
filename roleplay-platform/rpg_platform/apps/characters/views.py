from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Prefetch, F, Subquery, OuterRef, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View, TemplateView
)
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django import forms
import logging

# Setup logger
logger = logging.getLogger(__name__)

from rpg_platform.apps.characters.models import (
    Character, CharacterInfo, InfoField, InfoCategory,
    KinkCategory, Kink, CharacterKink, CustomKink,
    CharacterImage, CharacterRating, CharacterComment
)
from rpg_platform.apps.characters.forms import (
    CharacterForm,
    CharacterImageForm,
    CharacterKinkForm,
    CustomKinkForm,
    KinkBulkForm,
    MultipleImageUploadForm,
    CharacterSearchForm,
    CharacterRatingForm,
    CharacterCommentForm,
    CharacterReplyForm,
)


class CustomKinkListView(ListView):
    """
    Display a list of all custom kinks
    """
    model = CustomKink
    template_name = 'characters/custom_kink_list.html'
    context_object_name = 'custom_kinks'
    paginate_by = 24
    queryset = CustomKink.objects.all()



class CharacterListView(ListView):
    """
    Display a list of public characters
    """
    model = Character
    template_name = 'characters/character_list.html'
    context_object_name = 'characters'
    paginate_by = 24

    def get_queryset(self):
        queryset = super().get_queryset().filter(public=True)

        # Filter by search terms if provided
        search_term = self.request.GET.get('search', '')
        if search_term:
            queryset = queryset.filter(
                models.Q(name__icontains=search_term) |
                models.Q(species__icontains=search_term)
            )

        # Filter by gender if provided
        gender = self.request.GET.get('gender', '')
        if gender:
            queryset = queryset.filter(gender=gender)

        # Filter by species if provided
        species = self.request.GET.get('species', '')
        if species:
            queryset = queryset.filter(species__icontains=species)

        # Sort results
        sort_by = self.request.GET.get('sort', 'created_at')
        if sort_by.startswith('-'):
            sort_field = sort_by[1:]
            if hasattr(Character, sort_field):
                queryset = queryset.order_by(sort_by)
        else:
            if hasattr(Character, sort_by):
                queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        context['species_filter'] = self.request.GET.get('species', '')
        context['sort_by'] = self.request.GET.get('sort', 'created_at')
        return context


class UserCharacterListView(LoginRequiredMixin, ListView):
    """
    Display a list of the current user's characters
    """
    model = Character
    template_name = 'characters/user_character_list.html'
    context_object_name = 'characters'

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user)


class CharacterDetailView(DetailView):
    """
    Display a character profile
    """
    model = Character
    template_name = 'characters/character_detail.html'
    context_object_name = 'character'

    def get_object(self, queryset=None):
        """
        Check if the character is visible to the current user
        """
        obj = super().get_object(queryset)

        if obj.is_friends_only:
            # If character is friends-only, check if the user is authenticated and a friend
            if not self.request.user.is_authenticated or not obj.user.is_friend_with(self.request.user):
                raise Http404(_("Character not found"))
        elif not obj.public and not self.request.user == obj.user:
            raise Http404(_("Character not found"))

        return obj

    def get_queryset(self):
        """
        Only return characters that are visible to the current user
        """
        base_qs = super().get_queryset()

        if self.request.user.is_authenticated:
            # Authenticated users can see their own characters and public/friends-only characters
            return base_qs.filter(Q(
                Q(user=self.request.user) |  # Own characters
                Q(public=True) |  # Public characters
                (Q(is_friends_only=True) & Q(user__friendships__friend=self.request.user))
            ))
        else:
            """
            Unauthenticated users can only see public characters
            """
            return base_qs.filter(public=True)

    def get_context_data(self, **kwargs):
        """
        Add additional context data
        """
        context = super().get_context_data(**kwargs)

        # Add character info fields
        context['info_categories'] = InfoCategory.objects.all().prefetch_related(
            Prefetch(
                'fields',
                queryset=InfoField.objects.filter(required=True),
                to_attr='required_fields'
            )
        )

        # Add character's custom fields
        context['custom_fields'] = self.object.custom_fields.all()

        # Add character's kinks
        context['kink_categories'] = KinkCategory.objects.prefetch_related(
            Prefetch(
                'kinks',
                queryset=Kink.objects.filter(
                    characterkink__character=self.object
                ).annotate(
                    character_kink_rating=F('characterkink__rating')
                ),
                to_attr='character_kinks'
            )
        )

        # Add character's custom kinks
        context['custom_kinks'] = self.object.custom_kinks.all()

        # Add related characters
        context['related_characters'] = Character.objects.filter(
            user=self.object.user,
            public=True
        ).exclude(pk=self.object.pk)[:4]

        # Check if the user has rated this character
        if self.request.user.is_authenticated:
            context['user_rating'] = self.object.get_user_rating(self.request.user)

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.object

        # Get all images for the character
        context['images'] = CharacterImage.objects.filter(character=character).order_by('-is_primary', 'order')

        # Organize kinks by category
        kinks_by_category = {}

        # Add standard kinks
        character_kinks = CharacterKink.objects.filter(character=character).select_related('kink__category')
        for character_kink in character_kinks:
            category_name = character_kink.kink.category.name
            if category_name not in kinks_by_category:
                kinks_by_category[category_name] = []

            kinks_by_category[category_name].append({
                'name': character_kink.kink.name,
                'rating': character_kink.rating,
                'description': character_kink.kink.description
            })

        # Add custom kinks
        custom_kinks = CustomKink.objects.filter(character=character)
        for custom_kink in custom_kinks:
            category_name = custom_kink.category or _('Other')
            if category_name not in kinks_by_category:
                kinks_by_category[category_name] = []

            kinks_by_category[category_name].append({
                'name': custom_kink.name,
                'rating': custom_kink.rating,
                'description': custom_kink.description,
                'is_custom': True
            })

        context['kinks_by_category'] = kinks_by_category

        # Add ratings and comments to context
        context['ratings'] = CharacterRating.objects.filter(character=character)

        # Calculate average rating
        if context['ratings'].exists():
            total_rating = sum(rating.value for rating in context['ratings'])
            context['average_rating'] = total_rating / context['ratings'].count()
            context['rating_count'] = context['ratings'].count()
        else:
            context['average_rating'] = 0
            context['rating_count'] = 0

        # Get user's rating if they have rated this character
        if self.request.user.is_authenticated:
            try:
                context['user_rating'] = CharacterRating.objects.get(character=character, user=self.request.user)
            except CharacterRating.DoesNotExist:
                context['user_rating'] = None

        # Get comments
        context['comments'] = CharacterComment.objects.filter(
            character=character,
            parent=None,
            is_approved=True
        ).select_related('user').prefetch_related('replies')

        # Add forms for comments and ratings if user is authenticated
        if self.request.user.is_authenticated:
            context['comment_form'] = CharacterCommentForm()
            context['reply_form'] = CharacterReplyForm()
            context['rating_form'] = CharacterRatingForm()

        return context


class CharacterCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new character
    """
    model = Character
    form_class = CharacterForm
    template_name = 'characters/character_form.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page_title'] = _("Create New Character")
            context['submit_text'] = _("Create Character")
            context['max_characters'] = 10  # Consider moving to settings

            # Check for character limits
            user_character_count = Character.objects.filter(user=self.request.user).count()
            context['character_count'] = user_character_count
            context['can_create'] = user_character_count < context['max_characters']

            return context
        except Exception as e:
            logger.error(f"Error in CharacterCreateView.get_context_data: {str(e)}")
            messages.error(self.request, _("An error occurred while preparing the character creation form."))
            return super().get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            # Add user to the form instance
            form.instance.user = self.request.user

            # Check if user has reached their character limit
            user_character_count = Character.objects.filter(user=self.request.user).count()
            max_characters = 10  # Consider moving to settings

            if user_character_count >= max_characters:
                messages.error(self.request, _("You have reached your maximum character limit."))
                return self.form_invalid(form)

            # Save the character
            response = super().form_valid(form)
            messages.success(self.request, _("Character created successfully! You can now add more details, images, and preferences."))

            # Log successful character creation
            logger.info(f"User {self.request.user.username} created character ID {self.object.pk} - {self.object.name}")

            return response
        except Exception as e:
            logger.error(f"Error in CharacterCreateView.form_valid: {str(e)}")
            messages.error(self.request, _("An error occurred while creating your character. Please try again."))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors in the form."))
        logger.warning(f"Character creation form invalid for user {self.request.user.username}. Errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('characters:character_detail', kwargs={'pk': self.object.pk})


class CharacterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing character
    """
    model = Character
    form_class = CharacterForm
    template_name = 'characters/character_form.html'

    def test_func(self):
        try:
            return self.get_object().user == self.request.user
        except Exception as e:
            logger.error(f"Error in CharacterUpdateView.test_func: {str(e)}")
            return False

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page_title'] = _("Edit Character")
            context['submit_text'] = _("Update Character")
            context['is_update'] = True
            context['character'] = self.get_object()
            return context
        except Exception as e:
            logger.error(f"Error in CharacterUpdateView.get_context_data: {str(e)}")
            messages.error(self.request, _("An error occurred while preparing the character edit form."))
            return super().get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _("Character updated successfully!"))
            logger.info(f"User {self.request.user.username} updated character ID {self.object.pk} - {self.object.name}")
            return response
        except Exception as e:
            logger.error(f"Error in CharacterUpdateView.form_valid: {str(e)}")
            messages.error(self.request, _("An error occurred while updating your character. Please try again."))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors in the form."))
        logger.warning(f"Character update form invalid for user {self.request.user.username}, character ID {self.kwargs.get('pk')}. Errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('characters:character_detail', kwargs={'pk': self.object.pk})


class CharacterDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a character
    """
    model = Character
    template_name = 'characters/character_confirm_delete.html'
    success_url = reverse_lazy('characters:user_character_list')

    def test_func(self):
        return self.get_object().user == self.request.user


class CharacterKinkUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for bulk updating character kink preferences
    """
    template_name = 'characters/kink_form.html'

    def test_func(self):
        return self.get_character().user == self.request.user

    def get_character(self):
        return get_object_or_404(Character, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        character = self.get_character()
        kink_categories = KinkCategory.objects.all().prefetch_related('kinks')

        # Get existing character kinks
        character_kinks = {}
        for char_kink in CharacterKink.objects.filter(character=character):
            character_kinks[char_kink.kink_id] = char_kink.rating

        # Get custom kinks
        custom_kinks = CustomKink.objects.filter(character=character).order_by('category', 'name')

        context = {
            'character': character,
            'kink_categories': kink_categories,
            'character_kinks': character_kinks,
            'custom_kinks': custom_kinks,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        character = self.get_character()

        # Process all form fields to extract kink preferences
        with transaction.atomic():
            # Delete existing kink preferences (we'll recreate them)
            CharacterKink.objects.filter(character=character).delete()

            # Create new kink preferences
            created_count = 0
            for key, value in request.POST.items():
                if key.startswith('kink_') and value:
                    # Extract kink ID from field name
                    try:
                        kink_id = int(key[5:])  # Remove 'kink_' prefix
                        kink = Kink.objects.get(pk=kink_id)

                        # Create the character kink preference
                        CharacterKink.objects.create(
                            character=character,
                            kink=kink,
                            rating=value
                        )
                        created_count += 1
                    except (ValueError, Kink.DoesNotExist):
                        # Skip invalid kink IDs
                        pass

        messages.success(request, _("Successfully updated {} kink preferences.").format(created_count))
        return redirect('characters:character_detail', pk=character.pk)


class AddCustomKinkView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for adding a custom kink to a character
    """
    def test_func(self):
        character = get_object_or_404(Character, pk=self.kwargs['pk'])
        return character.user == self.request.user

    def post(self, request, *args, **kwargs):
        character = get_object_or_404(Character, pk=self.kwargs['pk'])

        # Check if custom kinks limit has been reached
        if CustomKink.objects.filter(character=character).count() >= 500:
            messages.error(request, _("You have reached the maximum limit of 500 custom kinks."))
            return redirect('characters:character_kinks', pk=character.pk)

        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        rating = request.POST.get('rating', '')

        if not name or not rating:
            messages.error(request, _("Kink name and rating are required."))
            return redirect('characters:character_kinks', pk=character.pk)

        # Create the custom kink
        CustomKink.objects.create(
            character=character,
            name=name,
            category=category,
            description=description,
            rating=rating
        )

        messages.success(request, _("Custom kink added successfully."))
        return redirect('characters:character_kinks', pk=character.pk)


class EditCustomKinkView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for editing a custom kink
    """
    model = CustomKink
    form_class = CustomKinkForm
    template_name = 'characters/custom_kink_form.html'

    def test_func(self):
        custom_kink = self.get_object()
        return custom_kink.character.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.get_object().character
        return context

    def get_success_url(self):
        return reverse('characters:character_kinks', kwargs={'pk': self.get_object().character.pk})


class DeleteCustomKinkView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting a custom kink
    """
    model = CustomKink

    def test_func(self):
        custom_kink = self.get_object()
        return custom_kink.character.user == self.request.user

    def get_success_url(self):
        return reverse('characters:character_kinks', kwargs={'pk': self.kwargs['character_pk']})

    def post(self, request, *args, **kwargs):
        # Direct deletion without confirmation
        custom_kink = self.get_object()
        character_pk = custom_kink.character.pk
        custom_kink.delete()

        messages.success(request, _("Custom kink deleted successfully."))
        return redirect('characters:character_kinks', pk=character_pk)


class CharacterImageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Display all images for a character
    """
    model = CharacterImage
    template_name = 'characters/image_list.html'
    context_object_name = 'images'
    paginate_by = 24

    def test_func(self):
        character = self.get_character()
        return character.user == self.request.user

    def get_character(self):
        return get_object_or_404(Character, pk=self.kwargs['pk'])

    def get_queryset(self):
        character = self.get_character()
        return CharacterImage.objects.filter(character=character)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.get_character()
        context['upload_form'] = MultipleImageUploadForm()
        return context


class CharacterImageUploadView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Upload one or more images for a character
    """
    def test_func(self):
        character = self.get_character()
        return character.user == self.request.user

    def get_character(self):
        return get_object_or_404(Character, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        character = self.get_character()
        form = MultipleImageUploadForm()
        return render(request, 'characters/image_upload.html', {
            'character': character,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        character = self.get_character()
        form = MultipleImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            files = request.FILES.getlist('images')

            # Check if we would exceed the maximum number of images (50 per character)
            current_count = CharacterImage.objects.filter(character=character).count()
            max_images = 50

            if current_count + len(files) > max_images:
                messages.error(request, _(
                    "You can have a maximum of %(max)s images per character. "
                    "You currently have %(current)s images."
                ) % {'max': max_images, 'current': current_count})
                return redirect('characters:image_list', pk=character.pk)

            # Process each uploaded file
            success_count = 0
            for image in files:
                try:
                    # Create a new CharacterImage for each file
                    character_image = CharacterImage(
                        character=character,
                        image=image,
                        # Use filename as default title
                        title=image.name.split('.')[0][:100],
                    )
                    character_image.save()
                    success_count += 1
                except Exception as e:
                    messages.error(request, _(
                        "Error uploading image %(name)s: %(error)s"
                    ) % {'name': image.name, 'error': str(e)})

            if success_count > 0:
                messages.success(request, _(
                    "Successfully uploaded %(count)s image(s)."
                ) % {'count': success_count})

            return redirect('characters:image_list', pk=character.pk)

        # If form is invalid, show errors
        return render(request, 'characters/image_upload.html', {
            'character': character,
            'form': form,
        })


class CharacterImageDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Display a single character image
    """
    model = CharacterImage
    template_name = 'characters/image_detail.html'
    context_object_name = 'image'

    def test_func(self):
        image = self.get_object()
        return image.character.user == self.request.user

    def get_object(self, queryset=None):
        return get_object_or_404(
            CharacterImage,
            pk=self.kwargs['pk'],
            character__pk=self.kwargs['character_pk']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.object.character

        # Get previous and next images for navigation
        all_images = list(CharacterImage.objects.filter(
            character=self.object.character
        ).order_by('-is_primary', 'order', 'uploaded_at').values_list('pk', flat=True))

        current_index = all_images.index(self.object.pk)
        prev_index = current_index - 1 if current_index > 0 else None
        next_index = current_index + 1 if current_index < len(all_images) - 1 else None

        context['prev_image_pk'] = all_images[prev_index] if prev_index is not None else None
        context['next_image_pk'] = all_images[next_index] if next_index is not None else None

        return context


class CharacterImageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update a character image
    """
    model = CharacterImage
    form_class = CharacterImageForm
    template_name = 'characters/image_form.html'

    def test_func(self):
        image = self.get_object()
        return image.character.user == self.request.user

    def get_object(self, queryset=None):
        return get_object_or_404(
            CharacterImage,
            pk=self.kwargs['pk'],
            character__pk=self.kwargs['character_pk']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.object.character
        return context

    def get_success_url(self):
        messages.success(self.request, _("Image updated successfully."))
        return reverse('characters:image_detail', kwargs={
            'character_pk': self.object.character.pk,
            'pk': self.object.pk
        })


class CharacterImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a character image
    """
    model = CharacterImage
    template_name = 'characters/image_confirm_delete.html'

    def test_func(self):
        image = self.get_object()
        return image.character.user == self.request.user

    def get_object(self, queryset=None):
        return get_object_or_404(
            CharacterImage,
            pk=self.kwargs['pk'],
            character__pk=self.kwargs['character_pk']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.object.character
        return context

    def get_success_url(self):
        messages.success(self.request, _("Image deleted successfully."))
        return reverse('characters:image_list', kwargs={'pk': self.object.character.pk})


class CharacterImageMakePrimaryView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Set an image as the primary image for a character
    """
    def test_func(self):
        image = self.get_object()
        return image.character.user == self.request.user

    def get_object(self):
        return get_object_or_404(
            CharacterImage,
            pk=self.kwargs['pk'],
            character__pk=self.kwargs['character_pk']
        )

    def post(self, request, *args, **kwargs):
        image = self.get_object()

        # Set this image as primary
        image.is_primary = True
        image.save()

        messages.success(request, _("Primary image set successfully."))

        # Redirect back to referrer or image list
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        else:
            return redirect('characters:image_list', pk=image.character.pk)


class CharacterImageReorderView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Reorder character images using drag and drop
    """
    def test_func(self):
        character = self.get_character()
        return character.user == self.request.user

    def get_character(self):
        return get_object_or_404(Character, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        character = self.get_character()
        images = CharacterImage.objects.filter(character=character).order_by('-is_primary', 'order', 'uploaded_at')

        return render(request, 'characters/image_reorder.html', {
            'character': character,
            'images': images,
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        character = self.get_character()

        try:
            # Get the new order from the request
            image_order = request.POST.getlist('image_order')

            # Validate that all IDs belong to this character
            if not image_order:
                return JsonResponse({'success': False, 'error': _("No order data provided.")})

            character_image_ids = set(CharacterImage.objects.filter(
                character=character
            ).values_list('id', flat=True))

            for image_id in image_order:
                if int(image_id) not in character_image_ids:
                    return JsonResponse({
                        'success': False,
                        'error': _("Invalid image ID in order data.")
                    })

            # Update the order
            with transaction.atomic():
                for i, image_id in enumerate(image_order):
                    CharacterImage.objects.filter(pk=image_id).update(order=i)

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class CharacterSearchView(TemplateView):
    """
    Advanced character search page
    """
    template_name = 'characters/character_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize the search form
        form = CharacterSearchForm(self.request.GET or None)
        context['form'] = form

        # Process search if form is valid
        if form.is_valid():
            search_query = form.cleaned_data.get('search', '')
            gender = form.cleaned_data.get('gender', '')
            min_age = form.cleaned_data.get('min_age')
            max_age = form.cleaned_data.get('max_age')
            species = form.cleaned_data.get('species', '')
            has_images = form.cleaned_data.get('has_images', False)
            kinks = form.cleaned_data.get('kinks', [])
            kink_rating = form.cleaned_data.get('kink_rating', '')
            sort_by = form.cleaned_data.get('sort_by', 'name')

            # Base queryset - public characters only
            queryset = Character.objects.filter(public=True)

            # Apply search filters
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(species__icontains=search_query) |
                    Q(personality__icontains=search_query) |
                    Q(appearance__icontains=search_query)
                )

            if gender:
                # If gender is one of the common values, filter exactly
                if gender in ['male', 'female', 'other']:
                    queryset = queryset.filter(gender__iexact=gender)
                else:
                    # Otherwise use a case-insensitive contains search
                    queryset = queryset.filter(gender__icontains=gender)

            if species:
                queryset = queryset.filter(species__icontains=species)

            if min_age is not None:
                queryset = queryset.filter(age__gte=min_age)

            if max_age is not None:
                queryset = queryset.filter(age__lte=max_age)

            if has_images:
                queryset = queryset.filter(images__isnull=False).distinct()

            if kinks:
                kink_filter = Q()
                for kink in kinks:
                    kink_filter |= Q(kinks__kink=kink)

                if kink_rating:
                    kink_filter &= Q(kinks__rating=kink_rating)

                queryset = queryset.filter(kink_filter).distinct()

            # Apply sorting
            if sort_by:
                queryset = queryset.order_by(sort_by)

            # Paginate results
            paginator = Paginator(queryset, 24)  # 24 characters per page
            page = self.request.GET.get('page')
            try:
                characters = paginator.page(page)
            except PageNotAnInteger:
                characters = paginator.page(1)
            except EmptyPage:
                characters = paginator.page(paginator.num_pages)

            context['characters'] = characters
            context['count'] = queryset.count()

        return context


@require_POST
def bbcode_preview(request):
    """
    AJAX endpoint for previewing BBCode
    """
    from .templatetags.bbcode import bbcode

    bbcode_text = request.POST.get('bbcode', '')
    html = bbcode(bbcode_text)

    return JsonResponse({'html': html})


@login_required
@require_POST
def rate_character(request, pk):
    """
    Rate a character
    """
    character = get_object_or_404(Character, pk=pk)

    # Check if the user is trying to rate their own character
    if character.user == request.user:
        messages.error(request, _("You cannot rate your own character."))
        return redirect('characters:character_detail', pk=pk)

    form = CharacterRatingForm(request.POST)
    if form.is_valid():
        # Try to get existing rating
        try:
            rating = CharacterRating.objects.get(character=character, user=request.user)
            # Update existing rating
            rating.value = form.cleaned_data['value']
            rating.save()
            messages.success(request, _("Your rating has been updated."))
        except CharacterRating.DoesNotExist:
            # Create new rating
            rating = form.save(commit=False)
            rating.character = character
            rating.user = request.user
            rating.save()
            messages.success(request, _("Your rating has been saved."))

            # Create notification for character owner
            from rpg_platform.apps.notifications.models import Notification
            Notification.objects.create(
                user=character.user,
                notification_type='character_like',
                actor=request.user,
                verb=_('rated your character'),
                target_id=character.id
            )
    else:
        messages.error(request, _("There was an error with your rating."))

    return redirect('characters:character_detail', pk=pk)


@login_required
@require_POST
def add_character_comment(request, pk):
    """
    Add a comment to a character
    """
    character = get_object_or_404(Character, pk=pk)

    form = CharacterCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.character = character
        comment.user = request.user
        comment.save()

        messages.success(request, _("Your comment has been added."))

        # Create notification for character owner if not the commenter
        if character.user != request.user:
            from rpg_platform.apps.notifications.models import Notification
            Notification.objects.create(
                user=character.user,
                notification_type='character_comment',
                actor=request.user,
                verb=_('commented on your character'),
                target_id=character.id,
                action_object_id=comment.id
            )
    else:
        messages.error(request, _("There was an error with your comment."))

    return redirect('characters:character_detail', pk=pk)


@login_required
@require_POST
def add_comment_reply(request, pk):
    """
    Add a reply to a comment
    """
    parent_comment = get_object_or_404(CharacterComment, pk=pk)
    character = parent_comment.character

    form = CharacterReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.character = character
        reply.user = request.user
        reply.parent = parent_comment
        reply.save()

        messages.success(request, _("Your reply has been added."))

        # Create notification for parent comment owner if not the replier
        if parent_comment.user != request.user:
            from rpg_platform.apps.notifications.models import Notification
            Notification.objects.create(
                user=parent_comment.user,
                notification_type='character_comment',
                actor=request.user,
                verb=_('replied to your comment'),
                target_id=character.id,
                action_object_id=reply.id
            )
    else:
        messages.error(request, _("There was an error with your reply."))

    return redirect('characters:character_detail', pk=character.pk)


@login_required
def delete_comment(request, pk):
    """
    Delete a comment or reply
    """
    comment = get_object_or_404(CharacterComment, pk=pk)
    character_pk = comment.character.pk

    # Only the comment owner or the character owner can delete comments
    if request.user != comment.user and request.user != comment.character.user:
        messages.error(request, _("You don't have permission to delete this comment."))
        return redirect('characters:character_detail', pk=character_pk)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, _("Comment deleted successfully."))

    return redirect('characters:character_detail', pk=character_pk)


class CharacterCommentCreateView(LoginRequiredMixin, CreateView):
    """View for creating a comment on a character"""
    model = CharacterComment
    form_class = CharacterCommentForm
    template_name = 'characters/character_comment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = get_object_or_404(Character, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """Set the character and author before saving"""
        form.instance.character = get_object_or_404(Character, pk=self.kwargs['pk'])
        form.instance.author = self.request.user

        # Check if character exists and is visible to the user
        character = form.instance.character
        if not character.is_visible_to(self.request.user):
            messages.error(self.request, _("You don't have permission to comment on this character."))
            return redirect('characters:character_list')

        response = super().form_valid(form)

        # Create notification for character owner
        if character.user != self.request.user:
            from rpg_platform.apps.notifications.models import Notification
            Notification.objects.create(
                user=character.user,
                notification_type='character_comment',
                actor=self.request.user,
                verb=_('commented on your character'),
                action_object_id=character.id,
                target_id=form.instance.id
            )

        messages.success(self.request, _("Your comment has been posted."))
        return response

    def get_success_url(self):
        """Redirect to the character detail page"""
        return reverse('characters:character_detail', kwargs={'pk': self.kwargs['pk']})


class CharacterCommentUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a comment on a character"""
    model = CharacterComment
    form_class = CharacterCommentForm
    template_name = 'characters/character_comment_form.html'
    pk_url_kwarg = 'comment_pk'

    def get_queryset(self):
        """Only allow users to edit their own comments"""
        return CharacterComment.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.object.character
        context['is_update'] = True
        return context

    def form_valid(self, form):
        """Save the form and return to the character detail page"""
        response = super().form_valid(form)
        messages.success(self.request, _("Your comment has been updated."))
        return response

    def get_success_url(self):
        """Redirect to the character detail page"""
        return reverse('characters:character_detail', kwargs={'pk': self.object.character.pk})


class CharacterCommentDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a comment on a character"""
    model = CharacterComment
    template_name = 'characters/character_comment_confirm_delete.html'
    pk_url_kwarg = 'comment_pk'

    def get_queryset(self):
        """Only allow users to delete their own comments or character owners to delete comments on their characters"""
        base_queryset = CharacterComment.objects.all()

        # Get the comment first to check if it's on the user's character
        comment = get_object_or_404(CharacterComment, pk=self.kwargs['comment_pk'])

        if comment.author == self.request.user:
            # User can delete their own comments
            return base_queryset.filter(author=self.request.user)
        elif comment.character.user == self.request.user:
            # Character owner can delete comments on their character
            return base_queryset.filter(character__user=self.request.user)
        else:
            # User can't delete this comment
            return CharacterComment.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = self.object.character
        return context

    def delete(self, request, *args, **kwargs):
        """Delete the comment and return to the character detail page"""
        self.object = self.get_object()
        character_pk = self.object.character.pk
        character_owner = self.object.character.user

        # Store who is deleting for the message
        if self.object.author == request.user:
            messages.success(request, _("Your comment has been deleted."))
        else:
            messages.success(request, _("The comment has been removed from your character."))

        # Delete the comment
        self.object.delete()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to the character detail page"""
        return reverse('characters:character_detail', kwargs={'pk': self.object.character.pk})


class CharacterCommentHideView(LoginRequiredMixin, View):
    """View for hiding/showing a comment on a character"""

    def post(self, request, pk, comment_pk):
        """Hide or show the comment"""
        # Get the character and verify ownership
        character = get_object_or_404(Character, pk=pk, user=request.user)
        comment = get_object_or_404(CharacterComment, pk=comment_pk, character=character)

        # Toggle hide status
        if comment.is_hidden:
            comment.unhide()
            messages.success(request, _("The comment is now visible on your character."))
        else:
            comment.hide()
            messages.success(request, _("The comment has been hidden from your character."))

        # Redirect back to character
        return redirect('characters:character_detail', pk=character.pk)


class CharacterRatingCreateView(LoginRequiredMixin, View):
    """View for rating a character"""

    def post(self, request, pk):
        """Create or update a rating for a character"""
        # Get the character
        character = get_object_or_404(Character, pk=pk)

        # Check if character exists and is visible to the user
        if not character.is_visible_to(request.user):
            messages.error(request, _("You don't have permission to rate this character."))
            return redirect('characters:character_list')

        # Don't allow users to rate their own characters
        if character.user == request.user:
            messages.error(request, _("You cannot rate your own character."))
            return redirect('characters:character_detail', pk=character.pk)

        # Get the rating value from the form
        rating_value = request.POST.get('rating')
        if not rating_value or not rating_value.isdigit() or int(rating_value) < 1 or int(rating_value) > 5:
            messages.error(request, _("Please provide a valid rating from 1 to 5."))
            return redirect('characters:character_detail', pk=character.pk)

        # Create or update the rating
        rating, created = CharacterRating.objects.update_or_create(
            character=character,
            user=request.user,
            defaults={'rating': int(rating_value)}
        )

        # Create notification for character owner if this is a new rating
        if created and character.user != request.user:
            from rpg_platform.apps.notifications.models import Notification
            Notification.objects.create(
                user=character.user,
                notification_type='character_like',
                actor=request.user,
                verb=_('rated your character'),
                action_object_id=character.id,
                target_id=rating.id
            )

        # Success message
        if created:
            messages.success(request, _("Your rating has been submitted."))
        else:
            messages.success(request, _("Your rating has been updated."))

        # Redirect back to character
        return redirect('characters:character_detail', pk=character.pk)


class CharacterRatingDeleteView(LoginRequiredMixin, View):
    """View for deleting a rating"""

    def post(self, request, pk):
        """Delete a rating for a character"""
        # Get the character
        character = get_object_or_404(Character, pk=pk)

        # Try to find and delete the rating
        try:
            rating = CharacterRating.objects.get(character=character, user=request.user)
            rating.delete()
            messages.success(request, _("Your rating has been removed."))
        except CharacterRating.DoesNotExist:
            messages.error(request, _("You don't have a rating for this character."))

        # Redirect back to character
        return redirect('characters:character_detail', pk=character.pk)


class CharacterRecommendationsView(LoginRequiredMixin, TemplateView):
    """View for character recommendations"""
    template_name = 'characters/character_recommendations.html'

    def get_context_data(self, **kwargs):
        """Add recommendations to context"""
        context = super().get_context_data(**kwargs)

        # Get recommended characters for the user
        from .utils import recommend_characters_for_user, get_popular_characters, recommend_characters_by_kinks

        # Get personalized recommendations for the user
        context['personalized_recommendations'] = recommend_characters_for_user(self.request.user, limit=12)

        # Get popular characters
        context['popular_characters'] = get_popular_characters(limit=12)

        # Get recently rated or commented characters by the user
        rated_ids = CharacterRating.objects.filter(
            user=self.request.user
        ).values_list('character_id', flat=True)

        # Get recently rated characters for the "based on your ratings" section
        recently_rated = Character.objects.filter(
            id__in=rated_ids
        ).annotate(
            user_rating=Subquery(
                CharacterRating.objects.filter(
                    character_id=OuterRef('id'),
                    user=self.request.user
                ).values('rating')[:1]
            )
        ).order_by('-ratings__created_at').distinct()[:5]

        context['recent_rated_characters'] = recently_rated

        # Get some recent highly rated characters from the user
        high_rated_ids = CharacterRating.objects.filter(
            user=self.request.user,
            rating__gte=4
        ).values_list('character_id', flat=True)

        # Get kinks from characters the user rated highly
        if high_rated_ids:
            favorite_kinks = CharacterKink.objects.filter(
                character_id__in=high_rated_ids,
                rating__in=['yes', 'fave']
            ).values('kink_id').annotate(
                count=Count('kink_id')
            ).order_by('-count')[:5]

            favorite_kink_ids = [item['kink_id'] for item in favorite_kinks]

            # Get kink objects
            context['favorite_kinks'] = Kink.objects.filter(id__in=favorite_kink_ids)

            # Get recommendations based on these kinks
            context['kink_based_recommendations'] = recommend_characters_by_kinks(
                favorite_kink_ids,
                exclude_ids=high_rated_ids,
                limit=12
            )
        else:
            context['favorite_kinks'] = []
            context['kink_based_recommendations'] = []

        return context
