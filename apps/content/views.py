import json
import logging
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import zipfile
import tempfile

from .models import ContenidoInteractivo, ContenidoRecurso
from .forms import PrompterForm, EditorContenidoForm, RecursoForm, BuscarImagenForm
from .services.image_service import image_service
from .services.scorm_service import scorm_generator
from apps.ai_content_generator.services.llm_service import DeepSeekService



logger = logging.getLogger(__name__)
# Posponer la inicialización hasta que se use


# Servicio de IA con manejo de errores
_openai_service = None

def get_openai_service():
    """Obtiene el servicio de IA con manejo de errores"""
    global _openai_service
    if _openai_service is None:
        try:
            _openai_service = DeepSeekService()
            logger.info("✅ Servicio de IA inicializado correctamente")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo inicializar el servicio de IA: {e}")
            _openai_service = None
    return _openai_service

# Alias para compatibilidad
openai_service = None

@login_required
def dashboard(request):
    """
    Dashboard principal para el módulo de contenido
    """
    # Obtener contenidos del usuario actual
    contenidos = ContenidoInteractivo.objects.filter(creado_por=request.user).order_by('-fecha_actualizacion')
    
    # Paginación
    paginator = Paginator(contenidos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas básicas
    stats = {
        'total': contenidos.count(),
        'publicados': contenidos.filter(estado='publicado').count(),
        'borradores': contenidos.filter(estado='borrador').count(),
        'con_scorm': contenidos.filter(convertido_scorm=True).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats
    }
    
    return render(request, 'content/dashboard.html', context)

@login_required
def generar_contenido(request):
    """
    Vista para generar contenido con IA a partir de un prompt
    """
    if request.method == 'POST':
        form = PrompterForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            nivel = form.cleaned_data['nivel_educativo']
            incluir_imagenes = form.cleaned_data['incluir_imagenes']
            incluir_actividades = form.cleaned_data['incluir_actividades']
            
            # Crear prompt enriquecido para la IA
            prompt_enriquecido = f"""
            Actúa como un experto en educación y crea contenido educativo de alta calidad sobre el siguiente tema:
            
            {prompt}
            
            """
            
            if nivel:
                prompt_enriquecido += f"\nEl contenido debe estar adaptado para el nivel educativo: {nivel}.\n"
            
            if incluir_imagenes:
                prompt_enriquecido += """
                Para cada sección, sugiere una imagen representativa describiendo qué debería mostrar.
                Por ejemplo: "Imagen: un diagrama del ciclo del agua mostrando evaporación y precipitación"
                """
            
            if incluir_actividades:
                prompt_enriquecido += """
                Incluye al final:
                - Al menos 3 actividades prácticas relacionadas con el tema
                - Un mini cuestionario de evaluación con 5 preguntas y respuestas
                """
                
            prompt_enriquecido += """
            Estructura el contenido con encabezados claros, párrafos concisos y listas cuando sea apropiado.
            Formatea la respuesta como JSON válido con esta estructura:
            {
                "titulo": "Título del tema",
                "descripcion": "Breve descripción de una o dos frases",
                "secciones": [
                    {
                        "titulo": "Título de la sección 1",
                        "contenido": "Contenido de la sección 1...",
                        "imagen_sugerida": "Descripción de la imagen para esta sección"
                    }
                ],
                "actividades": [
                    "Descripción de actividad 1",
                    "Descripción de actividad 2"
                ],
                "evaluacion": {
                    "preguntas": [
                        {
                            "pregunta": "¿Texto de la pregunta 1?",
                            "opciones": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
                            "respuesta_correcta": "Opción correcta"
                        }
                    ]
                }
            }
            """
            
            try:
                # Obtener el servicio de IA con manejo de errores
                ai_service = get_openai_service()
                
                if not ai_service:
                    messages.error(request, "El servicio de IA no está disponible en este momento. Por favor, configure la API key de DeepSeek.")
                    return render(request, 'content/generar.html', {'form': form})
                
                # Llamar al servicio de IA
                resultado = ai_service.generate_content(prompt_enriquecido)
                
                # El nuevo servicio retorna directamente el contenido, no un dict con 'success'
                if isinstance(resultado, str):
                    # El servicio retornó contenido directamente
                    contenido_generado = resultado
                else:
                    # Compatibilidad con el formato anterior
                    if not resultado.get('success', True):
                        messages.error(request, f"Error al generar contenido: {resultado.get('error', 'Error desconocido')}")
                        return render(request, 'content/generar.html', {'form': form})
                    contenido_generado = resultado.get('content', resultado)
                
                # Procesar la respuesta JSON
                try:
                    contenido_json = json.loads(contenido_generado)
                except json.JSONDecodeError as e:
                    # Si no es un JSON válido, intentar extraer el JSON de la respuesta
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', contenido_generado, re.DOTALL)
                    if json_match:
                        try:
                            contenido_json = json.loads(json_match.group(1))
                        except:
                            # Si aún falla, usar el contenido como texto plano
                            contenido_json = {
                                "titulo": "Contenido generado",
                                "descripcion": "Contenido educativo generado con IA",
                                "secciones": [
                                    {
                                        "titulo": "Contenido",
                                        "contenido": contenido_generado,
                                        "imagen_sugerida": ""
                                    }
                                ]
                            }
                    else:
                        # Usar el contenido como texto plano
                        contenido_json = {
                            "titulo": "Contenido generado",
                            "descripcion": "Contenido educativo generado con IA",
                            "secciones": [
                                {
                                    "titulo": "Contenido",
                                    "contenido": contenido_generado,
                                    "imagen_sugerida": ""
                                }
                            ]
                        }
                
                # Convertir el JSON a HTML
                html_contenido = convertir_json_a_html(contenido_json)
                
                # Crear objeto de contenido interactivo
                contenido = ContenidoInteractivo(
                    titulo=contenido_json.get('titulo', 'Contenido sin título'),
                    descripcion=contenido_json.get('descripcion', ''),
                    prompt_original=prompt,
                    contenido_ai_original=contenido_generado,
                    contenido_html=html_contenido,
                    creado_por=request.user,
                    nivel_educativo=nivel if nivel else None,
                    estado='borrador'
                )
                contenido.save()
                
                messages.success(request, "¡Contenido generado con éxito! Ahora puedes editarlo visualmente.")
                return redirect('content:editar_contenido', pk=contenido.id)
                
            except Exception as e:
                logger.exception("Error al generar contenido con IA")
                messages.error(request, f"Error al procesar la solicitud: {str(e)}")
    else:
        form = PrompterForm()
    
    return render(request, 'content/generar.html', {'form': form})

# @login_required  # Comentado temporalmente para debugging
def generar_cuestionario_ia(request):
    """
    Vista específica para generar cuestionarios con IA
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            nivel = data.get('nivel_educativo', '')
            
            if not prompt:
                return JsonResponse({
                    'success': False,
                    'error': 'Prompt es requerido'
                }, status=400)
            
            # Obtener el servicio de IA con manejo de errores
            ai_service = get_openai_service()
            
            if not ai_service:
                return JsonResponse({
                    'success': False,
                    'error': 'El servicio de IA no está disponible en este momento'
                }, status=503)
            
            # Llamar al servicio de IA
            resultado = ai_service.generate_content(prompt)
            
            # El nuevo servicio retorna directamente el contenido
            if isinstance(resultado, str):
                contenido_generado = resultado
            else:
                # Compatibilidad con formato anterior
                if not resultado.get('success', True):
                    return JsonResponse({
                        'success': False,
                        'error': f"Error al generar cuestionario: {resultado.get('error', 'Error desconocido')}"
                    }, status=500)
                contenido_generado = resultado.get('content', resultado)
            
            return JsonResponse({
                'success': True,
                'contenido': contenido_generado
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            logger.exception("Error al generar cuestionario con IA")
            return JsonResponse({
                'success': False,
                'error': f"Error interno del servidor: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)

def convertir_json_a_html(contenido_json):
    """
    Convierte la estructura JSON generada por la IA a HTML para el editor
    """
    html = f"<h1>{contenido_json.get('titulo', 'Contenido Educativo')}</h1>"
    
    if 'descripcion' in contenido_json and contenido_json['descripcion']:
        html += f"<p class='lead'>{contenido_json['descripcion']}</p>"
    
    # Procesar secciones
    if 'secciones' in contenido_json:
        for seccion in contenido_json['secciones']:
            html += f"<h2>{seccion.get('titulo', 'Sección')}</h2>"
            html += f"<div>{seccion.get('contenido', '')}</div>"
            
            # Incluir sugerencia de imagen si existe
            if 'imagen_sugerida' in seccion and seccion['imagen_sugerida']:
                html += f"""
                <div class='image-suggestion' style='background-color: #f0f8ff; padding: 10px; border-left: 4px solid #4682b4; margin: 15px 0;'>
                    <p><strong>🖼️ Sugerencia de imagen:</strong> {seccion['imagen_sugerida']}</p>
                    <button type='button' class='btn btn-sm btn-primary buscar-imagen-btn' 
                            data-bs-toggle='modal' data-bs-target='#imagenModal' 
                            data-query='{seccion['imagen_sugerida']}'>
                        Buscar imagen
                    </button>
                </div>
                """
    
    # Procesar actividades
    if 'actividades' in contenido_json and contenido_json['actividades']:
        html += "<h2>Actividades</h2>"
        html += "<ul class='list-group'>"
        for actividad in contenido_json['actividades']:
            html += f"<li class='list-group-item'>{actividad}</li>"
        html += "</ul>"
    
    # Procesar evaluación
    if 'evaluacion' in contenido_json and 'preguntas' in contenido_json['evaluacion']:
        html += "<h2>Evaluación</h2>"
        
        for i, pregunta in enumerate(contenido_json['evaluacion']['preguntas']):
            html += f"""
            <div class='card mb-3'>
                <div class='card-header'><strong>Pregunta {i+1}:</strong> {pregunta.get('pregunta', '')}</div>
                <div class='card-body'>
            """
            
            if 'opciones' in pregunta:
                html += "<ul class='list-group'>"
                for opcion in pregunta['opciones']:
                    is_correct = opcion == pregunta.get('respuesta_correcta', '')
                    html += f"""
                    <li class='list-group-item {is_correct and "list-group-item-success" or ""}'>
                        {opcion} {is_correct and "<span class='badge bg-success'>Correcta</span>" or ""}
                    </li>
                    """
                html += "</ul>"
            
            html += "</div></div>"
    
    return html

@login_required
def editar_contenido(request, pk):
    """
    Vista para editar visualmente el contenido con TinyMCE
    """
    contenido = get_object_or_404(ContenidoInteractivo, pk=pk, creado_por=request.user)
    
    if request.method == 'POST':
        form = EditorContenidoForm(request.POST, instance=contenido)
        if form.is_valid():
            contenido = form.save()
            messages.success(request, "Contenido actualizado con éxito")
            
            # Redirigir según el botón presionado
            if 'guardar_continuar' in request.POST:
                return redirect('content:editar_contenido', pk=contenido.id)
            elif 'guardar_publicar' in request.POST:
                contenido.estado = 'publicado'
                contenido.save()
                messages.success(request, "¡Contenido publicado correctamente!")
                return redirect('content:dashboard')
            elif 'guardar_convertir' in request.POST:
                return redirect('content:generar_scorm', pk=contenido.id)
            else:
                return redirect('content:dashboard')
    else:
        form = EditorContenidoForm(instance=contenido)
    
    # Formulario para buscar imágenes
    buscar_imagen_form = BuscarImagenForm()
    
    context = {
        'form': form,
        'contenido': contenido,
        'buscar_imagen_form': buscar_imagen_form,
    }
    
    return render(request, 'content/editor.html', context)

@login_required
@require_POST
def buscar_imagenes(request):
    """
    API para buscar imágenes desde el editor
    """
    form = BuscarImagenForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data['query']
        
        # Usar el servicio de búsqueda de imágenes
        imagenes = image_service.search_images(query, per_page=8)
        
        return JsonResponse({
            'success': True,
            'imagenes': imagenes
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Formulario inválido'
        }, status=400)

@login_required
def generar_scorm(request, pk):
    """
    Vista para generar un paquete SCORM a partir del contenido
    """
    contenido = get_object_or_404(ContenidoInteractivo, pk=pk, creado_por=request.user)
    
    if request.method == 'POST':
        try:
            # Generar el paquete SCORM
            output_path = os.path.join(settings.MEDIA_ROOT, f'scorm_packages/scorm_{contenido.id}.zip')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            scorm_file = scorm_generator.generate_scorm_package(contenido, output_path)
            
            if scorm_file:
                # Actualizar el objeto de contenido
                contenido.convertido_scorm = True
                contenido.paquete_scorm = f'scorm_packages/scorm_{contenido.id}.zip'
                contenido.save()
                
                messages.success(request, "¡Paquete SCORM generado con éxito!")
                return redirect('content:detalle_contenido', pk=contenido.id)
            else:
                messages.error(request, "Error al generar el paquete SCORM")
        except Exception as e:
            logger.exception("Error al generar paquete SCORM")
            messages.error(request, f"Error al generar el paquete SCORM: {str(e)}")
    
    context = {
        'contenido': contenido
    }
    
    return render(request, 'content/generar_scorm.html', context)

@login_required
def descargar_scorm(request, pk):
    """
    Vista para descargar un paquete SCORM
    """
    contenido = get_object_or_404(ContenidoInteractivo, pk=pk, creado_por=request.user)
    
    if not contenido.paquete_scorm:
        raise Http404("El paquete SCORM no existe")
    
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, str(contenido.paquete_scorm))
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{contenido.titulo.replace(" ", "_")}_SCORM.zip"'
                return response
        else:
            raise Http404("El archivo no existe en el sistema de archivos")
    except Exception as e:
        logger.exception("Error al descargar paquete SCORM")
        messages.error(request, f"Error al descargar el paquete SCORM: {str(e)}")
        return redirect('content:detalle_contenido', pk=contenido.id)

@login_required
def detalle_contenido(request, pk):
    """
    Vista de detalle de un contenido
    """
    contenido = get_object_or_404(ContenidoInteractivo, pk=pk, creado_por=request.user)
    
    context = {
        'contenido': contenido
    }
    
    return render(request, 'content/detalle.html', context)

@login_required
def eliminar_contenido(request, pk):
    """
    Vista para eliminar un contenido
    """
    contenido = get_object_or_404(ContenidoInteractivo, pk=pk, creado_por=request.user)
    
    if request.method == 'POST':
        contenido.delete()
        messages.success(request, "Contenido eliminado con éxito")
        return redirect('content:dashboard')
    
    context = {
        'contenido': contenido
    }
    
    return render(request, 'content/eliminar.html', context) 
