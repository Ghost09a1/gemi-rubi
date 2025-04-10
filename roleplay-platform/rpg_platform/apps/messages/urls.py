from django.urls import path
from . import views
from .views import ChatRoomCreateView

app_name = 'messages'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('<int:pk>/', views.room_detail, name='room_detail'),
    path('create/', views.ChatMessageCreateView.as_view(), name='chatmessage_create'),
    path('room/create/', ChatRoomCreateView.as_view(), name='room_create'),

]
