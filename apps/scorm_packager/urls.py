from django.urls import path
from . import views

app_name = 'scorm_packager'

urlpatterns = [
    path('packages/', views.SCORMPackageListView.as_view(), name='scorm_package_list'),
    path('packages/<int:pk>/', views.SCORMPackageDetailView.as_view(), name='scorm_package_detail'),
    path('packages/<int:pk>/download/', views.download_scorm_package, name='download_scorm_package'),
    path('packages/<int:pk>/delete/', views.delete_scorm_package, name='delete_scorm_package'),
    path('packages/<int:pk>/execute/', views.student_scorm_execute, name='student_scorm_execute'),
    path('packages/<int:pk>/viewer/', views.scorm_content_viewer, name='scorm_content_viewer'),
    path('packages/<int:pk>/viewer-raw/', views.scorm_content_viewer_raw, name='scorm_content_viewer_raw'),
    path('packages/<int:pk>/resource/<path:resource_path>', views.scorm_resource_viewer, name='scorm_resource_viewer'),
    path('generate/from-ai-content/<int:content_id>/', views.generate_from_ai_content, name='generate_from_ai_content'),
] 