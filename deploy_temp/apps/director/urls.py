from django.urls import path
from . import views, api_views
from django.http import HttpResponse

app_name = 'director'

# Debug view to test URL routing
def debug_view(request, path=''):
    return HttpResponse(f"Debug view - URL path: {request.path}")

urlpatterns = [
    # Debug URL for testing
    path('debug/', debug_view, name='debug'),
    path('teachers-debug/', lambda r: HttpResponse("Teacher debug view working"), name='teacher_debug'),
    
    # Dashboard principal
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='index'),
    path('redirect/', views.RedirectUserView.as_view(), name='redirect'),
    
    # Perfil de usuario
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='user_profile_edit'),
    
    # Información Institucional
    path('institution/', views.InstitutionInfoView.as_view(), name='institution_info'),
    path('institution/edit/', views.InstitutionEditView.as_view(), name='institution_edit'),
    path('institution/settings/', views.InstitutionSettingsUpdateView.as_view(), name='institution_settings'),
    
    # Configuración de usuario
    path('settings/', views.UserSettingsView.as_view(), name='user_settings'),
    
    # Gestión de cursos
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    
    # Estructura Académica (Grados y Secciones)
    path('academic-structure/', views.AcademicStructureView.as_view(), name='academic_structure'),
    path('sections/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/update/', views.SectionUpdateView.as_view(), name='section_update'),
    path('sections/<int:pk>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    path('sections/<int:pk>/', views.SectionDetailView.as_view(), name='section_detail'),
    
    # Gestión de docentes
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/create/', views.TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/update/', views.TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='teacher_delete'),
    
    # Vista para asignar cursos a secciones
    path('sections/<int:section_id>/assign/', views.CourseAssignmentView.as_view(), name='assign_courses'),
    # Vista para crear una nueva asignación de curso
    path('sections/<int:section_id>/courses/add/', views.CourseAssignmentCreateView.as_view(), name='create_course_assignment'),
    # Vista para editar una asignación existente
    path('course_assignments/<int:pk>/edit/', views.CourseAssignmentUpdateView.as_view(), name='edit_course_assignment'),
    # Vista para eliminar una asignación existente
    path('course_assignments/<int:pk>/delete/', views.CourseAssignmentDeleteView.as_view(), name='delete_course_assignment'),
    
    # Vista de prueba para el dropdown de profesores
    path('test-dropdown/', views.TestDropdownView.as_view(), name='test_dropdown'),
    
    # Students
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/create/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/update/', views.StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    
    # Enrollments
    path('enrollment/create/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),
    path('enrollment/create/<int:student_id>/', views.EnrollmentCreateView.as_view(), name='enrollment_create_for_student'),
    path('enrollment/<int:pk>/update/', views.EnrollmentUpdateView.as_view(), name='enrollment_update'),
    path('enrollment/<int:pk>/delete/', views.EnrollmentDeleteView.as_view(), name='enrollment_delete'),
    
    # APIs para notificaciones dinámicas
    path('api/teachers/stats/', api_views.teacher_stats_api, name='teacher_stats_api'),
    path('api/notifications/', api_views.system_notifications_api, name='system_notifications_api'),
    path('api/notifications/mark-read/', api_views.mark_notification_read_api, name='mark_notification_read_api'),
    path('api/teachers/search/', api_views.teacher_search_api, name='teacher_search_api'),
    path('api/dashboard/updates/', api_views.dashboard_updates_api, name='dashboard_updates_api'),
] 