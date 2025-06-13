from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.academic.models import (
    Course, Student, Teacher, Grade, Section, CourseAssignment, Enrollment, CourseMaterial, Assignment, CourseTopic
)
from apps.portfolios.models import StudentPortfolio, PortfolioTopic, PortfolioMaterial
from apps.institutions.models import Institution, Director
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.contrib import messages
import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse, Http404
import os
from django.conf import settings
from django.views.generic.edit import FormView
from django import forms
import uuid
from datetime import datetime, timedelta
from django.db.models import Q
import urllib.parse
from apps.accounts.models import UserSettings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views import View
import json
from django.utils import timezone
from django.db import models
from apps.scorm_packager.models import SCORMPackage
from apps.ai_content_generator.models import GeneratedContent

logger = logging.getLogger(__name__)

@login_required
def redirect_dashboard(request):
    """Redirige al usuario según su rol"""
    user = request.user
    
    logger.info(f"=== REDIRECT_DASHBOARD EJECUTADO ===")
    logger.info(f"Usuario: {user.username if user.is_authenticated else 'ANONIMO'}")
    logger.info(f"Usuario autenticado: {user.is_authenticated}")
    
    if user.is_authenticated:
        logger.info(f"Rol del usuario: {user.role}")
        logger.info(f"Es staff: {user.is_staff}")
        logger.info(f"Es superuser: {user.is_superuser}")
        logger.info(f"Tiene director_profile: {hasattr(user, 'director_profile')}")
        logger.info(f"Tiene teacher_profile: {hasattr(user, 'teacher_profile')}")
        logger.info(f"Tiene student_profile: {hasattr(user, 'student_profile')}")
    
    # Verificar si hay una redirección específica de rol en la sesión
    role_redirect = request.session.get('role_redirect')
    if role_redirect:
        if role_redirect == 'teacher':
            logger.debug(f"Redirigiendo a usuario {user.username} a dashboard de profesor por role_redirect")
            # Limpiar el valor de la sesión para futuras redirecciones
            request.session.pop('role_redirect', None)
            return redirect('dashboard:teacher')
        elif role_redirect == 'director':
            logger.debug(f"Redirigiendo a usuario {user.username} a dashboard de director por role_redirect")
            # Limpiar el valor de la sesión para futuras redirecciones
            request.session.pop('role_redirect', None)
            return redirect('director:index')
        elif role_redirect == 'student':
            logger.debug(f"Redirigiendo a usuario {user.username} a dashboard de estudiante por role_redirect")
            # Limpiar el valor de la sesión para futuras redirecciones
            request.session.pop('role_redirect', None)
            return redirect('dashboard:student')
    
    # Redirigir usuarios superuser/staff al admin
    if user.is_staff or user.is_superuser:
        logger.info(f"Redirigiendo superuser/staff {user.username} al admin")
        return redirect('admin:index')
    
    # Verificar perfiles específicos usando related_name
    if hasattr(user, 'director_profile'):
        logger.info(f"Redirigiendo a usuario {user.username} a dashboard de director")
        return redirect('director:dashboard')
    elif hasattr(user, 'teacher_profile'):
        logger.info(f"Redirigiendo a usuario {user.username} a dashboard de profesor")
        return redirect('dashboard:teacher')
    elif hasattr(user, 'student_profile'):
        logger.info(f"Redirigiendo a usuario {user.username} a dashboard de estudiante")
        return redirect('dashboard:student')
    
    # Si no tiene perfiles pero tiene rol definido, redirigir según el rol con mensaje de advertencia
    if user.role == 'director':
        logger.warning(f"Usuario {user.username} tiene rol director pero no perfil - redirigiendo a admin")
        messages.warning(request, 'Tu cuenta de director no está completamente configurada. Contacta al administrador.')
        return redirect('admin:index')
    elif user.role == 'teacher':
        logger.warning(f"Usuario {user.username} tiene rol teacher pero no perfil - redirigiendo a admin")
        messages.warning(request, 'Tu cuenta de profesor no está completamente configurada. Contacta al administrador.')
        return redirect('admin:index')
    elif user.role == 'student':
        logger.warning(f"Usuario {user.username} tiene rol student pero no perfil - redirigiendo a admin")
        messages.warning(request, 'Tu cuenta de estudiante no está completamente configurada. Contacta al administrador.')
        return redirect('admin:index')
    
    # Si no tiene rol definido, redirigir a admin con mensaje de error
    logger.error(f"Usuario {user.username} no tiene rol definido, redirigiendo a admin")
    messages.error(request, 'Tu cuenta no tiene un rol asignado. Contacta al administrador del sistema.')
    return redirect('admin:index')

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/admin/dashboard.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_students'] = Student.objects.count()
        context['total_teachers'] = Teacher.objects.count()
        context['total_courses'] = Course.objects.count()
        context['total_grades'] = Grade.objects.count()
        context['total_sections'] = Section.objects.count()
        context['institutions'] = Institution.objects.all()
        return context

class AdminCourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    template_name = 'dashboard/admin/course_create.html'
    fields = ['name', 'code', 'curricular_area', 'weekly_hours']
    success_url = reverse_lazy('dashboard:admin')

    def test_func(self):
        return self.request.user.is_superuser

class InstitutionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Institution
    template_name = 'dashboard/admin/institution_create.html'
    fields = ['name', 'code', 'domain', 'logo', 'address', 'phone', 'email', 'website']
    success_url = reverse_lazy('dashboard:admin')

    def test_func(self):
        return self.request.user.is_superuser

class DirectorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Director
    template_name = 'dashboard/admin/director_create.html'
    fields = ['dni', 'phone']
    success_url = reverse_lazy('dashboard:admin')


    def test_func(self):
        return self.request.user.is_superuser

    @transaction.atomic
    def form_valid(self, form):
        # Crear usuario para el director
        user_data = self.request.POST
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=True
        )
        
        # Asignar usuario y institución al director
        form.instance.user = user
        form.instance.institution_id = self.kwargs['institution_id']
        return super().form_valid(form)

class DirectorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/director/dashboard.html'
    login_url = '/login/'

    def test_func(self):
        return hasattr(self.request.user, 'director_profile')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('login')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        director = self.request.user.director_profile
        context['director'] = director
        context['institution'] = director.institution
        return context

class TeacherDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/teacher/dashboard.html'

    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
        
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "No tienes permisos de profesor para acceder a esta página.")
            return redirect('login')
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Información de la institución del profesor
        try:
            # Obtener la institución desde las asignaciones de curso del profesor
            from apps.institutions.models import Institution, InstitutionSettings
            course_assignment = CourseAssignment.objects.filter(teacher=teacher).first()
            if course_assignment:
                # Intentar obtener institución desde la sección del profesor
                # En un sistema real, esto podría ser más directo si hay una relación teacher->institution
                institution = None
                try:
                    # Buscar si hay un director asociado a esta institución que registró al profesor
                    from apps.institutions.models import Director
                    # Por ahora, obtener la primera institución disponible como fallback
                    institution = Institution.objects.first()
                except:
                    institution = None
                
                if institution:
                    context['institution'] = institution
                    # Obtener configuraciones de colores
                    try:
                        settings = institution.settings
                        context['institution_colors'] = {
                            'primary': settings.primary_color,
                            'secondary': settings.secondary_color,
                            'accent': settings.accent_color,
                            'logo_enabled': settings.logo_enabled
                        }
                    except InstitutionSettings.DoesNotExist:
                        context['institution_colors'] = {
                            'primary': '#005CFF',
                            'secondary': '#A142F5',
                            'accent': '#00CFFF',
                            'logo_enabled': True
                        }
        except Exception as e:
            # Valores por defecto si hay algún error
            context['institution'] = None
            context['institution_colors'] = {
                'primary': '#005CFF',
                'secondary': '#A142F5',
                'accent': '#00CFFF',
                'logo_enabled': True
            }
        
        # Obtener datos del profesor
        context['total_students'] = Student.objects.filter(
            enrollments__section__course_assignments__teacher=teacher
        ).distinct().count()
        
        context['total_courses'] = Course.objects.filter(
            course_assignments__teacher=teacher
        ).distinct().count()
        
        context['total_sections'] = Section.objects.filter(
            course_assignments__teacher=teacher
        ).distinct().count()
        
        # Obtener datos de portafolios pendientes que necesitan atención
        from django.db.models import Count, F, Q
        from datetime import datetime, timedelta
        
        # Portafolios pendientes de revisión (incompletos o con bajo progreso)
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        portfolios = PortfolioTopic.objects.filter(
            teacher=teacher, 
            portfolio__month=current_month,
            portfolio__academic_year=str(current_year),
            is_complete=False
        ).select_related(
            'portfolio', 'portfolio__student', 'portfolio__student__user', 'course'
        ).order_by('portfolio__student__user__last_name')[:5]
        
        pending_portfolios = []
        for topic in portfolios:
            portfolio_data = {
                'student': topic.portfolio.student,
                'course': topic.course,
                'completion_percentage': self.calculate_portfolio_completion(topic.portfolio)
            }
            # Solo agregar si no está ya en la lista
            if not any(p['student'].id == portfolio_data['student'].id and 
                      p['course'].id == portfolio_data['course'].id for p in pending_portfolios):
                pending_portfolios.append(portfolio_data)
        
        context['pending_portfolios'] = pending_portfolios[:5]  # Limitamos a 5 portafolios
        
        # Información de cursos y su progreso
        courses = Course.objects.filter(
            course_assignments__teacher=teacher
        ).distinct()
        
        teacher_courses = []
        for course in courses:
            # Obtener secciones para este curso
            sections = Section.objects.filter(
                course_assignments__course=course,
                course_assignments__teacher=teacher
            ).distinct()
            
            # Contar estudiantes para este curso
            students_count = Student.objects.filter(
                enrollments__section__in=sections
            ).distinct().count()
            
            # Calcular progreso promedio para este curso
            avg_progress = self.calculate_course_progress(course, teacher)
            
            teacher_courses.append({
                'id': course.id,
                'name': course.name,
                'sections_count': sections.count(),
                'students_count': students_count,
                'avg_progress': avg_progress
            })
        
        context['teacher_courses'] = teacher_courses[:4]  # Limitamos a 4 cursos
        
        # Obtener secciones asignadas al profesor
        sections = Section.objects.filter(
            course_assignments__teacher=teacher
        ).distinct().select_related('grade')
        context['sections'] = sections
        
        # Obtener estudiantes asignados al profesor
        students = Student.objects.filter(
            enrollments__section__course_assignments__teacher=teacher
        ).distinct().select_related('user')[:10]
        context['students'] = students
        
        return context
    
    def calculate_portfolio_completion(self, portfolio):
        """Calcula el porcentaje de completitud de un portafolio"""
        total_topics = PortfolioTopic.objects.filter(portfolio=portfolio).count()
        if total_topics == 0:
            return 0
            
        completed_topics = PortfolioTopic.objects.filter(
            portfolio=portfolio, 
            is_complete=True
        ).count()
        
        return int((completed_topics / total_topics) * 100)
    
    def calculate_course_progress(self, course, teacher):
        """Calcula el progreso promedio de un curso basado en los portafolios asociados"""
        # En un sistema real, esto podría incluir más factores
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        topics = PortfolioTopic.objects.filter(
            course=course,
            teacher=teacher,
            portfolio__month=current_month,
            portfolio__academic_year=str(current_year)
        )
        
        if not topics.exists():
            return 30  # Valor por defecto para visualización
            
        completed_count = topics.filter(is_complete=True).count()
        total_count = topics.count()
        
        if total_count == 0:
            return 30  # Valor por defecto
            
        return int((completed_count / total_count) * 100)

class StudentDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/student/dashboard.html'

    def test_func(self):
        return hasattr(self.request.user, 'student_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Obtener información de la institución educativa
        try:
            from apps.institutions.models import Institution, InstitutionSettings
            
            # Buscar la institución activa disponible
            institution = Institution.objects.filter(is_active=True).first()
            
            if institution:
                context['institution'] = institution
                
                # Obtener configuraciones de la institución
                try:
                    settings = institution.settings
                    context['institution_settings'] = settings
                except InstitutionSettings.DoesNotExist:
                    # Crear configuraciones por defecto si no existen
                    settings = InstitutionSettings.objects.create(
                        institution=institution,
                        primary_color='#005CFF',
                        secondary_color='#A142F5',
                        accent_color='#00CFFF',
                        logo_enabled=True
                    )
                    context['institution_settings'] = settings
            else:
                context['institution'] = None
                context['institution_settings'] = None
                
        except Exception as e:
            # Si hay error, usar valores por defecto
            context['institution'] = None
            context['institution_settings'] = None
        
        # Obtener información esencial de secciones y cursos
        sections = student.enrollments.filter(status='ACTIVE').select_related('section').values_list('section', flat=True)
        courses = self.get_student_courses(student)
        
        # Obtener materiales de cursos y de portafolios
        from apps.portfolios.models import PortfolioMaterial, StudentPortfolio
        
        # Materiales de cursos
        course_materials = CourseMaterial.objects.filter(
            course__in=courses,
            is_active=True
        ).select_related('course').order_by('-created_at')
        
        # Materiales de portafolio del estudiante
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        portfolio_materials = []
        try:
            student_portfolio = StudentPortfolio.objects.filter(
                student=student,
                academic_year=str(current_year),
                month=current_month
            ).first()
            
            if student_portfolio:
                portfolio_materials = PortfolioMaterial.objects.filter(
                    topic__portfolio=student_portfolio
                ).select_related('topic', 'topic__course').order_by('-created_at')
        except:
            pass
        
        # Combinar todos los materiales
        all_materials = []
        
        # Agregar materiales de curso
        for material in course_materials:
            all_materials.append({
                'title': material.title,
                'description': material.description,
                'course': material.course,
                'created_at': material.created_at,
                'type': 'course_material',
                'file': material.file if hasattr(material, 'file') else None
            })
        
        # Agregar materiales de portafolio
        for material in portfolio_materials:
            all_materials.append({
                'title': material.title,
                'description': material.description,
                'course': material.topic.course,
                'created_at': material.created_at,
                'type': 'portfolio_material',
                'file': material.file if material.file else None
            })
        
        # Ordenar por fecha y tomar los más recientes
        all_materials.sort(key=lambda x: x['created_at'], reverse=True)
        recent_materials = all_materials[:8]
        
        # Obtener temas del portafolio del estudiante
        portfolio_topics = []
        try:
            if student_portfolio:
                from apps.portfolios.models import PortfolioTopic
                portfolio_topics = PortfolioTopic.objects.filter(
                    portfolio=student_portfolio
                ).select_related('course').order_by('-created_at')[:5]
        except:
            pass
        
        # Actividades pendientes reales (tareas)
        pending_activities = Assignment.objects.filter(
            section__in=sections,
            due_date__gte=timezone.now(),
            is_active=True
        ).order_by('due_date')[:3]
        
        # Calcular progreso real por curso
        courses_with_progress = []
        for course in courses:
            progress = self.calculate_course_progress(student, course)
            courses_with_progress.append({
                'id': course.id,
                'name': course.name,
                'progress': progress,
                'code': course.code
            })
        
        # Agregar contenido relevante al contexto
        context.update({
            'student': student,
            'is_student_dashboard': True,
            'sections': student.enrollments.filter(status='ACTIVE').select_related('section__grade').all(),
            'courses': courses_with_progress,
            'pending_activities': pending_activities,
            'course_materials': recent_materials,
            'portfolio_topics': portfolio_topics,
        })
        
        return context
    
    def get_student_courses(self, student):
        """Obtiene los cursos en los que el estudiante está matriculado"""
        return Course.objects.filter(
            course_assignments__section__enrollments__student=student,
            course_assignments__section__enrollments__status='ACTIVE',
            course_assignments__is_active=True
        ).distinct()
    
    def calculate_course_progress(self, student, course):
        """Calcula el progreso real del estudiante en un curso específico"""
        from apps.portfolios.models import PortfolioTopic
        
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Buscar temas completados para este curso
        topics = PortfolioTopic.objects.filter(
            portfolio__student=student,
            portfolio__month=current_month,
            portfolio__academic_year=str(current_year),
            course=course
        )
        
        if not topics.exists():
            return 0
            
        # Calcular progreso basado en temas completados
        total_topics = topics.count()
        completed_topics = topics.filter(is_complete=True).count()
        
        return int((completed_topics / total_topics) * 100) if total_topics > 0 else 0

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'dashboard/director/courses/list.html', {
        'courses': courses
    })

@login_required
def course_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        credits = request.POST.get('credits')
        
        Course.objects.create(
            name=name,
            code=code,
            description=description,
            credits=credits
        )
        messages.success(request, 'Curso creado exitosamente')
        return redirect('director:course_list')
    
    return render(request, 'dashboard/director/courses/create.html')

@login_required
def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.code = request.POST.get('code')
        course.description = request.POST.get('description')
        course.credits = request.POST.get('credits')
        course.save()
        
        messages.success(request, 'Curso actualizado exitosamente')
        return redirect('director:course_list')
    
    return render(request, 'dashboard/director/courses/create.html', {
        'course': course,
        'edit_mode': True
    })

@login_required
def course_toggle_status(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.is_active = not course.is_active
    course.save()
    
    status = "activado" if course.is_active else "desactivado"
    messages.success(request, f'Curso {status} exitosamente')
    return redirect('director:course_list')

# Vistas específicas para el panel del profesor
class TeacherSectionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar todas las secciones asignadas a un profesor"""
    model = Section
    template_name = 'dashboard/teacher/sections/section_list.html'
    context_object_name = 'sections'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return Section.objects.filter(course_assignments__teacher=teacher).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        context['teacher'] = teacher
        context['is_teacher_dashboard'] = True
        return context

class TeacherSectionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para el detalle de una sección para profesores"""
    model = Section
    template_name = 'dashboard/teacher/sections/section_detail.html'
    context_object_name = 'section'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        section = self.get_object()
        
        # Obtener todos los estudiantes de esta sección
        students = Student.objects.filter(
            enrollments__section=section,
            enrollments__status='ACTIVE'
        ).distinct()
        
        # Obtener todas las asignaciones de cursos del profesor en esta sección
        course_assignments = CourseAssignment.objects.filter(
            section=section,
            teacher=teacher,
            is_active=True
        ).select_related('course')
        
        context['teacher'] = teacher
        context['students'] = students
        context['course_assignments'] = course_assignments
        
        # Obtener temas del curso para esta sección y profesor
        section_topics = CourseTopic.objects.filter(
            section=section,
            teacher=teacher,
            is_active=True
        ).select_related('course').order_by('course', 'created_at')
        
        context['section_topics'] = section_topics
        
        return context

class TeacherCourseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar todos los cursos asignados a un profesor"""
    model = Course
    template_name = 'dashboard/teacher/courses/course_list.html'
    context_object_name = 'courses'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return Course.objects.filter(course_assignments__teacher=teacher).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Agregar información de secciones para cada curso
        courses_with_sections = []
        total_sections = 0
        total_students = 0
        
        for course in context['courses']:
            # Obtener secciones asignadas a este profesor para este curso
            sections = Section.objects.filter(
                course_assignments__course=course,
                course_assignments__teacher=teacher
            ).distinct().select_related('grade')
            
            # Contar estudiantes en todas las secciones
            sections_students_count = 0
            for section in sections:
                # Contar estudiantes en esta sección
                student_count = Student.objects.filter(
                    enrollments__section=section,
                    enrollments__status='ACTIVE'
                ).distinct().count()
                
                # Agregar este conteo al total
                sections_students_count += student_count
                total_students += student_count
            
            # Agregar a la lista de cursos con secciones
            courses_with_sections.append({
                'course': course,
                'sections': sections,
                'sections_count': sections.count(),
                'students_count': sections_students_count
            })
            
            # Actualizar el contador total de secciones
            total_sections += sections.count()
        
        context['courses_with_sections'] = courses_with_sections
        context['total_sections'] = total_sections
        context['total_students'] = total_students
        context['teacher'] = teacher
        context['is_teacher_dashboard'] = True
        return context

class TeacherCourseDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para mostrar los detalles de un curso asignado a un profesor"""
    model = Course
    template_name = 'dashboard/teacher/courses/course_detail.html'
    context_object_name = 'course'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_object(self, queryset=None):
        # Obtener el curso y verificar que esté asignado al profesor
        course = super().get_object(queryset)
        teacher = self.request.user.teacher_profile
        
        # Verificar si el curso está asignado a este profesor
        if not CourseAssignment.objects.filter(course=course, teacher=teacher).exists():
            raise PermissionDenied("No tienes permiso para ver este curso")
        
        return course
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        teacher = self.request.user.teacher_profile
        
        # Obtener asignaciones de curso para este profesor y curso
        assignments = CourseAssignment.objects.filter(
            course=course, 
            teacher=teacher
        ).select_related('section', 'section__grade')
        
        # Obtener materiales del curso de la base de datos
        materials = CourseMaterial.objects.filter(course=course).order_by('-created_at')
        
        # Estadísticas básicas
        total_students = 0
        sections_count = assignments.count()
        
        for assignment in assignments:
            section = assignment.section
            student_count = Student.objects.filter(enrollments__section=section).count()
            # Adjuntar el conteo de estudiantes a cada asignación para mostrarlo en la plantilla
            assignment.student_count = student_count
            total_students += student_count
            
            # Calcular el porcentaje de capacidad para la barra de progreso
            if section.capacity > 0:
                assignment.capacity_percentage = (student_count / section.capacity) * 100
            else:
                assignment.capacity_percentage = 0
        
        # Agregar datos al contexto
        context['teacher'] = teacher
        context['is_teacher_dashboard'] = True
        context['assignments'] = assignments
        context['materials'] = materials
        context['total_students'] = total_students
        context['sections_count'] = sections_count
        
        return context

@login_required
def upload_course_material(request, course_id):
    """
    Vista para subir materiales de curso (archivos, documentos, etc.)
    """
    course = get_object_or_404(Course, id=course_id)
    
    # Verificar que el profesor esté asignado a este curso
    if not request.user.is_superuser and not CourseAssignment.objects.filter(
        course=course, 
        teacher=request.user.teacher_profile
    ).exists():
        messages.error(request, "No tienes permiso para subir materiales a este curso.")
        return redirect('dashboard:teacher_courses')
    
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear nuevo material de curso
            material = CourseMaterial(
                course=course,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                material_type=form.cleaned_data['material_type'],
                created_by=request.user
            )
            
            # Guardar archivo si se proporcionó uno
            if 'material_file' in request.FILES:
                material.file = request.FILES['material_file']
            
            material.save()
            
            messages.success(request, "Material de curso subido exitosamente.")
            return redirect('dashboard:teacher_course_detail', pk=course_id)
    else:
        form = CourseMaterialForm()
    
    return render(request, 'dashboard/teacher/courses/upload_material.html', {
        'form': form,
        'course': course,
        'teacher': request.user.teacher_profile if hasattr(request.user, 'teacher_profile') else None,
        'is_teacher_dashboard': True
    })

# Clase para el formulario de subida de materiales
class CourseMaterialForm(forms.Form):
    title = forms.CharField(
        max_length=100, 
        label="Título del material",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        max_length=500, 
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    material_file = forms.FileField(
        label="Archivo",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    material_type = forms.ChoiceField(
        choices=[
            ('TAREA', 'Tarea'),
            ('EXAMEN', 'Examen'),
            ('LECTURA', 'Lectura'),
            ('GUIA', 'Guía de estudio'),
            ('PRESENTACION', 'Presentación'),
            ('OTRO', 'Otro')
        ],
        label="Tipo de material",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PortfolioMaterialForm(forms.ModelForm):
    class Meta:
        model = PortfolioMaterial
        fields = ['title', 'description', 'file', 'material_type', 'topic']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'material_type': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo topic opcional
        self.fields['topic'].required = False
        self.fields['order'].required = False

@login_required
def redirect_to_portfolio_list(request):
    """Redirige a la vista de lista de portafolios en el namespace 'portfolios'"""
    # Obtener parámetros de la URL
    student_id = request.GET.get('student_id')
    section_id = request.GET.get('section_id')
    
    # Si se proporciona student_id, buscar el portafolio del estudiante y redirigir directamente
    if student_id:
        try:
            from apps.academic.models import Student
            from apps.portfolios.models import StudentPortfolio
            from datetime import datetime
            
            student = Student.objects.get(id=student_id)
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Obtener o crear el portafolio del estudiante para el mes actual
            portfolio, created = StudentPortfolio.objects.get_or_create(
                student=student,
                month=current_month,
                academic_year=str(current_year)
            )
            
            # Redirigir directamente al detalle del portafolio
            return redirect('portfolios:teacher_portfolio_detail', pk=portfolio.id)
            
        except Student.DoesNotExist:
            # Si el estudiante no existe, continuar con la redirección normal
            pass
    
    # Construir la URL con los parámetros originales
    portfolio_url = reverse('portfolios:teacher_portfolio_list')
    params = []
    
    if student_id:
        params.append(f'student_id={student_id}')
    if section_id:
        params.append(f'section_id={section_id}')
    
    if params:
        portfolio_url += '?' + '&'.join(params)
    
    return redirect(portfolio_url)

# Función para redirigir desde /dashboard/teacher/portfolios/<id>/ a /portfolios/teacher/portfolios/<id>/
@login_required
def redirect_to_portfolio_detail(request, portfolio_id):
    """Redirige a la vista de detalle de portafolio en el namespace 'portfolios'"""
    return redirect('portfolios:teacher_portfolio_detail', pk=portfolio_id)

# Vistas para estudiantes ver sus portafolios
class StudentPortfolioListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista temporal para listar portafolios de estudiantes mientras se soluciona el problema de la tabla"""
    template_name = 'dashboard/student/portfolios/portfolio_list.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context['student'] = student
        context['is_student_dashboard'] = True
        context['maintenance_message'] = "El sistema de portafolios está en mantenimiento. Por favor, inténtelo más tarde."
        
        return context

class StudentPortfolioDetailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista temporal para detalles de portafolios de estudiantes mientras se soluciona el problema de la tabla"""
    template_name = 'dashboard/student/portfolios/portfolio_detail.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context['student'] = student
        context['is_student_dashboard'] = True
        context['maintenance_message'] = "El sistema de portafolios está en mantenimiento. Por favor, inténtelo más tarde."
        
        return context

class TeacherProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'dashboard/teacher/profile/profile.html'
    context_object_name = 'user_profile'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        teacher = user.teacher_profile
        
        # Datos básicos sin cálculos complejos
        context['is_teacher'] = True
        context['profile'] = teacher
        context['academic_profile'] = Teacher.objects.filter(user=user).first()
        context['is_teacher_dashboard'] = True
        
        # Estadísticas académicas dinámicas
        try:
            # Cursos asignados
            assigned_courses = Course.objects.filter(
                course_assignments__teacher=teacher
            ).distinct()
            context['total_courses'] = assigned_courses.count()
            context['assigned_courses'] = assigned_courses[:5]  # Últimos 5 cursos
            
            # Secciones asignadas  
            assigned_sections = Section.objects.filter(
                course_assignments__teacher=teacher
            ).distinct()
            context['total_sections'] = assigned_sections.count()
            context['assigned_sections'] = assigned_sections[:5]  # Últimas 5 secciones
            
            # Estudiantes bajo su cargo
            students = Student.objects.filter(
                enrollments__section__course_assignments__teacher=teacher
            ).distinct()
            context['total_students'] = students.count()
            
            # Portafolios gestionados
            portfolios = Portfolio.objects.filter(teacher=teacher)
            context['total_portfolios'] = portfolios.count()
            context['recent_portfolios'] = portfolios.order_by('-updated_at')[:5]
            
            # Materiales de IA generados
            from apps.ai_content_generator.models import GeneratedContent
            ai_materials = GeneratedContent.objects.filter(teacher=teacher)
            context['total_ai_materials'] = ai_materials.count()
            context['recent_ai_materials'] = ai_materials.order_by('-created_at')[:5]
            
            # Paquetes SCORM creados
            from apps.scorm_packager.models import SCORMPackage
            scorm_packages = SCORMPackage.objects.filter(generated_content__teacher=teacher)
            context['total_scorm_packages'] = scorm_packages.count()
            
            # Materiales de portafolio
            from apps.portfolios.models import PortfolioMaterial
            portfolio_materials = PortfolioMaterial.objects.filter(
                topic__portfolio__teacher=teacher
            )
            context['total_portfolio_materials'] = portfolio_materials.count()
            
            # Actividad reciente
            context['has_recent_activity'] = (
                context['total_ai_materials'] > 0 or 
                context['total_portfolio_materials'] > 0 or
                context['total_portfolios'] > 0
            )
            
            # Fecha de último acceso (se puede implementar con un modelo de logging)
            context['last_login'] = user.last_login
            context['date_joined'] = user.date_joined
            
        except Exception as e:
            # Si hay algún error, no mostrar estadísticas
            context.update({
                'total_courses': 0,
                'total_sections': 0, 
                'total_students': 0,
                'total_portfolios': 0,
                'total_ai_materials': 0,
                'total_scorm_packages': 0,
                'total_portfolio_materials': 0,
                'has_recent_activity': False,
                'assigned_courses': [],
                'assigned_sections': [],
                'recent_portfolios': [],
                'recent_ai_materials': []
            })
        
        return context

class TeacherSettingsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/teacher/settings/settings.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        settings = UserSettings.get_or_create_settings(user)
        
        context['user'] = user
        context['is_teacher'] = True
        context['settings'] = settings
        context['is_teacher_dashboard'] = True
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        settings = UserSettings.get_or_create_settings(user)
        
        settings.theme = request.POST.get('theme', 'light')
        settings.email_notifications = 'email_notifications' in request.POST
        settings.system_notifications = 'system_notifications' in request.POST
        settings.reminders = 'reminders' in request.POST
        settings.animations_enabled = 'animations' in request.POST
        settings.compact_mode = 'compact_mode' in request.POST
        settings.show_contact_info = 'show_contact_info' in request.POST
        settings.two_factor_enabled = 'two_factor' in request.POST
        
        settings.save()
        
        messages.success(request, 'Configuración guardada correctamente')
        return redirect('dashboard:teacher_settings')

class TeacherStudentListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/teacher/students/list.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Obtener todos los estudiantes asignados al profesor
        students = Student.objects.filter(
            enrollments__section__course_assignments__teacher=teacher
        ).distinct().order_by('user__last_name', 'user__first_name')
        
        # Obtener las secciones asignadas al profesor
        sections = Section.objects.filter(
            course_assignments__teacher=teacher
        ).distinct().order_by('grade__name', 'name')
        
        # Preparar información de estudiantes
        for student in students:
            # Obtener las secciones del estudiante que están asignadas a este profesor
            student.sections = Section.objects.filter(
                enrollments__student=student,
                course_assignments__teacher=teacher
            ).distinct()
            
            # Corregir la consulta para obtener los cursos del estudiante asignados a este profesor
            student.courses = Course.objects.filter(
                course_assignments__section__enrollments__student=student,
                course_assignments__teacher=teacher
            ).distinct()
        
        context.update({
            'teacher': teacher,
            'is_teacher_dashboard': True,
            'students': students,
            'sections': sections,
            'total_students': students.count()
        })
        
        return context

class GenerateAIMaterialView(LoginRequiredMixin, View):
    """Vista para generar material educativo con IA para un tema específico del portafolio"""
    
    def post(self, request, *args, **kwargs):
        """Procesa la solicitud para generar material con IA"""
        topic_id = request.POST.get('topic_id')
        
        if not topic_id:
            return JsonResponse({
                'success': False,
                'message': 'Se requiere un ID de tema válido'
            }, status=400)
            
        try:
            # Obtener el tema del portafolio
            topic = PortfolioTopic.objects.get(pk=topic_id)
            
            # Verificar que el profesor tenga permiso para este tema
            if topic.teacher != request.user.teacher_profile:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permiso para generar material para este tema'
                }, status=403)
            
            # Obtener datos del formulario
            theme = request.POST.get('theme', topic.title)
            material_type = request.POST.get('material_type')
            include_images = request.POST.get('include_images') == 'on'
            include_examples = request.POST.get('include_examples') == 'on'
            include_exercises = request.POST.get('include_exercises') == 'on'
            add_to_portfolio = request.POST.get('add_to_portfolio') == 'on'
            
            # Mapear los tipos de material
            material_type_map = {
                'study_guide': 'LECTURA',
                'exercises': 'EJERCICIO',
                'assessment': 'EXAMEN',
                'project': 'PROYECTO',
                'other': 'OTRO'
            }
            
            # Obtener el tipo de material en el formato correcto para el modelo
            db_material_type = material_type_map.get(material_type, 'OTRO')
            
            # Si se debe agregar al portafolio, crear el material directamente
            if add_to_portfolio:
                # Crear el nuevo material
                material = PortfolioMaterial.objects.create(
                    topic=topic,
                    title=f"{theme} - {db_material_type}",
                    description=f"Material generado con IA para el tema: {theme}. Tipo: {db_material_type}",
                    material_type=db_material_type,
                    ai_generated=True
                )
                
                message = 'Material generado y añadido al portafolio exitosamente'
                material_id = material.id
            else:
                # En el caso de que no se deba agregar al portafolio, solo simular la generación
                # En un sistema real, se generaría el contenido pero no se asignaría al portafolio
                message = 'Material generado exitosamente. No se ha añadido al portafolio'
                material_id = None
            
            return JsonResponse({
                'success': True,
                'message': message,
                'material_id': material_id,
                'added_to_portfolio': add_to_portfolio,
                'redirect_url': reverse('portfolios:teacher_portfolio_detail', args=[topic.portfolio.id])
            })
            
        except PortfolioTopic.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'El tema especificado no existe'
            }, status=404)
        except Exception as e:
            logger.error(f"Error al generar material con IA: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al generar material: {str(e)}'
            }, status=500)

class TeacherAIGeneratorView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for the dedicated AI generator page for teachers"""
    template_name = 'dashboard/teacher/portfolios/ai_material_generator_page.html'
    
    def test_func(self):
        """Check if the user is a teacher"""
        return hasattr(self.request.user, 'teacher_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = self.kwargs.get('topic_id')
        
        try:
            topic = get_object_or_404(PortfolioTopic, id=topic_id)
            
            # Check if the teacher is assigned to this topic
            if topic.teacher != self.request.user.teacher_profile:
                raise PermissionDenied("No tienes permiso para acceder a este tema")
            
            context['topic'] = topic
            context['course'] = topic.course
            context['is_teacher_dashboard'] = True
            
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            
        return context

@method_decorator(csrf_protect, name='dispatch')
class CourseTopicDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para eliminar un tema de curso y todos sus temas relacionados en portafolios"""
    
    def test_func(self):
        if not hasattr(self.request.user, 'teacher_profile'):
            return False
        
        # Verificar que el profesor tenga permiso para eliminar este tema
        topic_id = self.kwargs.get('pk')
        try:
            topic = CourseTopic.objects.get(id=topic_id)
            return topic.teacher == self.request.user.teacher_profile
        except CourseTopic.DoesNotExist:
            return False
    
    def post(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('pk')
        
        try:
            topic = get_object_or_404(CourseTopic, id=topic_id)
            
            # Verificar permisos
            if topic.teacher != request.user.teacher_profile:
                messages.error(request, 'No tienes permiso para eliminar este tema.')
                return redirect('dashboard:teacher_section_detail', pk=topic.section.id)
            
            # Guardar información antes de eliminar
            topic_title = topic.title
            section_id = topic.section.id
            course = topic.course
            teacher = topic.teacher
            
            # Eliminar temas relacionados en portafolios de estudiantes
            from apps.portfolios.models import PortfolioTopic, StudentPortfolio
            
            # Buscar todos los temas de portafolio que corresponden a este tema de curso
            related_portfolio_topics = PortfolioTopic.objects.filter(
                course=course,
                teacher=teacher,
                title=topic_title
            )
            
            deleted_portfolios_count = 0
            deleted_materials_count = 0
            
            for portfolio_topic in related_portfolio_topics:
                # Contar materiales antes de eliminar
                materials_count = portfolio_topic.materials.count()
                deleted_materials_count += materials_count
                
                # Eliminar el tema del portafolio (esto también eliminará los materiales asociados)
                portfolio_topic.delete()
                deleted_portfolios_count += 1
            
            # Eliminar el tema de curso
            topic.delete()
            
            # Mensaje de éxito con información detallada
            success_message = f'Tema "{topic_title}" eliminado exitosamente.'
            if deleted_portfolios_count > 0:
                success_message += f' También se eliminaron {deleted_portfolios_count} temas relacionados de portafolios de estudiantes'
                if deleted_materials_count > 0:
                    success_message += f' y {deleted_materials_count} materiales asociados'
                success_message += '.'
            
            messages.success(request, success_message)
            
            return redirect('dashboard:teacher_section_detail', pk=section_id)
            
        except CourseTopic.DoesNotExist:
            messages.error(request, 'El tema especificado no existe.')
            return redirect('dashboard:teacher_sections')
        except Exception as e:
            logger.error(f"Error al eliminar tema de curso {topic_id}: {str(e)}")
            messages.error(request, f'Error al eliminar el tema: {str(e)}')
            return redirect('dashboard:teacher_sections')
    
    def get(self, request, *args, **kwargs):
        # Redirigir GET requests al detalle de la sección
        topic_id = self.kwargs.get('pk')
        try:
            topic = get_object_or_404(CourseTopic, id=topic_id)
            return redirect('dashboard:teacher_section_detail', pk=topic.section.id)
        except CourseTopic.DoesNotExist:
            return redirect('dashboard:teacher_sections')

@login_required
def delete_course_topic(request, pk):
    """Función de vista para eliminar un tema de curso"""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, 'No tienes permisos de profesor.')
        return redirect('dashboard:teacher_sections')
    
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('dashboard:teacher_sections')
    
    try:
        topic = get_object_or_404(CourseTopic, id=pk)
        
        # Verificar permisos
        if topic.teacher != request.user.teacher_profile:
            messages.error(request, 'No tienes permiso para eliminar este tema.')
            return redirect('dashboard:teacher_section_detail', pk=topic.section.id)
        
        # Guardar información antes de eliminar
        topic_title = topic.title
        section_id = topic.section.id
        course = topic.course
        teacher = topic.teacher
        
        # Eliminar temas relacionados en portafolios de estudiantes
        from apps.portfolios.models import PortfolioTopic
        
        # Buscar todos los temas de portafolio que corresponden a este tema de curso
        related_portfolio_topics = PortfolioTopic.objects.filter(
            course=course,
            teacher=teacher,
            title=topic_title
        )
        
        deleted_portfolios_count = 0
        deleted_materials_count = 0
        
        for portfolio_topic in related_portfolio_topics:
            # Contar materiales antes de eliminar
            materials_count = portfolio_topic.materials.count()
            deleted_materials_count += materials_count
            
            # Eliminar el tema del portafolio (esto también eliminará los materiales asociados)
            portfolio_topic.delete()
            deleted_portfolios_count += 1
        
        # Eliminar el tema de curso
        topic.delete()
        
        # Mensaje de éxito con información detallada
        success_message = f'Tema "{topic_title}" eliminado exitosamente.'
        if deleted_portfolios_count > 0:
            success_message += f' También se eliminaron {deleted_portfolios_count} temas relacionados de portafolios de estudiantes'
            if deleted_materials_count > 0:
                success_message += f' y {deleted_materials_count} materiales asociados'
            success_message += '.'
        
        messages.success(request, success_message)
        
        return redirect('dashboard:teacher_section_detail', pk=section_id)
        
    except CourseTopic.DoesNotExist:
        messages.error(request, 'El tema especificado no existe.')
        return redirect('dashboard:teacher_sections')
    except Exception as e:
        logger.error(f"Error al eliminar tema de curso {pk}: {str(e)}")
        messages.error(request, f'Error al eliminar el tema: {str(e)}')
        return redirect('dashboard:teacher_sections')

def delete_portfolio_topic(request, topic_id):
    """Vista para eliminar un tema del portafolio"""
    from apps.portfolios.models import PortfolioTopic
    
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
        return redirect('dashboard:teacher_portfolios')
    
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
    return redirect('dashboard:teacher_portfolio_detail', portfolio_id=portfolio.id)

class StudentContentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para que los estudiantes visualicen el contenido educativo generado por sus profesores"""
    template_name = 'dashboard/student/ai_content/content_list.html'
    context_object_name = 'content_list'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def get_queryset(self):
        """Obtiene el contenido generado para las asignaturas del estudiante"""
        from apps.ai_content_generator.models import GeneratedContent
        student = self.request.user.student_profile
        
        # Obtener los cursos del estudiante
        student_courses = self.get_student_courses(student)
        
        # Obtener contenido generado para esos cursos
        return GeneratedContent.objects.filter(
            request__course__in=student_courses
        ).select_related('request', 'request__content_type', 'request__course').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context.update({
            'student': student,
            'is_student_dashboard': True,
            'student_courses': self.get_student_courses(student)
        })
        
        return context
    
    def get_student_courses(self, student):
        """Obtiene los cursos en los que el estudiante está matriculado"""
        from apps.academic.models import Course
        return Course.objects.filter(
            course_assignments__section__enrollments__student=student,
            course_assignments__section__enrollments__status='ACTIVE',
            course_assignments__is_active=True
        ).distinct()

class StudentGoogleAccountLinkView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para vincular la cuenta de Google de un estudiante"""
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def post(self, request, *args, **kwargs):
        google_email = request.POST.get('google_email')
        
        if not google_email:
            messages.error(request, "Debes proporcionar una dirección de correo de Google válida")
            return redirect('dashboard:student')
            
        # Validar que sea un correo de Google
        if not google_email.endswith('@gmail.com') and not google_email.endswith('@googlemail.com'):
            messages.error(request, "Debes proporcionar una dirección de correo de Google válida (@gmail.com o @googlemail.com)")
            return redirect('dashboard:student')
            
        # Vincular la cuenta (simulado usando sesión)
        request.session['google_account'] = google_email
        request.session['google_linked_at'] = timezone.now().isoformat()
        
        messages.success(request, f"Cuenta de Google {google_email} vinculada correctamente")
        
        return redirect('dashboard:student')

class StudentGoogleAccountUnlinkView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para desvincular la cuenta de Google de un estudiante"""
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def post(self, request, *args, **kwargs):
        if 'google_account' not in request.session:
            messages.error(request, "No tienes una cuenta de Google vinculada actualmente")
            return redirect('dashboard:student')
            
        # Guardar el email para el mensaje
        previous_email = request.session.get('google_account')
        
        # Desvincular la cuenta (simulado usando sesión)
        if 'google_account' in request.session:
            del request.session['google_account']
        if 'google_linked_at' in request.session:
            del request.session['google_linked_at']
        
        messages.success(request, f"La cuenta de Google {previous_email} ha sido desvinculada correctamente")
        
        return redirect('dashboard:student')

class StudentProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para el perfil del estudiante"""
    template_name = 'dashboard/student/profile/profile.html'
    context_object_name = 'user_profile'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
        
    def get_object(self):
        return self.request.user
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['student'] = student
        return context

class StudentSalonView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para que el estudiante vea a sus compañeros de salón"""
    template_name = 'dashboard/student/salon/salon_list.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Obtener sección actual del estudiante (la más reciente)
        enrollment = Enrollment.objects.filter(
            student=student, 
            status='ACTIVE'
        ).select_related('section', 'section__grade').first()
        
        if enrollment:
            section = enrollment.section
            # Obtener compañeros de clase ordenados por apellido
            classmates = Student.objects.filter(
                enrollments__section=section,
                enrollments__status='ACTIVE'
            ).exclude(id=student.id).select_related('user').order_by('user__last_name')
            
            context.update({
                'student': student,
                'section': section,
                'classmates': classmates,
                'classmates_count': classmates.count()
            })
        else:
            context.update({
                'student': student,
                'section': None,
                'classmates': [],
                'classmates_count': 0
            })
        
        return context

class StudentCoursesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para que el estudiante vea sus cursos matriculados con su portafolio de temas y materiales"""
    template_name = 'dashboard/student/courses/course_list.html'
    context_object_name = 'courses'
    
    def test_func(self):
        return hasattr(self.request.user, 'student_profile')
    
    def get_queryset(self):
        student = self.request.user.student_profile
        
        # Obtener cursos activos en los que está matriculado el estudiante
        courses = Course.objects.filter(
            course_assignments__section__enrollments__student=student,
            course_assignments__section__enrollments__status='ACTIVE',
            course_assignments__is_active=True,
            is_active=True
        ).distinct()
        
        # Agregar información adicional a cada curso
        for course in courses:
            # Obtener el profesor asignado
            assignment = CourseAssignment.objects.filter(
                section__enrollments__student=student,
                section__enrollments__status='ACTIVE',
                course=course
            ).select_related('teacher', 'teacher__user').first()
            
            # Calcular el progreso real basado en las tareas y evaluaciones
            materials_count = CourseMaterial.objects.filter(
                course=course, is_active=True
            ).count()
            
            # Obtener la sección donde está matriculado el estudiante para este curso
            section = Section.objects.filter(
                course_assignments__course=course,
                enrollments__student=student,
                enrollments__status='ACTIVE'
            ).first()
            
            # Obtener tareas pendientes para este curso
            pending_assignments = Assignment.objects.filter(
                course=course,
                section=section,
                due_date__gte=timezone.now(),
                is_active=True
            ).count()
            
            # Asignar datos al curso
            course.teacher = assignment.teacher if assignment else None
            course.section = section
            course.materials_count = materials_count
            course.pending_assignments = pending_assignments
            
            # Obtener temas de portafolio para este curso
            from apps.portfolios.models import PortfolioTopic, StudentPortfolio
            
            # Primero obtenemos el portafolio actual (del mes actual)
            current_month = timezone.now().month
            current_year = timezone.now().year
            portfolio = StudentPortfolio.objects.filter(
                student=student,
                month=current_month,
                academic_year=str(current_year)
            ).first()
            
            # Si no hay portafolio para el mes actual, buscamos el más reciente
            if not portfolio:
                portfolio = StudentPortfolio.objects.filter(
                    student=student
                ).order_by('-academic_year', '-month').first()
            
            # Obtener los temas del portafolio para este curso específico
            if portfolio:
                topics = PortfolioTopic.objects.filter(
                    portfolio=portfolio,
                    course=course  # Filtro específico por este curso
                ).prefetch_related('materials').order_by('created_at')
                # Convertir a lista para evitar conflictos con Django related fields
                course.portfolio_topic_list = list(topics)
                # Asignar el portafolio específico para este curso
                course.portfolio_id = portfolio.id
            else:
                course.portfolio_topic_list = []
                course.portfolio_id = None
            
            # Calcular progreso basado en las actividades completadas de este curso específico
            if course.portfolio_topic_list:
                completed_topics = sum(1 for topic in course.portfolio_topic_list if topic.is_complete)
                total_topics = len(course.portfolio_topic_list)
                course.progress = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0
            else:
                course.progress = 0
        
        return courses
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Obtener datos globales
        total_courses = self.get_queryset().count()
        total_assignments = Assignment.objects.filter(
            course__in=self.get_queryset(),
            section__enrollments__student=student,
            section__enrollments__status='ACTIVE',
            is_active=True
        ).count()
        
        # Obtener datos del portafolio actual
        from apps.portfolios.models import StudentPortfolio
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        portfolio = StudentPortfolio.objects.filter(
            student=student,
            month=current_month,
            academic_year=str(current_year)
        ).first()
        
        # Si no hay portafolio para el mes actual, buscamos el más reciente
        if not portfolio:
            portfolio = StudentPortfolio.objects.filter(
                student=student
            ).order_by('-academic_year', '-month').first()
        
        context.update({
            'student': student,
            'is_student_dashboard': True,
            'total_courses': total_courses,
            'total_assignments': total_assignments,
            'portfolio': portfolio
        })
        
        return context

class CourseTopicDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para ver el detalle de un tema de curso"""
    model = CourseTopic
    template_name = 'dashboard/teacher/topics/course_topic_detail.html'
    context_object_name = 'course_topic'

    def test_func(self):
        return hasattr(self.request.user, 'teacher_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_topic = self.object
        
        # Obtener solo los materiales principales del CoursetTopic (no los de estudiantes individuales)
        # Los materiales principales tienen course_topic=X y topic=None
        materials = PortfolioMaterial.objects.filter(
            course_topic=course_topic,
            topic__isnull=True  # Solo materiales principales, no los distribuidos a estudiantes
        ).order_by('-created_at')
        
        context['materials'] = materials
        context['course'] = course_topic.course
        context['section'] = course_topic.section
        
        return context

class CourseTopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar un tema de curso"""
    model = CourseTopic
    template_name = 'dashboard/teacher/topics/course_topic_edit.html'
    fields = ['title', 'description']
    context_object_name = 'course_topic'
    
    def test_func(self):
        return (
            hasattr(self.request.user, 'teacher_profile') and
            self.get_object().teacher == self.request.user.teacher_profile
        )
    
    def form_valid(self, form):
        messages.success(self.request, f'Tema "{form.instance.title}" actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('dashboard:course_topic_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.object.section
        context['course'] = self.object.course
        return context

class CourseTopicCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para crear un nuevo tema de curso"""
    model = CourseTopic
    template_name = 'dashboard/teacher/topics/course_topic_create.html'
    fields = ['title', 'description']
    
    def test_func(self):
        # Verificar que el usuario es profesor
        if not hasattr(self.request.user, 'teacher_profile'):
            return False
        
        # Verificar que el profesor puede enseñar en esta sección y curso
        section_id = self.kwargs.get('section_id')
        course_id = self.kwargs.get('course_id')
        teacher = self.request.user.teacher_profile
        
        return CourseAssignment.objects.filter(
            teacher=teacher,
            course_id=course_id,
            section_id=section_id
        ).exists()
    
    @transaction.atomic
    def form_valid(self, form):
        # Asignar automáticamente la sección, curso y profesor
        section = get_object_or_404(Section, id=self.kwargs['section_id'])
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        
        # Verificar si ya existe un CourseTopic con el mismo título, curso, sección y profesor
        existing_course_topic = CourseTopic.objects.filter(
            section=section,
            course=course,
            teacher=self.request.user.teacher_profile,
            title=form.instance.title
        ).exists()
        
        if existing_course_topic:
            messages.error(
                self.request,
                f'Ya existe un tema con el título "{form.instance.title}" para este curso y sección.'
            )
            return self.form_invalid(form)
        
        form.instance.section = section
        form.instance.course = course
        form.instance.teacher = self.request.user.teacher_profile
        form.instance.is_active = True
        
        response = super().form_valid(form)
        
        # Crear automáticamente el tema en todos los portafolios de estudiantes de la sección
        try:
            from apps.portfolios.models import StudentPortfolio, PortfolioTopic
            
            # Obtener todos los estudiantes de la sección
            students = Student.objects.filter(
                enrollments__section=section,
                enrollments__status='ACTIVE'
            ).distinct()
            
            current_month = timezone.now().month
            current_year = timezone.now().year
            academic_year = str(current_year)
            topics_created = 0
            topics_skipped = 0
            
            for student in students:
                # Obtener o crear el portafolio del estudiante
                portfolio, _ = StudentPortfolio.objects.get_or_create(
                    student=student,
                    month=current_month,
                    academic_year=academic_year
                )
                
                # Verificar si ya existe un tema idéntico (mismos campos exactos)
                existing_topic = PortfolioTopic.objects.filter(
                    portfolio=portfolio,
                    course=course,
                    teacher=self.request.user.teacher_profile,
                    title=form.instance.title
                ).first()
                
                if not existing_topic:
                    # Crear el tema en el portafolio del estudiante
                    PortfolioTopic.objects.create(
                        portfolio=portfolio,
                        course=course,
                        teacher=self.request.user.teacher_profile,
                        title=form.instance.title,
                        description=form.instance.description,
                        is_complete=False,
                        last_updated_by=self.request.user
                    )
                    topics_created += 1
                else:
                    # Si ya existe, actualizar la descripción si es diferente
                    if existing_topic.description != form.instance.description:
                        existing_topic.description = form.instance.description
                        existing_topic.last_updated_by = self.request.user
                        existing_topic.save()
                        topics_created += 1
                    else:
                        topics_skipped += 1
            
            # Mensaje de éxito más detallado
            if topics_created > 0 and topics_skipped > 0:
                messages.success(
                    self.request,
                    f'Tema "{form.instance.title}" creado exitosamente. '
                    f'Distribuido a {topics_created} estudiantes. '
                    f'{topics_skipped} estudiantes ya tenían este tema.'
                )
            elif topics_created > 0:
                messages.success(
                    self.request,
                    f'Tema "{form.instance.title}" creado exitosamente y distribuido a {topics_created} estudiantes.'
                )
            elif topics_skipped > 0:
                messages.success(
                    self.request,
                    f'Tema "{form.instance.title}" creado exitosamente. '
                    f'Los {topics_skipped} estudiantes ya tenían este tema en sus portafolios.'
                )
            else:
                messages.success(
                    self.request,
                    f'Tema "{form.instance.title}" creado exitosamente.'
                )
        
        except Exception as e:
            messages.success(
                self.request,
                f'Tema "{form.instance.title}" creado exitosamente.'
            )
            messages.warning(
                self.request,
                f'No se pudo distribuir automáticamente a todos los estudiantes: {str(e)}'
            )
        
        return response
    
    def get_success_url(self):
        return reverse('dashboard:teacher_section_detail', kwargs={'pk': self.kwargs['section_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = get_object_or_404(Section, id=self.kwargs['section_id'])
        context['course'] = get_object_or_404(Course, id=self.kwargs['course_id'])
        return context


class StudentTeacherInfoView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para que el estudiante vea la información detallada de un profesor"""
    model = Teacher
    template_name = 'dashboard/student/teacher/teacher_info.html'
    context_object_name = 'teacher'
    
    def test_func(self):
        # Verificar que el usuario es un estudiante
        return hasattr(self.request.user, 'student_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        student = self.request.user.student_profile
        
        # Verificar que el estudiante tiene acceso a este profesor
        # (debe estar en una sección donde este profesor enseña)
        student_sections = Section.objects.filter(
            enrollments__student=student,
            enrollments__status='ACTIVE'
        )
        
        teacher_assignments = CourseAssignment.objects.filter(
            teacher=teacher,
            section__in=student_sections,
            is_active=True
        ).select_related('course', 'section')
        
        # Si no hay asignaciones compartidas, redirigir (seguridad)
        if not teacher_assignments.exists():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("No tienes acceso a la información de este profesor.")
        
        # Obtener los cursos que este profesor enseña al estudiante
        courses_with_teacher = []
        for assignment in teacher_assignments:
            courses_with_teacher.append({
                'course': assignment.course,
                'section': assignment.section,
                'assignment': assignment
            })
        
        # Obtener estadísticas del profesor
        total_sections = Section.objects.filter(
            course_assignments__teacher=teacher,
            course_assignments__is_active=True
        ).distinct().count()
        
        total_courses = Course.objects.filter(
            course_assignments__teacher=teacher,
            course_assignments__is_active=True
        ).distinct().count()
        
        total_students = Student.objects.filter(
            enrollments__section__course_assignments__teacher=teacher,
            enrollments__section__course_assignments__is_active=True,
            enrollments__status='ACTIVE'
        ).distinct().count()
        
        # Obtener materiales recientes creados por este profesor para el estudiante
        from apps.portfolios.models import PortfolioTopic, PortfolioMaterial
        recent_materials = PortfolioMaterial.objects.filter(
            topic__teacher=teacher,
            topic__portfolio__student=student,
            is_class_material=True
        ).order_by('-created_at')[:5]
        
        context.update({
            'student': student,
            'courses_with_teacher': courses_with_teacher,
            'teacher_assignments': teacher_assignments,
            'total_sections': total_sections,
            'total_courses': total_courses,
            'total_students': total_students,
            'recent_materials': recent_materials,
        })
        
        return context