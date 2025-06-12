from django.urls import path
from . import views
from apps.portfolios.views import (
    TopicDetailView, TopicUpdateView,
    StudentTopicDetailView, add_portfolio_material, delete_portfolio_material
)

app_name = 'dashboard'

urlpatterns = [
    path('', views.redirect_dashboard, name='index'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin'),
    path('admin/courses/create/', views.AdminCourseCreateView.as_view(), name='admin_course_create'),
    path('admin/institutions/create/', views.InstitutionCreateView.as_view(), name='institution_create'),
    path('admin/institutions/<int:institution_id>/directors/create/', views.DirectorCreateView.as_view(), name='director_create'),
    
    # Director URLs
    path('director/', views.DirectorDashboardView.as_view(), name='director'),
    
    # Teacher URLs
    path('teacher/', views.TeacherDashboardView.as_view(), name='teacher'),
    path('teacher/sections/', views.TeacherSectionListView.as_view(), name='teacher_sections'),
    path('teacher/sections/<int:pk>/', views.TeacherSectionDetailView.as_view(), name='teacher_section_detail'),
    path('teacher/courses/', views.TeacherCourseListView.as_view(), name='teacher_courses'),
    path('teacher/courses/<int:pk>/', views.TeacherCourseDetailView.as_view(), name='teacher_course_detail'),
    path('teacher/courses/<int:course_id>/upload/', views.upload_course_material, name='upload_course_material'),
    path('teacher/course-topics/<int:pk>/', views.CourseTopicDetailView.as_view(), name='course_topic_detail'),
    path('teacher/course-topics/<int:pk>/edit/', views.CourseTopicUpdateView.as_view(), name='course_topic_edit'),
    path('teacher/course-topics/<int:pk>/delete/', views.delete_course_topic, name='course_topic_delete'),
    path('teacher/course-topics/create/<int:section_id>/<int:course_id>/', views.CourseTopicCreateView.as_view(), name='course_topic_create'),
    
    # Portfolios (teacher view)
    path('teacher/portfolios/', views.redirect_to_portfolio_list, name='teacher_portfolios'),
    path('teacher/portfolios/<int:portfolio_id>/', views.redirect_to_portfolio_detail, name='portfolio_detail'),
    path('teacher/topics/<int:pk>/update/', TopicUpdateView.as_view(), name='update_topic'),
    path('teacher/topics/<int:topic_id>/delete/', views.delete_portfolio_topic, name='delete_topic'),
    path('teacher/topics/<int:entry_id>/add-material/', add_portfolio_material, name='add_material'),
    path('teacher/topics/materials/<int:material_id>/delete/', delete_portfolio_material, name='delete_material'),
    path('teacher/topics/<int:topic_id>/generate-with-ai/', views.TeacherAIGeneratorView.as_view(), name='ai_generator_page'),
    path('teacher/topics/<int:topic_id>/generate-ai-material/', views.GenerateAIMaterialView.as_view(), name='generate_ai_material'),
    
    # Student dashboard
    path('student/', views.StudentDashboardView.as_view(), name='student'),
    path('student/portfolios/', views.StudentPortfolioListView.as_view(), name='student_portfolio_list'),
    path('student/portfolios/<int:pk>/', views.StudentPortfolioDetailView.as_view(), name='student_portfolio_detail'),
    
    # Nuevas rutas para estudiantes
    path('student/salon/', views.StudentSalonView.as_view(), name='student_salon'),
    path('student/courses/', views.StudentCoursesView.as_view(), name='student_courses'),
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('student/teacher-info/<int:pk>/', views.StudentTeacherInfoView.as_view(), name='teacher_info'),
    
    # Student content viewing only
    path('student/content/ai/', views.StudentContentListView.as_view(), name='student_content_list'),
    
    # Student Google account management
    path('student/google/link/', views.StudentGoogleAccountLinkView.as_view(), name='student_google_link'),
    path('student/google/unlink/', views.StudentGoogleAccountUnlinkView.as_view(), name='student_google_unlink'),
    
    # Profile and settings
    path('teacher/profile/', views.TeacherProfileView.as_view(), name='teacher_profile'),
    path('teacher/settings/', views.TeacherSettingsView.as_view(), name='teacher_settings'),
    path('teacher/students/', views.TeacherStudentListView.as_view(), name='teacher_students'),
] 