from django.db import models
from django.contrib.auth import get_user_model
from apps.academic.models import Course  # Tu modelo de cursos existente
from apps.portfolios.models import PortfolioTopic  # Importamos el modelo correcto

User = get_user_model()

class ContentType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_prompt = models.TextField(help_text="Plantilla base para prompts")
    
    def __str__(self):
        return self.name

class ContentRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    )
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='content_requests')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    grade_level = models.CharField(max_length=50)
    additional_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_topic = models.ForeignKey(PortfolioTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='content_requests')
    for_class = models.BooleanField(default=False, help_text='Indica si el contenido es para toda la clase o individual')
    
    def __str__(self):
        return f"{self.topic} - {self.course} ({self.status})"
    
    class Meta:
        # Agregar índices para mejorar el rendimiento
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['course']),
            models.Index(fields=['status']),
            models.Index(fields=['for_class']),
        ]

class GeneratedContent(models.Model):
    request = models.ForeignKey(ContentRequest, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=255)
    raw_content = models.TextField()
    formatted_content = models.TextField()
    model_used = models.CharField(max_length=100)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        # Agregar índice para mejorar el rendimiento
        indexes = [
            models.Index(fields=['request']),
        ]

class GrapesJSTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='templates/thumbnails/', blank=True, null=True)
    html_content = models.TextField()
    css_content = models.TextField(blank=True)
    js_content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name 