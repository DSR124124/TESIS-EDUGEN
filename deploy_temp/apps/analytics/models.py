from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from apps.academic.models import Course, Student
from apps.ai_content_generator.models import ContentRequest, GeneratedContent

User = get_user_model()

class UsageMetric(models.Model):
    """Modelo para métricas de uso del sistema"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage_metrics')
    action = models.CharField(max_length=50)
    resource = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class ContentMetric(models.Model):
    """Modelo para métricas relacionadas con contenido generado"""
    content = models.ForeignKey(GeneratedContent, on_delete=models.CASCADE, related_name='metrics')
    tokens_used = models.IntegerField(default=0)
    generation_time = models.FloatField(default=0.0)  # en segundos
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Métricas para contenido #{self.content.id} - {self.timestamp.strftime('%Y-%m-%d')}"

class StudentProgress(models.Model):
    """Modelo para el seguimiento del progreso académico del estudiante"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    content = models.ForeignKey(GeneratedContent, on_delete=models.CASCADE, related_name='student_progress')
    
    # Campos de evaluación
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Indicadores de logro (basados en la rúbrica generada)
    indicators = models.JSONField(default=dict)
    
    # Campos para seguimiento
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    teacher_comments = models.TextField(blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_progress_records'
    )
    
    class Meta:
        verbose_name = "Progreso del Estudiante"
        verbose_name_plural = "Progreso de Estudiantes"
        ordering = ['-updated_at']
        unique_together = ['student', 'course', 'content']
    
    def __str__(self):
        return f"Progreso de {self.student.user.get_full_name()} en {self.course.name} - {self.content.title}"

class ContentInteractionMetric(models.Model):
    """
    Métricas relacionadas con la interacción de los usuarios con el contenido
    """
    # Referencia genérica para cualquier tipo de contenido
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    rating_sum = models.PositiveIntegerField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def average_rating(self):
        """
        Calcula la calificación promedio
        """
        if self.rating_count == 0:
            return 0
        return self.rating_sum / self.rating_count
    
    def __str__(self):
        return f"Métricas de interacción para {self.content_object}"
        
    @classmethod
    def log_view(cls, content_object):
        """
        Registra una vista de contenido
        """
        content_type = ContentType.objects.get_for_model(content_object.__class__)
        metric, created = cls.objects.get_or_create(
            content_type=content_type,
            object_id=content_object.id
        )
        
        metric.views += 1
        metric.save()
        
        return metric
    
    @classmethod
    def log_download(cls, content_object):
        """
        Registra una descarga de contenido
        """
        content_type = ContentType.objects.get_for_model(content_object.__class__)
        metric, created = cls.objects.get_or_create(
            content_type=content_type,
            object_id=content_object.id
        )
        
        metric.downloads += 1
        metric.save()
        
        return metric
    
    @classmethod
    def add_rating(cls, content_object, rating):
        """
        Agrega una calificación (1-5) al contenido
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating debe estar entre 1 y 5")
            
        content_type = ContentType.objects.get_for_model(content_object.__class__)
        metric, created = cls.objects.get_or_create(
            content_type=content_type,
            object_id=content_object.id
        )
        
        metric.rating_sum += rating
        metric.rating_count += 1
        metric.save()
        
        return metric 