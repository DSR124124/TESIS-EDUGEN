from django import template
from django.utils.safestring import mark_safe
import json
from django.utils.html import format_html
import re

register = template.Library()

@register.simple_tag
def get_topics_by_course(topics, course_id):
    """
    Returns topics that belong to a specific course
    Usage: {% get_topics_by_course topics course.id as course_topics %}
    """
    return [topic for topic in topics if topic.course.id == course_id]

@register.simple_tag
def topics_to_json(topics):
    """
    Converts topics to a JSON object for use in JavaScript
    Usage: {% topics_to_json topics as topics_json %}
    """
    topics_data = [{'id': topic.id, 'name': topic.name, 'course_id': topic.course.id} 
                 for topic in topics]
    return mark_safe(json.dumps(topics_data))

@register.simple_tag
def get_topic_count(topics, course_id=None):
    """
    Returns the count of topics, optionally filtered by course
    Usage: {% get_topic_count topics as topic_count %}
    or: {% get_topic_count topics course.id as topic_count %}
    """
    if course_id:
        return len([topic for topic in topics if topic.course.id == course_id])
    return len(topics)

@register.filter
def topic_completion_percentage(topic):
    """
    Calculates the completion percentage of a topic based on completed materials
    Usage: {{ topic|topic_completion_percentage }}
    """
    total_materials = topic.materials.count()
    if total_materials == 0:
        return 0
    completed_materials = topic.materials.filter(is_complete=True).count()
    return int((completed_materials / total_materials) * 100) if total_materials > 0 else 0

@register.simple_tag
def portfolio_status(percentage):
    """
    Returns a formatted status badge based on the portfolio completion percentage.
    """
    if percentage >= 100:
        return format_html('<span class="badge bg-success">Completado</span>')
    elif percentage > 50:
        return format_html('<span class="badge bg-warning">En progreso</span>')
    else:
        return format_html('<span class="badge bg-danger">Pendiente</span>')

@register.filter
def format_percentage(value):
    """
    Formats a number as a percentage.
    """
    return f"{value:.0f}%"

@register.filter
def split(value, separator=','):
    """
    Divides a string by a separator and returns a list
    Usage: {{ "item1,item2,item3"|split:"," }}
    """
    return value.split(separator)

@register.filter
def regex_search(value, pattern):
    """
    Busca un patrón regex en el texto y devuelve el resultado
    Ejemplo de uso: {{ texto|regex_search:"\[SCORM_ID:(\d+)\]" }}
    Devuelve un objeto match con grupos si encuentra coincidencia, None en caso contrario
    """
    if not value or not pattern:
        return None
    
    try:
        # Convertir value a string si no lo es
        if not isinstance(value, str):
            value = str(value)
            
        # Buscar el patrón en el texto
        match = re.search(pattern, value)
        return match
    except Exception:
        return None 