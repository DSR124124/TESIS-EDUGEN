from django.views.generic import ListView, DetailView, UpdateView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.db import transaction
import logging
import os
from django.contrib.auth.models import User

from .models import StudentPortfolio, PortfolioTopic, PortfolioMaterial
from .utils import (
    safe_prepare_topic_for_template, 
    safe_process_topics_list, 
    TopicMaterialsManager,
    get_unified_topic_context,
    make_topic_safe
)
from .decorators import AutoSafeTopicMixin, safe_topic_operation
from apps.academic.models import Course, Section, Student, CourseAssignment, Enrollment, CourseTopic, CourseMaterial
from .signals import manually_sync_student_with_section

logger = logging.getLogger(__name__)

class TeacherPortfolioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar los portafolios de los estudiantes asignados a un profesor"""
    model = StudentPortfolio
    template_name = 'portfolios/teacher/portfolio_list.html'
    context_object_name = 'portfolios'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        current_month = int(self.request.GET.get('month', datetime.now().month))
        current_year = int(self.request.GET.get('year', datetime.now().year))
        course_id = self.request.GET.get('course_id')
        section_id = self.request.GET.get('section_id')
        student_query = self.request.GET.get('student_query')
        
        # Filtros base para las secciones
        sections_filter = Q(course_assignments__teacher=teacher)
        
        if course_id:
            sections_filter &= Q(course_assignments__course_id=course_id)
            
        if section_id:
            sections_filter = Q(id=section_id) & Q(course_assignments__teacher=teacher)
        
        sections = Section.objects.filter(sections_filter).distinct()
        students_filter = Q(enrollments__section__in=sections)
        
        if student_query:
            students_filter &= (
                Q(user__first_name__icontains=student_query) | 
                Q(user__last_name__icontains=student_query) | 
                Q(dni__icontains=student_query)
            )
        
        students = Student.objects.filter(students_filter).distinct()
        
        # Crear los portafolios si no existen
        for student in students:
            StudentPortfolio.objects.get_or_create(
                student=student,
                month=current_month,
                academic_year=str(current_year),
            )
        
        return StudentPortfolio.objects.filter(
            student__in=students,
            month=current_month,
            academic_year=str(current_year)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        current_month = int(self.request.GET.get('month', datetime.now().month))
        current_year = int(self.request.GET.get('year', datetime.now().year))
        
        context['month_name'] = dict(StudentPortfolio.MONTH_CHOICES)[current_month]
        context['year'] = current_year
        context['months'] = StudentPortfolio.MONTH_CHOICES
        context['courses'] = Course.objects.filter(course_assignments__teacher=teacher).distinct()
        context['sections'] = Section.objects.filter(course_assignments__teacher=teacher).distinct()
        
        return context

class TeacherPortfolioDetailView(LoginRequiredMixin, UserPassesTestMixin, AutoSafeTopicMixin, DetailView):
    """Vista para ver el detalle de un portafolio de estudiante"""
    model = StudentPortfolio
    template_name = 'portfolios/teacher/portfolio_detail.html'
    context_object_name = 'portfolio'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        student = self.object.student
        
        # Obtener los cursos que el profesor imparte a este estudiante
        teacher_courses = Course.objects.filter(
            course_assignments__teacher=teacher,
            course_assignments__section__enrollments__student=student
        ).distinct()
        
        # Guardar todos los cursos del profesor para este estudiante
        context['available_courses'] = teacher_courses
        context['teacher_courses_count'] = teacher_courses.count()
        
        # Obtener secciones donde está matriculado el estudiante con este profesor
        student_sections = Section.objects.filter(
            enrollments__student=student,
            course_assignments__teacher=teacher
        ).distinct()
        context['student_sections'] = student_sections
        
        # Obtener los temas creados por el profesor para este portafolio
        portfolio_topics = self.object.portfolio_topics.filter(teacher=teacher)
        
        # Obtener los temas de curso (CourseTopic) para las secciones del estudiante
        course_topics = CourseTopic.objects.filter(
            teacher=teacher,
            section__enrollments__student=student,
            section__enrollments__status='ACTIVE',
            is_active=True
        ).distinct()
        
        # Filtrar CourseTopics que ya tienen PortfolioTopics correspondientes
        # para evitar duplicados en la visualización
        portfolio_topic_keys = set()
        for pt in portfolio_topics:
            key = (pt.course.id, pt.title)
            portfolio_topic_keys.add(key)
        
        # Solo incluir CourseTopics que NO tienen un PortfolioTopic correspondiente
        filtered_course_topics = []
        for ct in course_topics:
            key = (ct.course.id, ct.title)
            if key not in portfolio_topic_keys:
                filtered_course_topics.append(ct)
        
        # Combinar ambos tipos de temas (sin duplicados)
        all_topics = list(portfolio_topics) + filtered_course_topics
        
        # Calculate topic completion percentages using safe utilities
        topics_with_percentages = []
        for topic in all_topics:
            # Usar utilidades seguras para preparar el tema
            safe_topic = safe_prepare_topic_for_template(topic)
            
            # Calcular porcentaje de completitud basado en materiales
            total_materials = safe_topic.materials_count
            
            if total_materials > 0:
                completed_materials = total_materials  
                percentage = 100  
            else:
                percentage = 0
            
            safe_topic.completion_percentage = percentage
            topics_with_percentages.append(safe_topic)
        
        context['topics'] = topics_with_percentages
        
        # Obtener temas agrupados por curso para la interfaz
        topics_by_course = {}
        
        # Primero, inicializar todos los cursos del profesor para este estudiante
        for course in teacher_courses:
            topics_by_course[course.id] = {
                'course_name': course.name,
                'topics': [],
                'complete_count': 0,
                'complete_percentage': 0
            }
        
        # Luego, agregar los temas existentes a sus respectivos cursos
        for topic in topics_with_percentages:
            course_id = topic.course.id
            # Solo agregar si el curso está en la lista del profesor para este estudiante
            if course_id in topics_by_course:
                # Agregar el tema a la lista de temas del curso
                topics_by_course[course_id]['topics'].append(topic)
                
                # Incrementar el contador de temas completados si corresponde
                if topic.is_complete:
                    topics_by_course[course_id]['complete_count'] += 1
        
        # Calcular porcentajes de completitud por curso
        for course_id, course_data in topics_by_course.items():
            total_topics = len(course_data['topics'])
            complete_count = course_data['complete_count']
            
            if total_topics > 0:
                course_data['complete_percentage'] = int((complete_count / total_topics) * 100)
        
        context['topics_by_course'] = topics_by_course
        
        # Contar materiales totales
        total_materials = 0
        materials_by_type = {}
        
        for topic in topics_with_percentages:
            # Solo contar materiales para PortfolioTopic, no para CourseTopic
            if topic.topic_type == 'portfolio':
                topic_materials = topic.materials.all()
                total_materials += topic_materials.count()
                
                # Contar por tipo de material
                for material in topic_materials:
                    material_type = material.get_material_type_display()
                    if material_type not in materials_by_type:
                        materials_by_type[material_type] = 0
                    materials_by_type[material_type] += 1
        
        context['total_materials'] = total_materials
        context['materials_by_type'] = materials_by_type
        
        # Calcular porcentaje de completitud
        completed_topics = len([t for t in topics_with_percentages if t.is_complete])
        topic_count = len(topics_with_percentages)
        
        completion_percentage = 0
        if topic_count > 0:
            completion_percentage = int((completed_topics / topic_count) * 100)
        
        context['completion_percentage'] = completion_percentage
        context['completed_topics'] = completed_topics
        context['total_topics'] = topic_count
        context['pending_topics'] = topic_count - completed_topics
        
        # Datos del estudiante y periodo académico
        context['student_name'] = f"{student.user.first_name} {student.user.last_name}"
        context['student_dni'] = student.dni
        context['portfolio_month'] = self.object.get_month_display()
        context['portfolio_year'] = self.object.academic_year
        
        # Fecha de la última actualización
        context['last_updated'] = timezone.now().strftime("%d/%m/%Y %H:%M")
        
        return context

class TopicDetailView(LoginRequiredMixin, UserPassesTestMixin, AutoSafeTopicMixin, DetailView):
    """Vista para ver el detalle de un tema (PortfolioTopic o CourseTopic)"""
    template_name = 'portfolios/teacher/topic_detail.html'
    context_object_name = 'topic'
    
    def get_object(self, queryset=None):
        """Obtener el objeto, puede ser PortfolioTopic o CourseTopic"""
        topic_id = self.kwargs['pk']
        teacher = self.request.user.teacher_profile
        
        # Primero intentar obtener como PortfolioTopic
        try:
            topic = PortfolioTopic.objects.get(id=topic_id, teacher=teacher)
            return safe_prepare_topic_for_template(topic)
        except PortfolioTopic.DoesNotExist:
            pass
        
        # Si no es PortfolioTopic, intentar como CourseTopic
        try:
            topic = CourseTopic.objects.get(id=topic_id, teacher=teacher)
            return safe_prepare_topic_for_template(topic)
        except CourseTopic.DoesNotExist:
            pass
        
        # Si no se encuentra ninguno, lanzar 404
        from django.http import Http404
        raise Http404("No se encontró ningún tema con ese ID")
    
    def test_func(self):
        try:
            # Verificar que el usuario sea profesor y el tema le pertenezca
            return hasattr(self.request.user, 'teacher_profile')
        except:
            return False
    
    def get(self, request, *args, **kwargs):
        # Verificar si se solicitó arreglar el campo ai_generated
        if 'fix_ai_generated' in request.GET:
            try:
                # Obtener el tema actual
                topic = self.get_object()
                
                # Actualizar todos los materiales que no tienen el campo ai_generated establecido
                from django.db import connection
                with connection.cursor() as cursor:
                    # Verificar si la columna existe
                    cursor.execute("PRAGMA table_info(portfolios_portfoliomaterial)")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if 'ai_generated' in columns:
                        # Actualizar todos los materiales del tema a ai_generated=False por defecto
                        cursor.execute(
                            "UPDATE portfolios_portfoliomaterial SET ai_generated = 0 WHERE topic_id = %s AND ai_generated IS NULL",
                            [topic.id]
                        )
                        messages.success(request, "Se han actualizado los materiales correctamente.")
                    else:
                        messages.error(request, "La columna ai_generated no existe en la tabla.")
            except Exception as e:
                messages.error(request, f"Error al actualizar los materiales: {str(e)}")
                
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.object
        
        # Verificar si es un CourseTopic (no tiene portafolio individual)
        if getattr(topic, 'topic_type', None) == 'course':
            # Para CourseTopic, obtener TODOS los estudiantes de la sección y crear sus PortfolioTopic
            try:
                # Obtener todos los estudiantes activos de la sección
                student_enrollments = Enrollment.objects.filter(
                    section=topic.section,
                    status='ACTIVE'
                ).select_related('student__user', 'student__grade').order_by('student__user__last_name', 'student__user__first_name')
                
                # Para cada estudiante, crear o obtener su PortfolioTopic correspondiente
                students_with_topics = []
                
                for enrollment in student_enrollments:
                    student = enrollment.student
                    
                    # Buscar o crear el portfolio del estudiante para este curso
                    portfolio, created = StudentPortfolio.objects.get_or_create(
                        student=student,
                        course=topic.course,
                        teacher=topic.teacher,
                        defaults={
                            'title': f"Portafolio de {topic.course.name}",
                            'is_active': True
                        }
                    )
                    
                    # Buscar o crear el PortfolioTopic correspondiente al CourseTopic
                    portfolio_topic, topic_created = PortfolioTopic.objects.get_or_create(
                        portfolio=portfolio,
                        course=topic.course,
                        teacher=topic.teacher,
                        title=topic.title,
                        defaults={
                            'description': topic.description or f"Tema: {topic.title}"
                        }
                    )
                    
                    students_with_topics.append({
                        'student': student,
                        'portfolio': portfolio,
                        'portfolio_topic': portfolio_topic,
                        'enrollment': enrollment
                    })
                
                context['students_with_topics'] = students_with_topics
                context['total_students'] = len(students_with_topics)
                
            except Exception as e:
                logger.error(f"Error obteniendo estudiantes para CourseTopic {topic.id}: {e}")
                context['students_with_topics'] = []
                context['total_students'] = 0
            
            # Para CourseTopic, obtener materiales de clase de los PortfolioTopic asociados
            class_materials = []
            
            try:
                # Obtener todos los PortfolioTopic que corresponden a este CourseTopic
                # Estos se crean automáticamente cuando se suben materiales
                related_portfolio_topics = PortfolioTopic.objects.filter(
                    course=topic.course,
                    teacher=topic.teacher,
                    title=topic.title
                )
                
                # Obtener todos los materiales de clase de estos PortfolioTopic
                # Usar un conjunto para evitar duplicados basado en título y tipo
                materials_set = set()
                materials_list = []
                
                for portfolio_topic in related_portfolio_topics:
                    topic_materials = portfolio_topic.materials.filter(is_class_material=True)
                    for material in topic_materials:
                        # Crear un identificador único basado en título y tipo
                        material_key = (material.title, material.material_type)
                        if material_key not in materials_set:
                            materials_set.add(material_key)
                            # Marcar como material de clase y agregar información del topic
                            material.is_class_material = True
                            material.ai_generated = getattr(material, 'ai_generated', False)
                            material.source_portfolio_topic = portfolio_topic
                            
                            # Establecer atributos SCORM
                            material.is_scorm_package = (material.material_type == 'SCORM' or 
                                                       getattr(material, 'scorm_package', None) is not None)
                            if hasattr(material, 'scorm_package') and material.scorm_package:
                                material.scorm_id = material.scorm_package.id
                                material.scorm_version = material.scorm_package.version
                                material.scorm_standard = material.scorm_package.standard
                                material.created_by = material.scorm_package.created_by
                                material.is_published = material.scorm_package.is_published
                            elif getattr(material, 'material_type', None) == 'SCORM':
                                # Material marcado como SCORM pero sin paquete
                                material.scorm_id = None
                                material.scorm_version = None
                                material.scorm_standard = None
                                material.is_published = False
                                
                            materials_list.append(material)
                
                class_materials = materials_list
                
            except Exception as e:
                # En caso de error, no mostrar materiales
                pass
            
            # Para CourseTopic no hay materiales individuales en la vista general
            portfolio_materials = []
            portfolio_regular_materials = []
            portfolio_ai_materials = []
            
            # Todos los materiales son de clase
            all_class_materials = list(class_materials)
            all_materials = all_class_materials
            
            # Contadores
            context['regular_materials_count'] = len(all_class_materials)
            context['ai_materials_count'] = 0
            context['class_materials_count'] = len(class_materials)
            context['portfolio_materials_count'] = 0
            
            # Enviar materiales al template
            context['materials'] = all_materials
            context['class_materials'] = class_materials
            context['portfolio_ai_materials'] = []
            
            return context
        
        # Para PortfolioTopic, usar la lógica original
        # 1. Obtener materiales individuales del portafolio (del PortfolioTopic)
        portfolio_materials = topic.materials.all()
        
        # 2. Obtener materiales de clase (de CourseMaterial del curso y sección)
        # Los materiales de clase son los que el profesor sube para todo el curso/sección
        class_materials = []
        
        try:
            # Obtener la sección del estudiante para este curso
            student_enrollment = topic.portfolio.student.enrollments.filter(
                section__course_assignments__course=topic.course,
                status='ACTIVE'
            ).first()
            
            if student_enrollment:
                # Obtener materiales del curso que están activos
                class_materials = CourseMaterial.objects.filter(
                    course=topic.course,
                    is_active=True,
                    created_by=topic.teacher.user  # Solo materiales creados por el profesor del tema
                ).order_by('-created_at')
        except Exception as e:
            # En caso de error, solo mostrar materiales del portafolio
            pass
        
        # 3. ELIMINADO: Ya no buscar materiales de otros temas
        # Se ha eliminado la lógica que causaba que aparecieran materiales incorrectos
        
        # 4. Clasificar materiales del portafolio (SOLO del tema actual)
        portfolio_regular_materials = []
        portfolio_personal_materials = []
        portfolio_ai_materials = []
        portfolio_ai_class_materials = []  # Nueva categoría para material AI de clase
        
        # CORREGIDO: Solo usar materiales del tema actual, NO de otros temas
        all_portfolio_materials = list(portfolio_materials)  # SOLO materiales del tema actual
        
        for material in all_portfolio_materials:
            # Ya no hay materiales de otros temas, por lo que no es necesario marcarlos
            material.is_from_other_topic = False
            
            # Establecer atributos SCORM para materiales del portafolio
            material.is_scorm_package = (material.material_type == 'SCORM' or 
                                       getattr(material, 'scorm_package', None) is not None)
            if hasattr(material, 'scorm_package') and material.scorm_package:
                material.scorm_id = material.scorm_package.id
                material.scorm_version = material.scorm_package.version
                material.scorm_standard = material.scorm_package.standard
                material.created_by = material.scorm_package.created_by
                material.is_published = material.scorm_package.is_published
            elif material.material_type == 'SCORM':
                # Material marcado como SCORM pero sin paquete
                material.scorm_id = None
                material.scorm_version = None
                material.scorm_standard = None
                material.is_published = False
            
            # CORREGIDA: Lógica de clasificación de materiales
            ai_generated = getattr(material, 'ai_generated', False)
            is_class_material = getattr(material, 'is_class_material', True)  # Por defecto True
            
            if ai_generated:
                # Material generado por IA
                if is_class_material:
                    # Material AI de clase - debe aparecer en la sección de clase
                    portfolio_ai_class_materials.append(material)
                else:
                    # Material AI personalizado - aparece en personalizado
                    portfolio_ai_materials.append(material)
            elif is_class_material:
                # Material de clase regular (no AI)
                portfolio_regular_materials.append(material)
            else:
                # Material personalizado (no IA, no clase)
                portfolio_personal_materials.append(material)
        
        # 5. Procesar materiales de clase externos (CourseTopic)
        # NO sobrescribir ai_generated para materiales que ya lo tienen
        for material in class_materials:
            material.is_class_material = True
            # NO forzar ai_generated = False si ya es True
            
            # Establecer atributos SCORM para materiales de clase
            material.is_scorm_package = (material.material_type == 'SCORM' or 
                                       getattr(material, 'scorm_package', None) is not None)
            if hasattr(material, 'scorm_package') and material.scorm_package:
                material.scorm_id = material.scorm_package.id
                material.scorm_version = material.scorm_package.version
                material.scorm_standard = material.scorm_package.standard
                material.created_by = material.scorm_package.created_by
                material.is_published = material.scorm_package.is_published
            elif getattr(material, 'material_type', None) == 'SCORM':
                # Material marcado como SCORM pero sin paquete
                material.scorm_id = None
                material.scorm_version = None
                material.scorm_standard = None
                material.is_published = False
        
        # 6. Combinar materiales de clase (externos + AI de clase + regulares)
        all_class_materials = list(class_materials) + portfolio_ai_class_materials + portfolio_regular_materials
        
        # 7. Combinar materiales personalizados (solo personalizados + AI personalizado)
        all_personal_materials = portfolio_personal_materials + portfolio_ai_materials
        
        # 8. Combinar todos los materiales para el template
        all_materials = all_class_materials + all_personal_materials
        
        # 9. Añadir contadores al contexto
        context['regular_materials_count'] = len(all_class_materials)  # Total materiales de clase
        context['ai_materials_count'] = len(portfolio_ai_materials)  # Solo AI personalizado
        context['ai_class_materials_count'] = len(portfolio_ai_class_materials)  # AI de clase
        context['personal_materials_count'] = len(portfolio_personal_materials)  # Solo personalizado no-AI
        context['class_materials_count'] = len(class_materials)  # Solo externos
        context['portfolio_materials_count'] = len(portfolio_regular_materials)  # Solo regulares del portfolio
        
        # 10. Enviar todos los materiales al template con la nueva lógica
        context['materials'] = all_materials
        context['class_materials'] = all_class_materials  # Incluye AI de clase + externos + regulares
        context['portfolio_ai_materials'] = all_personal_materials  # Solo personalizados + AI personalizado
        
        return context

class TopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para actualizar un tema de portafolio"""
    model = PortfolioTopic
    template_name = 'portfolios/teacher/topic_form.html'
    fields = ['title', 'description']
    
    def test_func(self):
        return (
            hasattr(self.request.user, 'teacher_profile') and
            self.get_object().teacher == self.request.user.teacher_profile
        )
    
    def form_valid(self, form):
        form.instance.last_updated_by = self.request.user
        
        # Guardar la actualización
        response = super().form_valid(form)
        
        # Si es una solicitud AJAX, devolver una respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Tema actualizado exitosamente.',
                'topic_id': self.object.id,
                'topic_title': self.object.title,
            })
        
        # Si no es AJAX, usar la respuesta normal
        messages.success(self.request, 'Tema actualizado exitosamente.')
        return response
    
    def form_invalid(self, form):
        # Si es una solicitud AJAX, devolver errores como JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
                
            return JsonResponse({
                'success': False,
                'message': 'Por favor corrija los errores en el formulario.',
                'errors': errors
            }, status=400)
        
        # Si no es AJAX, devolver la respuesta normal
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio'] = self.object.portfolio
        context['portfolio_id'] = self.object.portfolio.id
        return context
    
    def get_success_url(self):
        portfolio_id = self.object.portfolio.id
        return reverse('portfolios:topic_detail', kwargs={'pk': self.object.pk})

def delete_portfolio_topic(request, topic_id):
    """Vista para eliminar un tema del portafolio"""
    topic = get_object_or_404(PortfolioTopic, id=topic_id)
    portfolio = topic.portfolio
    
    # Verificar que el profesor tenga permiso para este tema
    if topic.teacher != request.user.teacher_profile:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para eliminar este tema.'
            }, status=403)
        
        messages.error(request, 'No tienes permiso para eliminar este tema.')
        return redirect('portfolios:teacher_portfolio_list')
    
    # Datos del tema antes de eliminarlo
    topic_title = topic.title
    topic_id = topic.id
    
    # Eliminar el tema
    topic.delete()
    
    # Respuesta para solicitudes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Tema "{topic_title}" eliminado exitosamente.',
            'topic_id': topic_id
        })
    
    # Respuesta para solicitudes normales
    messages.success(request, 'Tema eliminado exitosamente.')
    return redirect('portfolios:teacher_portfolio_detail', pk=portfolio.id)

@safe_topic_operation
def add_portfolio_material(request, topic_id):
    """Vista para agregar material didáctico a un tema específico (PortfolioTopic o CourseTopic)"""
    if request.method == 'POST':
        # Verificar si viene con parámetro type=class
        force_course_behavior = request.GET.get('type') == 'class'
        
        # Intentar obtener el tema como PortfolioTopic o CourseTopic
        topic = None
        course_topic = None
        is_course_topic = False
        
        try:
            from apps.academic.models import CourseTopic
            course_topic = CourseTopic.objects.get(id=topic_id)
            teacher = course_topic.teacher
            is_course_topic = True
        except CourseTopic.DoesNotExist:
            try:
                topic = PortfolioTopic.objects.get(id=topic_id)
                teacher = topic.teacher
                # Si force_course_behavior está activo, tratar como CourseTopic
                if force_course_behavior:
                    is_course_topic = True
                    # Buscar o crear el CourseTopic correspondiente
                    course_topic, _ = CourseTopic.objects.get_or_create(
                        section=topic.portfolio.student.get_current_section(),
                        course=topic.course,
                        teacher=topic.teacher,
                        title=topic.title,
                        defaults={'description': topic.description}
                    )
            except PortfolioTopic.DoesNotExist:
                messages.error(request, 'El tema especificado no existe.')
                return redirect('portfolios:teacher_portfolio_list')
        
        # Verificar permisos
        if teacher != request.user.teacher_profile:
            messages.error(request, 'No tienes permiso para agregar materiales a este tema.')
            return redirect('portfolios:teacher_portfolio_list')
        
        title = request.POST.get('title')
        description = request.POST.get('description')
        material_type = request.POST.get('material_type')
        file = request.FILES.get('file')
        is_class_material = request.POST.get('is_class_material') == 'on' or is_course_topic
        
        if title and material_type and file:
            try:
                # Crear el material principal
                material = PortfolioMaterial.objects.create(
                    topic=topic if not is_course_topic else None,
                    course_topic=course_topic if is_course_topic else None,
                    title=title,
                    description=description,
                    material_type=material_type,
                    file=file,
                    ai_generated=False,
                    is_class_material=is_class_material
                )
                
                # Si es un CourseTopic, distribuir automáticamente a todos los estudiantes
                if is_course_topic and course_topic:
                    from apps.academic.models import Student
                    from django.core.files.base import ContentFile
                    
                    try:
                        # Obtener todos los estudiantes activos de la sección
                        students = Student.objects.filter(
                            enrollments__section=course_topic.section,
                            enrollments__status='ACTIVE'
                        ).distinct()
                        
                        if students.count() == 0:
                            messages.success(request, 'Material subido exitosamente, pero no hay estudiantes activos en esta sección.')
                        else:
                            # Leer el contenido del archivo para replicarlo
                            file.seek(0)
                            file_content = file.read()
                            file.seek(0)
                            
                            # Distribuir a cada estudiante
                            created_count = 0
                            for student in students:
                                # Obtener o crear el portafolio del estudiante
                                portfolio, _ = StudentPortfolio.objects.get_or_create(
                                    student=student,
                                    month=timezone.now().month,
                                    academic_year=str(timezone.now().year)
                                )
                                
                                # Obtener o crear el tema del portafolio
                                portfolio_topic, _ = PortfolioTopic.objects.get_or_create(
                                    portfolio=portfolio,
                                    course=course_topic.course,
                                    teacher=course_topic.teacher,
                                    title=course_topic.title,
                                    defaults={'description': course_topic.description}
                                )
                                
                                # Verificar si el material ya existe para este estudiante
                                existing_material = PortfolioMaterial.objects.filter(
                                    topic=portfolio_topic,
                                    course_topic=course_topic,
                                    title=title,
                                    material_type=material_type,
                                    created_at__date=timezone.now().date()
                                ).exists()
                                
                                if not existing_material:
                                    # Crear una copia del archivo para el estudiante
                                    new_file = ContentFile(file_content)
                                    new_file.name = file.name
                                    
                                    PortfolioMaterial.objects.create(
                                        topic=portfolio_topic,
                                        course_topic=course_topic,
                                        title=title,
                                        description=description,
                                        material_type=material_type,
                                        file=new_file,
                                        ai_generated=False,
                                        is_class_material=True
                                    )
                                    created_count += 1
                            
                            messages.success(request, f'Material subido exitosamente y distribuido a {created_count} estudiantes.')
                            
                    except Exception as e:
                        logger.error(f"Error al distribuir material: {str(e)}")
                        messages.success(request, 'Material subido exitosamente, pero hubo problemas al distribuir a algunos estudiantes.')
                else:
                    messages.success(request, 'Material subido exitosamente.')
                
                # Redireccionar según el tipo de tema
                if is_course_topic:
                    return redirect('dashboard:course_topic_detail', pk=course_topic.id)
                else:
                    return redirect('portfolios:topic_detail', pk=topic.id)
                    
            except Exception as e:
                messages.error(request, f'Error al crear el material: {str(e)}')
        else:
            messages.error(request, 'Por favor complete todos los campos requeridos: título, tipo de material y archivo.')
    
    return redirect('portfolios:add_material_form', topic_id=topic_id)

@safe_topic_operation
def add_material_form(request, topic_id):
    """Vista para mostrar un formulario dedicado para agregar material a un tema (PortfolioTopic o CourseTopic)"""
    # Intentar obtener el tema como PortfolioTopic o CourseTopic
    topic = None
    is_course_topic = False
    
    # Obtener el tipo de material desde el parámetro GET
    material_type_param = request.GET.get('type', 'class')  # 'class' o 'personal'
    
    try:
        topic = PortfolioTopic.objects.get(id=topic_id)
        teacher = topic.teacher
        # Si el parámetro type=class está presente, tratarlo como CourseTopic
        if material_type_param == 'class':
            is_course_topic = True
    except PortfolioTopic.DoesNotExist:
        try:
            topic = CourseTopic.objects.get(id=topic_id)
            teacher = topic.teacher
            is_course_topic = True
        except CourseTopic.DoesNotExist:
            messages.error(request, 'El tema especificado no existe.')
            return redirect('portfolios:teacher_portfolio_list')
    
    # Verificar permisos
    if teacher != request.user.teacher_profile:
        messages.error(request, 'No tienes permiso para agregar materiales a este tema.')
        return redirect('portfolios:teacher_portfolio_list')
    
    # Para CourseTopic, solo permitir material de clase
    if is_course_topic:
        material_type_param = 'class'
    
    context = {
        'topic': topic,
        'is_course_topic': is_course_topic,
        'material_type_param': material_type_param,
        'material_types': [
            ('EJERCICIO', 'Ejercicio'),
            ('TAREA', 'Tarea'),
            ('EXAMEN', 'Examen'),
            ('PROYECTO', 'Proyecto'),
            ('LECTURA', 'Lectura'),
            ('OTRO', 'Otro')
        ]
    }
    
    return render(request, 'portfolios/teacher/add_material.html', context)

def delete_portfolio_material(request, material_id):
    """Vista para eliminar un material didáctico de un tema del portafolio"""
    material = get_object_or_404(PortfolioMaterial, id=material_id)
    
    # Verificar permisos según el tipo de material
    if material.topic:
        # Material de PortfolioTopic
        if material.topic.teacher != request.user.teacher_profile:
            messages.error(request, 'No tienes permiso para eliminar este material.')
            return redirect('dashboard:teacher_portfolios')
        default_redirect_pk = material.topic.id
        default_redirect_view = 'portfolios:topic_detail'
    elif material.course_topic:
        # Material de CourseTopic
        if material.course_topic.teacher != request.user.teacher_profile:
            messages.error(request, 'No tienes permiso para eliminar este material.')
            return redirect('dashboard:teacher_course_topics')
        default_redirect_pk = material.course_topic.id
        default_redirect_view = 'dashboard:course_topic_detail'
    else:
        messages.error(request, 'Material no asociado a ningún tema válido.')
        return redirect('dashboard:teacher_portfolios')
    
    # Obtener URL de redirección del POST data si existe
    redirect_url = request.POST.get('redirect_url')
    
    # Guardar información antes de eliminar
    material_title = material.title
    material_is_class_material = getattr(material, 'is_class_material', False)
    course_topic = material.course_topic
    
    # Si es un material de clase asociado a un CourseTopic, eliminar también las copias en portafolios
    deleted_copies_count = 0
    if course_topic and material_is_class_material:
        try:
            # Buscar y eliminar todas las copias del material en los portafolios de estudiantes
            # Esto incluye:
            # 1. Materiales con el mismo course_topic, título y que son material de clase
            # 2. Materiales que están en portafolios de estudiantes (topic__isnull=False)
            # 3. También buscar por material_type y fecha cercana para mayor precisión
            
            # Filtro principal: mismo course_topic, título y es material de clase
            portfolio_copies = PortfolioMaterial.objects.filter(
                course_topic=course_topic,
                title=material_title,
                is_class_material=True,
                topic__isnull=False  # Solo materiales que están en portafolios de estudiantes
            ).exclude(id=material_id)  # Excluir el material principal que se va a eliminar
            
            # Filtro adicional: si el material tiene un tipo específico, filtrar por eso también
            if hasattr(material, 'material_type') and material.material_type:
                portfolio_copies = portfolio_copies.filter(material_type=material.material_type)
            
            deleted_copies_count = portfolio_copies.count()
            
            if deleted_copies_count > 0:
                # Log de los portafolios afectados para debugging
                affected_students = []
                for copy in portfolio_copies:
                    if copy.topic and copy.topic.portfolio:
                        student_name = copy.topic.portfolio.student.user.get_full_name()
                        affected_students.append(student_name)
                
                portfolio_copies.delete()
                
                logger.info(f"Eliminadas {deleted_copies_count} copias del material '{material_title}' de portafolios de estudiantes: {', '.join(affected_students[:5])}")
                if len(affected_students) > 5:
                    logger.info(f"... y {len(affected_students) - 5} estudiantes más")
            else:
                logger.info(f"No se encontraron copias del material '{material_title}' en portafolios de estudiantes")
            
        except Exception as e:
            logger.error(f"Error al eliminar copias del material en portafolios: {str(e)}")
            # Continuar con la eliminación del material principal aunque haya fallado la eliminación de copias
    
    # Eliminar el material principal
    material.delete()
    
    # Mensaje de éxito personalizado
    if deleted_copies_count > 0:
        messages.success(request, f'Material "{material_title}" eliminado exitosamente del tema y de {deleted_copies_count} portafolios de estudiantes.')
    else:
        messages.success(request, f'Material "{material_title}" eliminado exitosamente.')
    
    # Redirigir a la URL especificada o por defecto al detalle del tema
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect(default_redirect_view, pk=default_redirect_pk)

class StudentPortfolioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para que los estudiantes vean sus portafolios"""
    model = StudentPortfolio
    template_name = 'portfolios/student/portfolio_list.html'
    context_object_name = 'portfolios'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def get_queryset(self):
        return StudentPortfolio.objects.filter(student=self.request.user.student_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['months'] = StudentPortfolio.MONTH_CHOICES
        return context

class StudentPortfolioDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para que los estudiantes vean el detalle de su portafolio"""
    model = StudentPortfolio
    template_name = 'portfolios/student/portfolio_detail.html'
    context_object_name = 'portfolio'
    
    def test_func(self):
        return (
            hasattr(self.request.user, 'student_profile') and
            self.get_object().student == self.request.user.student_profile
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verificar si se está filtrando por curso específico
        course_id = self.kwargs.get('course_id')
        
        if course_id:
            # Filtrar solo los temas del curso específico
            topics = self.object.portfolio_topics.filter(course_id=course_id).order_by('created_at')
            
            # Obtener información del curso para mostrar en el header
            from apps.academic.models import Course
            try:
                course = Course.objects.get(id=course_id)
                context['filtered_course'] = course
                context['is_filtered_by_course'] = True
            except Course.DoesNotExist:
                context['filtered_course'] = None
                context['is_filtered_by_course'] = False
        else:
            # Mostrar todos los temas (comportamiento original)
            topics = self.object.portfolio_topics.all().order_by('course__name')
            context['filtered_course'] = None
            context['is_filtered_by_course'] = False
        
        context['topics'] = topics
        return context

class StudentTopicDetailView(LoginRequiredMixin, UserPassesTestMixin, AutoSafeTopicMixin, DetailView):
    """Vista para que los estudiantes vean el detalle de un tema"""
    model = PortfolioTopic
    template_name = 'portfolios/student/topic_detail.html'
    context_object_name = 'topic'
    
    def test_func(self):
        return (
            hasattr(self.request.user, 'student_profile') and
            self.get_object().portfolio.student == self.request.user.student_profile
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.object
        
        # Para PortfolioTopic, usar la lógica original
        # 1. Obtener materiales individuales del portafolio (del PortfolioTopic)
        portfolio_materials = topic.materials.all()
        
        # 2. Obtener materiales de clase (de CourseMaterial del curso y sección)
        # Los materiales de clase son los que el profesor sube para todo el curso/sección
        class_materials = []
        
        try:
            # Obtener la sección del estudiante para este curso
            student_enrollment = topic.portfolio.student.enrollments.filter(
                section__course_assignments__course=topic.course,
                status='ACTIVE'
            ).first()
            
            if student_enrollment:
                # Obtener materiales del curso que están activos
                class_materials = CourseMaterial.objects.filter(
                    course=topic.course,
                    is_active=True,
                    created_by=topic.teacher.user  # Solo materiales creados por el profesor del tema
                ).order_by('-created_at')
        except Exception as e:
            # En caso de error, solo mostrar materiales del portafolio
            pass
        
        # 3. ELIMINADO: Ya no buscar materiales de otros temas
        # Se ha eliminado la lógica que causaba que aparecieran materiales incorrectos
        
        # 4. Clasificar materiales del portafolio (SOLO del tema actual)
        portfolio_class_materials = []     # Materiales de clase (regulares)
        portfolio_personal_materials = []  # Materiales personalizados
        portfolio_ai_class_materials = []  # Materiales AI de clase
        portfolio_ai_personal_materials = []  # Materiales AI personalizados
        
        # CORREGIDO: Solo usar materiales del tema actual, NO de otros temas
        all_portfolio_materials = list(portfolio_materials)  # SOLO materiales del tema actual
        
        for material in all_portfolio_materials:
            # Ya no hay materiales de otros temas, por lo que no es necesario marcarlos
            material.is_from_other_topic = False
            
            # Establecer atributos SCORM para materiales del portafolio
            material.is_scorm_package = (material.material_type == 'SCORM' or 
                                       getattr(material, 'scorm_package', None) is not None)
            if hasattr(material, 'scorm_package') and material.scorm_package:
                material.scorm_id = material.scorm_package.id
                material.scorm_version = material.scorm_package.version
                material.scorm_standard = material.scorm_package.standard
                material.created_by = material.scorm_package.created_by
                material.is_published = material.scorm_package.is_published
            elif material.material_type == 'SCORM':
                # Material marcado como SCORM pero sin paquete
                material.scorm_id = None
                material.scorm_version = None
                material.scorm_standard = None
                material.is_published = False
            
            # CORREGIDA: Lógica de clasificación de materiales
            ai_generated = getattr(material, 'ai_generated', False)
            is_class_material = getattr(material, 'is_class_material', False)  # Cambio: Por defecto False
            
            if ai_generated and is_class_material:
                # Material AI de clase - aparece en la sección de clase
                portfolio_ai_class_materials.append(material)
            elif ai_generated and not is_class_material:
                # Material AI personalizado - aparece en personalizado
                portfolio_ai_personal_materials.append(material)
            elif not ai_generated and is_class_material:
                # Material de clase regular (no AI)
                portfolio_class_materials.append(material)
            else:
                # Material personalizado (no IA, no clase)
                portfolio_personal_materials.append(material)
        
        # 5. Procesar materiales de clase externos (CourseTopic)
        for material in class_materials:
            material.is_class_material = True
            
            # Establecer atributos SCORM para materiales de clase
            material.is_scorm_package = (material.material_type == 'SCORM' or 
                                       getattr(material, 'scorm_package', None) is not None)
            if hasattr(material, 'scorm_package') and material.scorm_package:
                material.scorm_id = material.scorm_package.id
                material.scorm_version = material.scorm_package.version
                material.scorm_standard = material.scorm_package.standard
                material.created_by = material.scorm_package.created_by
                material.is_published = material.scorm_package.is_published
            elif getattr(material, 'material_type', None) == 'SCORM':
                # Material marcado como SCORM pero sin paquete
                material.scorm_id = None
                material.scorm_version = None
                material.scorm_standard = None
                material.is_published = False
        
        # 6. Combinar materiales de clase: externos + AI de clase + regulares del portafolio
        all_class_materials = list(class_materials) + portfolio_ai_class_materials + portfolio_class_materials
        
        # 7. Combinar materiales personalizados: AI personalizado + regulares personalizados
        all_personal_materials = portfolio_ai_personal_materials + portfolio_personal_materials
        
        # 8. Combinar TODOS los materiales
        all_materials = all_class_materials + all_personal_materials
        
        # 9. Añadir contadores al contexto
        context['regular_materials_count'] = len(all_class_materials)  # Total de materiales de clase
        context['ai_materials_count'] = len(all_personal_materials)   # Total de materiales personalizados
        context['total_materials_count'] = len(all_materials)
        
        # 10. Enviar materiales clasificados al template
        context['materials'] = all_materials
        context['class_materials'] = all_class_materials      # Materiales de clase (aparecen en "Material de Clase")
        context['ai_materials'] = all_personal_materials      # Materiales personalizados (aparecen en "Personalizado")
        
        # Debug info
        logger.info(f"📚 Materiales encontrados para tema {topic.title}:")
        logger.info(f"  - Total: {len(all_materials)}")
        logger.info(f"  - De clase: {len(all_class_materials)}")
        logger.info(f"  - Personalizados: {len(all_personal_materials)}")
        logger.info(f"  - Del portafolio: {len(all_portfolio_materials)}")
        logger.info(f"  - De clase externa: {len(class_materials)}")
        
        return context

@login_required
def search_students_ajax(request):
    """Vista para buscar estudiantes vía AJAX"""
    if not hasattr(request.user, 'teacher_profile'):
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    teacher = request.user.teacher_profile
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Obtener las secciones asignadas al profesor
    sections_filter = Q(course_assignments__teacher=teacher)
    course_id = request.GET.get('course_id')
    section_id = request.GET.get('section_id')
    
    if course_id:
        sections_filter &= Q(course_assignments__course_id=course_id)
        
    if section_id:
        sections_filter = Q(id=section_id) & Q(course_assignments__teacher=teacher)
    
    sections = Section.objects.filter(sections_filter).distinct()
    
    # Buscar estudiantes en esas secciones
    students_filter = Q(enrollments__section__in=sections)
    students_filter &= (
        Q(user__first_name__icontains=query) | 
        Q(user__last_name__icontains=query) | 
        Q(dni__icontains=query)
    )
    
    students = Student.objects.filter(students_filter).distinct()[:10]  # Limitar a 10 resultados
    
    results = []
    for student in students:
        results.append({
            'id': student.id,
            'name': f"{student.user.get_full_name()}",
            'dni': student.dni,
            'sections': [f"{enrollment.section.grade.name} - {enrollment.section.name}" 
                         for enrollment in student.enrollments.filter(section__in=sections)]
        })
    
    return JsonResponse({'results': results})

@login_required
def preview_material(request, material_id):
    """Vista para previsualizar materiales"""
    try:
        # Obtener el material (solo PortfolioMaterial)
        material = get_object_or_404(PortfolioMaterial, id=material_id)
        
        # Verificar permisos
        if hasattr(request.user, 'teacher_profile'):
            # Para profesores, verificar que es el creador del material
            if material.topic.teacher != request.user.teacher_profile:
                messages.error(request, 'No tienes permisos para ver este material.')
                return redirect('dashboard:teacher')
        elif hasattr(request.user, 'student_profile'):
            # Para estudiantes, verificar que el material está en su portafolio
            if material.topic.portfolio.student != request.user.student_profile:
                messages.error(request, 'No tienes permisos para ver este material.')
                return redirect('portfolios:student_portfolio_list')
        else:
            messages.error(request, 'No tienes permisos para ver este material.')
            return redirect('dashboard:teacher')
        
        # Determinar el tipo de archivo
        file_extension = ''
        if material.file:
            file_extension = material.file.name.split('.')[-1].lower()
        
        context = {
            'material': material,
            'file_extension': file_extension,
            'is_teacher': hasattr(request.user, 'teacher_profile'),
            'is_student': hasattr(request.user, 'student_profile'),
        }
        
        return render(request, 'portfolios/preview_material.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar la vista previa: {str(e)}')
        return redirect('dashboard:teacher' if hasattr(request.user, 'teacher_profile') else 'portfolios:student_portfolio_list')

@login_required
def view_material(request, material_id):
    """Vista simple para ver un material"""
    material = get_object_or_404(PortfolioMaterial, id=material_id)
    
    # Verificar permisos: profesores pueden ver todos los materiales, estudiantes solo los suyos
    if hasattr(request.user, 'teacher_profile'):
        # Los profesores pueden ver todos los materiales
        pass
    elif hasattr(request.user, 'student_profile'):
        # Los estudiantes solo pueden ver materiales de sus portafolios
        if material.topic and material.topic.portfolio.student != request.user.student_profile:
            raise Http404("Material no encontrado")
    else:
        raise Http404("Sin permisos para ver este material")
    
    return render(request, 'portfolios/material_view.html', {
        'material': material
    })

@login_required
def sync_course_topic_materials(request, course_topic_id):
    """Vista para sincronizar materiales existentes de un CoursetTopic a portafolios de estudiantes"""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, 'No tienes permisos de profesor.')
        return redirect('dashboard:teacher')
    
    try:
        course_topic = get_object_or_404(CourseTopic, id=course_topic_id)
        
        # Verificar permisos
        if course_topic.teacher != request.user.teacher_profile:
            messages.error(request, 'No tienes permiso para sincronizar este tema.')
            return redirect('dashboard:teacher_sections')
        
        # Obtener materiales existentes del CoursetTopic
        existing_materials = PortfolioMaterial.objects.filter(course_topic=course_topic)
        
        if not existing_materials.exists():
            messages.info(request, 'No hay materiales para sincronizar en este tema.')
            return redirect('dashboard:course_topic_detail', pk=course_topic_id)
        
        # Obtener estudiantes de la sección
        students = Student.objects.filter(
            enrollments__section=course_topic.section,
            enrollments__status='ACTIVE'
        ).distinct()
        
        if not students.exists():
            messages.info(request, 'No hay estudiantes activos en esta sección.')
            return redirect('dashboard:course_topic_detail', pk=course_topic_id)
        
        total_materials_created = 0
        total_materials_skipped = 0
        
        for student in students:
            # Obtener o crear el portafolio del estudiante
            portfolio, _ = StudentPortfolio.objects.get_or_create(
                student=student,
                month=timezone.now().month,
                academic_year=str(timezone.now().year)
            )
            
            # Obtener o crear el tema del portafolio
            portfolio_topic, _ = PortfolioTopic.objects.get_or_create(
                portfolio=portfolio,
                course=course_topic.course,
                teacher=course_topic.teacher,
                title=course_topic.title,
                defaults={'description': course_topic.description}
            )
            
            # Sincronizar cada material
            for material in existing_materials:
                # Verificar si ya existe este material para este estudiante
                existing_material = PortfolioMaterial.objects.filter(
                    topic=portfolio_topic,
                    course_topic=course_topic,
                    title=material.title
                ).exists()
                
                if not existing_material:
                    # Crear una copia del material para este estudiante
                    if material.file:
                        # Leer el contenido del archivo original
                        material.file.open('rb')
                        file_content = material.file.read()
                        material.file.close()
                        
                        # Crear una nueva instancia del archivo
                        new_file = ContentFile(file_content)
                        new_file.name = material.file.name
                    else:
                        new_file = None
                    
                    # Crear el nuevo material
                    PortfolioMaterial.objects.create(
                        topic=portfolio_topic,
                        course_topic=course_topic,
                        title=material.title,
                        description=material.description,
                        material_type=material.material_type,
                        file=new_file,
                        ai_generated=material.ai_generated,
                        is_class_material=True
                    )
                    total_materials_created += 1
                else:
                    total_materials_skipped += 1
        
        # Mostrar mensaje de resultado
        if total_materials_created > 0:
            messages.success(
                request, 
                f'Sincronización completada: {total_materials_created} materiales distribuidos a {students.count()} estudiantes.'
            )
        
        if total_materials_skipped > 0:
            messages.info(
                request,
                f'{total_materials_skipped} materiales ya existían y se omitieron.'
            )
            
        if total_materials_created == 0 and total_materials_skipped == 0:
            messages.info(request, 'No se realizaron cambios durante la sincronización.')
            
    except Exception as e:
        logger.error(f"Error al sincronizar materiales del CoursetTopic {course_topic_id}: {str(e)}")
        messages.error(request, f'Error durante la sincronización: {str(e)}')
    
    return redirect('dashboard:course_topic_detail', pk=course_topic_id)

class AutoAssignmentMonitorView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Vista para monitorear las asignaciones automáticas de temas y materiales
    """
    template_name = 'portfolios/admin/auto_assignment_monitor.html'
    
    def test_func(self):
        return self.request.user.is_staff or hasattr(self.request.user, 'teacher')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        total_students = Student.objects.filter(
            enrollments__status='ACTIVE'
        ).distinct().count()
        
        total_sections = Section.objects.count()
        
        # Estudiantes con portafolios
        students_with_portfolios = Student.objects.filter(
            portfolios__isnull=False
        ).distinct().count()
        
        # Estudiantes sin portafolios (necesitan sincronización)
        students_without_portfolios = total_students - students_with_portfolios
        
        # Temas por sección
        sections_data = []
        for section in Section.objects.select_related('grade').prefetch_related('enrollments'):
            active_enrollments = section.enrollments.filter(status='ACTIVE')
            students_in_section = active_enrollments.count()
            
            # Contar temas disponibles en la sección
            course_topics = CourseTopic.objects.filter(
                section=section,
                is_active=True
            ).count()
            
            # Contar estudiantes con temas asignados
            students_with_topics = 0
            total_topics_assigned = 0
            
            for enrollment in active_enrollments:
                student_topics = PortfolioTopic.objects.filter(
                    portfolio__student=enrollment.student,
                    course__in=[ca.course for ca in CourseAssignment.objects.filter(section=section)]
                ).count()
                
                if student_topics > 0:
                    students_with_topics += 1
                    total_topics_assigned += student_topics
            
            sections_data.append({
                'section': section,
                'students_count': students_in_section,
                'course_topics_count': course_topics,
                'students_with_topics': students_with_topics,
                'students_without_topics': students_in_section - students_with_topics,
                'total_topics_assigned': total_topics_assigned,
                'sync_coverage': (students_with_topics / students_in_section * 100) if students_in_section > 0 else 0
            })
        
        # Actividad reciente (últimos logs)
        recent_activity = []
        try:
            # Esto requeriría un modelo de log personalizado o usar Django admin logs
            from django.contrib.admin.models import LogEntry
            recent_logs = LogEntry.objects.filter(
                content_type__model__in=['portfoliotopic', 'portfoliomaterial']
            ).select_related('user').order_by('-action_time')[:10]
            
            for log in recent_logs:
                recent_activity.append({
                    'timestamp': log.action_time,
                    'user': log.user,
                    'action': log.get_action_flag_display(),
                    'object': str(log.object_repr),
                    'model': log.content_type.model
                })
        except:
            pass
        
        context.update({
            'total_students': total_students,
            'total_sections': total_sections,
            'students_with_portfolios': students_with_portfolios,
            'students_without_portfolios': students_without_portfolios,
            'coverage_percentage': (students_with_portfolios / total_students * 100) if total_students > 0 else 0,
            'sections_data': sections_data,
            'recent_activity': recent_activity,
        })
        
        return context

class ManualSyncStudentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Vista para sincronizar manualmente un estudiante específico
    """
    
    def test_func(self):
        return self.request.user.is_staff or hasattr(self.request.user, 'teacher')
    
    def post(self, request, *args, **kwargs):
        student_id = request.POST.get('student_id')
        section_id = request.POST.get('section_id')
        
        try:
            student = Student.objects.get(id=student_id)
            section = Section.objects.get(id=section_id)
            
            # Verificar que el estudiante esté matriculado en esa sección
            enrollment = Enrollment.objects.filter(
                student=student,
                section=section,
                status='ACTIVE'
            ).first()
            
            if not enrollment:
                messages.error(
                    request, 
                    f'El estudiante {student.user.get_full_name()} no está matriculado en la sección {section.grade.name}-{section.name}'
                )
                return redirect('portfolios:auto_assignment_monitor')
            
            # Realizar sincronización manual
            success = manually_sync_student_with_section(student, section)
            
            if success:
                messages.success(
                    request, 
                    f'✅ Sincronización exitosa para {student.user.get_full_name()} en {section.grade.name}-{section.name}'
                )
            else:
                messages.error(
                    request, 
                    f'❌ Error en la sincronización de {student.user.get_full_name()}'
                )
                
        except (Student.DoesNotExist, Section.DoesNotExist):
            messages.error(request, '❌ Estudiante o sección no encontrados')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
        
        return redirect('portfolios:auto_assignment_monitor')

 