from rest_framework import serializers
from apps.academic.models import Course
from apps.ai_content_generator.models import GrapesJSTemplate

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'credits', 'is_active', 'created_at', 'updated_at'] 

class GrapesJSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrapesJSTemplate
        fields = ['id', 'name', 'description', 'thumbnail', 'html_content', 'css_content', 'js_content', 'order'] 