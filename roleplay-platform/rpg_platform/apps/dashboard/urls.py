from django.urls import path
from . import views

app_name = "dashboard"


urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
]
