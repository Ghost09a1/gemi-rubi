from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import CharacterRecommendation, UserPreference
from .tasks import generate_recommendations_for_user


class CharacterRecommendationsView(LoginRequiredMixin, ListView):
    """
    View showing character recommendations for the user
    """
    model = CharacterRecommendation
    template_name = 'recommendations/character_recommendations.html'
    context_object_name = 'recommendations'
    paginate_by = 12

    def get_queryset(self):
        """Return the user's non-dismissed recommendations with filtering options"""
        # Start with base query for user's non-dismissed recommendations
        queryset = CharacterRecommendation.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).select_related(
            'character', 'character__user', 'character__user__profile'
        )

        # Get filter parameters
        reason_filter = self.request.GET.get('reason')
        min_score = self.request.GET.get('min_score')
        date_filter = self.request.GET.get('date_filter')
        sort_by = self.request.GET.get('sort', '-score')

        # Filter by recommendation reason
        if reason_filter and reason_filter != 'all':
            queryset = queryset.filter(reason=reason_filter)

        # Filter by minimum score
        if min_score:
            try:
                min_score = float(min_score)
                queryset = queryset.filter(score__gte=min_score)
            except (ValueError, TypeError):
                pass

        # Filter by character creation date
        if date_filter:
            if date_filter == 'day':
                date_threshold = timezone.now() - timezone.timedelta(days=1)
            elif date_filter == 'week':
                date_threshold = timezone.now() - timezone.timedelta(days=7)
            elif date_filter == 'month':
                date_threshold = timezone.now() - timezone.timedelta(days=30)
            else:
                date_threshold = None

            if date_threshold:
                queryset = queryset.filter(character__created_at__gte=date_threshold)

        # Apply sorting
        valid_sort_fields = [
            '-score', 'score',
            '-character__created_at', 'character__created_at',
            '-recommendation_date', 'recommendation_date'
        ]

        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-score')

        return queryset

    def get_context_data(self, **kwargs):
        """Add recommendation stats, preferences, and filters to the context"""
        context = super().get_context_data(**kwargs)

        # Add recommendation reasons for filtering
        context['recommendation_reasons'] = dict(CharacterRecommendation.REASON_CHOICES)

        # Group recommendations by reason
        grouped_recommendations = {}

        for reason, label in CharacterRecommendation.REASON_CHOICES:
            recs = CharacterRecommendation.objects.filter(
                user=self.request.user,
                reason=reason,
                is_dismissed=False
            ).select_related('character').order_by('-score')[:5]

            if recs.exists():
                grouped_recommendations[reason] = {
                    'label': label,
                    'recommendations': recs
                }

        context['grouped_recommendations'] = grouped_recommendations

        # Add user preferences
        context['user_preferences'] = UserPreference.objects.filter(
            user=self.request.user
        ).order_by('attribute', '-weight')

        # Get number of recommendations by reason
        reason_counts = CharacterRecommendation.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).values('reason').annotate(count=Count('reason'))

        context['reason_counts'] = {
            item['reason']: item['count'] for item in reason_counts
        }

        # Add filter parameters to context
        context['reason_filter'] = self.request.GET.get('reason', 'all')
        context['min_score'] = self.request.GET.get('min_score', '')
        context['date_filter'] = self.request.GET.get('date_filter', '')
        context['sort_by'] = self.request.GET.get('sort', '-score')

        # Add filtering options
        context['score_ranges'] = [
            {'value': '0.8', 'label': _('Very High Match (80%+)')},
            {'value': '0.6', 'label': _('High Match (60%+)')},
            {'value': '0.4', 'label': _('Medium Match (40%+)')},
            {'value': '0.2', 'label': _('Low Match (20%+)')},
            {'value': '', 'label': _('All Matches')}
        ]

        context['date_ranges'] = [
            {'value': 'day', 'label': _('Last 24 Hours')},
            {'value': 'week', 'label': _('Last 7 Days')},
            {'value': 'month', 'label': _('Last 30 Days')},
            {'value': '', 'label': _('All Time')}
        ]

        context['sort_options'] = [
            {'value': '-score', 'label': _('Highest Score First')},
            {'value': 'score', 'label': _('Lowest Score First')},
            {'value': '-character__created_at', 'label': _('Newest First')},
            {'value': 'character__created_at', 'label': _('Oldest First')},
            {'value': '-recommendation_date', 'label': _('Recently Recommended')},
            {'value': 'recommendation_date', 'label': _('Oldest Recommendations')}
        ]

        return context


class DismissRecommendationView(LoginRequiredMixin, View):
    """
    Mark a recommendation as dismissed via AJAX
    """
    def post(self, request, pk):
        recommendation = get_object_or_404(
            CharacterRecommendation,
            pk=pk,
            user=request.user
        )

        recommendation.is_dismissed = True
        recommendation.save()

        return JsonResponse({'success': True})


class RegenerateRecommendationsView(LoginRequiredMixin, View):
    """
    Regenerate recommendations for the current user
    """
    def post(self, request):
        # Clear all existing recommendations
        CharacterRecommendation.objects.filter(
            user=request.user,
            is_dismissed=False
        ).delete()

        # Generate new recommendations
        generate_recommendations_for_user(request.user.id)

        messages.success(request, _("Your recommendations have been refreshed."))

        # Redirect back to recommendations page
        return redirect('recommendations:character_recommendations')


class UserPreferenceListView(LoginRequiredMixin, ListView):
    """
    View for managing user's character preferences
    """
    model = UserPreference
    template_name = 'recommendations/user_preference_list.html'
    context_object_name = 'preferences'

    def get_queryset(self):
        return UserPreference.objects.filter(
            user=self.request.user
        ).order_by('attribute', '-weight')


class UserPreferenceCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new user preference
    """
    model = UserPreference
    template_name = 'recommendations/user_preference_form.html'
    fields = ['attribute', 'value', 'weight']
    success_url = reverse_lazy('recommendations:user_preferences')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Add Preference")
        return context


class UserPreferenceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing user preference
    """
    model = UserPreference
    template_name = 'recommendations/user_preference_form.html'
    fields = ['attribute', 'value', 'weight']
    success_url = reverse_lazy('recommendations:user_preferences')

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Edit Preference")
        return context


class UserPreferenceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a user preference
    """
    model = UserPreference
    template_name = 'recommendations/user_preference_confirm_delete.html'
    success_url = reverse_lazy('recommendations:user_preferences')

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
