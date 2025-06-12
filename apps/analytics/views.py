from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta

from .services.metrics import MetricsService
from .models import UsageMetric, ContentMetric, StudentProgress
from apps.ai_content_generator.models import GeneratedContent
from apps.academic.models import Student, Course

class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Dashboard principal de análisis y métricas
    """
    template_name = 'analytics/dashboard.html'
    
    def test_func(self):
        # Solo permitir acceso a directores o administradores
        return (hasattr(self.request.user, 'director') or 
                self.request.user.is_staff or 
                self.request.user.is_superuser)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Período seleccionado (días)
        days = int(self.request.GET.get('days', 30))
        
        # Obtener resumen de métricas
        context['metrics_summary'] = MetricsService.get_usage_summary(days=days)
        context['days'] = days
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        # Si es una petición AJAX, devolver datos como JSON
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context['metrics_summary'])
        
        return super().render_to_response(context, **response_kwargs)

class AnalyticsTrendsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Vista de tendencias de uso a lo largo del tiempo
    """
    template_name = 'analytics/trends.html'
    
    def test_func(self):
        # Solo permitir acceso a directores o administradores
        return (hasattr(self.request.user, 'director') or 
                self.request.user.is_staff or 
                self.request.user.is_superuser)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Período seleccionado (días)
        days = int(self.request.GET.get('days', 30))
        
        # Tipo de agrupación (diario, semanal, mensual)
        period = self.request.GET.get('period', 'daily')
        if period not in ['daily', 'weekly', 'monthly']:
            period = 'daily'
        
        # Obtener datos de tendencia
        context['trends'] = MetricsService.get_usage_trends(period=period, days=days)
        context['days'] = days
        context['period'] = period
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        # Si es una petición AJAX, devolver datos como JSON
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context['trends'])
        
        return super().render_to_response(context, **response_kwargs)

class UserStatsView(LoginRequiredMixin, TemplateView):
    """
    Vista de estadísticas personales para cada usuario
    """
    template_name = 'analytics/user_stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Período seleccionado (días)
        days = int(self.request.GET.get('days', 30))
        
        # Obtener estadísticas del usuario
        context['user_stats'] = MetricsService.get_user_activity(self.request.user, days=days)
        context['days'] = days
        
        return context 

@login_required
def dashboard(request):
    """Vista para el dashboard de análisis"""
    # Implementar vista para el dashboard de análisis
    return render(request, 'analytics/dashboard.html', {})

@login_required
@require_POST
def register_progress(request, content_id):
    """Vista para registrar el progreso académico de un estudiante"""
    content = get_object_or_404(GeneratedContent, id=content_id)
    
    # Verificar permisos (solo profesores pueden registrar progreso)
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('ai:content_detail', pk=content_id)
    
    student_id = request.POST.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    course = content.request.course
    
    # Crear o actualizar el registro de progreso
    progress, created = StudentProgress.objects.update_or_create(
        student=student,
        course=course,
        content=content,
        defaults={
            'created_by': request.user,
        }
    )
    
    # Actualizar los campos del progreso
    if 'score' in request.POST and request.POST['score']:
        progress.score = float(request.POST['score'])
    
    progress.strengths = request.POST.get('strengths', '')
    progress.areas_for_improvement = request.POST.get('areas_for_improvement', '')
    progress.teacher_comments = request.POST.get('teacher_comments', '')
    
    # Marcar como completado si corresponde
    if request.POST.get('completed'):
        progress.completed = True
        progress.completion_date = timezone.now()
    
    # Procesar indicadores dinámicos
    indicators = {}
    indicator_names = request.POST.getlist('indicator_name[]')
    indicator_values = request.POST.getlist('indicator_value[]')
    
    for i, name in enumerate(indicator_names):
        if name.strip() and i < len(indicator_values):
            indicators[name.strip()] = indicator_values[i]
    
    progress.indicators = indicators
    progress.save()
    
    # Registrar la actividad en las métricas de uso
    UsageMetric.objects.create(
        user=request.user,
        action='register_progress',
        resource=f'content_{content_id}',
        details={
            'student_id': student_id,
            'course_id': course.id,
            'completed': progress.completed
        }
    )
    
    messages.success(request, f"Progreso académico registrado exitosamente para {student.user.get_full_name()}")
    return redirect('ai:content_detail', pk=content_id)

@login_required
def student_progress_report(request, student_id):
    """Vista para mostrar el reporte de progreso de un estudiante"""
    student = get_object_or_404(Student, id=student_id)
    
    # Verificar permisos
    if not (hasattr(request.user, 'teacher_profile') or request.user.is_staff):
        messages.error(request, "No tienes permisos para ver este reporte.")
        return redirect('dashboard:index')
    
    # Obtener todos los registros de progreso del estudiante
    progress_records = StudentProgress.objects.filter(
        student=student
    ).order_by('course', '-updated_at')
    
    # Agrupar por curso
    courses = {}
    for record in progress_records:
        if record.course.id not in courses:
            courses[record.course.id] = {
                'name': record.course.name,
                'records': []
            }
        courses[record.course.id]['records'].append(record)
    
    context = {
        'student': student,
        'courses': courses.values(),
        'progress_count': progress_records.count()
    }
    
    return render(request, 'analytics/student_progress_report.html', context) 