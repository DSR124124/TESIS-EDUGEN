from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('trends/', views.AnalyticsTrendsView.as_view(), name='trends'),
    path('user-stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('progress/register/<int:content_id>/', views.register_progress, name='register_progress'),
    path('progress/student/<int:student_id>/', views.student_progress_report, name='student_progress_report'),
] 