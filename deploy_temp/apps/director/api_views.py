"""
Vistas API para notificaciones dinámicas y actualizaciones en tiempo real
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count
from apps.accounts.models import Teacher
from apps.academic.models import Student, Enrollment
import json


@login_required
@require_http_methods(["GET"])
def teacher_stats_api(request):
    """
    API para obtener estadísticas actualizadas de profesores
    """
    try:
        stats = {
            'total_teachers': Teacher.objects.count(),
            'active_teachers': Teacher.objects.filter(user__is_active=True).count(),
            'inactive_teachers': Teacher.objects.filter(user__is_active=False).count(),
            'recent_teachers': Teacher.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
            'last_updated': timezone.now().isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required  
@require_http_methods(["GET"])
def system_notifications_api(request):
    """
    API para obtener notificaciones del sistema en tiempo real
    """
    try:
        notifications = []
        
        # Verificar si hay profesores recién creados
        recent_teachers = Teacher.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).count()
        
        if recent_teachers > 0:
            notifications.append({
                'type': 'success',
                'title': 'Nuevo Profesor',
                'message': f'{recent_teachers} profesor(es) registrado(s) recientemente',
                'timestamp': timezone.now().isoformat()
            })
        
        # Verificar estado del sistema
        total_users = Teacher.objects.count() + Student.objects.count()
        if total_users > 100:
            notifications.append({
                'type': 'info',
                'title': 'Sistema Activo',
                'message': f'El sistema tiene {total_users} usuarios registrados',
                'timestamp': timezone.now().isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_notification_read_api(request):
    """
    API para marcar notificaciones como leídas
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        # Aquí podrías implementar lógica para marcar como leída
        # Por ahora solo confirmamos que se recibió
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación marcada como leída'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def teacher_search_api(request):
    """
    API para búsqueda en tiempo real de profesores
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({
                'success': True,
                'results': [],
                'count': 0
            })
        
        teachers = Teacher.objects.filter(
            user__first_name__icontains=query
        ).union(
            Teacher.objects.filter(user__last_name__icontains=query)
        ).union(
            Teacher.objects.filter(user__email__icontains=query)
        ).union(
            Teacher.objects.filter(teacher_code__icontains=query)
        ).select_related('user')[:10]  # Limitar a 10 resultados
        
        results = []
        for teacher in teachers:
            results.append({
                'id': teacher.id,
                'name': teacher.user.get_full_name(),
                'email': teacher.user.email,
                'code': teacher.teacher_code,
                'is_active': teacher.user.is_active,
                'phone': teacher.phone or 'No disponible',
                'dni': teacher.dni or 'No disponible'
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def dashboard_updates_api(request):
    """
    API para obtener actualizaciones del dashboard en tiempo real
    """
    try:
        # Obtener estadísticas generales
        stats = {
            'teachers': {
                'total': Teacher.objects.count(),
                'active': Teacher.objects.filter(user__is_active=True).count(),
            },
            'students': {
                'total': Student.objects.count(),
                'active': Student.objects.filter(is_active=True).count(),
            },
            'enrollments': {
                'total': Enrollment.objects.count(),
                'active': Enrollment.objects.filter(status='ACTIVE').count(),
            }
        }
        
        # Obtener actividad reciente
        recent_activity = []
        
        # Profesores recientes
        recent_teachers = Teacher.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).select_related('user').order_by('-created_at')[:5]
        
        for teacher in recent_teachers:
            recent_activity.append({
                'type': 'teacher_created',
                'message': f'Nuevo profesor registrado: {teacher.user.get_full_name()}',
                'timestamp': teacher.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'stats': stats,
            'recent_activity': recent_activity,
            'last_update': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 