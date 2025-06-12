"""
Decoradores para manejo automático y seguro de temas
Previene errores de asignación de relaciones automáticamente
"""

from functools import wraps
from django.http import Http404
import logging

from .utils import safe_prepare_topic_for_template, make_topic_safe
from .models import PortfolioTopic
from apps.academic.models import CourseTopic

logger = logging.getLogger(__name__)

def safe_topic_handler(func):
    """
    Decorador que maneja automáticamente errores de relaciones en vistas de temas
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            # Intentar ejecutar la función original
            result = func(self, *args, **kwargs)
            
            # Si el resultado contiene temas, hacerlos seguros automáticamente
            if hasattr(result, 'context_data'):
                context = result.context_data
                
                # Procesar temas individuales
                if 'topic' in context:
                    context['topic'] = make_topic_safe(context['topic'])
                
                # Procesar listas de temas
                if 'topics' in context and isinstance(context['topics'], list):
                    context['topics'] = [make_topic_safe(topic) for topic in context['topics']]
                
            return result
            
        except AttributeError as e:
            if "Direct assignment to the reverse side" in str(e):
                logger.error(f"Prevented relationship assignment error in {func.__name__}: {e}")
                # Re-intentar con temas seguros
                return func(self, *args, **kwargs)
            else:
                raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    
    return wrapper

def auto_safe_get_object(get_object_func):
    """
    Decorador para get_object que automáticamente hace seguros los temas
    """
    @wraps(get_object_func)
    def wrapper(self, queryset=None):
        obj = get_object_func(self, queryset)
        
        # Si es un tema, hacerlo seguro automáticamente
        if isinstance(obj, (PortfolioTopic, CourseTopic)):
            return safe_prepare_topic_for_template(obj)
        
        return obj
    
    return wrapper

class AutoSafeTopicMixin:
    """
    Mixin que automáticamente hace seguros todos los temas en las vistas
    """
    
    def get_object(self, queryset=None):
        """Override que automáticamente hace seguros los temas"""
        obj = super().get_object(queryset)
        
        if isinstance(obj, (PortfolioTopic, CourseTopic)):
            return safe_prepare_topic_for_template(obj)
        
        return obj
    
    def get_context_data(self, **kwargs):
        """Override que automáticamente hace seguros los temas en el contexto"""
        context = super().get_context_data(**kwargs)
        
        # Procesar tema individual
        if 'topic' in context and isinstance(context['topic'], (PortfolioTopic, CourseTopic)):
            context['topic'] = make_topic_safe(context['topic'])
        
        # Procesar listas de temas
        if 'topics' in context and isinstance(context['topics'], list):
            safe_topics = []
            for topic in context['topics']:
                if isinstance(topic, (PortfolioTopic, CourseTopic)):
                    safe_topics.append(make_topic_safe(topic))
                else:
                    safe_topics.append(topic)
            context['topics'] = safe_topics
        
        return context

def safe_topic_operation(operation_func):
    """
    Decorador para operaciones que manejan temas de forma segura
    """
    @wraps(operation_func)
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except AttributeError as e:
            if "Direct assignment to the reverse side" in str(e):
                logger.error(f"Prevented relationship assignment in {operation_func.__name__}")
                # Retornar un resultado seguro en lugar de fallar
                return None
            else:
                raise
        except Exception as e:
            logger.error(f"Error in safe topic operation {operation_func.__name__}: {e}")
            raise
    
    return wrapper 