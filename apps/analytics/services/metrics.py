from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta

from ..models import UsageMetric, ContentMetric
from apps.ai_content_generator.models import ContentRequest, GeneratedContent
from apps.scorm_packager.models import SCORMPackage

class MetricsService:
    """
    Servicio para obtener y analizar métricas del sistema
    """
    
    @staticmethod
    def get_usage_summary(days=30):
        """
        Obtiene un resumen de uso del sistema en el período especificado
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Métricas generales
        usage_metrics = UsageMetric.objects.filter(
            last_used__gte=start_date
        ).values('feature').annotate(
            total_uses=Sum('count'),
            unique_users=Count('user', distinct=True)
        ).order_by('-total_uses')
        
        # Métricas de contenido generado
        content_requests = ContentRequest.objects.filter(
            created_at__gte=start_date
        )
        
        generated_content = GeneratedContent.objects.filter(
            created_at__gte=start_date
        )
        
        scorm_packages = SCORMPackage.objects.filter(
            created_at__gte=start_date
        )
        
        return {
            'usage': usage_metrics,
            'content_requests': {
                'total': content_requests.count(),
                'completed': content_requests.filter(status='completed').count(),
                'failed': content_requests.filter(status='failed').count(),
                'by_type': content_requests.values('content_type__name').annotate(
                    count=Count('id')
                ).order_by('-count'),
            },
            'generated_content': {
                'total': generated_content.count(),
                'avg_tokens': generated_content.aggregate(avg=Avg('tokens_used'))['avg'] or 0,
                'total_tokens': generated_content.aggregate(total=Sum('tokens_used'))['total'] or 0,
            },
            'scorm_packages': {
                'total': scorm_packages.count(),
                'published': scorm_packages.filter(is_published=True).count(),
            }
        }
    
    @staticmethod
    def get_usage_trends(period='daily', days=30):
        """
        Obtiene tendencias de uso a lo largo del tiempo
        
        period: 'daily', 'weekly', 'monthly'
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Definir función de truncamiento según período
        if period == 'weekly':
            trunc_func = TruncWeek('created_at')
        elif period == 'monthly':
            trunc_func = TruncMonth('created_at')
        else:  # default to daily
            trunc_func = TruncDay('created_at')
        
        # Tendencias de solicitudes de contenido
        content_trends = ContentRequest.objects.filter(
            created_at__gte=start_date
        ).annotate(
            period=trunc_func
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        # Tendencias de paquetes SCORM
        scorm_trends = SCORMPackage.objects.filter(
            created_at__gte=start_date
        ).annotate(
            period=trunc_func
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        return {
            'content_requests': list(content_trends),
            'scorm_packages': list(scorm_trends)
        }
        
    @staticmethod
    def get_top_content(limit=10):
        """
        Obtiene el contenido más popular basado en vistas y calificaciones
        """
        top_content = ContentMetric.objects.annotate(
            avg_rating=F('rating_sum') / F('rating_count')
        ).order_by('-views', '-avg_rating')[:limit]
        
        return top_content
        
    @staticmethod
    def get_user_activity(user, days=30):
        """
        Obtiene la actividad de un usuario específico
        """
        start_date = timezone.now() - timedelta(days=days)
        
        usage = UsageMetric.objects.filter(
            user=user,
            last_used__gte=start_date
        )
        
        content_requests = ContentRequest.objects.filter(
            teacher=user,
            created_at__gte=start_date
        )
        
        return {
            'usage': usage,
            'content_requests': content_requests,
            'total_generated': content_requests.filter(status='completed').count(),
            'recent_activity': content_requests.order_by('-created_at')[:5]
        } 