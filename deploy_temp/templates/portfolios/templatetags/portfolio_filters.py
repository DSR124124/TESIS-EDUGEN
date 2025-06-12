from django import template

register = template.Library()

@register.filter
def filter_by_course(topics, course_id):
    """
    Filter topics by course ID
    Usage: {% with course_topics=topics|filter_by_course:course.id %}
    """
    return [topic for topic in topics if topic.course.id == course_id] 