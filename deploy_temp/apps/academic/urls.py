from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('grades/', views.GradeListView.as_view(), name='grade_list'),
    path('sections/', views.SectionListView.as_view(), name='section_list'),
] 