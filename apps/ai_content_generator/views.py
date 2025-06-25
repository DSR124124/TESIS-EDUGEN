from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse, Http404
from django.conf import settings
from django.db.models import Count
import logging
import os
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import copy
import uuid
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.utils.decorators import method_decorator
import zipfile
from io import BytesIO
import time
from django.core.cache import cache

from .models import ContentType, ContentRequest, GeneratedContent
from .forms import ContentRequestForm
from .services.llm_service import OpenAIService
from apps.scorm_packager.services.packager import SCORMPackager
from apps.scorm_packager.models import SCORMPackage
from apps.portfolios.models import PortfolioTopic, PortfolioMaterial
from apps.academic.models import Course, Student, Enrollment, Grade, Section
from .tasks import get_generation_progress
from .utils.pdf_utils import extract_text_from_pdf
from .utils.openai_utils import analizar_con_openai
from apps.academic.models import Teacher
from .utils.enhanced_text_processor import EnhancedTextProcessor

logger = logging.getLogger(__name__)

class ContentRequestListView(LoginRequiredMixin, ListView):
    model = ContentRequest
    template_name = 'ai_content_generator/request_list.html'
    context_object_name = 'requests'
    paginate_by = 12  # Show 12 items per page for better grid layout
    
    def get_queryset(self):
        return ContentRequest.objects.filter(
            teacher=self.request.user
        ).select_related(
            'course', 'content_type'
        ).prefetch_related(
            'contents'
        ).order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        # Verificar si hay contenido pendiente para agregar al portafolio
        auto_add_info = request.session.get('auto_add_to_portfolio', None)
        if auto_add_info:
            try:
                content_request = ContentRequest.objects.get(id=auto_add_info['request_id'])
                # Verificar si el contenido ya se ha generado
                if content_request.status == 'completed' and content_request.contents.exists():
                    # Obtener el contenido generado más reciente
                    content = content_request.contents.latest('created_at')
                    topic_id = auto_add_info['topic_id']
                    
                    # Intentar agregar el contenido al portafolio
                    try:
                        topic = PortfolioTopic.objects.get(id=topic_id)
                        
                        # Verificar que el tema tiene un portafolio y estudiante asociado
                        if not topic.portfolio or not topic.portfolio.student:
                            logger.error(f"El tema {topic_id} no tiene un portafolio o estudiante válido")
                            messages.error(request, "El tema seleccionado no tiene un portafolio o estudiante válido asociado.")
                            return super().get(request, *args, **kwargs)
                            
                        # Crear material de portafolio con los campos correctos
                        material = PortfolioMaterial.objects.create(
                            topic=topic,
                            title=content.title,
                            description=f"Material generado con IA: {content_request.topic}",
                            material_type="OTRO",
                        )
                        
                        # Guardar el contenido en la descripción
                        material.description += "\n\n" + content.formatted_content
                        material.save()
                        
                        logger.info(f"Material creado con éxito para el tema {topic.id}: {material.id}")
                        
                        # También podemos crear el paquete SCORM automáticamente
                        try:
                            # Preparar metadatos
                            metadata = {
                                'title': content.title,
                                'description': f"Contenido generado para {content_request.course.name}",
                                'version': '1.0',
                                'standard': 'scorm_2004_4th'
                            }
                            
                            # Crear paquete SCORM
                            # Usar el contenido más actualizado para el paquete SCORM
                            scorm_content = content.formatted_content or content.raw_content or ""
                            packager = SCORMPackager(scorm_content, metadata)
                            package_path = packager.create_package()
                            
                            # Guardar referencia en la base de datos
                            from apps.scorm_packager.models import SCORMPackage
                            
                            # Convertir la ruta del paquete a string y manejar correctamente la ruta relativa
                            package_path_str = str(package_path)
                            media_root_str = str(settings.MEDIA_ROOT)
                            
                            # Reemplazar la parte de la ruta del MEDIA_ROOT usando os.path.relpath
                            relative_path = os.path.relpath(package_path_str, media_root_str)
                            
                            scorm_package = SCORMPackage.objects.create(
                                generated_content=content,
                                title=content.title,
                                description=metadata['description'],
                                standard=metadata['standard'],
                                package_file=relative_path  # Usar la ruta relativa
                            )
                            
                            # Asignamos el scorm_package y guardamos de nuevo
                            material.scorm_package = scorm_package
                            
                            # Añadir el ID del paquete SCORM a la descripción como solución temporal
                            # scorm_id = scorm_package.id
                            # Asegurarnos de que el formato sea exactamente el esperado
                            # material.description = f"{metadata['description'].strip()}\n\n[SCORM_ID:{scorm_id}]"
                            material.save()
                            
                            logger.info(f"Material SCORM creado correctamente con paquete ID {scorm_package.id}.")
                            
                            # Obtener el nombre del estudiante para el mensaje
                            student = topic.portfolio.student
                            student_name = student.get_full_name() if student else "desconocido"
                            
                            messages.success(request, f"El contenido se ha agregado al tema '{topic.title}' para el estudiante {student_name} con un paquete SCORM.")
                        except Exception as e:
                            # Si hay error creando el SCORM, continuamos sin él
                            logger.error(f"Error al crear paquete SCORM: {str(e)}")
                            
                            # Obtener el nombre del estudiante para el mensaje
                            student = topic.portfolio.student
                            student_name = student.get_full_name() if student else "desconocido"
                            
                            messages.success(request, f"El contenido se ha agregado al tema '{topic.title}' para el estudiante {student_name} (sin SCORM).")
                    except Exception as e:
                        logger.error(f"Error al agregar contenido al portafolio: {str(e)}")
                        messages.error(request, f"No se pudo agregar el contenido al portafolio: {str(e)}")
                    
                    # Eliminar la información de la sesión
                    del request.session['auto_add_to_portfolio']
                    request.session.modified = True
            except Exception as e:
                logger.error(f"Error al procesar auto_add_to_portfolio: {str(e)}")
                # Limpiamos la sesión en caso de error
                if 'auto_add_to_portfolio' in request.session:
                    del request.session['auto_add_to_portfolio']
                    request.session.modified = True
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimizar estadísticas con una sola consulta usando agregación
        from django.db.models import Count, Case, When, IntegerField
        
        stats = ContentRequest.objects.filter(
            teacher=self.request.user
        ).aggregate(
            total_count=Count('id'),
            completed_count=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            pending_count=Count(Case(When(status='pending', then=1), output_field=IntegerField())),
            processing_count=Count(Case(When(status='processing', then=1), output_field=IntegerField())),
            failed_count=Count(Case(When(status='failed', then=1), output_field=IntegerField())),
            cancelled_count=Count(Case(When(status='cancelled', then=1), output_field=IntegerField()))
        )
        
        context.update(stats)
        return context

class ContentRequestCreateView(LoginRequiredMixin, CreateView):
    model = ContentRequest
    form_class = ContentRequestForm
    template_name = 'ai_content_generator/request_form.html'
    success_url = reverse_lazy('ai:content_request_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # Verificar grados disponibles en la base de datos
        print("Grados disponibles en la base de datos:")
        grades = Grade.objects.all()
        for grade in grades:
            print(f" - {grade.pk}: {grade.name} ({grade.level}) - Activo: {grade.is_active}")
        
        # Verificar si hay cursos duplicados
        print("\nVerificando cursos duplicados:")
        duplicated_courses = Course.objects.values('id').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicated_courses.exists():
            print("¡Atención! Se encontraron cursos con IDs duplicados:")
            for dup in duplicated_courses:
                course_id = dup['id']
                courses = Course.objects.filter(id=course_id)
                print(f"  - ID {course_id} ({dup['count']} instancias):")
                for course in courses:
                    print(f"    * {course.pk}: {course.name} ({course.code})")
            
            # Solución: Crear una lista de cursos sin duplicados
            all_course_ids = Course.objects.values_list('id', flat=True).distinct()
            self.unique_courses = {}
            
            for course_id in all_course_ids:
                course = Course.objects.filter(id=course_id).first()
                if course:
                    self.unique_courses[course_id] = course
            
            print(f"Se han identificado {len(self.unique_courses)} cursos únicos.")
        
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        topic = self.request.GET.get('topic', '')
        course_id = self.request.GET.get('course', '')
        grade_level = self.request.GET.get('grade_level', '')
        topic_id = self.request.GET.get('topic_id', '')
        course_topic_id = self.request.GET.get('course_topic_id', '')
        for_class = self.request.GET.get('for_class', 'false').lower() == 'true'
        
        print(f"Parámetros iniciales: topic={topic}, course_id={course_id}, grade_level={grade_level}, topic_id={topic_id}, course_topic_id={course_topic_id}, for_class={for_class}")
        
        # Si viene course_topic_id, es para generar contenido para toda la clase
        if course_topic_id and not grade_level and hasattr(self.request.user, 'teacher_profile'):
            try:
                from apps.academic.models import CourseTopic
                course_topic_obj = CourseTopic.objects.get(pk=course_topic_id)
                print(f"CourseTopic encontrado: {course_topic_obj.title}")
                
                # Obtener el grado a través de la sección del CourseTopic
                if course_topic_obj.section and course_topic_obj.section.grade:
                    grade_level = course_topic_obj.section.grade.name
                    print(f"Grado obtenido desde CourseTopic: {grade_level}")
                    
                # Si no se especificó el curso, usar el del CourseTopic
                if not course_id:
                    course_id = course_topic_obj.course.id
                    print(f"Curso obtenido desde CourseTopic: {course_id}")
                    
            except Exception as e:
                print(f"Error al obtener información del CourseTopic: {str(e)}")
                pass
        
        # Si el usuario es profesor, intentar obtener el grado del tema relacionado
        elif topic_id and not grade_level and hasattr(self.request.user, 'teacher_profile'):
            try:
                topic_obj = PortfolioTopic.objects.get(pk=topic_id)
                print(f"Tema encontrado: {topic_obj.title}")
                
                # Modificación: Obtener el grado a través de la relación correcta
                if topic_obj.portfolio and topic_obj.portfolio.student:
                    # Buscar matrícula ACTIVE del estudiante
                    active_enrollment = Enrollment.objects.filter(
                        student=topic_obj.portfolio.student,
                        status='ACTIVE'
                    ).first()
                    
                    if active_enrollment and active_enrollment.section and active_enrollment.section.grade:
                        grade_level = active_enrollment.section.grade.name
                        print(f"Grado obtenido (matrícula activa): {grade_level}")
                    else:
                        # Si no hay matrícula ACTIVE, probar con cualquier matrícula
                        any_enrollment = Enrollment.objects.filter(
                            student=topic_obj.portfolio.student
                        ).first()
                        
                        if any_enrollment and any_enrollment.section and any_enrollment.section.grade:
                            grade_level = any_enrollment.section.grade.name
                            print(f"Grado obtenido (cualquier estado): {grade_level}")
                        else:
                            print("No se encontró ninguna matrícula con sección o grado")
                else:
                    print("El tema no tiene portafolio o estudiante asociado")
            except PortfolioTopic.DoesNotExist:
                print(f"No se encontró el tema con ID {topic_id}")
                pass
            except Exception as e:
                print(f"Error al obtener el grado: {str(e)}")
                pass
        
        initial.update({
            'topic': topic,
            'grade_level': grade_level,
            'topic_id': topic_id,
            'course_topic_id': course_topic_id,
            'for_class': for_class,
        })
        
        # Si se especifica un curso, seleccionarlo por defecto
        if course_id:
            try:
                from apps.academic.models import Course
                course = Course.objects.get(pk=course_id)
                initial['course'] = course
                print(f"Curso inicializado: {course.name}")
            except Course.DoesNotExist:
                print(f"No se encontró el curso con ID {course_id}")
                pass
        
        # Establecer tipo de contenido por defecto si no está especificado
        if not initial.get('content_type'):
            from .models import ContentType
            material_didactico = ContentType.objects.filter(name='Material didáctico').first()
            if material_didactico:
                initial['content_type'] = material_didactico.id
                print(f"Tipo de contenido por defecto: {material_didactico.name}")
        
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        print(f"Form initial data: {form.initial}")
        
        # Ver estado actual del campo grade_level
        if 'grade_level' in form.initial:
            print(f"Grade level en el formulario: {form.initial['grade_level']}")
            # Verificar si el valor está en las opciones disponibles
            if hasattr(form.fields['grade_level'], 'choices'):
                choices = [choice[0] for choice in form.fields['grade_level'].choices]
                print(f"Choices disponibles: {choices}")
                print(f"¿Valor en choices?: {form.initial['grade_level'] in choices}")
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el topic_id de la URL
        topic_id = self.request.GET.get('topic_id')
        course_topic_id = self.request.GET.get('course_topic_id')
        for_class = self.request.GET.get('for_class', 'false').lower() == 'true'
        
        # Si viene course_topic_id, es para generar contenido para toda la clase
        if course_topic_id:
            try:
                from apps.academic.models import CourseTopic
                course_topic_obj = CourseTopic.objects.get(pk=course_topic_id)
                
                # Obtener información de la sección y estudiantes
                section = course_topic_obj.section
                students = Student.objects.filter(
                    enrollments__section=section,
                    enrollments__status='ACTIVE'
                ).distinct().select_related('user')
                
                # Obtener todas las secciones del mismo grado que maneja este docente
                current_grade = section.grade
                available_sections = Section.objects.filter(
                    grade=current_grade,
                    course_assignments__teacher=self.request.user.teacher_profile,
                    course_assignments__course=course_topic_obj.course,
                    is_active=True
                ).distinct().select_related('grade').prefetch_related('enrollments')
                
                # Agregar conteo de estudiantes a cada sección
                for avail_section in available_sections:
                    avail_section.current_students = Student.objects.filter(
                        enrollments__section=avail_section,
                        enrollments__status='ACTIVE'
                    ).count()
                
                # Añadir información al contexto
                context['course_topic'] = course_topic_obj
                context['section'] = section
                context['students'] = students
                context['students_count'] = students.count()
                context['for_class'] = True
                context['from_course_dashboard'] = True
                context['available_sections'] = available_sections
                
                # Información adicional
                context['course_name'] = course_topic_obj.course.name
                context['section_name'] = f"{section.grade.name} - Sección {section.name}"
                
            except Exception as e:
                print(f"Error al obtener información del CourseTopic: {str(e)}")
        
        # Lógica original para PortfolioTopic
        elif topic_id:
            try:
                # Obtener el tema del portafolio
                topic_obj = PortfolioTopic.objects.get(pk=topic_id)
                
                # Si el tema tiene un portafolio y estudiante asociado, agregar la información
                if topic_obj.portfolio and topic_obj.portfolio.student:
                    student = topic_obj.portfolio.student
                    
                    # Buscar la matrícula actual del estudiante para obtener datos adicionales
                    enrollment = Enrollment.objects.filter(
                        student=student, 
                        status='ACTIVE'
                    ).first()
                    
                    # Añadir la información al contexto
                    context['portfolio_topic'] = topic_obj
                    context['student'] = student
                    context['enrollment'] = enrollment
                    context['from_portfolio'] = True
            except PortfolioTopic.DoesNotExist:
                pass
            except Exception as e:
                print(f"Error al obtener información del portafolio: {str(e)}")
        
        return context
    
    def form_valid(self, form):
        content_request = form.save(commit=False)
        content_request.teacher = self.request.user
        
        # Obtener parámetros adicionales
        topic_id = self.request.GET.get('topic_id')
        course_topic_id = self.request.GET.get('course_topic_id')
        for_class = self.request.GET.get('for_class', 'false').lower() == 'true'
        
        # Información del estudiante (solo para PortfolioTopic)
        student_info = None
        
        # Manejar CourseTopic (contenido para toda la clase)
        if course_topic_id:
            try:
                from apps.academic.models import CourseTopic
                course_topic = CourseTopic.objects.get(pk=course_topic_id)
                
                # Agregar información del CourseTopic al campo additional_instructions
                additional_instructions = content_request.additional_instructions or ""
                class_info_text = f"\n\nINFORMACIÓN DEL TEMA DE CLASE:\nTema: {course_topic.title}\nCurso: {course_topic.course.name}\nSección: {course_topic.section.grade.name} - Sección {course_topic.section.name}\nProfesor: {course_topic.teacher.user.get_full_name()}\n\nEste contenido será utilizado como material de clase para todos los estudiantes de la sección. Por favor, genera contenido apropiado para el nivel educativo y que pueda ser aplicado a toda la clase."
                
                if course_topic.description:
                    class_info_text += f"\nDescripción del tema: {course_topic.description}"
                
                content_request.additional_instructions = additional_instructions + class_info_text
                
                # No marcar como para clase - se decidirá al momento de asignar
                # content_request.for_class = True
                
            except Exception as e:
                print(f"Error al obtener información del CourseTopic: {str(e)}")
        
        # Manejar PortfolioTopic (contenido individual)
        elif topic_id:
            try:
                topic = PortfolioTopic.objects.get(pk=topic_id)
                content_request.related_topic = topic
                
                # Guardar información del estudiante para el prompt
                if topic.portfolio and topic.portfolio.student:
                    student = topic.portfolio.student
                    # Obtener matrícula del estudiante
                    enrollment = Enrollment.objects.filter(
                        student=student, 
                        status='ACTIVE'
                    ).first()
                    
                    # Guardar información del estudiante en el campo additional_instructions
                    if enrollment:
                        student_info = {
                            'nombre': student.user.get_full_name(),
                            'grado': enrollment.section.grade.name if enrollment.section and enrollment.section.grade else content_request.grade_level,
                            'curso': content_request.course.name,
                            'tema_portafolio': topic.title,
                            'descripcion_tema': topic.description
                        }
                        
                        # Añadir información del estudiante al campo de instrucciones adicionales
                        additional_instructions = content_request.additional_instructions or ""
                        student_info_text = f"\n\nINFORMACIÓN DEL ESTUDIANTE:\nNombre: {student_info['nombre']}\nGrado: {student_info['grado']}\nCurso: {student_info['curso']}\nTema del portafolio: {student_info['tema_portafolio']}\nDescripción del tema: {student_info['descripcion_tema']}\n\nPor favor, personaliza el contenido para este estudiante específico considerando su nivel educativo y el tema del portafolio."
                        
                        content_request.additional_instructions = additional_instructions + student_info_text
                        
            except PortfolioTopic.DoesNotExist:
                print(f"No se encontró el tema de portafolio con ID {topic_id}")
                pass
            except Exception as e:
                print(f"Error al procesar tema de portafolio: {str(e)}")
                pass
        
        # Guardar la solicitud
        content_request.save()
        
        # Enviar la solicitud para procesamiento
        try:
            from .tasks import generate_content
            result = generate_content(content_request.id)
            
            # Eliminar el mensaje de Django y pasar información en el contexto de redirección
            # En lugar de usar messages.success, pasamos un parámetro en la URL
            redirect_url = reverse('ai:content_request_list') + '?request_created=true'
            
            # Si hay un tema relacionado y se marcó la opción para agregar al portafolio,
            # configuramos una marca para verificar luego el contenido generado
            if topic_id and form.cleaned_data.get('add_to_portfolio', False):
                # Guardamos la referencia al topic_id en la sesión para usarla cuando se complete
                self.request.session['auto_add_to_portfolio'] = {
                    'request_id': content_request.id,
                    'topic_id': topic_id
                }
                self.request.session.modified = True
                messages.info(self.request, "El contenido se agregará automáticamente al portafolio cuando termine de generarse.")
                
                if student_info:
                    messages.info(self.request, f"El contenido será personalizado para el estudiante {student_info['nombre']}.")
                    
            elif course_topic_id:
                # Para temas de clase, mostrar información apropiada
                try:
                    from apps.academic.models import CourseTopic
                    course_topic = CourseTopic.objects.get(pk=course_topic_id)
                    
                    messages.info(self.request, f"El contenido se está generando para la clase {course_topic.section.grade.name} - Sección {course_topic.section.name}. Podrás asignarlo manualmente a toda la sección o a estudiantes específicos cuando esté listo.")
                except Exception as e:
                    logger.error(f"Error obteniendo información del tema de clase: {str(e)}")
                    messages.info(self.request, "El contenido se está generando para toda la clase. Podrás asignarlo a los estudiantes cuando esté listo.")
                    
            return redirect(redirect_url)
            
        except Exception as e:
            messages.warning(self.request, f"Error al iniciar la generación: {str(e)}")
        
        return redirect('ai:content_request_list')

@login_required
def create_content_async(request):
    """
    Vista AJAX para crear contenido de forma asíncrona
    """
    logger.info(f"create_content_async llamada - Método: {request.method}")
    
    if request.method != 'POST':
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Crear el formulario con los datos POST
        logger.info(f"Datos POST recibidos: {list(request.POST.keys())}")
        form = ContentRequestForm(request.POST, user=request.user)
        
        if form.is_valid():
            logger.info("Formulario válido - procesando...")
            content_request = form.save(commit=False)
            content_request.teacher = request.user
            
            # Obtener parámetros adicionales
            topic_id = request.POST.get('topic_id')
            course_topic_id = request.POST.get('course_topic_id')
            for_class = request.POST.get('for_class', 'false').lower() == 'true'
            
            # Manejar CourseTopic (contenido para toda la clase)
            if course_topic_id:
                try:
                    from apps.academic.models import CourseTopic
                    course_topic = CourseTopic.objects.get(pk=course_topic_id)
                    
                    # Agregar información del CourseTopic al campo additional_instructions
                    additional_instructions = content_request.additional_instructions or ""
                    class_info_text = f"\n\nINFORMACIÓN DEL TEMA DE CLASE:\nTema: {course_topic.title}\nCurso: {course_topic.course.name}\nSección: {course_topic.section.grade.name} - Sección {course_topic.section.name}\nProfesor: {course_topic.teacher.user.get_full_name()}\n\nEste contenido será utilizado como material de clase para todos los estudiantes de la sección. Por favor, genera contenido apropiado para el nivel educativo y que pueda ser aplicado a toda la clase."
                    
                    if course_topic.description:
                        class_info_text += f"\nDescripción del tema: {course_topic.description}"
                    
                    content_request.additional_instructions = additional_instructions + class_info_text
                    
                except Exception as e:
                    logger.error(f"Error al obtener información del CourseTopic: {str(e)}")
            
            # Manejar PortfolioTopic (contenido individual)
            elif topic_id:
                try:
                    topic = PortfolioTopic.objects.get(pk=topic_id)
                    content_request.related_topic = topic
                    
                    # Guardar información del estudiante para el prompt
                    if topic.portfolio and topic.portfolio.student:
                        student = topic.portfolio.student
                        enrollment = Enrollment.objects.filter(
                            student=student, 
                            status='ACTIVE'
                        ).first()
                        
                        if enrollment:
                            student_info = {
                                'nombre': student.user.get_full_name(),
                                'grado': enrollment.section.grade.name if enrollment.section and enrollment.section.grade else content_request.grade_level,
                                'curso': content_request.course.name,
                                'tema_portafolio': topic.title,
                                'descripcion_tema': topic.description
                            }
                            
                            additional_instructions = content_request.additional_instructions or ""
                            student_info_text = f"\n\nINFORMACIÓN DEL ESTUDIANTE:\nNombre: {student_info['nombre']}\nGrado: {student_info['grado']}\nCurso: {student_info['curso']}\nTema del portafolio: {student_info['tema_portafolio']}\nDescripción del tema: {student_info['descripcion_tema']}\n\nPor favor, personaliza el contenido para este estudiante específico considerando su nivel educativo y el tema del portafolio."
                            
                            content_request.additional_instructions = additional_instructions + student_info_text
                            
                except PortfolioTopic.DoesNotExist:
                    logger.warning(f"No se encontró el tema de portafolio con ID {topic_id}")
                except Exception as e:
                    logger.error(f"Error al procesar tema de portafolio: {str(e)}")
            
            # Guardar la solicitud
            content_request.save()
            
            # Enviar la solicitud para procesamiento asíncrono
            try:
                from .tasks import generate_content
                
                # Intentar usar Celery primero
                try:
                    result = generate_content.delay(content_request.id)
                    task_id = result.id
                    logger.info(f"Tarea Celery iniciada: {task_id} para request {content_request.id}")
                    
                except Exception as celery_error:
                    logger.warning(f"Celery no disponible, usando procesamiento directo: {str(celery_error)}")
                    # Fallback: usar procesamiento directo en hilo separado
                    from .tasks import start_content_generation_thread
                    thread = start_content_generation_thread(content_request.id)
                    task_id = f"thread_{content_request.id}"
                    logger.info(f"Hilo de procesamiento iniciado para request {content_request.id}")
                
                response_data = {
                    'success': True,
                    'message': 'Su contenido se está generando en segundo plano. Será notificado cuando esté listo.',
                    'request_id': content_request.id,
                    'task_id': task_id,
                    'redirect_url': reverse('ai:content_request_list')
                }
                logger.info(f"Respuesta exitosa: {response_data}")
                return JsonResponse(response_data)
                
            except Exception as e:
                logger.error(f"Error al iniciar generación: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al iniciar la generación: {str(e)}'
                }, status=500)
        
        else:
            # Errores de validación del formulario
            logger.warning(f"Errores de validación del formulario: {form.errors}")
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{form.fields.get(field, {}).get('label', field)}: {error}")
            
            error_response = {
                'success': False,
                'error': 'Errores de validación',
                'errors': errors
            }
            logger.warning(f"Respuesta de error: {error_response}")
            return JsonResponse(error_response, status=400)
    
    except Exception as e:
        logger.error(f"Error general en create_content_async: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)

@login_required
def check_content_status(request, request_id):
    """
    Vista AJAX para verificar el estado de generación de contenido
    """
    try:
        content_request = get_object_or_404(ContentRequest, id=request_id, teacher=request.user)
        
        # Verificar si hay contenido generado
        generated_content = content_request.contents.first()
        
        if generated_content:
            return JsonResponse({
                'status': 'completed',
                'message': 'Su contenido ya está listo, puede ir a revisarlo',
                'content_id': generated_content.id,
                'content_url': reverse('ai:content_detail', args=[generated_content.id]),
                'content_title': generated_content.title
            })
        elif content_request.status == 'failed':
            return JsonResponse({
                'status': 'failed',
                'message': 'Ha ocurrido un error al generar el contenido'
            })
        elif content_request.status == 'cancelled':
            return JsonResponse({
                'status': 'cancelled',
                'message': 'La generación fue cancelada'
            })
        else:
            return JsonResponse({
                'status': 'processing',
                'message': 'Su contenido se está generando...'
            })
            
    except Exception as e:
        logger.error(f"Error al verificar estado del contenido {request_id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error al verificar estado: {str(e)}'
        }, status=500)

def improve_content_formatting(html_content, request=None):
    """
    Mejora el formato del contenido HTML para una mejor visualización.
    Si el contenido ya es HTML bien formado, lo preserva.
    Si es texto plano con formato tipo markdown, lo convierte a HTML estructurado.
    Ahora incluye header institucional con logo.
    """
    # Obtener información institucional para el header
    # Header institucional eliminado por solicitud del usuario
    
    if not html_content or html_content.strip() == '':
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contenido Vacío</title>
            {get_institutional_styles()}
        </head>
        <body>
            <div class="content-container">
                <div class="alert alert-warning">
                    <h3>Contenido no disponible</h3>
                    <p>El contenido no está disponible o está vacío. Por favor, intente regenerar el contenido.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    # Verificar si el contenido ya es HTML completo
    if html_content.strip().startswith('<!DOCTYPE html>') or html_content.strip().startswith('<html'):
        # Si ya es HTML completo generado por IA, NO MODIFICAR para evitar conflictos
        # El HTML generado por IA ya incluye todo lo necesario
        return html_content
    
    # Verificar si el contenido tiene etiquetas HTML básicas
    if '<div' in html_content or '<section' in html_content or '<h1' in html_content:
        # Si ya tiene estructura HTML básica pero no es un documento completo,
        # lo envolvemos en una estructura HTML mínima que preserva los estilos propios
        if not ('<html' in html_content and '</html>' in html_content):
            # Buscar estilos personalizados en el contenido
            custom_styles = ""
            style_match = re.search(r'<style[^>]*>([\s\S]*?)<\/style>', html_content)
            if style_match:
                custom_styles = style_match.group(0)
                # Eliminar los estilos del contenido ya que los agregaremos en el head
                html_content = html_content.replace(style_match.group(0), '')
            
            return f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {custom_styles}
                {get_institutional_styles()}
            </head>
            <body>
                <div class="content-container">
                    {html_content}
                </div>
            </body>
            </html>
            """
        return html_content
    
    # Si llegamos aquí, el contenido es probablemente texto plano o formato markdown
    # Intentamos convertirlo a HTML estructurado
    try:
        # Convertir encabezados con formato markdown a HTML
        lines = html_content.split('\n')
        formatted_lines = []
        
        in_list = False
        list_type = None
        
        for line in lines:
            # Convertir encabezados markdown
            if line.strip().startswith('# '):
                formatted_lines.append(f'<h1>{line.strip()[2:]}</h1>')
            elif line.strip().startswith('## '):
                formatted_lines.append(f'<h2>{line.strip()[3:]}</h2>')
            elif line.strip().startswith('### '):
                formatted_lines.append(f'<h3>{line.strip()[4:]}</h3>')
            elif line.strip().startswith('#### '):
                formatted_lines.append(f'<h4>{line.strip()[5:]}</h4>')
            # Convertir listas markdown
            elif line.strip().startswith('- '):
                if not in_list or list_type != 'ul':
                    if in_list:
                        formatted_lines.append(f'</{list_type}>')
                    formatted_lines.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                formatted_lines.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
                if not in_list or list_type != 'ol':
                    if in_list:
                        formatted_lines.append(f'</{list_type}>')
                    formatted_lines.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                text = line.strip()[line.find('. ')+2:]
                formatted_lines.append(f'<li>{text}</li>')
            # Manejando títulos con asteriscos o negrita
            elif '**' in line and line.strip():
                # Reemplazar el texto en negrita manteniendo los asteriscos para la conversión posterior
                formatted_lines.append(f'<p>{line}</p>')
            # Líneas en blanco cierran listas
            elif not line.strip() and in_list:
                formatted_lines.append(f'</{list_type}>')
                formatted_lines.append('<p></p>')
                in_list = False
                list_type = None
            # Líneas normales de texto
            elif line.strip():
                formatted_lines.append(f'<p>{line}</p>')
            else:
                formatted_lines.append('<p></p>')
        
        # Cerrar cualquier lista abierta
        if in_list:
            formatted_lines.append(f'</{list_type}>')
        
        # Unir líneas y convertir formato de texto
        html_content = '\n'.join(formatted_lines)
        
        # Convertir formato de texto en línea (negrita, cursiva)
        # Primero guardamos el contenido en etiquetas ya formateadas
        html_saved_tags = []
        html_temp = html_content
        
        # Extraer y guardar etiquetas HTML existentes
        tags_pattern = re.compile(r'<[^>]+>.*?</[^>]+>', re.DOTALL)
        for i, match in enumerate(tags_pattern.finditer(html_temp)):
            placeholder = f'___HTML_TAG_{i}___'
            html_saved_tags.append(match.group(0))
            html_temp = html_temp.replace(match.group(0), placeholder)
        
        # Convertir formato markdown en el texto
        # Negrita (**texto**)
        html_temp = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_temp)
        # Cursiva (*texto*)
        html_temp = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_temp)
        # Código (`código`)
        html_temp = re.sub(r'`(.*?)`', r'<code>\1</code>', html_temp)
        
        # Restaurar etiquetas HTML guardadas
        for i, tag in enumerate(html_saved_tags):
            placeholder = f'___HTML_TAG_{i}___'
            html_temp = html_temp.replace(placeholder, tag)
        
        html_content = html_temp
        
    except Exception as e:
        # Si hay algún error en el procesamiento, mantener el contenido original
        # pero envuelto en párrafos
        paragraphs = html_content.split('\n\n')
        html_content = ''.join([f'<p>{p.strip()}</p>' if p.strip() else '<p></p>' for p in paragraphs])
    
    # Envolver el contenido final en un documento HTML completo con header institucional
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Material Educativo Generado con IA</title>
        {get_institutional_styles()}
    </head>
    <body>
        <div class="content-container">
            {html_content}
        </div>
    </body>
    </html>
    """

def get_institution_info(request=None):
    """
    Obtiene información de la institución del usuario actual
    """
    if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
        return None
    
    try:
        from apps.institutions.models import Institution
        institution = None
        
        # Intentar obtener la institución desde diferentes perfiles
        if hasattr(request.user, 'teacher_profile') and hasattr(request.user.teacher_profile, 'institution'):
            institution = request.user.teacher_profile.institution
        elif hasattr(request.user, 'director_profile') and hasattr(request.user.director_profile, 'institution'):
            institution = request.user.director_profile.institution
        elif hasattr(request.user, 'student_profile'):
            # Para estudiantes, obtener la institución desde su matrícula activa
            from apps.academic.models import Enrollment
            enrollment = Enrollment.objects.filter(
                student=request.user.student_profile,
                status='ACTIVE'
            ).first()
            if enrollment and hasattr(enrollment.section, 'institution'):
                institution = enrollment.section.institution
        
        if institution:
            institution_info = {
                'name': institution.name,
                'address': institution.address,
                'phone': institution.phone,
                'email': institution.email,
                'website': institution.website,
            }
            
            # Agregar URL del logo si existe
            if institution.logo:
                institution_info['logo_url'] = institution.logo.url
            
            # Obtener colores institucionales si existen
            try:
                settings = institution.settings
                if settings.logo_enabled:
                    institution_info['colors'] = {
                        'primary': settings.primary_color,
                        'secondary': settings.secondary_color,
                        'accent': settings.accent_color,
                    }
            except:
                pass
            
            return institution_info
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error obteniendo información institucional: {str(e)}")
    
    return None

def get_institutional_styles():
    """
    Genera los estilos CSS para el header institucional y el contenido
    """
    return """
    <style>
        .institutional-header {
            background: linear-gradient(135deg, #005CFF 0%, #A142F5 50%, #00CFFF 100%);
            color: white;
            padding: 2rem 2rem 1.5rem 2rem;
            margin: -20px -20px 2rem -20px;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 8px 32px rgba(0, 92, 255, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .institutional-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
            opacity: 0.7;
            z-index: 0;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        .institution-logo {
            width: 80px;
            height: 80px;
            object-fit: contain;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 0.5rem;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.2);
        }
        
        .institution-logo-placeholder {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .institution-info {
            flex: 1;
        }
        
        .institution-name {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0 0 0.3rem 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .institution-subtitle {
            font-size: 1rem;
            margin: 0 0 0.2rem 0;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .institution-address {
            font-size: 0.85rem;
            margin: 0;
            opacity: 0.8;
        }
        
        .header-right {
            display: flex;
            flex-direction: column;
            gap: 0.8rem;
            align-items: flex-end;
        }
        
        .ai-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 25px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .generation-date {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .content-container {
            padding: 0;
        }
        
        body {
            font-family: 'Inter', 'Poppins', 'Segoe UI', sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
        }
        
        h1, h2, h3, h4 {
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
            color: #2c3e50;
        }
        
        h1 { 
            font-size: 2.2rem; 
            border-bottom: 3px solid #005CFF; 
            padding-bottom: 0.5rem; 
            color: #005CFF;
        }
        
        h2 { 
            font-size: 1.8rem; 
            color: #A142F5;
            position: relative;
        }
        
        h2::before {
            content: '';
            position: absolute;
            left: -1rem;
            top: 50%;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, #A142F5, #00CFFF);
            transform: translateY(-50%);
            border-radius: 2px;
        }
        
        h3 { 
            font-size: 1.5rem; 
            color: #00CFFF;
        }
        
        p { 
            margin-bottom: 1.2rem; 
            text-align: justify;
        }
        
        ul, ol { 
            margin-bottom: 1.5rem; 
            padding-left: 2rem; 
        }
        
        li { 
            margin-bottom: 0.8rem; 
            line-height: 1.6;
        }
        
        strong {
            color: #2c3e50;
            font-weight: 600;
        }
        
        em {
            color: #7f8c8d;
            font-style: italic;
        }
        
        code {
            background: #f8f9fa;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            border: 1px solid #e9ecef;
        }
        
        a {
            color: #005CFF;
            text-decoration: none;
            font-weight: 500;
        }
        
        a:hover {
            color: #A142F5;
            text-decoration: underline;
        }
        
        img {
            max-width: 100%;
            height: auto;
            margin: 1.5rem 0;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        th, td {
            border: 1px solid #e9ecef;
            padding: 1rem;
            text-align: left;
        }
        
        th {
            background: linear-gradient(135deg, #005CFF, #A142F5);
            color: white;
            font-weight: 600;
        }
        
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        @media (max-width: 768px) {
            .institutional-header {
                padding: 1.5rem 1rem;
                margin: -20px -20px 1.5rem -20px;
            }
            
            .header-content {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            
            .header-left {
                flex-direction: column;
                gap: 1rem;
            }
            
            .institution-logo,
            .institution-logo-placeholder {
                width: 60px;
                height: 60px;
            }
            
            .institution-name {
                font-size: 1.4rem;
            }
            
            body {
                padding: 15px;
            }
        }
        
        @media print {
            .institutional-header {
                background: #005CFF !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Establecer la fecha de generación
            const dateElement = document.getElementById('generation-date');
            if (dateElement) {
                const now = new Date();
                const formattedDate = now.toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                dateElement.textContent = formattedDate;
            }
        });
    </script>
    """

class ContentDetailView(LoginRequiredMixin, DetailView):
    model = GeneratedContent
    template_name = 'ai_content_generator/content_detail.html'
    context_object_name = 'content'
    
    def get_queryset(self):
        """Optimizar las consultas SQL usando select_related"""
        return GeneratedContent.objects.select_related(
            'request',
            'request__teacher',
            'request__course',
            'request__content_type'
        )
    
    def get(self, request, *args, **kwargs):
        # Limpiar la sesión de paquete SCORM creado después de mostrar la página
        if 'scorm_package_created' in request.session:
            logger.info(f"Limpiando datos de paquete SCORM de la sesión: {request.session['scorm_package_created']}")
            # No eliminamos inmediatamente para que la plantilla pueda usar los datos
            request.session['_clear_scorm_data'] = True


        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            # Check if this pk corresponds to a ContentRequest instead of a GeneratedContent
            content_request_id = kwargs.get('pk')
            try:
                # Check if there's a ContentRequest with this ID
                content_request = ContentRequest.objects.get(pk=content_request_id)
                # If it exists, redirect to the content_request_redirect view
                return redirect('ai:content_request_redirect', pk=content_request_id)
            except ContentRequest.DoesNotExist:
                # If neither GeneratedContent nor ContentRequest exists with this ID
                raise Http404("No se encontró ningún contenido generado con ese ID.")
    
    def post(self, request, *args, **kwargs):
        """
        Manejar las actualizaciones de contenido cuando se envía el formulario de edición
        """
        content = self.get_object()
        
        # Verificar que el usuario tiene permisos para editar este contenido
        if content.request.teacher != request.user and not request.user.is_staff:
            messages.error(request, "No tiene permisos para editar este contenido.")
            return redirect('ai:content_detail', pk=content.id)
            
        # Obtener el contenido editado del formulario
        edited_content = request.POST.get('content_html', '')
        
        if edited_content:
            try:
                # Comprobar si el contenido ha sido cambiado
                if content.formatted_content != edited_content:
                    # Actualizar el contenido formateado
                    content.formatted_content = edited_content
                    content.save()
                    messages.success(request, "Contenido actualizado exitosamente.")
                else:
                    messages.info(request, "No se detectaron cambios en el contenido.")
            except Exception as e:
                logger.exception(f"Error al actualizar contenido: {str(e)}")
                messages.error(request, f"Error al guardar el contenido: {str(e)}")
        else:
            messages.error(request, "El contenido no puede estar vacío.")
        
        # Volver a cargar la página actual en lugar de redirigir
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()
        context['request'] = content.request
        
        # Mejorar el formato del contenido para la visualización
        if content.formatted_content:
            try:
                # Verificar si el contenido está en formato markdown con comillas triples
                if content.formatted_content.strip().startswith('```html'):
                    # Extraer el contenido HTML real del formato markdown
                    import re
                    html_match = re.search(r'```html\s*([\s\S]*?)\s*```', content.formatted_content)
                    if html_match:
                        extracted_html = html_match.group(1).strip()
                        content.formatted_content = extracted_html
                        logger.info(f"Se extrajo contenido HTML del formato markdown para el contenido {content.id}")
                
                # Verificar si el contenido ya es HTML completo (no necesita procesamiento adicional)
                content_clean = content.formatted_content.strip()
                is_complete_html = (
                    content_clean.startswith('<!DOCTYPE html>') or 
                    content_clean.startswith('<html') or
                    content_clean.startswith('<meta') or
                    '<style>' in content_clean[:1000]  # Detectar contenido con estilos CSS
                )
                
                if is_complete_html:
                    logger.info(f"Contenido {content.id} ya es HTML completo, manteniendo formato original")
                    # No aplicar improve_content_formatting para preservar el HTML original generado por IA
                else:
                    # Solo aplicar formatting si no es HTML completo
                    content.formatted_content = improve_content_formatting(content.formatted_content, request)
                    logger.info(f"Se aplicó mejora de formato al contenido {content.id}")
            except Exception as e:
                logger.error(f"Error al procesar el formato del contenido: {str(e)}")
                # En caso de error, establecer un HTML básico de error
                content.formatted_content = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Error al procesar el contenido</title>
                </head>
                <body>
                    <div style="padding: 20px; background-color: #fff5f5; border-left: 4px solid #ff5252; margin: 20px 0;">
                        <h3 style="color: #e53e3e;">Error al procesar el contenido</h3>
                        <p>Se produjo un error al intentar formatear el contenido. Por favor, intente regenerar el contenido.</p>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                </body>
                </html>
                """
        
        # Garantizar que siempre se muestren botones de edición y establecer edit_mode a True siempre
        context['edit_mode'] = True  # Forzar modo de edición por defecto
        context['show_edit_buttons'] = True
        logger.info(f"Modo de edición activado por defecto para usuario {self.request.user.username}")
        
        # Extraer el topic_id directamente de la URL y pasarlo al contexto
        topic_id = self.request.GET.get('topic_id')
        context['topic_id'] = topic_id
        logger.info(f"ContentDetailView - topic_id en URL: '{topic_id}'")
        
        # Obtener los estudiantes para el selector independientemente del tipo de usuario
        try:
            from apps.academic.models import Student
            
            # Verificar que el curso sea válido antes de usarlo en el filtro
            course = content.request.course
            logger.info(f"Curso asociado: {course}")
            
            # Intentar obtener todos los estudiantes para propósitos de depuración
            all_students = Student.objects.all()
            logger.info(f"Total de estudiantes en el sistema: {all_students.count()}")
            for idx, student in enumerate(all_students[:5]):  # Mostrar solo los primeros 5 para evitar logs muy largos
                logger.info(f"Estudiante #{idx+1}: ID={student.id}, Nombre={student.user.get_full_name() if hasattr(student, 'user') and student.user else 'Sin nombre'}")
            
            # Buscar estudiantes matriculados en secciones del curso
            students = Student.objects.filter(
                enrollments__section__course_assignments__course=course
            ).distinct()
            
            # Si no hay estudiantes con la consulta anterior, buscar de forma más general
            if students.count() == 0:
                logger.warning(f"No se encontraron estudiantes con la consulta principal. Intentando consulta alternativa...")
                students = Student.objects.filter(
                    enrollments__section__course_assignments__course__name=course.name
                ).distinct()
                
                # Si aún no hay estudiantes, intentar otra consulta más general
                if students.count() == 0:
                    logger.warning(f"No se encontraron estudiantes con la consulta alternativa. Cargando todos los estudiantes...")
                    students = Student.objects.all()
            
            context['students'] = students
            logger.info(f"Cargados {students.count()} estudiantes para el selector")
            
            # Debug info - verificar si los estudiantes tienen nombres
            for idx, student in enumerate(students[:10]):
                try:
                    full_name = student.user.get_full_name() if hasattr(student, 'user') and student.user else 'Sin nombre'
                    logger.info(f"Estudiante cargado #{idx+1}: ID={student.id}, Nombre={full_name}")
                except Exception as e:
                    logger.error(f"Error al acceder al nombre del estudiante {student.id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error al cargar estudiantes: {str(e)}")
            context['students'] = []
            context['students_error'] = str(e)
        
        # Obtener temas de portafolio disponibles para el curso
        try:
            from apps.portfolios.models import PortfolioTopic, StudentPortfolio
            
            # Cargar todos los temas con información de sus portafolios y estudiantes
            portfolio_topics = PortfolioTopic.objects.filter(
                course=content.request.course
            ).select_related('portfolio', 'portfolio__student', 'portfolio__student__user').order_by('-created_at')
            
            # Añadir información del estudiante a cada tema
            topics_with_students = []
            for topic in portfolio_topics:
                try:
                    student_id = topic.portfolio.student.id
                    student_name = topic.portfolio.student.user.get_full_name()
                    logger.info(f"Tema: {topic.title} - Estudiante: {student_name} (ID: {student_id})")
                    topics_with_students.append({
                        'id': topic.id,
                        'title': topic.title,
                        'course_name': topic.course.name,
                        'student_id': student_id,
                        'student_name': student_name,
                        'topic': topic  # Objeto original
                    })
                except Exception as e:
                    logger.error(f"Error al procesar tema {topic.id}: {str(e)}")
            
            context['portfolio_topics'] = topics_with_students
            logger.info(f"Cargados {len(topics_with_students)} temas con información de estudiantes")
        except Exception as e:
            logger.error(f"Error al cargar temas de portafolio: {str(e)}")
            context['portfolio_topics'] = []
            context['portfolio_topics_error'] = str(e)
        
        # Si hay topic_id, obtener el tema específico
        if topic_id:
            try:
                topic = PortfolioTopic.objects.get(pk=topic_id)
                context['selected_topic'] = topic
                logger.info(f"Tema seleccionado: {topic.title}")
            except PortfolioTopic.DoesNotExist:
                logger.warning(f"No se encontró el tema con ID {topic_id}")
            except Exception as e:
                logger.error(f"Error al obtener tema: {str(e)}")
        
        # Limpiar datos de sesión si es necesario
        if '_clear_scorm_data' in self.request.session:
            del self.request.session['_clear_scorm_data']
            if 'scorm_package_created' in self.request.session:
                del self.request.session['scorm_package_created']
                self.request.session.modified = True
        
        return context

def create_scorm_package(request, content_id):
    """
    Crea un paquete SCORM para un contenido generado específico.
    """
    if not request.user.is_authenticated:
        logger.warning(f"Intento de generación de SCORM sin autenticación - content_id: {content_id}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
        else:
            messages.error(request, "Debe iniciar sesión para crear un paquete SCORM.")
            return redirect('login')
    
    try:
        # Obtener el contenido
        content = get_object_or_404(GeneratedContent, pk=content_id)
        logger.info(f"Creando paquete SCORM para contenido {content_id}")

        # Verificar que el usuario tiene permisos para este contenido
        if content.request.teacher != request.user and not request.user.is_staff:
            error_msg = "No tiene permisos para crear paquetes SCORM para este contenido."
            logger.warning(f"Usuario {request.user.username} intentó crear SCORM sin permisos para contenido {content_id}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=403)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)

        # Verificar si ya existe un paquete
        existing_package = SCORMPackage.objects.filter(generated_content=content).first()
        
        if existing_package:
            logger.info(f"Paquete SCORM ya existe para contenido {content_id}: ID={existing_package.id}")
            
            # Determinar si es AJAX o no
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Paquete SCORM ya existente',
                    'package_id': existing_package.id,
                    'download_url': reverse('scorm_packager:download_scorm_package', args=[existing_package.id]),
                    'view_url': reverse('scorm_packager:scorm_package_detail', args=[existing_package.id])
                })
            else:
                # Si no es AJAX, redirigir a la descarga
                messages.success(request, "Utilizando paquete SCORM existente. Comenzando descarga...")
                return redirect('scorm_packager:download_scorm_package', pk=existing_package.id)

        # Preparar metadatos
        metadata = {
            'title': content.title,
            'description': f"Contenido generado para {content.request.course.name}",
            'version': '1.0',
            'standard': 'scorm_2004_4th'
        }

        # Crear paquete SCORM usando el servicio
        try:
            # Usar el contenido crudo que es el que contiene el contenido educativo real
            source_content = content.raw_content or content.formatted_content or ""
            
            logger.info(f"📋 SCORM Content length: {len(source_content)}")
            logger.info(f"📋 SCORM Content preview: {source_content[:500]}...")
            
            if not source_content.strip():
                logger.error("⚠️ Contenido vacío para generar SCORM")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'El contenido está vacío y no se puede generar un paquete SCORM'
                    }, status=400)
                messages.error(request, "El contenido está vacío y no se puede generar un paquete SCORM")
                return redirect('ai:content_detail', pk=content_id)
            
            # Crear nuevo paquete usando el contenido educativo completo
            packager = SCORMPackager(source_content, metadata)
            package_path = packager.create_package()
            
            # Convertir la ruta del paquete a una ruta relativa
            relative_path = os.path.relpath(package_path, settings.MEDIA_ROOT)
            
            # Crear registro en la base de datos
            scorm_package = SCORMPackage.objects.create(
                generated_content=content,
                title=content.title,
                description=metadata['description'],
                standard=metadata['standard'],
                package_file=relative_path,
                created_by=request.user
            )
            logger.info(f"Nuevo paquete SCORM creado: ID={scorm_package.id}, Ruta={relative_path}")

            # Preparar respuesta
            response_data = {
                'success': True,
                'message': 'Paquete SCORM creado exitosamente',
                'package_id': scorm_package.id,
                'download_url': reverse('scorm_packager:download_scorm_package', args=[scorm_package.id]),
                'view_url': reverse('scorm_packager:scorm_package_detail', args=[scorm_package.id])
            }

            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            
            # Si no es AJAX, redirigir directamente a la descarga
            messages.success(request, "Paquete SCORM creado exitosamente. Comenzando descarga...")
            return redirect(response_data['download_url'])

        except Exception as e:
            logger.error(f"Error al crear paquete SCORM: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)  # Incluir el mensaje de error específico
                }, status=500)
            messages.error(request, f"Error al crear el paquete SCORM: {str(e)}")
            return redirect('ai:content_detail', pk=content_id)

    except Exception as e:
        logger.error(f"Error general al crear paquete SCORM: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)  # Incluir el mensaje de error específico
            }, status=500)
        messages.error(request, f"Error al procesar la solicitud: {str(e)}")
        return redirect('ai:content_detail', pk=content_id)

def get_generation_progress_view(request, request_id):
    """
    Obtiene el progreso de la generación de contenido con manejo mejorado de errores
    """
    try:
        # Verificar que la solicitud existe
        try:
            content_request = ContentRequest.objects.get(id=request_id)
        except ContentRequest.DoesNotExist:
            logger.warning(f"Solicitud {request_id} no encontrada - posiblemente eliminada")
            return JsonResponse({
                'status': 'not_found',
                'progress': 0,
                'message': 'Solicitud no encontrada',
                'error': 'La solicitud de contenido no existe o fue eliminada',
                'updated_at': time.time()
            }, status=404)
        
        # Verificar permisos
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error', 
                'message': 'Usuario no autenticado', 
                'progress': 0
            }, status=401)
        
        # Si el usuario no es un superusuario, verificar que sea el propietario de la solicitud
        if not request.user.is_superuser:
            # Simplificar verificación: comprobar directamente si el usuario es el profesor
            if content_request.teacher != request.user:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'No tiene permiso para acceder a esta solicitud', 
                    'progress': 0
                }, status=403)
        
        # Verificar si hay contenido generado que indique que la solicitud está completada
        has_content = GeneratedContent.objects.filter(request_id=request_id).exists()
        if has_content and content_request.status != 'completed':
            # Actualizar estado en la base de datos
            content_request.status = 'completed'
            content_request.save(update_fields=['status'])
            # Limpiar caché
            cache_key = f"content_progress_{request_id}"
            cache.delete(cache_key)
            
            # Responder con estado completo
            return JsonResponse({
                'status': 'completed',
                'progress': 100,
                'message': 'Contenido generado con éxito',
                'updated_at': time.time()
            })
        
        # Verificar si la solicitud está atorada (más de 2 horas en processing)
        from django.utils import timezone
        from datetime import timedelta
        if (content_request.status == 'processing' and 
            content_request.updated_at < timezone.now() - timedelta(hours=2)):
            
            logger.warning(f"Solicitud {request_id} atorada por más de 2 horas, reseteando a failed")
            content_request.status = 'failed'
            content_request.save(update_fields=['status'])
            
            # Limpiar caché obsoleto
            cache_key = f"content_progress_{request_id}"
            cache.delete(cache_key)
            
            return JsonResponse({
                'status': 'failed',
                'progress': 0,
                'message': 'La generación ha sido cancelada por timeout',
                'error': 'La generación tomó demasiado tiempo y fue cancelada automáticamente',
                'updated_at': time.time()
            })
        
        # Verificar si la solicitud falló pero no se actualizó correctamente
        if content_request.status not in ['completed', 'processing', 'pending'] and not has_content:
            content_request.status = 'failed'
            content_request.save(update_fields=['status'])
            return JsonResponse({
                'status': 'failed',
                'progress': 0,
                'message': 'Error en la generación de contenido',
                'error': 'La generación falló',
                'updated_at': time.time()
            })
                
        # Obtener información de progreso desde el servicio de tasks
        progress_data = get_generation_progress(request_id)
        
        # Limpiar información de error si existe
        if 'error_details' in progress_data and progress_data['error_details']:
            # Limitar los detalles del error a un número razonable de líneas para evitar sobrecarga
            error_lines = progress_data['error_details'].split('\n')
            if len(error_lines) > 20:
                # Tomar las primeras 10 líneas y las últimas 10 líneas si es muy largo
                shortened_error = '\n'.join(error_lines[:10] + ['...'] + error_lines[-10:])
                progress_data['error_details'] = shortened_error
        
        logger.info(f"Progreso para solicitud {request_id}: {progress_data}")
        return JsonResponse(progress_data)
    
    except Exception as e:
        logger.exception(f"Error al obtener progreso para solicitud {request_id}: {str(e)}")
        return JsonResponse({
            'status': 'error', 
            'message': f'Error al obtener progreso: {str(e)}', 
            'progress': 0,
            'updated_at': time.time()
        }, status=500)

def regenerate_content_view(request, request_id):
    """
    Vista para regenerar contenido fallido
    """
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Usuario no autenticado'}, status=401)
        messages.error(request, "Debe iniciar sesión para regenerar contenido.")
        return redirect('login')
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        content_request = ContentRequest.objects.get(id=request_id)
        
        # Verificar permiso
        if content_request.teacher != request.user and not request.user.is_staff:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'No tiene permisos para regenerar este contenido'}, status=403)
            messages.error(request, "No tiene permisos para regenerar este contenido.")
            return redirect('ai:content_request_list')
        
        # Restablecer el estado a pendiente
        content_request.status = 'pending'
        content_request.save()
        
        # Volver a iniciar la generación
        from .tasks import generate_content
        result = generate_content(content_request.id)
        
        logger.info(f"Regeneración iniciada para solicitud {request_id}")
        
        # Si es AJAX, devolver JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Regeneración iniciada correctamente'})
        
        # Si no es AJAX, redirigir con mensaje
        messages.success(request, "Regeneración de contenido iniciada correctamente. Por favor, espere unos momentos...")
        
        # Redirigir a la lista de solicitudes
        return redirect('ai:content_request_list')
    
    except ContentRequest.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Solicitud no encontrada'}, status=404)
        messages.error(request, "La solicitud no fue encontrada.")
        return redirect('ai:content_request_list')
    
    except Exception as e:
        logger.exception(f"Error al regenerar contenido para solicitud {request_id}: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Error al regenerar: {str(e)}'}, status=500)
        messages.error(request, f"Error al regenerar contenido: {str(e)}")
        return redirect('ai:content_request_list')

def add_content_to_topic(request):
    """
    Añade contenido generado a un tema del portafolio.
    Puede recibir el parámetro 'direct=1' para operación en un solo paso.
    """
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
        messages.error(request, "Debe iniciar sesión para añadir contenido a un tema.")
        return redirect('login')
    
    try:
        # Determinar si es operación directa, AJAX o normal
        is_direct = request.GET.get('direct') == '1' or request.POST.get('direct') == '1'
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        logger.info(f"Añadir contenido a tema - Usuario: {request.user.username} - Método: {request.method} - Modo directo: {is_direct} - AJAX: {is_ajax}")
        
        # Obtener parámetros (de GET o POST según el método)
        if request.method == 'GET':
            content_id = request.GET.get('content_id')
            topic_id = request.GET.get('topic_id')
            title = request.GET.get('title', '')
            description = request.GET.get('description', 'Material generado por IA')
            material_type = request.GET.get('material_type', 'TEXT')
        else:  # POST
            content_id = request.POST.get('content_id')
            topic_id = request.POST.get('topic_id')
            title = request.POST.get('title', '')
            description = request.POST.get('description', 'Material generado por IA')
            material_type = request.POST.get('material_type', 'TEXT')
        
        logger.info(f"Parámetros: content_id={content_id}, topic_id={topic_id}, material_type={material_type}")
        
        # Validar que se recibieron los parámetros requeridos
        if not content_id:
            error_msg = "No se especificó un contenido para añadir."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ai:content_request_list')
            
        if not topic_id:
            error_msg = "No se especificó un tema de portafolio."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)
            
        if not title:
            error_msg = "El título es obligatorio."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)
            
        if not material_type:
            error_msg = "El tipo de material es obligatorio."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)
        
        # Obtener objetos necesarios
        content = get_object_or_404(GeneratedContent, pk=content_id)
        
        try:
            topic = PortfolioTopic.objects.get(pk=topic_id)
        except PortfolioTopic.DoesNotExist:
            error_msg = f"El tema de portafolio con ID {topic_id} no existe."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=404)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)
            
        # Verificar que el tema tenga un portafolio y estudiante asociado
        if not topic.portfolio or not topic.portfolio.student:
            error_msg = "El tema seleccionado no tiene un portafolio o estudiante válido asociado."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)
        
        # Obtener estudiante del portafolio
        student = topic.portfolio.student
        
        # MODIFICACIÓN TEMPORAL: Omitir verificación de permisos para pruebas
        # Comentario: Esta modificación es solo para propósitos de prueba y debe revertirse en producción
        """
        # Verificar permisos
        if not (request.user.is_staff or request.user == topic.teacher):
            error_msg = "No tiene permisos para agregar material a este tema."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=403)
            messages.error(request, error_msg)
            return redirect('ai:content_detail', pk=content_id)
        """
        
        # Crear material en el portafolio
        # Verificar si existe un paquete SCORM para este contenido o crear uno nuevo
        from apps.scorm_packager.models import SCORMPackage

        scorm_package = SCORMPackage.objects.filter(generated_content=content).first()
        if not scorm_package:
            logger.warning(f"No existe paquete SCORM para el contenido {content.id}, creando uno nuevo")
            
            # Crear el paquete SCORM automáticamente
            try:
                from apps.scorm_packager.services import SCORMPackageManager
                
                scorm_manager = SCORMPackageManager()
                scorm_package = scorm_manager.create_package(
                    title=content.title,
                    content=content.formatted_content,
                    user=request.user,
                    content_obj=content
                )
                logger.info(f"Paquete SCORM generado automáticamente: ID={scorm_package.id}")
            except Exception as e:
                logger.error(f"Error al generar paquete SCORM automáticamente: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error al generar el paquete SCORM automáticamente'
                }, status=400)

        # Asegurar que tenemos un título para el material
        material_name = title or f"Contenido generado para {content.request.course.name}"
        
        # Asegurar que el tipo de material sea SCORM si tenemos un paquete SCORM
        if scorm_package:
            # Forzar el tipo de material a SCORM independientemente de lo que venga en el parámetro
            material_type = 'SCORM'
            logger.info(f"Forzando tipo de material a SCORM ya que existe paquete SCORM con ID {scorm_package.id}")
        
        # Crear descripción limpia sin HTML/CSS
        from django.utils.html import strip_tags
        import re
        
        # Limpiar el contenido de HTML y CSS
        clean_content = strip_tags(content.formatted_content)
        # Remover CSS extra que pueda quedar
        clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r':\s*root\s*{[^}]*}', '', clean_content)
        clean_content = re.sub(r'--[a-zA-Z-]+:\s*[^;]+;', '', clean_content)
        # Limitar la descripción a las primeras 200 palabras
        words = clean_content.split()[:200]
        clean_description = ' '.join(words)
        if len(words) == 200:
            clean_description += '...'
        
        # Crear material con el tipo correcto
        material = PortfolioMaterial.objects.create(
            topic=topic,
            title=material_name,
            description=f"Material generado con IA: {content.title}\n\n{clean_description}",
            material_type=material_type,
            scorm_package=scorm_package if material_type == 'SCORM' else None,
            ai_generated=True
        )
        logger.info(f"Material creado: ID={material.id}, Título={material.title}, SCORM_ID={scorm_package.id if scorm_package else 'None'}, Tipo={material_type}")

        # Preparar URLs para descarga y visualización
        response_data = {
            'success': True,
            'message': 'Material asignado correctamente',
            'material_id': material.id,
            'topic_id': topic.id,
            'topic_name': topic.title
        }

        # Agregar URLs de SCORM si es material tipo SCORM
        if material_type == 'SCORM' and scorm_package:
            response_data.update({
                'scorm_package_id': scorm_package.id,
                'download_url': reverse('scorm_packager:download_scorm_package', args=[scorm_package.id]),
                'view_url': reverse('scorm_packager:scorm_package_detail', args=[scorm_package.id])
            })

        if is_ajax:
            return JsonResponse(response_data)
        else:
            # Redirigir al portafolio del estudiante
            return redirect('portfolios:teacher_portfolio_detail', pk=topic.portfolio.id)
    
    except Exception as e:
        logger.exception(f"Error al asignar contenido al portafolio: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': f'Error al asignar contenido: {str(e)}'
            }, status=500)
        else:
            messages.error(request, f'Error al asignar contenido: {str(e)}')
            return redirect('ai:content_detail', pk=content_id)

@login_required
def direct_assign_view(request, pk):
    """
    Vista para asignar contenido directamente a un estudiante o a toda la clase
    """
    try:
        # Mensaje de inicio
        logger.info(f"Iniciando direct_assign_view para contenido ID: {pk}")
        
        # Obtener el contenido
        try:
            content = get_object_or_404(GeneratedContent, pk=pk)
            logger.info(f"Contenido recuperado: ID={pk}, Title={content.title}")
        except Exception as get_obj_error:
            logger.error(f"Error al obtener contenido con ID {pk}: {str(get_obj_error)}")
            messages.error(request, f"No se pudo encontrar el contenido: {str(get_obj_error)}")
            return redirect('ai:content_request_list')
        
        # Verificar permisos
        if content.request.teacher != request.user and not request.user.is_staff:
            logger.warning(f"Usuario {request.user.username} intentó acceder a contenido {pk} sin permisos")
            messages.error(request, "No tiene permisos para asignar este contenido.")
            return redirect('ai:content_detail', pk=content.id)
        
        # Variables para información de clase
        class_info = None
        course_topic_info = None
        section_students = []
        
        # Si el contenido es para toda la clase, extraer información del CourseTopic
        if content.request.for_class:
            try:
                # Extraer información del additional_instructions
                additional_instructions = content.request.additional_instructions or ""
                
                # Buscar información del tema de clase en las instrucciones
                if "INFORMACIÓN DEL TEMA DE CLASE:" in additional_instructions:
                    import re
                    
                    # Extraer información usando regex
                    tema_match = re.search(r'Tema: ([^\n]+)', additional_instructions)
                    curso_match = re.search(r'Curso: ([^\n]+)', additional_instructions)
                    seccion_match = re.search(r'Sección: ([^\n]+)', additional_instructions)
                    
                    if tema_match and curso_match and seccion_match:
                        tema_nombre = tema_match.group(1).strip()
                        curso_nombre = curso_match.group(1).strip()
                        seccion_nombre = seccion_match.group(1).strip()
                        
                        logger.info(f"Información extraída - Tema: {tema_nombre}, Curso: {curso_nombre}, Sección: {seccion_nombre}")
                        
                        # Buscar el CourseTopic correspondiente
                        from apps.academic.models import CourseTopic, Course, Section
                        
                        try:
                            # Buscar el curso
                            course = Course.objects.filter(name=curso_nombre).first()
                            if course:
                                # Buscar el tema de curso
                                course_topic = CourseTopic.objects.filter(
                                    title=tema_nombre,
                                    course=course
                                ).first()
                                
                                if course_topic:
                                    course_topic_info = {
                                        'id': course_topic.id,
                                        'title': course_topic.title,
                                        'course': course,
                                        'section': course_topic.section,
                                        'teacher': course_topic.teacher
                                    }
                                    
                                    # Obtener estudiantes de la sección
                                    if course_topic.section:
                                        from apps.academic.models import Enrollment
                                        enrollments = Enrollment.objects.filter(
                                            section=course_topic.section,
                                            status='ACTIVE'
                                        ).select_related('student', 'student__user')
                                        
                                        section_students = [enrollment.student for enrollment in enrollments]
                                        logger.info(f"Encontrados {len(section_students)} estudiantes en la sección")
                                    
                                    class_info = {
                                        'course_topic': course_topic,
                                        'course': course,
                                        'section': course_topic.section,
                                        'students': section_students,
                                        'tema_nombre': tema_nombre,
                                        'curso_nombre': curso_nombre,
                                        'seccion_nombre': seccion_nombre
                                    }
                                    
                        except Exception as lookup_error:
                            logger.error(f"Error al buscar CourseTopic: {str(lookup_error)}")
                            
            except Exception as extract_error:
                logger.error(f"Error al extraer información de clase: {str(extract_error)}")
        
        # Obtener estudiantes para mostrar (si no es para clase o como fallback)
        student_objects = []
        if not class_info or not section_students:
            try:
                from apps.academic.models import Student, Enrollment
                
                # Enfoque simplificado: Mostrar todos los estudiantes activos
                student_qs = Student.objects.filter(
                    user__is_active=True
                ).select_related('user').order_by('user__first_name', 'user__last_name')
                
                if student_qs.exists():
                    student_objects = list(student_qs)
                    logger.info(f"Encontrados {len(student_objects)} estudiantes activos")
                else:
                    logger.warning("No se encontraron estudiantes activos en el sistema")
            except Exception as student_error:
                logger.error(f"Error al obtener estudiantes: {str(student_error)}")
                student_objects = []
                messages.warning(request, f"Error al cargar estudiantes: {str(student_error)}")
        
        # Si tenemos información de clase, usar esos estudiantes como principales
        if class_info and section_students:
            student_objects = section_students
            logger.info(f"Usando {len(section_students)} estudiantes de la sección")
        
        # Obtener temas de portafolio disponibles
        portfolio_topics = []
        try:
            from apps.portfolios.models import PortfolioTopic, StudentPortfolio
            
            # Si es para clase, filtrar por estudiantes de la sección
            if class_info and section_students:
                portfolios = StudentPortfolio.objects.filter(
                    student__in=section_students
                ).select_related('student', 'student__user')
            else:
                portfolios = StudentPortfolio.objects.all().select_related('student', 'student__user')
            
            logger.info(f"Total de portfolios encontrados: {portfolios.count()}")
            
            # Obtener temas asociados a esos portfolios
            topics = PortfolioTopic.objects.filter(portfolio__in=portfolios).select_related(
                'portfolio', 'portfolio__student', 'portfolio__student__user', 'course'
            ).order_by('-created_at')
            
            # Si es para clase, filtrar por el curso específico
            if class_info and class_info['course']:
                topics = topics.filter(course=class_info['course'])
            
            logger.info(f"Total de temas encontrados: {topics.count()}")
            
            # Procesar temas para el formato JSON
            for topic in topics:
                try:
                    if not topic.portfolio or not topic.portfolio.student:
                        logger.warning(f"Tema {topic.id} sin portfolio o estudiante válido")
                        continue
                    
                    student_id = topic.portfolio.student.id
                    student_name = topic.portfolio.student.user.get_full_name() if hasattr(topic.portfolio.student, 'user') else 'Sin nombre'
                    
                    course_name = "Sin curso"
                    if hasattr(topic, 'course') and topic.course:
                        course_name = topic.course.name
                    
                    portfolio_topics.append({
                        'id': topic.id,
                        'title': topic.title,
                        'student_id': student_id,
                        'student_name': student_name,
                        'course_name': course_name
                    })
                except Exception as topic_error:
                    logger.error(f"Error al procesar tema {topic.id}: {str(topic_error)}")
            
            logger.info(f"Total de temas procesados para JavaScript: {len(portfolio_topics)}")
            
        except Exception as portfolio_error:
            logger.error(f"Error al obtener temas de portafolio: {str(portfolio_error)}")
            portfolio_topics = []
            messages.warning(request, f"Error al cargar temas de portafolio: {str(portfolio_error)}")
        
        # Convertir a JSON para JavaScript
        try:
            import json
            from django.core.serializers.json import DjangoJSONEncoder
            
            topics_json = json.dumps(portfolio_topics, cls=DjangoJSONEncoder)
            logger.info("JSON de temas generado correctamente")
        except Exception as json_error:
            logger.error(f"Error al generar JSON de temas: {str(json_error)}")
            topics_json = "[]"
            messages.warning(request, "Error al procesar la información de temas de portafolio.")
        
        # Mensajes informativos
        if content.request.for_class:
            if class_info:
                messages.info(request, f"Este contenido fue generado para la clase: {class_info['tema_nombre']} ({class_info['curso_nombre']} - {class_info['seccion_nombre']})")
            else:
                messages.info(request, "Este contenido fue generado para toda la clase.")
        
        if not portfolio_topics:
            messages.warning(request, "No se encontraron temas de portafolio para los estudiantes. Debes crear temas en la sección de portafolios primero.")
        
        if not student_objects:
            messages.warning(request, "No se encontraron estudiantes. Debes crear estudiantes primero.")
        
        # Datos de context
        context_data = {
            'content': content,
            'students': student_objects,
            'portfolio_topics': topics_json,
            'topics_count': len(portfolio_topics),
            'class_info': class_info,
            'course_topic_info': course_topic_info,
            'is_for_class': content.request.for_class,
        }
        
        logger.info(f"Context data para template: content_id={content.id}, students_count={len(student_objects)}, topics_count={len(portfolio_topics)}, is_for_class={content.request.for_class}")
        
        # Renderizar la plantilla
        try:
            response = render(request, 'ai_content_generator/direct_assign.html', context_data)
            logger.info("Plantilla renderizada correctamente")
            return response
        except Exception as render_error:
            logger.error(f"Error al renderizar plantilla: {str(render_error)}")
            messages.error(request, f"Error al renderizar la página: {str(render_error)}")
            return redirect('ai:content_detail', pk=content.id)
            
    except Exception as e:
        import traceback
        logger.exception(f"Error general en direct_assign_view: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, f"Error al cargar la vista de asignación: {str(e)}")
        return redirect('ai:content_detail', pk=pk)

@login_required
def get_student_topics(request, student_id):
    """
    API para obtener los temas de portafolio disponibles para un estudiante específico,
    filtrados por los cursos que dicta el profesor actual (no todos los cursos del estudiante).
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Usuario no autenticado'
        }, status=401)
    
    try:
        from apps.academic.models import Student, Enrollment, CourseAssignment, Teacher
        from apps.portfolios.models import PortfolioTopic, StudentPortfolio
        from django.utils import timezone
        
        # Buscar el estudiante
        student = get_object_or_404(Student, id=student_id)
        
        # Verificar que el estudiante exista y tenga un usuario asociado
        if not hasattr(student, 'user'):
            return JsonResponse({
                'success': False,
                'message': 'Estudiante sin usuario asociado'
            }, status=404)
        
        # Obtener el profesor actual (el que está haciendo la consulta)
        try:
            current_teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Usuario actual no es un profesor válido'
            }, status=403)
        
        logger.info(f"Profesor actual: {current_teacher.user.get_full_name()} consultando temas para estudiante {student_id}")
        
        # Obtener año académico actual
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        # Obtener matrículas activas del estudiante
        active_enrollments = Enrollment.objects.filter(
            student=student,
            status='ACTIVE'
        ).select_related('section', 'section__grade')
        
        logger.info(f"Estudiante {student_id}: {active_enrollments.count()} matrículas activas")
        
        # Obtener SOLO los cursos que dicta el profesor actual donde está matriculado el estudiante
        teacher_courses = set()
        courses_info = {}
        
        for enrollment in active_enrollments:
            section = enrollment.section
            
            # Obtener asignaciones de cursos para esta sección SOLO del profesor actual
            course_assignments = CourseAssignment.objects.filter(
                section=section,
                teacher=current_teacher,  # FILTRO CLAVE: solo cursos del profesor actual
                is_active=True
            ).select_related('course', 'teacher', 'teacher__user')
            
            for assignment in course_assignments:
                if assignment.course:
                    teacher_courses.add(assignment.course)
                    
                    # Guardar información del curso
                    courses_info[assignment.course.id] = {
                        'id': assignment.course.id,
                        'name': assignment.course.name,
                        'teacher_name': assignment.teacher.user.get_full_name() if assignment.teacher.user else 'Sin nombre',
                        'section_name': f"{section.grade.name} - Sección {section.name}",
                        'topics_count': 0  # Se calculará después
                    }
        
        logger.info(f"Profesor {current_teacher.user.get_full_name()}: {len(teacher_courses)} cursos donde está matriculado el estudiante {student_id}")
        
        # Si el profesor no dicta ningún curso donde esté matriculado el estudiante
        if not teacher_courses:
            return JsonResponse({
                'success': True,
                'student_id': student_id,
                'student_name': student.user.get_full_name(),
                'topics': [],
                'courses': [],
                'active_enrollments_count': active_enrollments.count(),
                'total_topics': 0,
                'message': f'El estudiante no está matriculado en ningún curso que usted dicte'
            })
        
        # Buscar portafolios del estudiante (preferir del año actual)
        student_portfolios = StudentPortfolio.objects.filter(
            student=student
        ).order_by('-academic_year', '-month')
        
        # Filtrar temas SOLO por los cursos que dicta el profesor actual
        topics_query = PortfolioTopic.objects.filter(
            portfolio__in=student_portfolios,
            course__in=teacher_courses,  # FILTRO CLAVE: solo cursos del profesor actual
            teacher=current_teacher  # FILTRO ADICIONAL: solo temas creados por el profesor actual
        ).select_related('portfolio', 'course', 'teacher__user').order_by('-created_at')
        
        logger.info(f"Temas encontrados para estudiante {student_id} en cursos del profesor actual: {topics_query.count()}")
        
        # Transformar a lista para la respuesta JSON
        topics_list = []
        
        for topic in topics_query:
            try:
                # Información del curso
                course_name = topic.course.name if topic.course else 'Sin curso'
                course_id = topic.course.id if topic.course else None
                
                # Información del profesor
                teacher_name = topic.teacher.user.get_full_name() if topic.teacher and topic.teacher.user else 'Sin profesor'
                
                # Información del portafolio
                portfolio_period = f"{topic.portfolio.get_month_display()} {topic.portfolio.academic_year}" if topic.portfolio else 'Sin período'
                
                topic_data = {
                    'id': topic.id,
                    'title': topic.title,
                    'course_id': course_id,
                    'course_name': course_name,
                    'teacher_name': teacher_name,
                    'portfolio_id': topic.portfolio.id if topic.portfolio else None,
                    'portfolio_period': portfolio_period,
                    'created_at': topic.created_at.strftime('%d/%m/%Y') if topic.created_at else '',
                    'is_complete': getattr(topic, 'is_complete', False)
                }
                
                topics_list.append(topic_data)
                
                # Actualizar contador de temas por curso
                if course_id and course_id in courses_info:
                    courses_info[course_id]['topics_count'] += 1
                
                logger.debug(f"Tema procesado: ID={topic.id}, Título={topic.title}, Curso={course_name}")
                
            except Exception as e:
                logger.error(f"Error al procesar tema {topic.id}: {str(e)}")
        
        # Convertir courses_info a lista
        courses_list = list(courses_info.values())
        
        return JsonResponse({
            'success': True,
            'student_id': student_id,
            'student_name': student.user.get_full_name(),
            'topics': topics_list,
            'courses': courses_list,
            'active_enrollments_count': active_enrollments.count(),
            'total_topics': len(topics_list),
            'teacher_info': {
                'name': current_teacher.user.get_full_name(),
                'courses_with_student': len(teacher_courses)
            }
        })
    
    except Exception as e:
        logger.error(f"Error al obtener temas del estudiante: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener temas: {str(e)}'
        }, status=500)

@login_required
def assign_to_portfolio(request, pk=None):
    """
    Función para manejar asignaciones a portafolio. Puede recibir una solicitud AJAX o una solicitud directa.
    """
    try:
        # Verificar si es una solicitud AJAX
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if is_ajax and request.method == 'POST':
            # Si es AJAX y POST, usar la API de asignación
            logger.info(f"Solicitud AJAX para asignar a portafolio")
            return assign_to_portfolio_api(request)
        
        # Si llegamos aquí, es una solicitud normal (no AJAX) o una solicitud AJAX que no es POST
        if pk is None:
            logger.warning("Intento de acceder a assign_to_portfolio sin pk")
            messages.error(request, "Identificador de contenido no especificado")
            return redirect('ai:content_request_list')
        
        # Obtener el contenido
        content = get_object_or_404(GeneratedContent, pk=pk)
        logger.info(f"Redirigiendo desde assign_to_portfolio a direct_assign_view para contenido ID {pk}")
        
        # Si no es AJAX, redirigir a la vista de asignación
        messages.info(request, "Has sido redirigido a la nueva interfaz de asignación.")
        return redirect('ai:direct_assign', pk=content.id)
    except Exception as e:
        logger.exception(f"Error en assign_to_portfolio: {str(e)}")
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        messages.error(request, f"Error al procesar la solicitud: {str(e)}")
        return redirect('ai:content_request_list')

def generate_scorm_api(request):
    """API para generar paquetes SCORM desde la interfaz de GrapesJS"""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        html_content = data.get('html', '')
        css_content = data.get('css', '')
        js_content = data.get('js', '')
        metadata = data.get('metadata', {})
        content_id = data.get('content_id', None)
        
        if not html_content:
            return JsonResponse({"success": False, "error": "Contenido HTML requerido"}, status=400)
        
        # Si hay un content_id, obtener el contenido generado asociado
        generated_content = None
        if content_id:
            try:
                generated_content = GeneratedContent.objects.get(id=content_id)
            except GeneratedContent.DoesNotExist:
                pass
        
        # Combinar HTML, CSS y JS en un solo documento
        combined_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{metadata.get('title', 'Contenido Educativo')}</title>
            <style>{css_content}</style>
        </head>
        <body>
            {html_content}
            <script>{js_content}</script>
        </body>
        </html>
        """
        
        # Preparar metadatos para el paquete SCORM
        scorm_metadata = {
            'title': metadata.get('title', 'Contenido Educativo'),
            'description': metadata.get('description', 'Contenido educativo generado'),
            'version': metadata.get('version', '1.0'),
            'standard': metadata.get('standard', 'scorm_2004_4th')
        }
        
        # Crear el paquete SCORM
        packager = SCORMPackager(combined_html, scorm_metadata)
        package_path = packager.create_package()
        
        # Convertir la ruta del paquete a string y manejar correctamente la ruta relativa
        package_path_str = str(package_path)
        media_root_str = str(settings.MEDIA_ROOT)
        
        # Reemplazar la parte de la ruta del MEDIA_ROOT
        relative_path = os.path.relpath(package_path_str, media_root_str)
        
        # Guardar referencia en la base de datos
        scorm_package = SCORMPackage.objects.create(
            generated_content=generated_content,
            title=scorm_metadata['title'],
            description=scorm_metadata['description'],
            standard=scorm_metadata['standard'],
            package_file=relative_path
        )
        
        # Obtener la URL del paquete
        package_url = settings.MEDIA_URL + relative_path
        
        return JsonResponse({
            "success": True, 
            "message": "Paquete SCORM generado correctamente",
            "package_id": scorm_package.id,
            "package_url": package_url
        })
    except Exception as e:
        logger.exception(f"Error al generar paquete SCORM: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def edit_content_view(request, pk):
    """Vista para editar el contenido generado con iframe-based editor"""
    content = get_object_or_404(GeneratedContent, pk=pk)
    # Verificar que el usuario sea el dueño del contenido
    if content.request.teacher != request.user:
        messages.error(request, "No tienes permiso para editar este contenido")
        return redirect('ai:content_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            # Get content from iframe-based editor
            content_html = request.POST.get('content_html', '')
            formatted_content = request.POST.get('formatted_content', '')
            
            # Use the HTML content as the main content
            updated_content = content_html or formatted_content
            
            if not updated_content:
                messages.error(request, "El contenido no puede estar vacío")
                return render(request, 'ai_content_generator/edit_content.html', {
                    'content': content
                })
            
            # Save the content preserving the original formatting
            content.formatted_content = updated_content
            content.raw_content = updated_content  # Also update raw content
            content.save()
            
            messages.success(request, "Contenido actualizado correctamente. Los cambios se han guardado preservando el formato original.")
            
            # Redirect to content detail to show the updated content
            return redirect('ai:content_detail', pk=pk)
            
        except Exception as e:
            logger.exception(f"Error al editar contenido con iframe: {str(e)}")
            messages.error(request, f"Error al editar el contenido: {str(e)}")
    
    return render(request, 'ai_content_generator/edit_content.html', {
        'content': content
    })

@login_required
def simple_assign_test_view(request, pk):
    """
    Vista simplificada para diagnosticar problemas con la asignación
    """
    try:
        # Obtener el contenido
        content = get_object_or_404(GeneratedContent, pk=pk)
        
        # Preparar contexto mínimo
        context = {
            'content': content,
            'title': f"Asignar {content.title}",
            'debug_info': {
                'content_id': pk,
                'content_title': content.title,
                'user': request.user.username,
            }
        }
        
        # Devolver una respuesta muy simple
        return render(request, 'ai_content_generator/simple_assign_test.html', context)
    except Exception as e:
        # Capturar y mostrar cualquier error
        error_message = f"Error: {str(e)}"
        return HttpResponse(f"""
        <html>
            <head><title>Error de diagnóstico</title></head>
            <body>
                <h1>Error de diagnóstico</h1>
                <p>{error_message}</p>
                <p><a href="{reverse('ai:content_detail', args=[pk])}">Volver al contenido</a></p>
            </body>
        </html>
        """)

@login_required
def assign_to_portfolio_api(request):
    """
    API para asignar contenido a un tema de portafolio mediante AJAX.
    Esta función recibe los datos en formato JSON y no espera un parámetro pk en la URL.
    """
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)
    
    try:
        # Obtener los datos JSON del cuerpo de la solicitud
        try:
            data = json.loads(request.body)
            logger.info(f"Datos recibidos en assign_to_portfolio_api: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON: {str(e)}")
            return JsonResponse({"success": False, "error": "Datos JSON inválidos"}, status=400)
        
        # Validar que se recibieron los datos necesarios
        content_id = data.get('content_id')
        material_type = data.get('material_type', 'TEXT')
        
        if not content_id:
            return JsonResponse({"success": False, "error": "ID de contenido requerido"}, status=400)
        
        # Obtener el contenido (forzar refresh desde la base de datos)
        try:
            content = GeneratedContent.objects.select_related('request', 'request__course').get(id=content_id)
            # Forzar refresh para asegurar que tenemos la versión más reciente
            content.refresh_from_db()
            logger.info(f"📊 Contenido obtenido - raw_content: {len(content.raw_content or '')} chars, formatted_content: {len(content.formatted_content or '')} chars")
        except GeneratedContent.DoesNotExist:
            return JsonResponse({"success": False, "error": f"Contenido con ID {content_id} no encontrado"}, status=404)
        
        # Determinar el tipo de material
        is_personal_material = material_type == 'personal'
        is_class_material = material_type == 'class'
        
        # Si es material de clase, procesar automáticamente para todos los estudiantes
        if is_class_material:
            return handle_class_material_assignment(request, content, data)
        
        # Si es material personalizado, verificar parámetros
        topic_id = data.get('topic_id')
        target_students = data.get('target_students', [])
        
        if not topic_id:
            return JsonResponse({"success": False, "error": "ID de tema requerido para material personalizado"}, status=400)
        
        if not target_students:
            return JsonResponse({"success": False, "error": "Lista de estudiantes requerida para material personalizado"}, status=400)
        
        # Para material personalizado con múltiples estudiantes, usar handler especial
        if len(target_students) > 1:
            return handle_personal_material_assignment(request, content, data)
        
        # Manejo de estudiante único (código original)
        # Obtener el tema - necesitamos extraer el título del topic_id compuesto
        topic_title = None
        if isinstance(topic_id, str) and topic_id.startswith('topic_'):
            parts = topic_id.split('_', 2)
            if len(parts) >= 3:
                topic_title = parts[2]
        else:
            topic_title = topic_id
            
        if not topic_title:
            return JsonResponse({"success": False, "error": "ID de tema inválido"}, status=400)
        
        # Buscar el tema específico para el estudiante
        student_id = target_students[0]
        try:
            from apps.portfolios.models import PortfolioTopic, PortfolioMaterial
            from apps.academic.models import Student
            
            student = Student.objects.get(id=student_id)
            
            # Buscar el tema en el portafolio del estudiante
            topic = PortfolioTopic.objects.filter(
                portfolio__student=student,
                title=topic_title,
                teacher=request.user.teacher_profile
            ).first()
            
            if not topic:
                return JsonResponse({"success": False, "error": f"Tema '{topic_title}' no encontrado en el portafolio del estudiante"}, status=404)
                
        except Student.DoesNotExist:
            return JsonResponse({"success": False, "error": f"Estudiante con ID {student_id} no encontrado"}, status=404)
        except PortfolioTopic.DoesNotExist:
            return JsonResponse({"success": False, "error": f"Tema con título '{topic_title}' no encontrado para el estudiante"}, status=404)
        
        # Verificar que el tema tiene un portafolio y estudiante
        if not topic.portfolio or not topic.portfolio.student:
            return JsonResponse({"success": False, "error": "El tema seleccionado no tiene un portafolio o estudiante válido"}, status=400)
        
        # SIEMPRE generar/regenerar paquete SCORM limpio para material personalizado
        scorm_package = SCORMPackage.objects.filter(generated_content=content).first()
        
        try:
            logger.info(f"📦 Generando/Regenerando paquete SCORM LIMPIO para material personalizado {content.id}...")
            
            # Importar el packager
            from apps.scorm_packager.services.packager import SCORMPackager
            
            # Preparar metadatos para el paquete SCORM
            metadata = {
                'title': content.title,
                'description': f"Material personalizado - {content.request.course.name}",
                'version': '1.0',
                'standard': 'scorm_2004_4th'
            }
            
            # Obtener contenido educativo LIMPIO (SIN cabecera institucional) para SCORM
            clean_content = get_clean_educational_content(content)
            logger.info(f"📚 Usando contenido educativo LIMPIO de {len(clean_content)} caracteres para SCORM")
            
            # Crear el paquete SCORM usando solo el contenido educativo limpio
            packager = SCORMPackager(clean_content, metadata)
            package_path = packager.create_package()
            
            # Convertir a ruta relativa
            relative_path = os.path.relpath(package_path, settings.MEDIA_ROOT)
            
            # Si ya existía un paquete, actualizarlo; si no, crear uno nuevo
            if scorm_package:
                # Eliminar archivo anterior si existe
                old_file_path = os.path.join(settings.MEDIA_ROOT, scorm_package.package_file)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    logger.info(f"Archivo SCORM anterior eliminado: {old_file_path}")
                
                # Actualizar paquete existente
                scorm_package.package_file = relative_path
                scorm_package.title = content.title
                scorm_package.description = metadata['description']
                scorm_package.save()
                logger.info(f"✅ Paquete SCORM actualizado: ID={scorm_package.id}")
            else:
                # Crear nuevo paquete SCORM
                scorm_package = SCORMPackage.objects.create(
                    generated_content=content,
                    title=content.title,
                    description=metadata['description'],
                    standard=metadata['standard'],
                    package_file=relative_path,
                    created_by=request.user
                )
                logger.info(f"✅ Nuevo paquete SCORM creado: ID={scorm_package.id}")
                
        except Exception as scorm_error:
            logger.warning(f"No se pudo crear/actualizar paquete SCORM: {str(scorm_error)}")
            # Si falla la creación, usar paquete existente si lo hay
            if not scorm_package:
                scorm_package = None

        
        # Determinar el tipo de material más apropiado
        if scorm_package:
            material_type = 'SCORM'
            logger.info(f"Usando paquete SCORM con ID {scorm_package.id} para material de clase")
        else:
            # Si no hay paquete SCORM, usar LECTURA como tipo más apropiado para contenido de IA
            material_type = 'LECTURA'
            logger.info(f"Usando tipo LECTURA para contenido de clase sin paquete SCORM")
        
        # Obtener el curso del contenido
        course = content.request.course
        
        # Crear el material
        material_title = data.get('material_name', content.title)
        
        # Agregar ID de SCORM al título si es necesario
        # if scorm_package:
        #     material_title = f"{material_title} [SCORM_ID:{scorm_package.id}]"
        
        # Crear descripción limpia sin HTML/CSS usando el contenido más actualizado
        from django.utils.html import strip_tags
        import re
        
        # Usar el contenido más actualizado (priorizar formatted_content)
        source_content = content.formatted_content or content.raw_content or ""
        logger.info(f"📝 Creando descripción desde contenido de {len(source_content)} caracteres")
        
        # Limpiar el contenido de HTML y CSS
        clean_content = strip_tags(source_content)
        # Remover CSS extra que pueda quedar
        clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r':\s*root\s*{[^}]*}', '', clean_content)
        clean_content = re.sub(r'--[a-zA-Z-]+:\s*[^;]+;', '', clean_content)
        # Limitar la descripción a las primeras 200 palabras
        words = clean_content.split()[:200]
        clean_description = ' '.join(words)
        if len(words) == 200:
            clean_description += '...'
        
        logger.info(f"📝 Descripción limpia creada: {len(clean_description)} caracteres")
        
        # Crear contenido con cabecera institucional
    # Header institucional eliminado por solicitud del usuario
        institutional_styles = get_institutional_styles()
        
        # Crear HTML completo con cabecera institucional
        content_with_header = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    {institutional_styles}
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: white;
        }}
        .content {{
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #005CFF;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        p {{
            margin: 1em 0;
            text-align: justify;
        }}
        ul, ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        li {{
            margin: 0.5em 0;
        }}
    </style>
</head>
<body>
    <div class="content">
        {source_content}
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const dateElement = document.getElementById('generation-date');
            if (dateElement) {{
                const now = new Date();
                dateElement.textContent = now.toLocaleDateString('es-ES', {{
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }});
            }}
        }});
    </script>
</body>
</html>"""
        
        # Crear el material en el portafolio
        material = PortfolioMaterial.objects.create(
            topic=topic,
            title=material_title,
            description=content_with_header,  # Usar contenido completo con cabecera
            material_type=material_type,
            scorm_package=scorm_package,  # Siempre usar el paquete SCORM si existe
            ai_generated=True,
            is_class_material=False  # Material personalizado
        )
        
        logger.info(f"Material personalizado creado: ID={material.id}, Título={material.title}, Tipo={material_type}")
        logger.info(f"Paquete SCORM asignado: {scorm_package.id if scorm_package else 'None'}")
        
        # Preparar respuesta
        response_data = {
            "success": True,
            "message": "Material personalizado creado correctamente",
            "material_id": material.id,
            "topic_id": topic.id,
            "student_id": topic.portfolio.student.id,
            "material_type": material_type,
            "is_class_material": False,
            "topic_url": reverse('portfolios:topic_detail', kwargs={'pk': topic.id})
        }
        
        # Agregar información del paquete SCORM si existe
        if scorm_package:
            response_data.update({
                "scorm_package_id": scorm_package.id,
                "download_url": reverse('scorm_packager:download_scorm_package', args=[scorm_package.id])
            })
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        logger.exception(f"Error en assign_to_portfolio_api: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def handle_class_material_assignment(request, content, data):
    """
    Maneja la asignación de material de clase a estudiantes de múltiples secciones seleccionadas.
    FLUJO: 1) Empaquetar en SCORM, 2) Asignar como material de clase, 3) Replicar para las secciones seleccionadas
    """
    try:
        from apps.portfolios.models import PortfolioTopic, PortfolioMaterial, StudentPortfolio
        from apps.academic.models import Student, Enrollment, Section
        from apps.scorm_packager.models import SCORMPackage
        from django.utils import timezone
        from django.conf import settings
        import os
        
        # Obtener parámetros
        material_title = data.get('material_name', content.title)
        course_topic_title = data.get('course_topic_title')
        use_scorm_format = data.get('use_scorm_format', True)
        target_sections = data.get('target_sections', [])
        
        # Validar que se especificó un tema del curso
        if not course_topic_title:
            return JsonResponse({
                "success": False, 
                "error": "Debe seleccionar un tema del curso para el material de clase"
            }, status=400)
        
        # Validar que se seleccionaron secciones
        if not target_sections:
            return JsonResponse({
                "success": False, 
                "error": "Debe seleccionar al menos una sección para asignar el material"
            }, status=400)
        
        # Convertir target_sections a lista si es un string
        if isinstance(target_sections, str):
            target_sections = [target_sections]
        
        logger.info(f"🎯 INICIANDO asignación de material de clase para contenido {content.id} en secciones: {target_sections}")
        
        # Forzar refresh del contenido para asegurar que tenemos la versión más reciente
        content.refresh_from_db()
        logger.info(f"📊 Contenido refrescado - raw_content: {len(content.raw_content or '')} chars, formatted_content: {len(content.formatted_content or '')} chars")
        
        # ========== PASO 1: EMPAQUETAR EN SCORM (OBLIGATORIO PARA MATERIAL DE CLASE) ==========
        scorm_package = SCORMPackage.objects.filter(generated_content=content).first()
        
        # SIEMPRE generar/regenerar paquete SCORM limpio para material de clase
        try:
            logger.info(f"📦 PASO 1: Generando/Regenerando paquete SCORM LIMPIO para material de clase {content.id}...")
            
            # Importar el packager
            from apps.scorm_packager.services.packager import SCORMPackager
            
            # Preparar metadatos para el paquete SCORM
            metadata = {
                'title': content.title,
                'description': f"Material educativo - {content.request.course.name} - {course_topic_title}",
                'version': '1.0',
                'standard': 'scorm_2004_4th'
            }
            
            # Obtener contenido educativo LIMPIO (SIN cabecera institucional) para SCORM
            clean_content = get_clean_educational_content(content)
            logger.info(f"📚 Usando contenido educativo LIMPIO de {len(clean_content)} caracteres para SCORM")
            
            # Crear el paquete SCORM usando solo el contenido educativo limpio
            packager = SCORMPackager(clean_content, metadata)
            package_path = packager.create_package()
            
            # Convertir a ruta relativa
            relative_path = os.path.relpath(package_path, settings.MEDIA_ROOT)
            
            # Si ya existía un paquete, actualizarlo; si no, crear uno nuevo
            if scorm_package:
                # Eliminar archivo anterior si existe
                old_file_path = os.path.join(settings.MEDIA_ROOT, scorm_package.package_file)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    logger.info(f"Archivo SCORM anterior eliminado: {old_file_path}")
                
                # Actualizar paquete existente
                scorm_package.package_file = relative_path
                scorm_package.title = content.title
                scorm_package.description = metadata['description']
                scorm_package.save()
                logger.info(f"✅ Paquete SCORM actualizado para material de clase: ID={scorm_package.id}")
            else:
                # Crear nuevo paquete SCORM
                scorm_package = SCORMPackage.objects.create(
                    generated_content=content,
                    title=content.title,
                    description=metadata['description'],
                    standard=metadata['standard'],
                    package_file=relative_path,
                    created_by=request.user
                )
                logger.info(f"✅ Nuevo paquete SCORM creado para material de clase: ID={scorm_package.id}")
                
        except Exception as scorm_error:
            logger.error(f"❌ Error al crear/actualizar paquete SCORM para material de clase: {str(scorm_error)}")
            # Si falla la creación, usar paquete existente si lo hay
            if not scorm_package:
                return JsonResponse({
                    "success": False, 
                    "error": f"No se pudo crear el paquete SCORM requerido para material de clase: {str(scorm_error)}"
                }, status=500)
            else:
                logger.warning(f"Usando paquete SCORM existente debido a error: ID={scorm_package.id}")
        
        # ========== PASO 2: CONFIGURAR COMO MATERIAL DE CLASE SCORM ==========
        # Para material de clase SIEMPRE debe ser SCORM
        material_type = 'SCORM'
        logger.info(f"🏫 PASO 2: Configurando como material de clase en formato SCORM")
        
        # Obtener el curso del contenido
        course = content.request.course
        
        # Obtener las secciones seleccionadas
        selected_sections = Section.objects.filter(
            id__in=target_sections,
            course_assignments__teacher=request.user.teacher_profile,
            course_assignments__course=course,
            is_active=True
        ).distinct()
        
        if not selected_sections.exists():
            return JsonResponse({
                "success": False, 
                "error": "No se encontraron secciones válidas seleccionadas"
            }, status=400)
        
        # ========== PASO 2.5: CREAR MATERIALES PRINCIPALES EN LOS COURSE TOPICS ==========
        from apps.academic.models import CourseTopic
        
        materials_created = 0
        topics_found = 0
        topics_not_found = 0
        students_processed = []
        sections_processed = []
        
        current_month = timezone.now().month
        current_year = timezone.now().year
        academic_year = str(current_year)
        
        # ========== PASO 3: PROCESAR CADA SECCIÓN SELECCIONADA ==========
        for section in selected_sections:
            try:
                logger.info(f"📚 Procesando sección: {section.grade.name} - Sección {section.name}")
                sections_processed.append(f"{section.grade.name} - Sección {section.name}")
                
                # Buscar el CourseTopic correspondiente para esta sección
                course_topic = CourseTopic.objects.filter(
                    course=course,
                    title=course_topic_title,
                    section=section,
                    teacher=request.user.teacher_profile
                ).first()
                
                if course_topic:
                    # Verificar si ya existe un material principal para este course_topic
                    existing_main_material = PortfolioMaterial.objects.filter(
                        course_topic=course_topic,
                        topic__isnull=True,  # Material principal
                        title=material_title,
                        ai_generated=True
                    ).first()
                    
                    if not existing_main_material:
                        # Crear descripción limpia sin HTML/CSS para material principal
                        from django.utils.html import strip_tags
                        import re
                        
                        # Usar el contenido más actualizado (priorizar formatted_content)
                        source_content = content.formatted_content or content.raw_content or ""
                        logger.info(f"📝 Creando descripción principal desde contenido de {len(source_content)} caracteres")
                        
                        # Limpiar el contenido de HTML y CSS
                        clean_content = strip_tags(source_content)
                        clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
                        clean_content = re.sub(r':\s*root\s*{[^}]*}', '', clean_content)
                        clean_content = re.sub(r'--[a-zA-Z-]+:\s*[^;]+;', '', clean_content)
                        # Limitar la descripción a las primeras 150 palabras para material principal
                        words = clean_content.split()[:150]
                        clean_description = ' '.join(words)
                        if len(words) == 150:
                            clean_description += '...'
                        
                        # Crear contenido con cabecera institucional para material principal
    # Header institucional eliminado por solicitud del usuario
                        institutional_styles = get_institutional_styles()
                        
                        # Crear HTML completo con cabecera institucional
                        content_with_header = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    {institutional_styles}
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: white;
        }}
        .content {{
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #005CFF;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        p {{
            margin: 1em 0;
            text-align: justify;
        }}
        ul, ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        li {{
            margin: 0.5em 0;
        }}
    </style>
</head>
<body>
    <div class="content">
        {source_content}
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const dateElement = document.getElementById('generation-date');
            if (dateElement) {{
                const now = new Date();
                dateElement.textContent = now.toLocaleDateString('es-ES', {{
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }});
            }}
        }});
    </script>
</body>
</html>"""
                        
                        # Crear el material principal asociado al CourseTopic
                        main_material = PortfolioMaterial.objects.create(
                            course_topic=course_topic,
                            topic=None,  # Material principal
                            title=material_title,
                            description=content_with_header,  # Usar contenido completo con cabecera
                            material_type=material_type,  # SCORM
                            scorm_package=scorm_package,
                            ai_generated=True,
                            is_class_material=True
                        )
                        logger.info(f"✅ Material principal creado en CourseTopic (Sección {section.name}): ID={main_material.id}")
                    else:
                        logger.info(f"⚠️  Material principal ya existe en CourseTopic (Sección {section.name}): ID={existing_main_material.id}")
                
                # Obtener estudiantes matriculados en esta sección
                enrollments = Enrollment.objects.filter(
                    section=section,
                    status='ACTIVE'
                ).select_related('student', 'student__user')
                
                logger.info(f"👥 Procesando {enrollments.count()} estudiantes en la sección {section.name}")
                
                # ========== PASO 4: REPLICAR PARA ESTUDIANTES DE ESTA SECCIÓN ==========
                for enrollment in enrollments:
                    try:
                        student = enrollment.student
                        student_name = student.user.get_full_name()
                        
                        if student_name not in students_processed:
                            students_processed.append(student_name)
                        
                        # Obtener o crear el portafolio del estudiante
                        portfolio, portfolio_created = StudentPortfolio.objects.get_or_create(
                            student=student,
                            month=current_month,
                            academic_year=academic_year,
                            defaults={
                                'course': course
                            }
                        )
                        
                        # Buscar un tema existente con el título especificado
                        existing_topic = PortfolioTopic.objects.filter(
                            portfolio=portfolio,
                            title=course_topic_title
                        ).first()
                        
                        if existing_topic:
                            topics_found += 1
                            topic = existing_topic
                            
                            # Verificar si ya existe un material similar
                            material_exists = PortfolioMaterial.objects.filter(
                                topic=topic,
                                title=material_title,
                                ai_generated=True,
                                is_class_material=True
                            ).exists()
                            
                            if not material_exists:
                                # Crear descripción limpia sin HTML/CSS para material de clase
                                from django.utils.html import strip_tags
                                import re
                                
                                # Usar el contenido más actualizado (priorizar formatted_content)
                                source_content = content.formatted_content or content.raw_content or ""
                                logger.info(f"📝 Creando descripción de clase desde contenido de {len(source_content)} caracteres")
                                
                                # Limpiar el contenido de HTML y CSS
                                clean_content = strip_tags(source_content)
                                clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
                                clean_content = re.sub(r':\s*root\s*{[^}]*}', '', clean_content)
                                clean_content = re.sub(r'--[a-zA-Z-]+:\s*[^;]+;', '', clean_content)
                                # Limitar la descripción a las primeras 100 palabras para material de clase
                                words = clean_content.split()[:100]
                                clean_description = ' '.join(words)
                                if len(words) == 100:
                                    clean_description += '...'
                                
                                # Crear contenido con cabecera institucional para material de clase
    # Header institucional eliminado por solicitud del usuario
                                institutional_styles = get_institutional_styles()
                                
                                # Crear HTML completo con cabecera institucional
                                content_with_header = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    {institutional_styles}
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: white;
        }}
        .content {{
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #005CFF;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        p {{
            margin: 1em 0;
            text-align: justify;
        }}
        ul, ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        li {{
            margin: 0.5em 0;
        }}
    </style>
</head>
<body>
    <div class="content">
        {source_content}
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const dateElement = document.getElementById('generation-date');
            if (dateElement) {{
                const now = new Date();
                dateElement.textContent = now.toLocaleDateString('es-ES', {{
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }});
            }}
        }});
    </script>
</body>
</html>"""
                                
                                # Crear el material de clase en formato SCORM
                                material = PortfolioMaterial.objects.create(
                                    topic=topic,
                                    title=material_title,
                                    description=content_with_header,  # Usar contenido completo con cabecera
                                    material_type=material_type,  # Siempre SCORM para material de clase
                                    scorm_package=scorm_package,  # Siempre debe tener paquete SCORM
                                    ai_generated=True,
                                    is_class_material=True  # IMPORTANTE: Marcar como material de clase (no personalizado)
                                )
                                materials_created += 1
                                logger.info(f"✅ Material de clase SCORM creado para {student_name} (Sección {section.name}): ID={material.id}")
                                logger.info(f"Paquete SCORM asignado al material de clase: {scorm_package.id if scorm_package else 'None'}")
                            else:
                                logger.info(f"⚠️  Material ya existe para {student_name} en sección {section.name}, omitiendo creación")
                                
                        else:
                            topics_not_found += 1
                            logger.warning(f"❌ No se encontró tema '{course_topic_title}' para {student_name} en sección {section.name}")
                            # Continuar sin crear material para este estudiante
                        
                    except Exception as e:
                        logger.error(f"❌ Error al procesar estudiante {student_name} en sección {section.name}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"❌ Error al procesar sección {section.name}: {str(e)}")
                continue
        
        # ========== RESPUESTA FINAL ==========
        success_message = f"🎯 Material de clase SCORM procesado exitosamente:\n"
        success_message += f"📦 Paquete SCORM: ID {scorm_package.id}\n"
        success_message += f"✅ {materials_created} materiales de clase creados\n"
        success_message += f"🏫 {len(sections_processed)} secciones procesadas: {', '.join(sections_processed)}\n"
        success_message += f"👥 {len(students_processed)} estudiantes únicos procesados\n"
        success_message += f"📚 {topics_found} estudiantes tenían el tema '{course_topic_title}'\n"
        
        if topics_not_found > 0:
            success_message += f"⚠️  {topics_not_found} estudiantes no tenían el tema (se omitieron)\n"
        
        return JsonResponse({
            "success": True,
            "message": success_message,
            "scorm_package_id": scorm_package.id,
            "materials_created": materials_created,
            "sections_processed": len(sections_processed),
            "students_processed": len(students_processed),
            "topics_found": topics_found,
            "topics_not_found": topics_not_found
        })
        
    except Exception as e:
        import traceback
        logger.exception(f"Error en handle_class_material_assignment: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            "success": False, 
            "error": f"Error interno del servidor: {str(e)}"
        }, status=500)

def handle_personal_material_assignment(request, content, data):
    """
    Maneja la asignación de material personalizado a múltiples estudiantes seleccionados.
    """
    try:
        from apps.portfolios.models import PortfolioTopic, PortfolioMaterial, StudentPortfolio
        from apps.academic.models import Student
        from apps.scorm_packager.models import SCORMPackage
        from django.utils.html import strip_tags
        import re
        
        # Obtener parámetros
        material_title = data.get('material_name', content.title)
        topic_id = data.get('topic_id')
        target_students = data.get('target_students', [])
        
        # Extraer el título del tema del topic_id compuesto
        topic_title = None
        if isinstance(topic_id, str) and topic_id.startswith('topic_'):
            parts = topic_id.split('_', 2)  # Dividir en máximo 3 partes
            if len(parts) >= 3:
                topic_title = parts[2]  # La tercera parte es el título
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de tema inválido'
                }, status=400)
        else:
            topic_title = topic_id
            
        if not topic_title:
            return JsonResponse({"success": False, "error": "ID de tema inválido"}, status=400)
        
        logger.info(f"Iniciando asignación personalizada para {len(target_students)} estudiantes en tema '{topic_title}'")
        
        # Forzar refresh del contenido para asegurar que tenemos la versión más reciente
        content.refresh_from_db()
        logger.info(f"📊 Contenido refrescado para asignación personalizada - raw_content: {len(content.raw_content or '')} chars, formatted_content: {len(content.formatted_content or '')} chars")
        
        # Verificar si hay un paquete SCORM para este contenido
        scorm_package = SCORMPackage.objects.filter(generated_content=content).first()
        
        # Si no hay paquete SCORM, intentar crear uno automáticamente
        if not scorm_package:
            try:
                logger.info(f"Creando paquete SCORM para material personalizado...")
                
                from apps.scorm_packager.services.packager import SCORMPackager
                from django.conf import settings
                import os
                
                metadata = {
                    'title': content.title,
                    'description': f"Material personalizado generado para {content.request.course.name}",
                    'version': '1.0',
                    'standard': 'scorm_2004_4th'
                }
                
                # Usar solo el contenido educativo para SCORM (sin cabecera institucional)
                source_content = get_clean_educational_content(content)
                
                # Crear el paquete SCORM usando solo el contenido educativo
                packager = SCORMPackager(source_content, metadata)
                package_path = packager.create_package()
                relative_path = os.path.relpath(package_path, settings.MEDIA_ROOT)
                
                scorm_package = SCORMPackage.objects.create(
                    generated_content=content,
                    title=content.title,
                    description=metadata['description'],
                    standard=metadata['standard'],
                    package_file=relative_path,
                    created_by=request.user
                )
                
                logger.info(f"Paquete SCORM creado para material personalizado: ID={scorm_package.id}")
                
            except Exception as scorm_error:
                logger.warning(f"No se pudo crear paquete SCORM para material personalizado: {str(scorm_error)}")
                scorm_package = None
        
        # Determinar el tipo de material
        if scorm_package:
            material_type = 'SCORM'
        else:
            material_type = 'LECTURA'
        
        # Crear descripción limpia usando el contenido más actualizado
        source_content = content.formatted_content or content.raw_content or ""
        logger.info(f"📝 Creando descripción personalizada desde contenido de {len(source_content)} caracteres")
        
        clean_content = strip_tags(source_content)
        clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r':\s*root\s*{[^}]*}', '', clean_content)
        clean_content = re.sub(r'--[a-zA-Z-]+:\s*[^;]+;', '', clean_content)
        words = clean_content.split()[:200]
        clean_description = ' '.join(words)
        if len(words) == 200:
            clean_description += '...'
        
        logger.info(f"📝 Descripción personalizada creada: {len(clean_description)} caracteres")
        
        # Procesar cada estudiante
        materials_created = 0
        students_processed = 0
        failed_students = []
        
        for student_id in target_students:
            try:
                # Obtener el estudiante
                student = Student.objects.get(id=student_id)
                students_processed += 1
                
                # Buscar el tema específico en el portafolio del estudiante
                topic = PortfolioTopic.objects.filter(
                    portfolio__student=student,
                    title=topic_title,
                    teacher=request.user.teacher_profile
                ).first()
                
                if not topic:
                    logger.warning(f"Tema '{topic_title}' no encontrado para estudiante {student_id}")
                    failed_students.append({
                        'student_id': student_id,
                        'student_name': student.user.get_full_name() if student.user else f'Estudiante {student_id}',
                        'error': f"Tema '{topic_title}' no encontrado en su portafolio"
                    })
                    continue
                
                # Crear contenido con cabecera institucional para material personalizado
    # Header institucional eliminado por solicitud del usuario
                institutional_styles = get_institutional_styles()
                
                # Crear HTML completo con cabecera institucional
                content_with_header = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    {institutional_styles}
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
            background-color: white;
        }}
        .content {{
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #005CFF;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        p {{
            margin: 1em 0;
            text-align: justify;
        }}
        ul, ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        li {{
            margin: 0.5em 0;
        }}
    </style>
</head>
<body>
    <div class="content">
        {source_content}
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const dateElement = document.getElementById('generation-date');
            if (dateElement) {{
                const now = new Date();
                dateElement.textContent = now.toLocaleDateString('es-ES', {{
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }});
            }}
        }});
    </script>
</body>
</html>"""
                
                # Crear el material en el portafolio del estudiante
                material = PortfolioMaterial.objects.create(
                    topic=topic,
                    title=material_title,
                    description=content_with_header,  # Usar contenido completo con cabecera
                    material_type=material_type,
                    scorm_package=scorm_package,  # Siempre usar el paquete SCORM si existe
                    ai_generated=True,
                    is_class_material=False
                )
                
                materials_created += 1
                logger.info(f"Material personalizado creado para estudiante {student_id}: Material ID={material.id}")
                
            except Student.DoesNotExist:
                logger.error(f"Estudiante con ID {student_id} no encontrado")
                failed_students.append({
                    'student_id': student_id,
                    'student_name': f'Estudiante {student_id}',
                    'error': 'Estudiante no encontrado'
                })
            except Exception as student_error:
                logger.error(f"Error procesando estudiante {student_id}: {str(student_error)}")
                failed_students.append({
                    'student_id': student_id,
                    'student_name': f'Estudiante {student_id}',
                    'error': str(student_error)
                })
        
        # Preparar respuesta
        response_data = {
            "success": True,
            "message": f"Material personalizado asignado a {materials_created} de {len(target_students)} estudiantes",
            "materials_created": materials_created,
            "students_processed": students_processed,
            "failed_students": failed_students,
            "material_type": material_type
        }
        
        # Agregar información del paquete SCORM si existe
        if scorm_package:
            response_data.update({
                "scorm_package_id": scorm_package.id,
                "scorm_package_created": True
            })
        
        # Si hubo algunos fallos pero también éxitos, es éxito parcial
        if failed_students and materials_created > 0:
            response_data["success"] = True
            response_data["message"] += f". {len(failed_students)} estudiantes tuvieron errores."
        elif materials_created == 0:
            response_data["success"] = False
            response_data["message"] = "No se pudo asignar el material a ningún estudiante"
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        logger.exception(f"Error en handle_personal_material_assignment: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "error": f"Error al procesar material personalizado: {str(e)}"
        }, status=500)

@login_required
def get_portfolio_topics(request, section_id, course_id):
    """
    API para obtener los temas de portafolio disponibles para una sección y curso específicos
    """
    try:
        from apps.academic.models import Course, Section, Teacher
        from apps.portfolios.models import PortfolioTopic
        
        # Verificar que el usuario sea profesor
        if not hasattr(request.user, 'teacher_profile'):
            return JsonResponse({
                'success': False,
                'message': 'Usuario no es un profesor válido'
            }, status=403)
        
        teacher = request.user.teacher_profile
        
        # Verificar que la sección y curso existen
        try:
            section = Section.objects.get(id=section_id)
            course = Course.objects.get(id=course_id)
        except Section.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Sección con ID {section_id} no encontrada'
            }, status=404)
        except Course.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Curso con ID {course_id} no encontrado'
            }, status=404)
        
        # Verificar que el profesor dicta este curso en esta sección
        course_assignment = section.course_assignments.filter(
            teacher=teacher,
            course=course,
            is_active=True
        ).first()
        
        if not course_assignment:
            return JsonResponse({
                'success': False,
                'message': 'No tienes asignado este curso en esta sección'
            }, status=403)
        
        # Obtener temas de portafolio únicos por título
        # Filtramos por estudiantes de la sección y curso específico
        portfolio_topics = PortfolioTopic.objects.filter(
            portfolio__student__enrollments__section=section,
            portfolio__student__enrollments__status='ACTIVE',
            course=course,
            teacher=teacher
        ).values('title', 'description').distinct().order_by('title')
        
        topics_data = []
        topic_id_counter = 1
        
        for topic_info in portfolio_topics:
            # Para cada título único, buscar uno de los PortfolioTopics
            sample_topic = PortfolioTopic.objects.filter(
                portfolio__student__enrollments__section=section,
                portfolio__student__enrollments__status='ACTIVE',
                course=course,
                teacher=teacher,
                title=topic_info['title']
            ).first()
            
            if sample_topic:
                topics_data.append({
                    'id': f"topic_{topic_id_counter}_{topic_info['title']}",  # ID único para el formulario
                    'title': topic_info['title'],
                    'description': topic_info['description'] or '',
                    'real_topic_title': topic_info['title']  # Para buscar los topics reales después
                })
                topic_id_counter += 1
        
        return JsonResponse({
            'success': True,
            'topics': topics_data,
            'section_id': section_id,
            'section_name': f"{section.grade.name} - Sección {section.name}",
            'course_id': course_id,
            'course_name': course.name,
            'total_topics': len(topics_data)
        })
        
    except Exception as e:
        logger.error(f"Error al obtener temas de portafolio para sección {section_id} y curso {course_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener temas de portafolio: {str(e)}'
        }, status=500)

@login_required
def get_students_for_topic(request, section_id, topic_id):
    """
    API para obtener los estudiantes que tienen un tema específico en sus portafolios
    """
    try:
        from apps.academic.models import Section, Student, Enrollment, Teacher
        from apps.portfolios.models import PortfolioTopic
        
        # Verificar que el usuario sea profesor
        if not hasattr(request.user, 'teacher_profile'):
            return JsonResponse({
                'success': False,
                'message': 'Usuario no es un profesor válido'
            }, status=403)
        
        teacher = request.user.teacher_profile
        
        # Verificar que la sección existe
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Sección con ID {section_id} no encontrada'
            }, status=404)
        
        # Extraer el título del tema del topic_id compuesto
        if topic_id.startswith('topic_'):
            parts = topic_id.split('_', 2)  # Dividir en máximo 3 partes
            if len(parts) >= 3:
                topic_title = parts[2]  # La tercera parte es el título
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de tema inválido'
                }, status=400)
        else:
            topic_title = topic_id
        
        # Obtener estudiantes de la sección que tienen el tema específico
        students_with_topic = Student.objects.filter(
            enrollments__section=section,
            enrollments__status='ACTIVE',
            portfolios__portfolio_topics__title=topic_title,
            portfolios__portfolio_topics__teacher=teacher
        ).distinct().select_related('user')
        
        students_data = []
        for student in students_with_topic:
            students_data.append({
                'id': student.id,
                'name': student.user.get_full_name() if student.user else f'Estudiante {student.id}',
                'email': student.user.email if student.user else '',
                'username': student.user.username if student.user else ''
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data,
            'section_id': section_id,
            'section_name': f"{section.grade.name} - Sección {section.name}",
            'topic_title': topic_title,
            'total_students': len(students_data)
        })
        
    except Exception as e:
        logger.error(f"Error al obtener estudiantes para sección {section_id} y tema {topic_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener estudiantes: {str(e)}'
        }, status=500)

class ContentEditView(View):
    def get(self, request, pk):
        try:
            content = GeneratedContent.objects.get(pk=pk)
            if content.request.teacher != request.user:
                messages.error(request, "No tienes permiso para editar este contenido.")
                return redirect('ai:content_detail', pk=pk)
            
            return render(request, 'ai_content_generator/edit_content.html', {
                'content': content
            })
        except GeneratedContent.DoesNotExist:
            messages.error(request, "El contenido solicitado no existe.")
            return redirect('ai:content_request_list')
    
    def post(self, request, pk):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"🔄 Recibiendo solicitud POST para editar contenido {pk}")
            logger.info(f"📋 Campos POST recibidos: {list(request.POST.keys())}")
            
            content = GeneratedContent.objects.get(pk=pk)
            if content.request.teacher != request.user:
                messages.error(request, "No tienes permiso para editar este contenido.")
                return redirect('ai:content_detail', pk=pk)
            
            # Obtener el contenido actualizado desde los campos enviados por el frontend
            content_html = request.POST.get('content_html', '')
            formatted_content = request.POST.get('formatted_content', '')
            
            logger.info(f"📝 Contenido HTML recibido: {len(content_html)} caracteres")
            logger.info(f"📝 Contenido formateado recibido: {len(formatted_content)} caracteres")
            
            # Usar el contenido HTML como contenido principal
            updated_content = content_html or formatted_content
            
            if not updated_content:
                logger.warning("⚠️ No se recibió contenido para guardar")
                messages.error(request, "No se recibió contenido para guardar")
                return redirect('ai:edit_content', pk=pk)
            
            # Verificar si el contenido ya es HTML completo (generado por IA)
            if updated_content.strip().startswith('<!DOCTYPE html>') or updated_content.strip().startswith('<html'):
                # Si ya es HTML completo, NO PROCESARLO para evitar alteración del contenido
                logger.info("📝 Contenido es HTML completo, preservando estructura original")
                content.formatted_content = updated_content
                
                # Intentar extraer contenido sin HTML para raw_content
                import re
                # Extraer solo el texto del body para raw_content
                body_match = re.search(r'<body[^>]*>(.*?)</body>', updated_content, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)
                    # Remover tags HTML básicos para obtener texto limpio
                    clean_text = re.sub(r'<[^>]+>', '', body_content).strip()
                    content.raw_content = clean_text if clean_text else updated_content
                else:
                    content.raw_content = updated_content
            else:
                # Si es contenido parcial, guardarlo como está en raw_content
                logger.info("📝 Contenido es parcial, guardando sin alteración")
                content.raw_content = updated_content
                content.formatted_content = updated_content
            content.save()
            
            logger.info(f"✅ Contenido {pk} actualizado correctamente")
            messages.success(request, "Contenido actualizado correctamente. El header y contenido se han preservado.")
            return redirect('ai:content_detail', pk=pk)
        except GeneratedContent.DoesNotExist:
            logger.error(f"❌ Contenido {pk} no encontrado")
            messages.error(request, "El contenido solicitado no existe.")
            return redirect('ai:content_request_list')
        except Exception as e:
            logger.error(f"❌ Error al editar contenido {pk}: {str(e)}")
            messages.error(request, f"Error al editar el contenido: {str(e)}")
            return redirect('ai:edit_content', pk=pk)

@method_decorator(xframe_options_sameorigin, name='get')
class ContentPreviewView(View):
    """Vista que devuelve el contenido formateado como HTML puro para ser mostrado en un iframe."""
    
    def get(self, request, pk):
        logger = logging.getLogger(__name__)
        try:
            content = GeneratedContent.objects.select_related(
                'request',
                'request__teacher',
                'request__course',
                'request__content_type'
            ).get(pk=pk)
            
            # Solo verificar permisos si el usuario está autenticado
            # Si no está autenticado, permitir acceso para iframes
            if request.user.is_authenticated:
                if content.request.teacher != request.user and not request.user.is_staff:
                    return HttpResponse("""
                        <div style="padding: 40px; text-align: center; font-family: Arial, sans-serif;">
                            <h2 style="color: #dc3545;">Acceso Denegado</h2>
                            <p>No tienes permisos para ver este contenido.</p>
                        </div>
                    """)
            else:
                # Para usuarios no autenticados (como requests de iframe), permitir acceso
                logger.info(f"Acceso al preview sin autenticación para contenido {pk}")
            
            # Remover verificación de referer para permitir iframes
            # Los iframes pueden no enviar referer correctamente
            
            # Usar contenido con lógica mejorada y menos restrictiva
            formatted_content = content.formatted_content or ""
            raw_content_fallback = content.raw_content or ""
            
            # Lógica mejorada para determinar si el contenido está completo
            is_formatted_complete = (
                formatted_content and 
                len(formatted_content.strip()) > 500 and  # Reducido de 1000 a 500
                '<div class="main-container"></div>' not in formatted_content and
                'main-container">' not in formatted_content.replace(' ', '').replace('\n', '') and
                # Verificar que hay contenido de texto real (no solo HTML vacío)
                len(formatted_content.strip().replace('<', '').replace('>', '').replace(' ', '').replace('\n', '')) > 100
            )
            
            # Logging para debug
            logger.info(f"Contenido {pk} - análisis: formatted_len={len(formatted_content)}, raw_len={len(raw_content_fallback)}, is_complete={is_formatted_complete}")
            
            if is_formatted_complete:
                raw_content = content.formatted_content
                logger.info(f"Contenido {pk} - usando formatted_content")
            elif raw_content_fallback and len(raw_content_fallback.strip()) > 100:
                raw_content = raw_content_fallback
                logger.info(f"Contenido {pk} - usando raw_content (formatted incompleto)")
            else:
                # Usar el mejor contenido disponible
                raw_content = formatted_content if len(formatted_content) > len(raw_content_fallback) else raw_content_fallback
                logger.info(f"Contenido {pk} - usando mejor contenido disponible")
            
            if not raw_content.strip():
                logger.warning(f"Contenido {pk} está completamente vacío")
                return HttpResponse(f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Contenido No Disponible</title>
                        <style>
                            body {{
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                padding: 40px;
                                text-align: center;
                                background: #f8f9fa;
                                color: #333;
                            }}
                            .warning-box {{
                                background: #fff3cd;
                                border: 2px solid #ffc107;
                                border-radius: 8px;
                                padding: 30px;
                                margin: 20px auto;
                                max-width: 600px;
                            }}
                            h2 {{ color: #856404; margin-bottom: 15px; }}
                            p {{ color: #856404; margin-bottom: 10px; }}
                            .content-id {{ font-size: 0.9em; color: #6c757d; }}
                        </style>
                    </head>
                    <body>
                        <div class="warning-box">
                            <h2>⚠️ Contenido No Disponible</h2>
                            <p>Este contenido aún no ha sido generado completamente o está vacío.</p>
                            <p><strong>Qué puedes hacer:</strong></p>
                            <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                                <li>Esperar a que termine la generación</li>
                                <li>Recargar la página</li>
                                <li>Volver a la lista de contenidos</li>
                            </ul>
                            <p class="content-id">ID: {pk}</p>
                        </div>
                    </body>
                    </html>
                """)
            
            # Verificar si el contenido ya es HTML completo (puede empezar con meta o html)
            raw_content_clean = raw_content.strip()
            is_complete_html = (
                raw_content_clean.startswith('<!DOCTYPE html>') or 
                raw_content_clean.startswith('<html') or
                raw_content_clean.startswith('<meta') or
                '<style>' in raw_content_clean[:1000]  # Detectar contenido con estilos CSS
            )
            
            if is_complete_html:
                # El contenido ya es HTML completo generado por IA, completar estructura si es necesario
                logger.info(f"Contenido {pk} es HTML completo, completando estructura si es necesario")
                
                # Obtener cabecera institucional
    # Header institucional eliminado por solicitud del usuario
                
                # Completar estructura HTML si es necesario
                if raw_content_clean.startswith('<!DOCTYPE html>'):
                    # Ya tiene DOCTYPE, insertar cabecera después del <body>
                    import re
                    body_match = re.search(r'<body[^>]*>', raw_content, re.IGNORECASE)
                    if body_match:
                        body_end = body_match.end()
                        content_with_header = (
                            raw_content[:body_end] + 
                            raw_content[body_end:]
                        )
                        # Agregar script para fecha
                        script_tag = '''
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const dateElement = document.getElementById('generation-date');
                    if (dateElement) {
                        const now = new Date();
                        dateElement.textContent = now.toLocaleDateString('es-ES', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        });
                    }
                });
            </script>
        </body>'''
                        content_with_header = content_with_header.replace('</body>', script_tag)
                        return HttpResponse(content_with_header)
                    else:
                        logger.info(f"Contenido {pk} tiene DOCTYPE completo, devolviendo sin modificaciones")
                        return HttpResponse(raw_content)
                elif raw_content_clean.startswith('<html'):
                    # Ya tiene html tag, agregar DOCTYPE y cabecera
                    import re
                    body_match = re.search(r'<body[^>]*>', raw_content, re.IGNORECASE)
                    if body_match:
                        body_end = body_match.end()
                        content_with_header = (
                            raw_content[:body_end] + 
                            raw_content[body_end:]
                        )
                        complete_html = f"<!DOCTYPE html>\n{content_with_header}"
                    else:
                        complete_html = f"<!DOCTYPE html>\n{raw_content}"
                else:
                    # Necesita estructura completa, detectar dónde está el contenido del body
                    # Buscar dónde termina el head (después de </style> o </head>)
                    import re
                    
                    # Intentar encontrar el final del head
                    head_end_match = re.search(r'</style>\s*', raw_content, re.IGNORECASE | re.DOTALL)
                    if head_end_match:
                        head_end_pos = head_end_match.end()
                        head_content = raw_content[:head_end_pos].strip()
                        body_content = raw_content[head_end_pos:].strip()
                        
                        complete_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
{head_content}
</head>
<body>
{body_content}
</body>
</html>"""
                    else:
                        # Si no se encuentra </style>, asumir que todo es head
                        complete_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
{raw_content}
</head>
<body>
<div style="padding: 20px;">
<p>Contenido cargado</p>
</div>
</body>
</html>"""
                
                final_html = self._ensure_no_javascript(complete_html)
                return HttpResponse(final_html)
            else:
                # El contenido necesita procesamiento (formato de marcadores)
                logger.info(f"Contenido {pk} requiere procesamiento de marcadores")
                cleaned_content = self._clean_content_for_display(raw_content)
                simple_html = self._create_simple_display_html(cleaned_content, content)
                final_html = self._ensure_no_javascript(simple_html)
                return HttpResponse(final_html)
            
        except GeneratedContent.DoesNotExist:
            return HttpResponse("""
                <div style="padding: 40px; text-align: center; font-family: Arial, sans-serif;">
                    <h2 style="color: #dc3545;">Contenido No Encontrado</h2>
                    <p>El contenido solicitado no existe o ha sido eliminado.</p>
                </div>
            """)
        except Exception as e:
            logger.error(f"Error al mostrar preview del contenido {pk}: {str(e)}")
            return HttpResponse(f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Error al Cargar Contenido</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            padding: 40px;
                            text-align: center;
                            background: #f8f9fa;
                            color: #333;
                        }}
                        .error-box {{
                            background: #f8d7da;
                            border: 2px solid #dc3545;
                            border-radius: 8px;
                            padding: 30px;
                            margin: 20px auto;
                            max-width: 600px;
                        }}
                        h2 {{ color: #721c24; margin-bottom: 15px; }}
                        p {{ color: #721c24; margin-bottom: 10px; }}
                        .error-details {{ font-size: 0.9em; color: #6c757d; }}
                    </style>
                </head>
                <body>
                    <div class="error-box">
                        <h2>❌ Error al Cargar Contenido</h2>
                        <p>Se produjo un error al intentar mostrar el contenido.</p>
                        <p><strong>Qué puedes hacer:</strong></p>
                        <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                            <li>Refresca la página</li>
                            <li>Vuelve a la lista de contenidos</li>
                            <li>Reporta este error al administrador</li>
                        </ul>
                        <p class="error-details">ID: {pk} | Error: {str(e)[:100]}</p>
                    </div>
                </body>
                </html>
            """)
    
    def _clean_content_for_display(self, content: str) -> str:
        """
        Limpia el contenido SOLO de elementos JavaScript peligrosos, preservando todo el contenido educativo
        """
        import re
        
        # Solo eliminar JavaScript peligroso, NO contenido educativo
        problematic_patterns = [
            # JavaScript específico y peligroso
            r'<script[^>]*>.*?</script>',  # Etiquetas script completas
            r'`;\s*if\s*\(contentData\s*&&\s*iframe\).*?}\s*\)\s*;\s*}',  # Código iframe específico
            r'const\s+blob\s*=\s*new\s+Blob.*?;',  # Blob creation específico
            r'iframe\.src\s*=\s*URL\.createObjectURL.*?;',  # iframe src específico
            r'URL\.createObjectURL\(.*?\)',  # URL.createObjectURL específico
            r'new\s+Blob\(\[.*?\]\)',  # new Blob específico
            # Solo frases técnicas muy específicas que no son contenido educativo
            r'```javascript.*?```',  # Bloques de código JavaScript
            r'```html.*?```',  # Bloques de código HTML
        ]
        
        cleaned = content
        
        # Aplicar solo las limpiezas de seguridad (JavaScript peligroso)
        for pattern in problematic_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Mantener TODAS las líneas excepto las que contienen JavaScript muy específico
        lines = cleaned.split('\n')
        clean_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Solo eliminar líneas que claramente son JavaScript peligroso
            if (line_stripped.startswith('<script') or
                'new Blob(' in line_stripped or
                'URL.createObjectURL(' in line_stripped or
                'iframe.src =' in line_stripped or
                line_stripped.startswith('```javascript') or
                line_stripped.startswith('```html')):
                continue
            
            # Preservar TODAS las demás líneas, incluso las vacías para mantener formato
            clean_lines.append(line)
        
        # Mantener el formato original, solo limpiar espacios excesivos al final
        cleaned = '\n'.join(clean_lines)
        cleaned = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', cleaned)  # Máximo 3 líneas vacías
        
        return cleaned.strip()
    
    def _ensure_no_javascript(self, html: str) -> str:
        """
        Garantiza que el HTML final no contenga JavaScript
        """
        import re
        
        # Eliminar todas las etiquetas script
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Eliminar eventos JavaScript inline
        html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
        
        # Eliminar href="javascript:"
        html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', '', html, flags=re.IGNORECASE)
        
        return html
    
    def _create_safe_fallback_html(self, content: str, generated_content) -> str:
        """
        Crea HTML seguro sin JavaScript como fallback
        """
        import re
        
        # Procesar marcadores básicos manualmente
        processed_content = content
        
        # Reemplazar marcadores con HTML básico
        processed_content = re.sub(r'\[TÍTULO\]\s*([^\n]+)', r'<h1>\1</h1>', processed_content)
        processed_content = re.sub(r'\[SUBTÍTULO\]\s*([^\n]+)', r'<h2>\1</h2>', processed_content)
        processed_content = re.sub(r'\[PÁRRAFO\]\s*', r'<p>', processed_content)
        processed_content = re.sub(r'\[EJEMPLO\]\s*', r'<div class="ejemplo"><h3>💡 Ejemplo:</h3><p>', processed_content)
        processed_content = re.sub(r'\[ACTIVIDAD\]\s*', r'<div class="actividad"><h3>🎯 Actividad:</h3><p>', processed_content)
        processed_content = re.sub(r'\[MULTIMEDIA\]\s*', r'<div class="multimedia"><h3>🎥 Recurso Multimedia:</h3><p>', processed_content)
        processed_content = re.sub(r'\[EVALUACIÓN\]\s*', r'<div class="evaluacion"><h3>📊 Evaluación:</h3><p>', processed_content)
        
        # Dividir en párrafos y cerrar etiquetas
        lines = processed_content.split('\n')
        final_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Cerrar párrafos antes de nuevos títulos o secciones
            if (line.startswith('<h') or 
                line.startswith('<div class="ejemplo">') or
                line.startswith('<div class="actividad">') or
                line.startswith('<div class="multimedia">') or
                line.startswith('<div class="evaluacion">')):
                if final_lines and not final_lines[-1].endswith(('</p>', '</div>', '</h1>', '</h2>', '</h3>')):
                    final_lines.append('</p>')
            
            final_lines.append(line)
            
            # Cerrar divs de secciones especiales
            if line.startswith('<div class="') and i < len(lines) - 1:
                next_lines = lines[i+1:]
                # Buscar el próximo marcador o final del contenido
                for j, next_line in enumerate(next_lines):
                    if (next_line.strip().startswith('[') or 
                        next_line.strip().startswith('<h') or
                        next_line.strip().startswith('<div class="') or
                        j == len(next_lines) - 1):
                        # Insertar cierre de párrafo y div
                        if not final_lines[-1].endswith('</p>'):
                            final_lines.append('</p>')
                        final_lines.append('</div>')
                        break
        
        # Cerrar etiquetas pendientes
        if final_lines and not final_lines[-1].endswith(('</p>', '</div>', '</h1>', '</h2>', '</h3>')):
            final_lines.append('</p>')
        
        processed_content = '\n'.join(final_lines)
        
        html_wrapper = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{generated_content.title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #333;
                    background-color: #f8f9fa;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                    margin-top: 30px;
                    margin-bottom: 15px;
                }}
                h1 {{
                    color: #005CFF;
                    border-bottom: 3px solid #005CFF;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #A142F5;
                }}
                p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                .ejemplo, .actividad, .multimedia, .evaluacion {{
                    background: #fff;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .ejemplo {{
                    border-left: 4px solid #28a745;
                }}
                .actividad {{
                    border-left: 4px solid #007bff;
                }}
                .multimedia {{
                    border-left: 4px solid #ffc107;
                }}
                .evaluacion {{
                    border-left: 4px solid #dc3545;
                }}
                .header {{
                    background: linear-gradient(135deg, #005CFF 0%, #A142F5 50%, #00CFFF 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{generated_content.title}</h1>
                <p><strong>Curso:</strong> {generated_content.request.course.name if generated_content.request.course else 'Sin curso'} | 
                <strong>Grado:</strong> {generated_content.request.grade_level if generated_content.request.grade_level else 'Sin grado'}</p>
            </div>
            <div class="content">
                {processed_content}
            </div>
        </body>
        </html>
        """
        
        return html_wrapper

    def _create_simple_display_html(self, content: str, generated_content) -> str:
        """
        Crea HTML simple preservando TODO el contenido sin procesamiento complejo
        """
        import re
        
        # Convertir marcadores básicos pero preservar TODO el contenido
        html_content = content
        
        # Solo reemplazos básicos y seguros
        html_content = re.sub(r'\[TÍTULO\]\s*([^\n]+)', r'<h1 style="color: #005CFF; border-bottom: 2px solid #005CFF; padding-bottom: 10px;">\1</h1>', html_content)
        html_content = re.sub(r'\[SUBTÍTULO\]\s*([^\n]+)', r'<h2 style="color: #A142F5; margin-top: 25px;">\1</h2>', html_content)
        html_content = re.sub(r'\[PÁRRAFO\]\s*', r'', html_content)
        
        # Procesar secciones especiales preservando MÚLTIPLES instancias
        html_content = re.sub(r'\[EJEMPLO\]', r'<div class="ejemplo"><h3 style="color: #28a745;">💡 Ejemplo:</h3>', html_content)
        html_content = re.sub(r'\[ACTIVIDAD\]', r'<div class="actividad"><h3 style="color: #007bff;">🎯 Actividad:</h3>', html_content)
        html_content = re.sub(r'\[MULTIMEDIA\]', r'<div class="multimedia"><h3 style="color: #ffc107;">🎥 Recurso Multimedia:</h3>', html_content)
        html_content = re.sub(r'\[EVALUACIÓN\]', r'<div class="evaluacion"><h3 style="color: #dc3545;">📊 Evaluación:</h3>', html_content)
        
        # Convertir saltos de línea a párrafos, preservando estructura
        lines = html_content.split('\n')
        processed_lines = []
        in_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if not in_section:
                    processed_lines.append('<br>')
                continue
            
            # Detectar inicio de secciones
            if line.startswith('<div class="'):
                in_section = True
                processed_lines.append(line)
            elif in_section and (line.startswith('<h1') or line.startswith('<h2') or line.startswith('<div class="')):
                # Cerrar sección anterior
                processed_lines.append('</div>')
                processed_lines.append(line)
                in_section = line.startswith('<div class="')
            elif line.startswith('<h1') or line.startswith('<h2'):
                if in_section:
                    processed_lines.append('</div>')
                    in_section = False
                processed_lines.append(line)
            else:
                # Contenido normal
                if not line.startswith('<'):
                    processed_lines.append(f'<p>{line}</p>')
                else:
                    processed_lines.append(line)
        
        # Cerrar última sección si está abierta
        if in_section:
            processed_lines.append('</div>')
        
        processed_content = '\n'.join(processed_lines)
        
        # Obtener cabecera institucional
    # Header institucional eliminado por solicitud del usuario
        institutional_styles = get_institutional_styles()
        
        html_wrapper = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{generated_content.title}</title>
            {institutional_styles}
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    color: #333;
                    background-color: white;
                }}
                
                /* Estilos básicos de HTML idénticos a la vista de edición */
                h1 {{
                    font-size: 2em;
                    font-weight: bold;
                    margin: 0.67em 0;
                }}
                h2 {{
                    font-size: 1.5em;
                    font-weight: bold;
                    margin: 0.75em 0;
                }}
                h3 {{
                    font-size: 1.3em;
                    font-weight: bold;
                    margin: 0.83em 0;
                }}
                h4 {{
                    font-size: 1.1em;
                    font-weight: bold;
                    margin: 1.12em 0;
                }}
                h5 {{
                    font-size: 0.9em;
                    font-weight: bold;
                    margin: 1.5em 0;
                }}
                h6 {{
                    font-size: 0.8em;
                    font-weight: bold;
                    margin: 1.67em 0;
                }}
                p {{
                    margin: 1em 0;
                }}
                ul, ol {{
                    margin: 1em 0;
                    padding-left: 2em;
                }}
                li {{
                    margin: 0.5em 0;
                }}
                strong, b {{
                    font-weight: bold;
                }}
                em, i {{
                    font-style: italic;
                }}
                u {{
                    text-decoration: underline;
                }}
                s, strike {{
                    text-decoration: line-through;
                }}
                blockquote {{
                    margin: 1em 0;
                    padding-left: 1em;
                    border-left: 3px solid #ccc;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                a {{
                    color: #0066cc;
                    text-decoration: underline;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: monospace;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    margin: 1em 0;
                }}
                
                /* Estilos para encabezado institucional idénticos al editor */
                .institutional-header {{
                    background: linear-gradient(135deg, #005CFF 0%, #A142F5 50%, #00CFFF 100%) !important;
                    color: white !important;
                    padding: 2rem 2rem 1.5rem 2rem !important;
                    margin: 0 0 2rem 0 !important;
                    border-radius: 0 0 20px 20px !important;
                    box-shadow: 0 8px 32px rgba(0, 92, 255, 0.3) !important;
                    position: relative !important;
                    overflow: hidden !important;
                }}
                .header-content {{
                    display: flex !important;
                    justify-content: space-between !important;
                    align-items: center !important;
                    position: relative !important;
                    z-index: 1 !important;
                }}
                .header-left {{
                    display: flex !important;
                    align-items: center !important;
                    gap: 1.5rem !important;
                }}
                .institution-logo {{
                    width: 80px !important;
                    height: 80px !important;
                    object-fit: contain !important;
                    background: rgba(255, 255, 255, 0.1) !important;
                    border-radius: 15px !important;
                    padding: 0.5rem !important;
                    backdrop-filter: blur(10px) !important;
                    border: 2px solid rgba(255, 255, 255, 0.2) !important;
                }}
                .institution-info h1, .institution-name {{
                    font-size: 1.8rem !important;
                    font-weight: 700 !important;
                    margin: 0 0 0.3rem 0 !important;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
                    color: white !important;
                }}
                .institution-subtitle {{
                    font-size: 1rem !important;
                    margin: 0 0 0.2rem 0 !important;
                    opacity: 0.9 !important;
                    font-weight: 500 !important;
                    color: #FFD700 !important;
                }}
                .institution-address {{
                    font-size: 0.85rem !important;
                    margin: 0 !important;
                    opacity: 0.8 !important;
                    color: rgba(255, 255, 255, 0.8) !important;
                }}
                .header-right {{
                    display: flex !important;
                    flex-direction: column !important;
                    gap: 0.8rem !important;
                    align-items: flex-end !important;
                }}
                .ai-badge {{
                    background: rgba(255, 215, 0, 0.2) !important;
                    padding: 0.5rem 1rem !important;
                    border-radius: 25px !important;
                    display: flex !important;
                    align-items: center !important;
                    gap: 0.5rem !important;
                    font-size: 0.9rem !important;
                    font-weight: 600 !important;
                    backdrop-filter: blur(10px) !important;
                    border: 1px solid rgba(255, 215, 0, 0.3) !important;
                    color: #FFD700 !important;
                }}
                .generation-date {{
                    display: flex !important;
                    align-items: center !important;
                    gap: 0.4rem !important;
                    font-size: 0.8rem !important;
                    opacity: 0.8 !important;
                    color: rgba(255, 255, 255, 0.9) !important;
                }}
                
                /* Contenido principal */
                .content {{
                    padding: 20px;
                }}
                
                /* Secciones especiales */
                .ejemplo, .actividad, .multimedia, .evaluacion {{
                    background: #fff;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .ejemplo {{
                    border-left: 4px solid #28a745;
                }}
                .actividad {{
                    border-left: 4px solid #007bff;
                }}
                .multimedia {{
                    border-left: 4px solid #ffc107;
                }}
                .evaluacion {{
                    border-left: 4px solid #dc3545;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {processed_content}
            </div>
            <script>
                // Establecer fecha de generación
                document.addEventListener('DOMContentLoaded', function() {{
                    const dateElement = document.getElementById('generation-date');
                    if (dateElement) {{
                        const now = new Date();
                        dateElement.textContent = now.toLocaleDateString('es-ES', {{
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        }});
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        return html_wrapper

@login_required
def cancel_generation_view(request, request_id):
    """
    Vista para cancelar la generación de contenido en proceso
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        # Obtener la solicitud
        content_request = get_object_or_404(ContentRequest, id=request_id, teacher=request.user)
        
        # Verificar que la solicitud esté en un estado cancelable
        if content_request.status not in ['pending', 'processing']:
            return JsonResponse({
                'success': False, 
                'message': f'No se puede cancelar una solicitud en estado "{content_request.get_status_display()}"'
            })
        
        # Actualizar el estado
        content_request.status = 'cancelled'
        content_request.save()
        
        logger.info(f"Solicitud {request_id} cancelada por usuario {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'La generación de contenido ha sido cancelada exitosamente.',
            'new_status': 'cancelled'
        })
        
    except ContentRequest.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Solicitud no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error al cancelar solicitud {request_id}: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'}, status=500)

@login_required
def content_request_redirect(request, pk):
    """
    Redirects from a ContentRequest ID to the corresponding GeneratedContent.
    This handles the case where users directly access /ai/contents/<request_id>/ 
    using ContentRequest ID instead of GeneratedContent ID.
    """
    content_request = get_object_or_404(ContentRequest, pk=pk)
    
    # Check if the user has permission to view this content
    if content_request.teacher != request.user and not request.user.is_staff:
        messages.error(request, "No tiene permisos para ver este contenido.")
        return redirect('ai:content_request_list')
    
    # Get the first generated content for this request
    generated_content = content_request.contents.first()
    
    if generated_content:
        # Redirect to the actual content detail view
        return redirect('ai:content_detail', pk=generated_content.id)
    else:
        messages.warning(request, "Este contenido aún no ha sido generado o ya no está disponible.")
        return redirect('ai:content_request_list')

@login_required
def get_progress(request, request_id):
    """Obtener progreso de generación de contenido"""
    try:
        content_request = ContentRequest.objects.get(id=request_id)
        return JsonResponse({
            'status': content_request.status,
            'progress': 100 if content_request.status == 'completed' else 50
        })
    except ContentRequest.DoesNotExist:
        return JsonResponse({'status': 'not_found', 'progress': 0}, status=404)

@login_required
def delete_request_view(request, request_id):
    """
    Vista para eliminar completamente una solicitud de contenido y su contenido relacionado
    """
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        # Obtener la solicitud
        content_request = get_object_or_404(ContentRequest, id=request_id, teacher=request.user)
        
        # Verificar que solo se puedan eliminar solicitudes completadas, canceladas o fallidas
        if content_request.status in ['pending', 'processing']:
            return JsonResponse({
                'success': False, 
                'message': 'No se puede eliminar una solicitud que está en proceso. Primero cancélala.'
            })
        
        # Eliminar contenido relacionado y archivos SCORM
        try:
            for content in content_request.contents.all():
                # Eliminar paquetes SCORM relacionados
                for package in content.scorm_packages.all():
                    try:
                        # Eliminar archivo físico del paquete SCORM
                        if package.package_file and os.path.exists(package.package_file.path):
                            os.remove(package.package_file.path)
                        package.delete()
                    except Exception as e:
                        logger.warning(f"Error al eliminar paquete SCORM {package.id}: {str(e)}")
                
                # Eliminar el contenido generado
                content.delete()
                
        except Exception as e:
            logger.warning(f"Error al eliminar contenido relacionado para solicitud {request_id}: {str(e)}")
        
        # Guardar información para el log antes de eliminar
        request_topic = content_request.topic
        request_course = content_request.course.name if content_request.course else "Sin curso"
        
        # Eliminar la solicitud
        content_request.delete()
        
        logger.info(f"Solicitud {request_id} ({request_topic} - {request_course}) eliminada completamente por usuario {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'La solicitud y todo su contenido relacionado han sido eliminados exitosamente.'
        })
        
    except ContentRequest.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Solicitud no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error al eliminar solicitud {request_id}: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Error interno: {str(e)}'}, status=500)

@login_required
def get_grades_for_course(request, course_id):
    """
    API para obtener los grados donde el profesor actual dicta el curso especificado
    """
    try:
        from apps.academic.models import Course, Grade, CourseAssignment, Teacher
        
        # Verificar que el usuario sea profesor
        if not hasattr(request.user, 'teacher_profile'):
            return JsonResponse({
                'success': False,
                'message': 'Usuario no es un profesor válido'
            }, status=403)
        
        teacher = request.user.teacher_profile
        
        # Verificar que el curso existe
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Curso con ID {course_id} no encontrado'
            }, status=404)
        
        # Obtener grados donde el profesor dicta este curso
        grades = Grade.objects.filter(
            sections__course_assignments__teacher=teacher,
            sections__course_assignments__course=course,
            sections__course_assignments__is_active=True
        ).distinct().order_by('level', 'name')
        
        grades_data = []
        for grade in grades:
            grades_data.append({
                'id': grade.id,
                'name': grade.name,
                'level': grade.level
            })
        
        return JsonResponse({
            'success': True,
            'grades': grades_data,
            'course_id': course_id,
            'course_name': course.name
        })
        
    except Exception as e:
        logger.error(f"Error al obtener grados para curso {course_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener grados: {str(e)}'
        }, status=500)

@login_required
def get_sections_for_grade(request, grade_id, course_id):
    """
    API para obtener las secciones de un grado específico donde el profesor dicta el curso
    """
    try:
        from apps.academic.models import Course, Grade, Section, CourseAssignment, Teacher, Enrollment
        
        # Verificar que el usuario sea profesor
        if not hasattr(request.user, 'teacher_profile'):
            return JsonResponse({
                'success': False,
                'message': 'Usuario no es un profesor válido'
            }, status=403)
        
        teacher = request.user.teacher_profile
        
        # Verificar que el grado y curso existen
        try:
            grade = Grade.objects.get(id=grade_id)
            course = Course.objects.get(id=course_id)
        except Grade.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Grado con ID {grade_id} no encontrado'
            }, status=404)
        except Course.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Curso con ID {course_id} no encontrado'
            }, status=404)
        
        # Obtener secciones del grado donde el profesor dicta el curso
        sections = Section.objects.filter(
            grade=grade,
            course_assignments__teacher=teacher,
            course_assignments__course=course,
            course_assignments__is_active=True,
            is_active=True
        ).distinct().order_by('name')
        
        sections_data = []
        for section in sections:
            # Contar estudiantes activos en la sección
            students_count = Enrollment.objects.filter(
                section=section,
                status='ACTIVE'
            ).count()
            
            sections_data.append({
                'id': section.id,
                'name': section.name,
                'students_count': students_count,
                'capacity': section.capacity or 30
            })
        
        return JsonResponse({
            'success': True,
            'sections': sections_data,
            'grade_id': grade_id,
            'grade_name': grade.name,
            'course_id': course_id,
            'course_name': course.name
        })
        
    except Exception as e:
        logger.error(f"Error al obtener secciones para grado {grade_id} y curso {course_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener secciones: {str(e)}'
        }, status=500)

@login_required
def get_course_topics(request, section_id, course_id):
    """
    API para obtener los temas del curso (CourseTopics) para una sección específica
    """
    try:
        from apps.academic.models import Course, Section, CourseTopic, Teacher
        
        # Verificar que el usuario sea profesor
        if not hasattr(request.user, 'teacher_profile'):
            return JsonResponse({
                'success': False,
                'message': 'Usuario no es un profesor válido'
            }, status=403)
        
        teacher = request.user.teacher_profile
        
        # Verificar que la sección y curso existen
        try:
            section = Section.objects.get(id=section_id)
            course = Course.objects.get(id=course_id)
        except Section.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Sección con ID {section_id} no encontrada'
            }, status=404)
        except Course.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Curso con ID {course_id} no encontrado'
            }, status=404)
        
        # Verificar que el profesor dicta este curso en esta sección
        course_assignment = section.course_assignments.filter(
            teacher=teacher,
            course=course,
            is_active=True
        ).first()
        
        if not course_assignment:
            return JsonResponse({
                'success': False,
                'message': 'No tienes asignado este curso en esta sección'
            }, status=403)
        
        # Obtener temas del curso para esta sección y profesor
        course_topics = CourseTopic.objects.filter(
            section=section,
            course=course,
            teacher=teacher,
            is_active=True
        ).order_by('created_at')
        
        topics_data = []
        for topic in course_topics:
            topics_data.append({
                'id': topic.id,
                'title': topic.title,
                'description': topic.description or '',
                'created_at': topic.created_at.strftime('%d/%m/%Y') if topic.created_at else ''
            })
        
        return JsonResponse({
            'success': True,
            'topics': topics_data,
            'section_id': section_id,
            'section_name': f"{section.grade.name} - Sección {section.name}",
            'course_id': course_id,
            'course_name': course.name,
            'total_topics': len(topics_data)
        })
        
    except Exception as e:
        logger.error(f"Error al obtener temas para sección {section_id} y curso {course_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener temas: {str(e)}'
        }, status=500)


class MaterialPreviewView(LoginRequiredMixin, TemplateView):
    """
    Vista para mostrar la preview del nuevo header institucional en materiales de IA
    """
    template_name = 'ai_content_generator/material_preview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener información institucional para la preview
        context['institution'] = None
        
        try:
            from apps.institutions.models import Institution
            institution = None
            
            # Intentar obtener la institución desde diferentes perfiles
            if hasattr(self.request.user, 'teacher_profile') and hasattr(self.request.user.teacher_profile, 'institution'):
                institution = self.request.user.teacher_profile.institution
            elif hasattr(self.request.user, 'director_profile') and hasattr(self.request.user.director_profile, 'institution'):
                institution = self.request.user.director_profile.institution
            elif hasattr(self.request.user, 'student_profile'):
                # Para estudiantes, obtener la institución desde su matrícula activa
                from apps.academic.models import Enrollment
                enrollment = Enrollment.objects.filter(
                    student=self.request.user.student_profile,
                    status='ACTIVE'
                ).first()
                if enrollment and hasattr(enrollment.section, 'institution'):
                    institution = enrollment.section.institution
            
            context['institution'] = institution
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error obteniendo institución para preview: {str(e)}")
        
        return context

def test_content_styles_view(request):
    """
    Vista de prueba para verificar que todos los tipos de contenido se generen correctamente
    """
    from .utils.enhanced_text_processor import EnhancedTextProcessor
    
    # Contenido de prueba con diferentes tipos de secciones
    test_content = """
[TÍTULO] Matemáticas aplicadas a la nutrición: Cálculo de porcentajes en etiquetas nutricionales

[PÁRRAFO] El análisis matemático de las etiquetas nutricionales es una habilidad fundamental para tomar decisiones alimenticias informadas. Al comprender cómo calcular porcentajes, los estudiantes pueden determinar exactamente qué proporción de sus necesidades diarias aporta cada alimento.

[EJEMPLO] Consideremos un caso práctico con una popular bebida energética: La etiqueta indica que una lata de 250ml contiene 27g de azúcares. Para contextualizar este valor, primero debemos conocer que la Organización Mundial de la Salud recomienda un máximo de 25g de azúcares añadidos por día para adolescentes.

[ACTIVIDAD] "Analizamos nuestra lonchera": Esta actividad práctica se desarrolla en tres fases. Primero, los estudiantes traerán etiquetas nutricionales de alimentos que consumen habitualmente. En grupos de 3, crearán una base de datos con los valores nutricionales principales.

[MULTIMEDIA] Infografía interactiva "Descifrando etiquetas nutricionales": Este recurso visual muestra una etiqueta nutricional ampliada con explicaciones emergentes al pasar el cursor. Cada componente nutricional tiene un círculo porcentual que se completa dinámicamente.

[EVALUACIÓN] La evaluación consta de cuatro componentes que miden diferentes competencias. La parte teórica incluye resolver 5 problemas de cálculo de porcentajes nutricionales a partir de etiquetas reales.
"""

    processor = EnhancedTextProcessor()
    
    try:
        # Procesar el contenido de prueba
        processed_html = processor.process_to_structured_html(
            raw_text=test_content,
            topic="Matemáticas aplicadas a la nutrición",
            course="Matemáticas",
            grade="4to Grado"
        )
        
        return HttpResponse(processed_html)
        
    except Exception as e:
        logger.error(f"Error en test_content_styles_view: {str(e)}")
        return HttpResponse(f"""
            <div style="padding: 40px; font-family: Arial, sans-serif;">
                <h2 style="color: #dc3545;">Error en la prueba de contenido</h2>
                <p>Se produjo un error al procesar el contenido de prueba.</p>
                <p style="color: #6c757d; font-size: 0.9em;">Error: {str(e)}</p>
                <h3>Contenido original:</h3>
                <pre style="background: #f8f9fa; padding: 20px; border-radius: 5px; white-space: pre-wrap;">{test_content}</pre>
            </div>
        """)

def debug_content_processing_view(request):
    """
    Vista de debug para verificar el procesamiento del contenido
    """
    from .utils.enhanced_text_processor import EnhancedTextProcessor
    
    # Contenido de prueba con diferentes tipos de secciones
    test_content = """
[TÍTULO] Matemáticas aplicadas a la nutrición: Cálculo de porcentajes en etiquetas nutricionales

[PÁRRAFO] El análisis matemático de las etiquetas nutricionales es una habilidad fundamental para tomar decisiones alimenticias informadas. Al comprender cómo calcular porcentajes, los estudiantes pueden determinar exactamente qué proporción de sus necesidades diarias aporta cada alimento.

[EJEMPLO] Consideremos un caso práctico con una popular bebida energética: La etiqueta indica que una lata de 250ml contiene 27g de azúcares. Para contextualizar este valor, primero debemos conocer que la Organización Mundial de la Salud recomienda un máximo de 25g de azúcares añadidos por día para adolescentes.

[ACTIVIDAD] "Analizamos nuestra lonchera": Esta actividad práctica se desarrolla en tres fases. Primero, los estudiantes traerán etiquetas nutricionales de alimentos que consumen habitualmente.

[MULTIMEDIA] Infografía interactiva "Descifrando etiquetas nutricionales": Este recurso visual muestra una etiqueta nutricional ampliada con explicaciones emergentes.

[EVALUACIÓN] La evaluación consta de cuatro componentes que miden diferentes competencias. La parte teórica incluye resolver 5 problemas de cálculo de porcentajes nutricionales.
"""

    processor = EnhancedTextProcessor()
    
    try:
        # Limpiar el contenido
        cleaned_content = processor._clean_problematic_content(test_content)
        
        # Extraer elementos
        elements = processor._extract_all_elements(cleaned_content)
        
        # Debug HTML
        debug_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Debug - Procesamiento de contenido</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
                .original { background: #f0f0f0; }
                .cleaned { background: #e8f5e8; }
                .elements { background: #e8f0ff; }
                pre { white-space: pre-wrap; word-wrap: break-word; }
                h3 { color: #333; }
            </style>
        </head>
        <body>
            <h1>Debug - Procesamiento de Contenido</h1>
            
            <div class="section original">
                <h3>Contenido Original:</h3>
                <pre>{test_content}</pre>
            </div>
            
            <div class="section cleaned">
                <h3>Contenido Limpio:</h3>
                <pre>{cleaned_content}</pre>
            </div>
            
            <div class="section elements">
                <h3>Elementos Extraídos:</h3>
                <h4>Título:</h4>
                <p>{elements.get('title', 'NO ENCONTRADO')}</p>
                
                <h4>Secciones ({len(elements.get('sections', []))}):</h4>
                <ul>
                    {''.join([f"<li><strong>{s['type']}:</strong> {s['content'][:100]}...</li>" for s in elements.get('sections', [])])}
                </ul>
                
                <h4>Ejemplos ({len(elements.get('examples', []))}):</h4>
                <ul>
                    {''.join([f"<li>{ex[:100]}...</li>" for ex in elements.get('examples', [])])}
                </ul>
                
                <h4>Actividades ({len(elements.get('activities', []))}):</h4>
                <ul>
                    {''.join([f"<li>{act[:100]}...</li>" for act in elements.get('activities', [])])}
                </ul>
                
                <h4>Multimedia ({len(elements.get('multimedia', []))}):</h4>
                <ul>
                    {''.join([f"<li>{mult[:100]}...</li>" for mult in elements.get('multimedia', [])])}
                </ul>
                
                <h4>Evaluación ({len(elements.get('evaluation', []))}):</h4>
                <ul>
                    {''.join([f"<li>{ev[:100]}...</li>" for ev in elements.get('evaluation', [])])}
                </ul>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(debug_html)
        
    except Exception as e:
        return HttpResponse(f"""
            <html>
            <head><title>Error de Debug</title></head>
            <body>
                <h1>Error en el procesamiento</h1>
                <p>Error: {str(e)}</p>
                <pre>{test_content}</pre>
            </body>
            </html>
        """)

def final_content_test_view(request):
    """
    Vista final de prueba para verificar que todos los tipos de contenido se generen correctamente
    """
    from .utils.enhanced_text_processor import EnhancedTextProcessor
    
    # Contenido completo de prueba con todos los tipos de secciones
    test_content = """
[TÍTULO] Matemáticas aplicadas a la nutrición: Cálculo de porcentajes en etiquetas nutricionales

[PÁRRAFO] El análisis matemático de las etiquetas nutricionales es una habilidad fundamental para tomar decisiones alimenticias informadas. Al comprender cómo calcular porcentajes, los estudiantes pueden determinar exactamente qué proporción de sus necesidades diarias aporta cada alimento. Por ejemplo, una etiqueta que indica 15g de carbohidratos por porción representa un porcentaje específico de la ingesta diaria recomendada.

[EJEMPLO] Consideremos un caso práctico con una popular bebida energética: La etiqueta indica que una lata de 250ml contiene 27g de azúcares. Para contextualizar este valor, primero debemos conocer que la Organización Mundial de la Salud recomienda un máximo de 25g de azúcares añadidos por día para adolescentes. Realizando el cálculo: (27g/25g)×100 = 108%. Esto significa que una sola lata supera la recomendación diaria completa.

[ACTIVIDAD] "Analizamos nuestra lonchera": Esta actividad práctica se desarrolla en tres fases. Primero, los estudiantes traerán etiquetas nutricionales de alimentos que consumen habitualmente. En grupos de 3, crearán una base de datos con los valores nutricionales principales: calorías, carbohidratos, proteínas, grasas, azúcares y sodio. Usando hojas de cálculo, calcularán el porcentaje que cada alimento aporta respecto a las recomendaciones diarias para su edad.

[MULTIMEDIA] Infografía interactiva "Descifrando etiquetas nutricionales": Este recurso visual muestra una etiqueta nutricional ampliada con explicaciones emergentes al pasar el cursor. Cada componente nutricional tiene un círculo porcentual que se completa dinámicamente al ingresar diferentes valores de consumo diario. Incluye un comparador de productos donde los estudiantes pueden arrastrar dos alimentos y ver una representación gráfica de sus diferencias nutricionales.

[EVALUACIÓN] La evaluación consta de cuatro componentes que miden diferentes competencias. La parte teórica incluye resolver 5 problemas de cálculo de porcentajes nutricionales a partir de etiquetas reales. En la sección práctica, los estudiantes recibirán datos nutricionales de tres desayunos diferentes y deberán: 1) Calcular el porcentaje de CDR para cada nutriente principal, 2) Crear una representación gráfica comparativa, 3) Justificar matemáticamente cuál es la opción más balanceada.
"""

    processor = EnhancedTextProcessor()
    
    try:
        # Procesar el contenido completo
        processed_html = processor.process_to_structured_html(
            raw_text=test_content,
            topic="Matemáticas aplicadas a la nutrición",
            course="Matemáticas",
            grade="4to Grado"
        )
        
        return HttpResponse(processed_html)
        
    except Exception as e:
        logger.error(f"Error en final_content_test_view: {str(e)}")
        return HttpResponse(f"""
            <div style="padding: 40px; font-family: Arial, sans-serif;">
                <h2 style="color: #dc3545;">Error en la prueba final de contenido</h2>
                <p>Se produjo un error al procesar el contenido de prueba final.</p>
                <p style="color: #6c757d; font-size: 0.9em;">Error: {str(e)}</p>
                <h3>Contenido original:</h3>
                <pre style="background: #f8f9fa; padding: 20px; border-radius: 5px; white-space: pre-wrap;">{test_content}</pre>
            </div>
        """)

def debug_line_by_line_view(request):
    """
    Vista de debug línea por línea para ver exactamente qué está pasando
    """
    from .utils.enhanced_text_processor import EnhancedTextProcessor
    import re
    
    # Contenido de prueba
    test_content = """
[TÍTULO] Matemáticas aplicadas a la nutrición: Cálculo de porcentajes en etiquetas nutricionales

[PÁRRAFO] El análisis matemático de las etiquetas nutricionales es una habilidad fundamental para tomar decisiones alimenticias informadas.

[EJEMPLO] Consideremos un caso práctico con una popular bebida energética.

[ACTIVIDAD] "Analizamos nuestra lonchera": Esta actividad práctica se desarrolla en tres fases.

[MULTIMEDIA] Infografía interactiva "Descifrando etiquetas nutricionales".

[EVALUACIÓN] La evaluación consta de cuatro componentes que miden diferentes competencias.
"""

    processor = EnhancedTextProcessor()
    
    # Limpiar el contenido
    cleaned_content = processor._clean_problematic_content(test_content)
    
    # Procesar línea por línea
    lines = cleaned_content.split('\n')
    debug_info = []
    
    current_section = None
    current_content = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Verificar si es marcador
        is_marker = re.match(r'\[([A-ZÁÉÍÓÚÜ\s]+)\]', line_stripped) is not None
        marker_type = ""
        
        if is_marker:
            match = re.match(r'\[([A-ZÁÉÍÓÚÜ\s]+)\]', line_stripped)
            marker_type = match.group(1).strip() if match else ''
        
        debug_info.append({
            'line_num': i + 1,
            'original': repr(line),
            'stripped': repr(line_stripped),
            'is_empty': not line_stripped,
            'is_marker': is_marker,
            'marker_type': marker_type,
            'current_section': current_section
        })
        
        # Simular el procesamiento
        if not line_stripped:
            continue
            
        if is_marker:
            if current_section and current_content:
                debug_info[-1]['action'] = f"Guardando sección '{current_section}' con {len(current_content)} líneas"
            
            current_section = marker_type
            current_content = []
            
            if current_section == 'TÍTULO':
                title_text = line_stripped.replace('[TÍTULO]', '').strip()
                debug_info[-1]['action'] = f"Título extraído: '{title_text}'"
                current_section = None
            else:
                debug_info[-1]['action'] = f"Iniciando nueva sección: '{current_section}'"
        else:
            if current_section:
                current_content.append(line_stripped)
                debug_info[-1]['action'] = f"Agregando a sección '{current_section}' (total: {len(current_content)})"
            else:
                debug_info[-1]['action'] = "Línea ignorada (no hay sección activa)"
    
    # Generar HTML de debug
    debug_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Debug Línea por Línea</title>
        <style>
            body { font-family: monospace; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f0f0f0; }
            .marker { background: #ffffcc; }
            .empty { background: #f8f8f8; color: #999; }
            .content { background: #e8f5e8; }
        </style>
    </head>
    <body>
        <h1>Debug Línea por Línea</h1>
        
        <h3>Contenido Original:</h3>
        <pre>{test_content}</pre>
        
        <h3>Contenido Limpio:</h3>
        <pre>{cleaned_content}</pre>
        
        <h3>Procesamiento Línea por Línea:</h3>
        <table>
            <tr>
                <th>#</th>
                <th>Línea Original</th>
                <th>Línea Limpia</th>
                <th>¿Vacía?</th>
                <th>¿Marcador?</th>
                <th>Tipo Marcador</th>
                <th>Sección Actual</th>
                <th>Acción</th>
            </tr>
    """
    
    for info in debug_info:
        row_class = ""
        if info['is_marker']:
            row_class = "marker"
        elif info['is_empty']:
            row_class = "empty"
        elif info.get('action', '').startswith('Agregando'):
            row_class = "content"
        
        debug_html += f"""
            <tr class="{row_class}">
                <td>{info['line_num']}</td>
                <td>{info['original']}</td>
                <td>{info['stripped']}</td>
                <td>{'Sí' if info['is_empty'] else 'No'}</td>
                <td>{'Sí' if info['is_marker'] else 'No'}</td>
                <td>{info['marker_type']}</td>
                <td>{info['current_section'] or '-'}</td>
                <td>{info.get('action', '-')}</td>
            </tr>
        """
    
    debug_html += """
        </table>
    </body>
    </html>
    """
    
    return HttpResponse(debug_html)

@login_required
def auto_generate_content_view(request):
    """
    Vista para generar contenido automáticamente basado en parámetros de URL
    """
    # Obtener parámetros de la URL
    course_topic_id = request.GET.get('course_topic_id')
    course_id = request.GET.get('course')
    topic = request.GET.get('topic')
    grade_level = request.GET.get('grade_level')
    for_class = request.GET.get('for_class', 'false').lower() == 'true'
    
    if not all([course_topic_id, course_id, topic, grade_level]):
        messages.error(request, 'Faltan parámetros requeridos para la generación automática.')
        return redirect('ai:generator')
    
    try:
        # Verificar que el usuario sea profesor
        if not hasattr(request.user, 'teacher_profile'):
            messages.error(request, 'Solo los profesores pueden generar contenido.')
            return redirect('dashboard:index')
        
        # Obtener el curso
        from apps.academic.models import Course
        course = get_object_or_404(Course, id=course_id)
        
        # Obtener el tipo de contenido por defecto (Material didáctico)
        content_type = get_object_or_404(ContentType, id=4)  # Material didáctico
        
        # Crear la solicitud de contenido
        content_request = ContentRequest.objects.create(
            teacher=request.user,
            course=course,
            content_type=content_type,
            topic=topic,
            grade_level=grade_level,
            additional_instructions="Contenido generado automáticamente desde el generador de IA.",
            status='pending',
            for_class=for_class,
            related_topic_id=course_topic_id
        )
        
        # Iniciar la generación de contenido
        try:
            llm_service = OpenAIService()
            
            # Generar el prompt
            prompt = f"""
            Genera material didáctico completo sobre el tema "{topic}" para estudiantes de {grade_level}.
            
            El contenido debe incluir:
            1. Introducción al tema
            2. Conceptos principales con explicaciones claras
            3. Ejemplos prácticos y ejercicios
            4. Actividades interactivas
            5. Evaluación o preguntas de comprensión
            
            Formato el contenido de manera educativa y atractiva para estudiantes de {grade_level}.
            Usa un lenguaje apropiado para el nivel educativo.
            """
            
            # Generar contenido
            generated_text = llm_service.generate_content(prompt)
            
            if generated_text:
                # Crear el contenido generado
                content = GeneratedContent.objects.create(
                    request=content_request,
                    title=f"Material Didáctico: {topic}",
                    raw_content=generated_text,
                    formatted_content=improve_content_formatting(generated_text, request),
                    model_used=settings.OPENAI_MODEL,
                    tokens_used=len(generated_text.split())
                )
                
                # Actualizar estado de la solicitud
                content_request.status = 'completed'
                content_request.save()
                
                messages.success(request, f'Contenido generado exitosamente para el tema "{topic}".')
                return redirect('ai:content_detail', pk=content.id)
            else:
                content_request.status = 'failed'
                content_request.save()
                messages.error(request, 'No se pudo generar el contenido. Intenta nuevamente.')
                
        except Exception as e:
            logger.error(f"Error en generación automática: {str(e)}")
            content_request.status = 'failed'
            content_request.save()
            messages.error(request, f'Error al generar contenido: {str(e)}')
        
        return redirect('ai:generator')
        
    except Exception as e:
        logger.error(f"Error en auto_generate_content_view: {str(e)}")
        messages.error(request, f'Error en la generación automática: {str(e)}')
        return redirect('ai:generator')

@login_required
def regenerate_scorm_package(request, content_id):
    """
    Regenera un paquete SCORM existente con el contenido más actualizado incluyendo cabecera institucional.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
    
    try:
        # Obtener el contenido
        content = get_object_or_404(GeneratedContent, pk=content_id)
        logger.info(f"Regenerando paquete SCORM para contenido {content_id}")

        # Verificar permisos
        if content.request.teacher != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'No tiene permisos para regenerar este paquete SCORM'}, status=403)

        # Buscar paquete SCORM existente
        existing_package = SCORMPackage.objects.filter(generated_content=content).first()
        
        if not existing_package:
            return JsonResponse({'success': False, 'error': 'No existe un paquete SCORM para este contenido'}, status=404)

        # Eliminar el archivo anterior si existe
        if existing_package.package_file:
            try:
                old_file_path = os.path.join(settings.MEDIA_ROOT, str(existing_package.package_file))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    logger.info(f"Archivo SCORM anterior eliminado: {old_file_path}")
            except Exception as delete_error:
                logger.warning(f"No se pudo eliminar archivo anterior: {delete_error}")

        # Preparar metadatos
        metadata = {
            'title': content.title,
            'description': f"Contenido regenerado para {content.request.course.name}",
            'version': '1.0',
            'standard': 'scorm_2004_4th'
        }

        # Usar el contenido crudo que es el que contiene el contenido educativo real
        source_content = content.raw_content or content.formatted_content or ""
        
        logger.info(f"🔄 REGENERANDO SCORM - Content ID: {content.id}")
        logger.info(f"🔄 REGENERANDO SCORM - Source content length: {len(source_content)}")
        logger.info(f"🔄 REGENERANDO SCORM - Content preview: {source_content[:500]}...")
        
        if not source_content.strip():
            logger.error("⚠️ Contenido vacío para regenerar SCORM")
            return JsonResponse({
                'success': False, 
                'error': 'El contenido está vacío y no se puede regenerar un paquete SCORM'
            }, status=400)

        # Crear nuevo paquete SCORM
        try:
            from apps.scorm_packager.services.packager import SCORMPackager
            packager = SCORMPackager(source_content, metadata)
            package_path = packager.create_package()
            
            # Convertir a ruta relativa
            relative_path = os.path.relpath(package_path, settings.MEDIA_ROOT)
            
            # Actualizar el registro existente
            existing_package.package_file = relative_path
            existing_package.description = metadata['description']
            existing_package.save()
            
            logger.info(f"Paquete SCORM regenerado exitosamente: ID={existing_package.id}")

            return JsonResponse({
                'success': True,
                'message': 'Paquete SCORM regenerado exitosamente con cabecera institucional',
                'package_id': existing_package.id,
                'download_url': reverse('scorm_packager:download_scorm_package', args=[existing_package.id]),
                'view_url': reverse('scorm_packager:scorm_package_detail', args=[existing_package.id])
            })

        except Exception as e:
            logger.error(f"Error al regenerar paquete SCORM: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error al regenerar el paquete SCORM: {str(e)}'
            }, status=500)

    except Exception as e:
        logger.error(f"Error general al regenerar paquete SCORM: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)

def get_clean_educational_content(content):
    """
    Obtiene solo el contenido educativo, sin cabeceras institucionales
    Para uso en paquetes SCORM
    """
    import re
    from bs4 import BeautifulSoup
    
    # Usar el contenido más apropiado
    source_content = content.formatted_content or content.raw_content or ""
    
    if not source_content:
        return ""
    
    try:
        # Parsear el HTML con Beautiful Soup
        soup = BeautifulSoup(source_content, 'html.parser')
        
        # Remover elementos institucionales específicos
        institutional_selectors = [
            '.institutional-header',
            '.institution-header',
            '.header-institucional',
            '.encabezado-institucional',
            'header.institutional',
            'div.institutional',
            '[class*="institutional"]',
            '[class*="institution"]'
        ]
        
        for selector in institutional_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        # Remover elementos que contengan texto institucional
        institutional_texts = [
            'INSTITUCIÓN EDUCATIVA',
            'UNIDAD EDUCATIVA',
            'COLEGIO NACIONAL',
            'Fecha de generación',
            '🎓'
        ]
        
        for text in institutional_texts:
            # Buscar todos los elementos que contengan este texto
            elements = soup.find_all(text=re.compile(text, re.IGNORECASE))
            for element in elements:
                parent = element.parent
                if parent:
                    parent.decompose()
        
        # Remover imágenes de logos
        logo_imgs = soup.find_all('img', alt=re.compile(r'logo', re.IGNORECASE))
        for img in logo_imgs:
            img.decompose()
            
        # Remover scripts relacionados con fecha de generación
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'generation-date' in script.string:
                script.decompose()
        
        # Obtener solo el contenido del body si existe, o todo si no
        body = soup.find('body')
        if body:
            # Extraer contenido del body
            cleaned_html = str(body)
            # Remover las etiquetas <body> pero mantener el contenido
            cleaned_html = re.sub(r'^<body[^>]*>', '', cleaned_html)
            cleaned_html = re.sub(r'</body>$', '', cleaned_html)
        else:
            cleaned_html = str(soup)
        
        # Limpiar estilos CSS institucionales
        cleaned_html = re.sub(r'\.institutional[^{]*{[^}]*}', '', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
        cleaned_html = re.sub(r'\.institution[^{]*{[^}]*}', '', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios excesivos
        cleaned_html = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_html)
        cleaned_html = re.sub(r'^\s+', '', cleaned_html, flags=re.MULTILINE)
        
        # Si el contenido resultante está muy vacío, usar un método más simple
        if len(cleaned_html.strip()) < 100:
            # Método de respaldo: usar expresiones regulares más simples
            cleaned_content = source_content
            
            # Patrones para remover cabeceras institucionales
            patterns_to_remove = [
                r'<div[^>]*class="[^"]*institutional[^"]*"[^>]*>.*?</div>',
                r'<header[^>]*>.*?INSTITUCIÓN.*?</header>',
                r'<div[^>]*>.*?🎓.*?INSTITUCIÓN.*?</div>',
                r'<div[^>]*>.*?Fecha de generación.*?</div>',
                r'<img[^>]*alt="[^"]*logo[^"]*"[^>]*/?>'
            ]
            
            for pattern in patterns_to_remove:
                cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
            
            return cleaned_content.strip()
        
        return cleaned_html.strip()
        
    except Exception as e:
        # Si hay error en el parsing, usar método simple
        logger.warning(f"Error al limpiar contenido con BeautifulSoup: {e}")
        
        cleaned_content = source_content
        
        # Patrones básicos para remover cabeceras institucionales
        patterns_to_remove = [
            r'<div[^>]*class="[^"]*institutional[^"]*"[^>]*>.*?</div>',
            r'<header[^>]*>.*?INSTITUCIÓN.*?</header>',
            r'<div[^>]*>.*?🎓.*?INSTITUCIÓN.*?</div>',
            r'<div[^>]*>.*?Fecha de generación.*?</div>',
            r'<img[^>]*alt="[^"]*logo[^"]*"[^>]*/?>'
        ]
        
        for pattern in patterns_to_remove:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned_content.strip()


