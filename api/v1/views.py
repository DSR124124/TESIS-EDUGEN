from rest_framework import viewsets
from apps.academic.models import Course
from .serializers import CourseSerializer, GrapesJSTemplateSerializer
from apps.ai_content_generator.models import GrapesJSTemplate

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para ver los cursos.
    """
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer 

class GrapesJSTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para ver las plantillas de GrapesJS.
    """
    queryset = GrapesJSTemplate.objects.all().order_by('order', 'name')
    serializer_class = GrapesJSTemplateSerializer 