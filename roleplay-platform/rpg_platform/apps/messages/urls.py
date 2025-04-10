from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    # Chat room views
    path('', views.ChatRoomListView.as_view(), name='room_list'),
    path('create/', views.ChatRoomCreateView.as_view(), name='room_create'),
    path('<int:pk>/', views.ChatRoomDetailView.as_view(), name='room_detail'),
    path('<int:pk>/delete/', views.ChatRoomDeleteView.as_view(), name='room_delete'),

    # API endpoints
    path('<int:room_id>/messages/', views.chat_messages_api, name='messages_api'),
    path('<int:room_id>/send/', views.send_message_api, name='send_message_api'),
    path('message/<int:message_id>/read/', views.mark_message_read_api, name='mark_message_read'),
    path('characters/', views.user_characters_api, name='user_characters_api'),

    # Scene boundaries
    path('<int:room_id>/boundaries/', views.SceneBoundaryView.as_view(), name='scene_boundaries'),
    path('<int:room_id>/boundaries/agree/', views.SceneBoundaryAgreementView.as_view(), name='scene_boundaries_agree'),

    # Scene settings
    path('scene-settings/', views.SceneSettingListView.as_view(), name='scene_setting_list'),
    path('scene-settings/create/', views.SceneSettingCreateView.as_view(), name='scene_setting_create'),
    path('scene-settings/<int:pk>/update/', views.SceneSettingUpdateView.as_view(), name='scene_setting_update'),
    path('scene-settings/<int:pk>/delete/', views.SceneSettingDeleteView.as_view(), name='scene_setting_delete'),
    path('<int:room_id>/apply-scene/<int:setting_id>/', views.apply_scene_setting, name='apply_scene_setting'),
    path('<int:room_id>/update-status/', views.update_scene_status, name='update_scene_status'),

    # Quick responses
    path('quick-responses/', views.QuickResponseListView.as_view(), name='quick_response_list'),
    path('quick-responses/create/', views.QuickResponseCreateView.as_view(), name='quick_response_create'),
    path('quick-responses/<int:pk>/update/', views.QuickResponseUpdateView.as_view(), name='quick_response_update'),
    path('quick-responses/<int:pk>/delete/', views.QuickResponseDeleteView.as_view(), name='quick_response_delete'),
    path('quick-responses/<int:response_id>/use/', views.use_quick_response, name='use_quick_response'),

    # Private notes
    path('private-notes/', views.PrivateNoteListView.as_view(), name='private_note_list'),
    path('private-notes/create/', views.PrivateNoteCreateView.as_view(), name='private_note_create'),
    path('<int:room_id>/private-notes/', views.PrivateNoteListView.as_view(), name='private_note_list_room'),
    path('<int:room_id>/private-notes/create/', views.PrivateNoteCreateView.as_view(), name='private_note_create_room'),
    path('private-notes/<int:pk>/update/', views.PrivateNoteUpdateView.as_view(), name='private_note_update'),
    path('private-notes/<int:pk>/delete/', views.PrivateNoteDeleteView.as_view(), name='private_note_delete'),
]
