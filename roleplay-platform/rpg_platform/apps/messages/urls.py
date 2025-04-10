from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('rooms/', views.ChatRoomListView.as_view(), name='room_list'),
    path('rooms/create/', views.ChatRoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/', views.ChatRoomDetailView.as_view(), name='room_detail'),
    path('rooms/<int:pk>/new/', views.ChatRoomDetailNewView.as_view(), name='room_detail_new'),
    path('rooms/<int:pk>/update/', views.ChatRoomUpdateView.as_view(), name='room_update'),
    path('rooms/<int:pk>/delete/', views.ChatRoomDeleteView.as_view(), name='room_delete'),
    path('rooms/<int:pk>/send/', views.send_message, name='send_message'),
    path('rooms/<int:pk>/agreements/', views.SceneBoundaryAgreementView.as_view(), name='scene_boundary_agreement'),
    path('rooms/<int:pk>/agreements/create/', views.SceneBoundaryFormView.as_view(), name='scene_boundary_create'),

    path('rooms/private/<str:username>/', views.create_private_room, name='create_private_room'),

    path('settings/', views.SceneSettingListView.as_view(), name='scene_setting_list'),
    path('settings/create/', views.SceneSettingCreateView.as_view(), name='scene_setting_create'),
    path('settings/<int:pk>/update/', views.SceneSettingUpdateView.as_view(), name='scene_setting_update'),
    path('settings/<int:pk>/delete/', views.SceneSettingDeleteView.as_view(), name='scene_setting_delete'),

    path('quick-responses/', views.QuickResponseListView.as_view(), name='quick_response_list'),
    path('quick-responses/create/', views.QuickResponseCreateView.as_view(), name='quick_response_create'),
    path('quick-responses/<int:pk>/update/', views.QuickResponseUpdateView.as_view(), name='quick_response_update'),
    path('quick-responses/<int:pk>/delete/', views.QuickResponseDeleteView.as_view(), name='quick_response_delete'),

    path('notes/', views.PrivateNoteListView.as_view(), name='private_note_list'),
    path('notes/create/', views.PrivateNoteCreateView.as_view(), name='private_note_create'),
    path('notes/<int:pk>/update/', views.PrivateNoteUpdateView.as_view(), name='private_note_update'),
    path('notes/<int:pk>/delete/', views.PrivateNoteDeleteView.as_view(), name='private_note_delete'),
]
