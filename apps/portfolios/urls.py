from django.urls import path
from . import views

app_name = 'portfolios'

urlpatterns = [
    # URLs para profesores - Portfolio Views
    path('teacher/', views.TeacherPortfolioListView.as_view(), name='teacher_list'),
    path('teacher/portfolios/', views.TeacherPortfolioListView.as_view(), name='teacher_portfolio_list'),
    path('teacher/portfolios/<int:pk>/', views.TeacherPortfolioDetailView.as_view(), name='teacher_portfolio_detail'),
    
    # Topics
    path('teacher/topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('teacher/topics/<int:pk>/update/', views.TopicUpdateView.as_view(), name='update_topic'),
    path('teacher/topics/<int:topic_id>/delete/', views.delete_portfolio_topic, name='delete_topic'),
    
    # Materials
    path('teacher/topics/<int:topic_id>/add-material/', views.add_portfolio_material, name='add_portfolio_material'),
    path('teacher/topics/<int:topic_id>/add-material-form/', views.add_material_form, name='add_material_form'),
    path('teacher/materials/<int:material_id>/delete/', views.delete_portfolio_material, name='delete_portfolio_material'),
    
    # Sync materials
    path('teacher/course-topics/<int:course_topic_id>/sync-materials/', views.sync_course_topic_materials, name='sync_course_topic_materials'),
    
    # API AJAX
    path('api/search-students/', views.search_students_ajax, name='search_students_ajax'),
    
    # URLs para estudiantes
    path('student/', views.StudentPortfolioListView.as_view(), name='student_portfolio'),
    path('student/portfolios/', views.StudentPortfolioListView.as_view(), name='student_portfolio_list'),
    path('student/portfolios/<int:pk>/', views.StudentPortfolioDetailView.as_view(), name='student_portfolio_detail'),
    path('student/portfolios/<int:pk>/course/<int:course_id>/', views.StudentPortfolioDetailView.as_view(), name='student_portfolio_detail_by_course'),
    path('student/topics/<int:pk>/', views.StudentTopicDetailView.as_view(), name='student_topic_detail'),
    
    # Material previews
    path('materials/<int:material_id>/preview/', views.preview_material, name='preview_material'),
    path('materials/<int:material_id>/view/', views.view_material, name='view_material'),
    
    # Auto Assignment Management (solo vistas que existen realmente)
    path('admin/auto-assignment-monitor/', views.AutoAssignmentMonitorView.as_view(), name='auto_assignment_monitor'),
    path('admin/manual-sync-student/', views.ManualSyncStudentView.as_view(), name='manual_sync_student'),
] 