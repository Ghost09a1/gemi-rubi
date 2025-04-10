from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Character recommendations page
    path('characters/', views.CharacterRecommendationsView.as_view(), name='character_recommendations'),

    # Mark recommendation as dismissed (AJAX)
    path('dismiss/<int:pk>/', views.DismissRecommendationView.as_view(), name='dismiss_recommendation'),

    # Regenerate recommendations (AJAX)
    path('regenerate/', views.RegenerateRecommendationsView.as_view(), name='regenerate_recommendations'),

    # User preference management
    path('preferences/', views.UserPreferenceListView.as_view(), name='user_preferences'),
    path('preferences/add/', views.UserPreferenceCreateView.as_view(), name='add_preference'),
    path('preferences/<int:pk>/edit/', views.UserPreferenceUpdateView.as_view(), name='edit_preference'),
    path('preferences/<int:pk>/delete/', views.UserPreferenceDeleteView.as_view(), name='delete_preference'),
]
