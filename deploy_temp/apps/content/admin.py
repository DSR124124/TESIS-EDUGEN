from django.contrib import admin
from .models import ContenidoInteractivo, ContenidoRecurso

@admin.register(ContenidoInteractivo)
class ContenidoInteractivoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creado_por', 'estado', 'fecha_creacion', 'convertido_scorm')
    list_filter = ('estado', 'nivel_educativo', 'convertido_scorm', 'creado_por')
    search_fields = ('titulo', 'descripcion', 'etiquetas')
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        (None, {
            'fields': ('titulo', 'descripcion', 'estado', 'nivel_educativo', 'etiquetas')
        }),
        ('Contenido', {
            'fields': ('prompt_original', 'contenido_ai_original', 'contenido_html')
        }),
        ('SCORM', {
            'fields': ('convertido_scorm', 'paquete_scorm')
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(ContenidoRecurso)
class ContenidoRecursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'contenido', 'fecha_creacion')
    list_filter = ('tipo',)
    search_fields = ('titulo', 'descripcion')
    
    fieldsets = (
        (None, {
            'fields': ('contenido', 'titulo', 'tipo', 'descripcion', 'orden')
        }),
        ('Archivo/URL', {
            'fields': ('archivo', 'url')
        }),
    ) 