from django.db import models
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField
import os
import uuid

User = get_user_model()

class ContenidoInteractivo(models.Model):
    """
    Modelo para gestionar contenido educativo interactivo creado con IA
    y editado por docentes a través de editor visual
    """
    ESTADO_CHOICES = (
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción", blank=True, null=True)
    
    # Contenido original generado por IA
    prompt_original = models.TextField(verbose_name="Prompt Original")
    contenido_ai_original = models.TextField(verbose_name="Contenido IA Original")
    
    # Contenido editado por el docente
    contenido_html = HTMLField(verbose_name="Contenido HTML Editado")
    
    # Metadatos
    creado_por = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='contenidos_creados',
        verbose_name="Creado por"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    
    # Campos para SCORM
    convertido_scorm = models.BooleanField(default=False, verbose_name="Convertido a SCORM")
    paquete_scorm = models.FileField(
        upload_to='scorm_packages/', 
        blank=True, null=True,
        verbose_name="Paquete SCORM"
    )
    
    # Datos adicionales
    etiquetas = models.CharField(max_length=255, blank=True, null=True, verbose_name="Etiquetas")
    nivel_educativo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nivel Educativo")
    
    class Meta:
        verbose_name = "Contenido Interactivo"
        verbose_name_plural = "Contenidos Interactivos"
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return self.titulo
        
    def delete(self, *args, **kwargs):
        # Eliminar archivo SCORM si existe
        if self.paquete_scorm:
            if os.path.isfile(self.paquete_scorm.path):
                os.remove(self.paquete_scorm.path)
        super().delete(*args, **kwargs)


class ContenidoRecurso(models.Model):
    """
    Modelo para gestionar recursos adicionales (imágenes, archivos, videos)
    asociados al contenido interactivo
    """
    TIPO_CHOICES = (
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('documento', 'Documento'),
        ('link', 'Enlace'),
        ('otro', 'Otro'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contenido = models.ForeignKey(
        ContenidoInteractivo, 
        on_delete=models.CASCADE, 
        related_name='recursos',
        verbose_name="Contenido relacionado"
    )
    titulo = models.CharField(max_length=255, verbose_name="Título")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de recurso")
    
    # Archivo o URL
    archivo = models.FileField(upload_to='recursos/', blank=True, null=True, verbose_name="Archivo")
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    
    # Metadatos
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    orden = models.IntegerField(default=0, verbose_name="Orden")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Recurso de Contenido"
        verbose_name_plural = "Recursos de Contenido"
        ordering = ['orden', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"
    
    def delete(self, *args, **kwargs):
        # Eliminar archivo si existe
        if self.archivo:
            if os.path.isfile(self.archivo.path):
                os.remove(self.archivo.path)
        super().delete(*args, **kwargs) 