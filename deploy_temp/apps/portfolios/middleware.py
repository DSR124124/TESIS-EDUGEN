"""
Middleware para manejar automáticamente errores de relaciones de temas
Previene que lleguen errores de asignación de relaciones al usuario
"""

import logging
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class TopicRelationshipErrorMiddleware:
    """
    Middleware que automáticamente captura y maneja errores de relaciones de temas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except TypeError as e:
            if "Direct assignment to the reverse side of a related set is prohibited" in str(e):
                return self._handle_relationship_error(request, e)
            else:
                raise
        except AttributeError as e:
            if "Direct assignment to the reverse side" in str(e):
                return self._handle_relationship_error(request, e)
            else:
                raise
    
    def _handle_relationship_error(self, request, error):
        """
        Maneja automáticamente errores de relaciones de temas
        """
        logger.error(f"Prevented topic relationship error: {error}")
        
        # Si es una petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Error interno del sistema. El equipo técnico ha sido notificado.',
                'message': 'La operación no pudo completarse. Por favor, intenta nuevamente.'
            }, status=500)
        
        # Para peticiones normales, redirigir con mensaje
        if hasattr(request.user, 'teacher_profile'):
            messages.error(
                request, 
                'Se produjo un error interno. El equipo técnico ha sido notificado. '
                'Por favor, intenta la operación nuevamente.'
            )
            return HttpResponseRedirect(reverse('dashboard:teacher'))
        elif hasattr(request.user, 'student_profile'):
            messages.error(
                request,
                'Se produjo un error interno. Por favor, contacta a tu profesor.'
            )
            return HttpResponseRedirect(reverse('dashboard:student'))
        else:
            messages.error(request, 'Se produjo un error interno.')
            return HttpResponseRedirect(reverse('dashboard:index'))
    
    def process_exception(self, request, exception):
        """
        Procesa excepciones que se escapen del middleware principal
        """
        if isinstance(exception, (TypeError, AttributeError)):
            if ("Direct assignment to the reverse side" in str(exception) or
                "related set is prohibited" in str(exception)):
                return self._handle_relationship_error(request, exception)
        
        return None

class AutoTopicSafetyMiddleware:
    """
    Middleware que automáticamente aplica protecciones a contextos de temas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Verificar si la respuesta contiene temas y aplicar protecciones automáticamente
        if hasattr(response, 'context_data'):
            self._make_context_safe(response.context_data)
        
        return response
    
    def _make_context_safe(self, context):
        """
        Hace seguros automáticamente todos los temas en el contexto
        """
        if not context:
            return
        
        try:
            from .utils import make_topic_safe
            from .models import PortfolioTopic
            from apps.academic.models import CourseTopic
            
            # Procesar temas individuales
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
                
        except Exception as e:
            logger.warning(f"Could not apply automatic topic safety: {e}")

class PortfolioErrorRecoveryMiddleware:
    """
    Middleware que automaticamente recupera de errores comunes de portafolios
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except ValidationError as e:
            if 'portfolio' in str(e).lower() or 'topic' in str(e).lower():
                return self._handle_portfolio_validation_error(request, e)
            else:
                raise
    
    def _handle_portfolio_validation_error(self, request, error):
        """
        Maneja automáticamente errores de validación de portafolios
        """
        logger.warning(f"Portfolio validation error handled: {error}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Error de validación de datos.',
                'message': 'Por favor, verifica la información ingresada.'
            }, status=400)
        
        messages.error(
            request,
            'Error de validación. Por favor, verifica la información e intenta nuevamente.'
        )
        
        # Redirigir a una página segura
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard:index'))) 