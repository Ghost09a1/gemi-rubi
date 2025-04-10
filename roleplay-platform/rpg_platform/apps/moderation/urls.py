from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    # Dashboard for moderators
    path('dashboard/', views.ModerationDashboardView.as_view(), name='dashboard'),

    # User activity stats
    path('analytics/', views.UserActivityStatsView.as_view(), name='analytics'),

    # Advanced search
    path('search/', views.AdvancedSearchView.as_view(), name='advanced_search'),

    # User management
    path('users/', views.UserManagementView.as_view(), name='user_management'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<str:username>/update-role/', views.update_user_role, name='update_user_role'),
    path('users/<str:username>/suspend/', views.suspend_user, name='suspend_user'),
    path('users/<str:username>/unsuspend/', views.unsuspend_user, name='unsuspend_user'),

    # Reports management
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('reports/<int:pk>/update/', views.ReportUpdateView.as_view(), name='report_update'),

    # Report content
    path('report/<str:model_name>/<int:object_id>/', views.report_content, name='report_content'),

    # Actions management
    path('actions/', views.ModeratorActionListView.as_view(), name='action_list'),
    path('actions/<int:pk>/', views.ModeratorActionDetailView.as_view(), name='action_detail'),
    path('actions/create/<str:username>/', views.create_moderator_action, name='create_action'),

    # Moderator applications
    path('apply/', views.ModeratorApplicationCreateView.as_view(), name='apply'),
    path('applications/', views.ModeratorApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.ModeratorApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/update/', views.ModeratorApplicationUpdateView.as_view(), name='application_update'),

    # Logs
    path('logs/', views.ModerationLogListView.as_view(), name='log_list'),
]
