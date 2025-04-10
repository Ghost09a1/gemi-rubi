from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification center views
    path('', views.NotificationCenterView.as_view(), name='center'),
    path('list/', views.NotificationListView.as_view(), name='notification_list'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),

    # Action URLs
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:pk>/mark-read/', views.mark_read, name='mark_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete'),

    # API endpoints
    path('api/', views.NotificationsAPIView.as_view(), name='notifications_api'),
    path('api/categories/', views.CategoriesAPIView.as_view(), name='categories_api'),
    path('api/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_read_api'),
    path('api/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_read_api'),
    path('api/<int:pk>/delete/', views.DeleteNotificationView.as_view(), name='delete_api'),
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
    path('api/recent/', views.recent_notifications_api, name='recent_notifications_api'),
]
