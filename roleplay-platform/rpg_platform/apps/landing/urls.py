from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('tos/', views.terms_of_service, name='tos'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('community-guidelines/', views.community_guidelines, name='community_guidelines'),
]
