import time
import threading
import logging
import traceback
import json
from django.db import transaction, close_old_connections
from django.db.utils import OperationalError, InterfaceError
from django.core.cache import cache
from .models import ContentRequest, GeneratedContent
from .services.llm_service import DeepSeekService
from .utils.prompts import create_content_prompt
# Template manager removido - ahora generamos HTML directo
from celery import shared_task
from celery import current_app
import kombu.exceptions
import requests  # Para usar requests.ConnectionError

logger = logging.getLogger(__name__)

# Variable global para mantener el seguimiento del progreso
generation_progress = {}

def initialize_progress(request_id):
    """Inicializa el progreso para una solicitud"""
    progress_data = {
        'status': 'processing',
        'progress': 10,
        'message': 'Comenzando generación de contenido...',
        'error': None,
        'updated_at': time.time()
    }
    cache_key = f"content_progress_{request_id}"
    cache.set(cache_key, progress_data, timeout=3600)
    return progress_data

def update_progress(request_id, progress, message, status='processing', error=None, log_important_only=False):
    """Actualiza el progreso de una solicitud"""
    progress_data = {
        'status': status,
        'progress': progress,
        'message': message,
        'error': error,
        'updated_at': time.time()
    }
    cache_key = f"content_progress_{request_id}"
    cache.set(cache_key, progress_data, timeout=3600)
    
    # Solo hacer log de eventos importantes (inicio y fin)
    if log_important_only or status in ['completed', 'failed'] or progress in [0, 100]:
        logger.info(f"Estado solicitud {request_id}: {status} - {message}")
    
    # Actualizar también el estado en la base de datos para garantizar consistencia
    try:
        content_request = ContentRequest.objects.get(id=request_id)
        content_request.status = status
        content_request.save(update_fields=['status'])
    except Exception as e:
        logger.error(f"Error al actualizar estado en BD: {str(e)}")
    
    return progress_data

def generate_content_sync(request_id):
    """
    Función sincrónica para generar contenido basado en la solicitud.
    Versión optimizada con DeepSeek.
    """
    logger.info(f"Iniciando generación de contenido para solicitud {request_id}")
    
    # Obtener la solicitud de contenido
    try:
        content_request = ContentRequest.objects.get(pk=request_id)
        content_request.status = 'processing'
        content_request.save()
        logger.info(f"Solicitud {request_id} actualizada a estado 'processing'")
    except ContentRequest.DoesNotExist:
        logger.error(f"No se encontró la solicitud con ID {request_id}")
        return False
    
    # Intentar generar el contenido
    try:
        # Log inicial importante
        update_progress(request_id, 5, '🚀 Iniciando generación de contenido estructurado...', log_important_only=True)
        
        # Obtener datos de la solicitud
        content_type_id = content_request.content_type.id if content_request.content_type else 2  # Default a Material de Apoyo
        original_topic = content_request.topic
        original_grade_level = content_request.grade_level
        original_course = content_request.course.name if content_request.course else "General"
        original_instructions = content_request.additional_instructions or ''
        
        update_progress(request_id, 10, f'📚 Analizando tema: "{original_topic}"...')
        
        # VALIDAR Y AJUSTAR automáticamente para evitar fallos
        from apps.ai_content_generator.services.content_validator import ContentValidator
        
        validation_result = ContentValidator.validate_and_adjust_request(
            topic=original_topic,
            course=original_course,
            grade_level=original_grade_level,
            additional_instructions=original_instructions
        )
        
        # Usar datos validados y ajustados
        topic = validation_result['topic']
        grade_level = validation_result['grade_level']
        course = validation_result['course']
        enhanced_instructions = validation_result['additional_instructions']
        
        update_progress(request_id, 15, f'🎓 Configurando para {grade_level} - {course}...')
        update_progress(request_id, 20, '🔧 Preparando prompt educativo optimizado...')
        update_progress(request_id, 25, '🤖 Conectando con IA DeepSeek...')
        
        # Obtener instancia del servicio DeepSeek optimizado
        llm_service = DeepSeekService()
        
        update_progress(request_id, 30, '✨ Iniciando generación de contenido ultra-estructurado...')
        update_progress(request_id, 35, '📝 La IA está creando material educativo extenso...')
        update_progress(request_id, 40, '🎯 Generando secciones principales del contenido...')
        
        # Usar el método DIRECTO para generar HTML completo sin plantillas
        try:
            # Usar el método directo que genera HTML adaptativo automáticamente
            response = llm_service.generate_content_for_grapesjs(
                content_type_id=content_type_id,
                topic=topic,
                grade_level=grade_level,
                course=course,
                additional_instructions=enhanced_instructions
            )
            
            # Verificar si la respuesta es un string (nuevo formato) o dict (formato anterior)
            if isinstance(response, str):
                # Nuevo formato: respuesta directa como string
                if response.startswith("Error:"):
                    logger.error(f"Error en generación para solicitud {request_id}: {response}")
                    
                    # Análisis específico del error para mejor diagnóstico
                    error_analysis = ""
                    if "API de DeepSeek inválida" in response:
                        error_analysis = "Problema de autenticación con DeepSeek API"
                    elif "Tiempo de espera agotado" in response:
                        error_analysis = "Timeout en la conexión con DeepSeek"
                    elif "No se pudo conectar" in response:
                        error_analysis = "Error de conectividad con DeepSeek API"
                    elif "Cuota agotada" in response:
                        error_analysis = "Límite de cuota excedido en DeepSeek"
                    else:
                        error_analysis = "Error desconocido en DeepSeek API"
                    
                    detailed_error = f"{error_analysis}: {response}"
                    update_progress(request_id, 0, f'Error: {error_analysis}', status='failed', error=detailed_error)
                    content_request.status = 'failed'
                    content_request.save()
                    return False
                else:
                    # Contenido generado exitosamente
                    content_text = response
            else:
                # Formato anterior: respuesta como diccionario
                if not response["success"] or not response.get("content"):
                    error_msg = response.get("error", "No se pudo generar el contenido")
                    logger.error(f"Error en generación DeepSeek para solicitud {request_id}: {error_msg}")
                    update_progress(request_id, 0, 'Error al generar contenido', status='failed', error=error_msg)
                    content_request.status = 'failed'
                    content_request.save()
                    return False
                content_text = response["content"]
                
        except Exception as generation_error:
            logger.error(f"Error durante la generación para solicitud {request_id}: {str(generation_error)}")
            # Capturar detalles específicos del error
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Traceback completo para solicitud {request_id}: {error_details}")
            
            # Crear mensaje de error detallado
            error_msg = f"Error específico: {str(generation_error)}"
            if "max_tokens" in str(generation_error).lower():
                error_msg += " | CAUSA: Límite de tokens excedido. Máximo permitido: 8192"
            elif "api" in str(generation_error).lower():
                error_msg += " | CAUSA: Error de conectividad con DeepSeek API"
            elif "timeout" in str(generation_error).lower():
                error_msg += " | CAUSA: Tiempo de espera agotado"
            else:
                error_msg += f" | DETALLES: {str(generation_error)[:200]}"
            
            update_progress(request_id, 0, f'Error: {error_msg}', status='failed', error=error_msg)
            content_request.status = 'failed'
            content_request.save()
            return False
        
        # Progreso con análisis
        update_progress(request_id, 50, '🔍 Analizando calidad del contenido generado...')
        
        # VERIFICAR COMPLETITUD DEL CONTENIDO GENERADO
        from apps.ai_content_generator.services.content_completeness_checker import ContentCompletenessChecker
        
        completeness_analysis = ContentCompletenessChecker.analyze_content_completeness(
            content_text, topic
        )
        
        word_count = completeness_analysis.get('word_count', 0)
        completion_score = completeness_analysis.get('completion_score', 0)
        
        update_progress(request_id, 60, f'📊 Contenido: {word_count} palabras, calidad: {completion_score}%')
        
        # Si el contenido está incompleto, intentar extenderlo
        if not completeness_analysis['is_complete'] and completion_score < 70:
            update_progress(request_id, 65, '🔧 Contenido incompleto, extendiendo automáticamente...')
            
            # Crear prompt de extensión
            extension_prompt = ContentCompletenessChecker.create_extension_prompt(
                content_text, completeness_analysis, topic, course, grade_level
            )
            
            try:
                update_progress(request_id, 70, '✨ IA generando contenido adicional...')
                # Intentar extender el contenido
                extension_response = llm_service.generate_content(extension_prompt, max_tokens=8000, temperature=0.7)
                
                if isinstance(extension_response, str) and not extension_response.startswith("Error:"):
                    # Combinar contenido original con extensión
                    content_text = content_text + "\n\n" + extension_response
                    
                    # Re-analizar completitud
                    final_analysis = ContentCompletenessChecker.analyze_content_completeness(content_text, topic)
                    new_word_count = final_analysis.get('word_count', 0)
                    update_progress(request_id, 75, f'📈 Contenido extendido a {new_word_count} palabras')
                    
            except Exception as extension_error:
                update_progress(request_id, 75, '⚠️ No se pudo extender, usando contenido original')
        else:
            update_progress(request_id, 70, f'✅ Contenido completo y de alta calidad ({completion_score}%)')
        
        update_progress(request_id, 80, '🎨 Aplicando diseño y formato profesional...')
        
        # Extraer título y contenido
        title = extract_title(content_text, topic)
        
        # El contenido ya es HTML completo, no necesita procesamiento adicional
        try:
            update_progress(request_id, 85, '💅 Validando HTML generado...')
            # Verificar que el contenido es HTML válido
            if content_text.strip().startswith('<!DOCTYPE') or content_text.strip().startswith('<html'):
                formatted_content = content_text  # Ya es HTML completo
            else:
                # Si por alguna razón no es HTML, crear HTML básico
                formatted_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }}
        .content {{ max-width: 1200px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="content">{content_text}</div>
</body>
</html>"""
        except Exception as content_error:
            # Fallback simple
            formatted_content = content_text
        
        update_progress(request_id, 90, '💾 Guardando en base de datos...')
        
        # Guardar el contenido generado
        # Manejar campos opcionales según el tipo de response
        if isinstance(response, dict):
            model_used = response.get("model_used", "deepseek-chat")
            tokens_used = response.get("tokens", 0)
        else:
            # Respuesta es string, usar valores por defecto
            model_used = "deepseek-chat"
            tokens_used = len(content_text.split()) * 1.3  # Estimación básica
        
        generated_content = GeneratedContent(
            request=content_request,
            title=title,
            raw_content=content_text,
            formatted_content=formatted_content,
            model_used=model_used,
            tokens_used=int(tokens_used)
        )
        generated_content.save()
        
        # Actualizar estado de la solicitud
        content_request.status = 'completed'
        content_request.save()
        
        # Log final importante
        word_count = len(content_text.split())
        update_progress(request_id, 100, f'✅ Contenido generado: {word_count} palabras', status='completed', log_important_only=True)
        
        return True
    except Exception as e:
        # Capturar traceback completo para diagnóstico detallado
        import traceback
        full_traceback = traceback.format_exc()
        logger.exception(f"Error en proceso de generación para solicitud {request_id}: {str(e)}")
        logger.error(f"Traceback completo para solicitud {request_id}:\n{full_traceback}")
        
        # Crear mensaje de error muy detallado para mostrar al usuario
        error_type = type(e).__name__
        error_message = str(e)
        
        # Mensaje detallado con causa específica
        detailed_error = f"TIPO: {error_type} | ERROR: {error_message}"
        
        # Agregar diagnósticos específicos según el tipo de error
        if "NOT NULL constraint failed" in error_message:
            if "content_type_id" in error_message:
                detailed_error += " | CAUSA: Falta asignar tipo de contenido (ContentType). Revisar configuración de modelos."
            else:
                detailed_error += " | CAUSA: Campo requerido faltante en base de datos. Revisar migraciones."
        elif "no such table" in error_message:
            detailed_error += " | CAUSA: Tabla no existe. Ejecutar: python manage.py migrate"
        elif "connection" in error_message.lower():
            detailed_error += " | CAUSA: Error de conexión a base de datos"
        elif "max_tokens" in error_message.lower():
            detailed_error += " | CAUSA: Límite de tokens excedido. Máximo: 8192"
        elif "timeout" in error_message.lower():
            detailed_error += " | CAUSA: Tiempo de espera agotado. Contenido muy complejo."
        elif "api" in error_message.lower():
            detailed_error += " | CAUSA: Error de API DeepSeek. Verificar conectividad."
        
        # Truncar error si es muy largo pero mantener información útil
        if len(detailed_error) > 300:
            detailed_error = detailed_error[:297] + "..."
        
        update_progress(request_id, 0, f'Error crítico: {detailed_error}', status='failed', error=detailed_error)
        content_request.status = 'failed'
        content_request.save()
        return False

def simplify_prompt(prompt):
    """Simplifica el prompt para un segundo intento si el primero falló"""
    # Añadir instrucciones para simplificar pero mantener estructura
    simplified = prompt + "\n\nIMPORTANTE: Genera un contenido más simplificado pero completo, manteniendo la estructura básica requerida."
    return simplified

def extract_title(content, default_topic):
    """Extrae un título del contenido generado o usa el tema por defecto"""
    import re
    
    # Intentar extraer el título de un encabezado h1 o h2
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if h1_match:
        return h1_match.group(1).strip()
    
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE | re.DOTALL)
    if h2_match:
        return h2_match.group(1).strip()
    
    # Buscar un título en formato markdown
    md_title_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
    if md_title_match:
        return md_title_match.group(1).strip()
    
    # Si no hay título, usar el tema como título
    return default_topic.strip()

def start_content_generation_thread(request_id):
    """
    Inicia un hilo para generar contenido en segundo plano
    cuando la generación asíncrona no está disponible.
    """
    thread = threading.Thread(target=generate_content_sync, args=(request_id,))
    thread.daemon = True
    thread.start()
    return thread

def get_generation_progress(request_id):
    """
    Obtiene el progreso actual de la generación de contenido.
    """
    cache_key = f"content_progress_{request_id}"
    progress_info = cache.get(cache_key)
    
    if progress_info:
        return progress_info
    
    try:
        content_request = ContentRequest.objects.get(id=request_id)
        
        # Verificar si hay contenido generado
        has_content = GeneratedContent.objects.filter(request_id=request_id).exists()
        
        # Construir respuesta basada en el estado de la solicitud
        progress_info = {
            'status': content_request.status,
            'progress': 0,
            'message': '',
            'error': None,
            'updated_at': time.time()
        }
        
        if content_request.status == 'pending':
            progress_info['message'] = 'En espera de procesamiento'
        elif content_request.status == 'processing':
            progress_info['message'] = 'Generando contenido...'
            progress_info['progress'] = 50
        elif content_request.status == 'completed':
            progress_info['message'] = 'Contenido generado con éxito'
            progress_info['progress'] = 100
        elif content_request.status == 'failed':
            progress_info['message'] = 'Error en la generación de contenido'
            progress_info['error'] = 'Error desconocido'
        
        # Si está completado pero el estado no coincide, corregir
        if has_content and content_request.status != 'completed':
            content_request.status = 'completed'
            content_request.save(update_fields=['status'])
            progress_info['status'] = 'completed'
            progress_info['message'] = 'Contenido generado con éxito'
            progress_info['progress'] = 100
        
        # Guardar en caché para futuras consultas
        cache.set(cache_key, progress_info, timeout=3600)
        return progress_info
        
    except ContentRequest.DoesNotExist:
        logger.warning(f"Solicitud de contenido no encontrada: {request_id}")
        return {
            'status': 'unknown',
            'progress': 0,
            'message': 'Solicitud de contenido no encontrada',
            'error': 'Solicitud no encontrada'
        }
    except Exception as e:
        logger.exception(f"Error al obtener progreso: {str(e)}")
        return {
            'status': 'error',
            'progress': 0,
            'message': f'Error al obtener información de progreso: {str(e)}',
            'error': str(e)
        }

@shared_task(bind=True, time_limit=600, soft_time_limit=550)
def generate_content(self, request_id):
    """
    Tarea asíncrona para generación de contenido EXTENSO en segundo plano
    Configurada para 10 minutos máximo para contenido completo
    """
    logging.info(f"Iniciando tarea Celery EXTENSA para solicitud {request_id}")
    
    try:
        # Ejecutar generación completa directamente en Celery
        logging.info(f"Ejecutando generación EXTENSA en background para solicitud {request_id}")
        result = generate_content_sync(request_id)
        
        if result:
            logging.info(f"Generación EXTENSA completada exitosamente para solicitud {request_id}")
            return {"status": "success", "message": "Contenido extenso generado exitosamente", "request_id": request_id}
        else:
            logging.error(f"Error en generación extensa para solicitud {request_id}")
            return {"status": "error", "message": "Error en generación extensa", "request_id": request_id}
            
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"Error inesperado en generate_content extenso para solicitud {request_id}: {str(e)}")
        logging.error(error_details)
        
        # Crear mensaje detallado del error
        error_type = type(e).__name__
        detailed_message = f"CELERY ERROR - TIPO: {error_type} | {str(e)}"
        
        # Agregar contexto específico
        if "connection" in str(e).lower():
            detailed_message += " | CAUSA: Error de conexión"
        elif "timeout" in str(e).lower():
            detailed_message += " | CAUSA: Timeout en tarea async"
        elif "memory" in str(e).lower():
            detailed_message += " | CAUSA: Error de memoria"
        
        try:
            # Actualizar el estado de la solicitud a fallido
            with transaction.atomic():
                content_request = ContentRequest.objects.get(id=request_id)
                content_request.status = 'failed'
                content_request.save()
            
            # Actualizar información de progreso con detalles completos
            update_progress(request_id, 0, f"Error async: {detailed_message}", 'failed', detailed_message)
            
        except Exception as inner_e:
            logging.error(f"Error al actualizar estado de solicitud {request_id}: {str(inner_e)}")
        
        return {"status": "error", "message": detailed_message} 