from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
    # Character URLs
    path('', views.CharacterListView.as_view(), name='character_list'),
    path('create/', views.CharacterCreateView.as_view(), name='character_create'),
    path('<int:pk>/', views.CharacterDetailView.as_view(), name='character_detail'),
    path('<int:pk>/update/', views.CharacterUpdateView.as_view(), name='character_update'),
    path('<int:pk>/delete/', views.CharacterDeleteView.as_view(), name='character_delete'),

    # Character search
    path('search/', views.CharacterSearchView.as_view(), name='character_search'),

    # BBCode preview
    path('bbcode-preview/', views.bbcode_preview, name='bbcode_preview'),

    # Character kink URLs
    path('<int:pk>/kinks/', views.CharacterKinkUpdateView.as_view(), name='kink_update'),
    path('<int:pk>/kinks/custom/', views.AddCustomKinkView.as_view(), name='custom_kink_create'),
    path('<int:character_pk>/kinks/custom/<int:pk>/update/', views.EditCustomKinkView.as_view(), name='custom_kink_update'),
    path('<int:character_pk>/kinks/custom/<int:pk>/delete/', views.DeleteCustomKinkView.as_view(), name='custom_kink_delete'),

    # Character image URLs
    path('<int:pk>/images/', views.CharacterImageListView.as_view(), name='image_list'),
    path('<int:pk>/images/add/', views.CharacterImageUploadView.as_view(), name='image_create'),
    path('<int:character_pk>/images/<int:pk>/', views.CharacterImageDetailView.as_view(), name='image_detail'),
    path('<int:character_pk>/images/<int:pk>/update/', views.CharacterImageUpdateView.as_view(), name='image_update'),
    path('<int:character_pk>/images/<int:pk>/delete/', views.CharacterImageDeleteView.as_view(), name='image_delete'),
    path('<int:character_pk>/images/<int:pk>/set-primary/', views.CharacterImageMakePrimaryView.as_view(), name='set_primary_image'),
    path('<int:pk>/images/reorder/', views.CharacterImageReorderView.as_view(), name='image_reorder'),

    # Character rating and comments
    path('<int:pk>/rate/', views.rate_character, name='rate_character'),
    path('<int:pk>/comment/', views.add_character_comment, name='add_comment'),
    path('comments/<int:pk>/reply/', views.add_comment_reply, name='add_reply'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Character comments URLs
    path('<int:pk>/comments/add/', views.CharacterCommentCreateView.as_view(), name='add_comment'),
    path('<int:pk>/comments/<int:comment_pk>/edit/', views.CharacterCommentUpdateView.as_view(), name='edit_comment'),
    path('<int:pk>/comments/<int:comment_pk>/delete/', views.CharacterCommentDeleteView.as_view(), name='delete_comment'),
    path('<int:pk>/comments/<int:comment_pk>/toggle_visibility/', views.CharacterCommentHideView.as_view(), name='toggle_comment_visibility'),

    # Character ratings URLs
    path('<int:pk>/rate/', views.CharacterRatingCreateView.as_view(), name='rate_character'),
    path('<int:pk>/rating/delete/', views.CharacterRatingDeleteView.as_view(), name='delete_rating'),

    # Character recommendations
    path('recommendations/', views.CharacterRecommendationsView.as_view(), name='recommendations'),
]
