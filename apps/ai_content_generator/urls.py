from django.urls import path
from .views import (
    ContentRequestCreateView, ContentRequestListView,
    ContentDetailView, get_generation_progress_view, create_scorm_package,
    regenerate_content_view, add_content_to_topic, direct_assign_view,
    get_student_topics, assign_to_portfolio, generate_scorm_api,
    simple_assign_test_view, assign_to_portfolio_api, ContentEditView,
    ContentPreviewView, cancel_generation_view, content_request_redirect,
    delete_request_view, get_grades_for_course, get_sections_for_grade,
    get_course_topics, get_progress, get_portfolio_topics, get_students_for_topic,
    MaterialPreviewView, test_content_styles_view, debug_content_processing_view,
    debug_line_by_line_view, final_content_test_view, auto_generate_content_view,
    regenerate_scorm_package
)

app_name = 'ai'

urlpatterns = [
    path('generator/', ContentRequestCreateView.as_view(), name='generator'),
    path('auto-generate/', auto_generate_content_view, name='auto_generate'),
    path('requests/create/', ContentRequestCreateView.as_view(), name='content_request_create'),
    path('requests/', ContentRequestListView.as_view(), name='content_request_list'),
    path('content-request/<int:pk>/', content_request_redirect, name='content_request_redirect'),
    path('contents/<int:pk>/', ContentDetailView.as_view(), name='content_detail'),
    path('contents/<int:pk>/edit/', ContentEditView.as_view(), name='edit_content'),
    path('contents/<int:pk>/preview/', ContentPreviewView.as_view(), name='content_preview'),

    path('contents/<int:pk>/assign/', direct_assign_view, name='direct_assign'),
    path('progress/<int:request_id>/', get_generation_progress_view, name='get_generation_progress'),
    path('requests/progress/<int:request_id>/', get_generation_progress_view, name='get_generation_progress_alt'),
    path('regenerate/<int:request_id>/', regenerate_content_view, name='regenerate_content'),
    path('cancel/<int:request_id>/', cancel_generation_view, name='cancel_generation'),
    path('requests/delete/<int:request_id>/', delete_request_view, name='delete_request'),
    path('add-to-topic/', add_content_to_topic, name='add_content_to_topic'),
    path('api/create-scorm-package/<int:content_id>/', create_scorm_package, name='create_scorm_package'),
    path('api/regenerate-scorm-package/<int:content_id>/', regenerate_scorm_package, name='regenerate_scorm_package'),
    path('api/generate-scorm/', generate_scorm_api, name='generate_scorm_api'),
    path('api/get-student-topics/<int:student_id>/', get_student_topics, name='get_student_topics'),
    path('api/assign-to-portfolio/', assign_to_portfolio, name='assign_to_portfolio'),
    path('api/assign-to-portfolio/<int:pk>/', assign_to_portfolio, name='assign_to_portfolio_with_pk'),
    path('api/assign-to-portfolio-api/', assign_to_portfolio_api, name='assign_to_portfolio_api'),
    path('api/get-grades-for-course/<int:course_id>/', get_grades_for_course, name='get_grades_for_course'),
    path('api/get-sections-for-grade/<int:grade_id>/<int:course_id>/', get_sections_for_grade, name='get_sections_for_grade'),
    path('api/get-course-topics/<int:section_id>/<int:course_id>/', get_course_topics, name='get_course_topics'),
    path('api/get-portfolio-topics/<int:section_id>/<int:course_id>/', get_portfolio_topics, name='get_portfolio_topics'),
    path('api/get-students-for-topic/<int:section_id>/<str:topic_id>/', get_students_for_topic, name='get_students_for_topic'),
    path('simple-assign-test/<int:pk>/', simple_assign_test_view, name='simple_assign_test'),
    path('preview-institutional-header/', MaterialPreviewView.as_view(), name='material_preview'),
    path('test-content-styles/', test_content_styles_view, name='test_content_styles'),
    path('debug-content-processing/', debug_content_processing_view, name='debug_content_processing'),
    path('debug-line-by-line/', debug_line_by_line_view, name='debug_line_by_line'),
    path('final-content-test/', final_content_test_view, name='final_content_test'),
] 