from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Crear plantillas predeterminadas para el editor visual GrapesJS'

    def handle(self, *args, **kwargs):
        templates = [
            {
                'name': 'Presentación Educativa',
                'description': 'Plantilla para crear presentaciones de clase con diapositivas',
                'thumbnail': 'templates/thumbnails/presentation.jpg',
                'content': {
                    'html': """
                    <div class="gjs-row">
                        <div class="gjs-cell">
                            <h1 class="title">Título de la Presentación</h1>
                            <h3 class="subtitle">Subtítulo o descripción breve</h3>
                        </div>
                    </div>
                    <div class="gjs-row content-row">
                        <div class="gjs-cell">
                            <div class="content-block">
                                <h2>Contenido Principal</h2>
                                <p>Escribe aquí el contenido educativo principal.</p>
                                <ul>
                                    <li>Punto clave 1</li>
                                    <li>Punto clave 2</li>
                                    <li>Punto clave 3</li>
                                </ul>
                            </div>
                        </div>
                        <div class="gjs-cell">
                            <div class="image-placeholder">
                                <span>Arrastra una imagen aquí</span>
                            </div>
                        </div>
                    </div>
                    """,
                    'css': """
                    .title {
                        font-size: 2.5rem;
                        color: #3a86ff;
                        text-align: center;
                        margin-bottom: 1rem;
                    }
                    .subtitle {
                        font-size: 1.5rem;
                        color: #4a4a4a;
                        text-align: center;
                        margin-bottom: 2rem;
                    }
                    .content-row {
                        min-height: 300px;
                    }
                    .content-block {
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        height: 100%;
                    }
                    .image-placeholder {
                        height: 100%;
                        min-height: 300px;
                        background-color: #e9ecef;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 8px;
                        color: #6c757d;
                    }
                    """
                }
            },
            {
                'name': 'Ficha de Ejercicios',
                'description': 'Plantilla para crear hojas de ejercicios y problemas',
                'thumbnail': 'templates/thumbnails/exercises.jpg',
                'content': {
                    'html': """
                    <div class="exercise-header">
                        <h1>Ficha de Ejercicios</h1>
                        <div class="metadata">
                            <div class="metadata-item">
                                <span class="label">Asignatura:</span>
                                <span class="value">Matemáticas</span>
                            </div>
                            <div class="metadata-item">
                                <span class="label">Tema:</span>
                                <span class="value">Álgebra Básica</span>
                            </div>
                            <div class="metadata-item">
                                <span class="label">Grado:</span>
                                <span class="value">Primero de Secundaria</span>
                            </div>
                        </div>
                    </div>
                    <div class="instructions">
                        <h3>Instrucciones</h3>
                        <p>Resuelve los siguientes ejercicios mostrando todo el procedimiento necesario.</p>
                    </div>
                    <div class="exercise-container">
                        <div class="exercise">
                            <div class="exercise-number">1</div>
                            <div class="exercise-content">
                                <p>Descripción del ejercicio o problema a resolver.</p>
                            </div>
                        </div>
                        <div class="exercise">
                            <div class="exercise-number">2</div>
                            <div class="exercise-content">
                                <p>Descripción del ejercicio o problema a resolver.</p>
                            </div>
                        </div>
                        <div class="exercise">
                            <div class="exercise-number">3</div>
                            <div class="exercise-content">
                                <p>Descripción del ejercicio o problema a resolver.</p>
                            </div>
                        </div>
                    </div>
                    """,
                    'css': """
                    .exercise-header {
                        text-align: center;
                        margin-bottom: 2rem;
                        padding-bottom: 1rem;
                        border-bottom: 2px solid #3a86ff;
                    }
                    .metadata {
                        display: flex;
                        justify-content: space-around;
                        margin-top: 1rem;
                    }
                    .metadata-item {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }
                    .label {
                        font-weight: bold;
                        color: #4a4a4a;
                    }
                    .value {
                        color: #3a86ff;
                    }
                    .instructions {
                        margin-bottom: 2rem;
                        padding: 1rem;
                        background-color: #f8f9fa;
                        border-radius: 8px;
                    }
                    .exercise-container {
                        display: flex;
                        flex-direction: column;
                        gap: 1.5rem;
                    }
                    .exercise {
                        display: flex;
                        background-color: #ffffff;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        overflow: hidden;
                    }
                    .exercise-number {
                        background-color: #3a86ff;
                        color: white;
                        font-weight: bold;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 1rem;
                        min-width: 50px;
                    }
                    .exercise-content {
                        padding: 1rem;
                        flex-grow: 1;
                    }
                    """
                }
            },
            {
                'name': 'Guía de Estudio',
                'description': 'Plantilla para crear materiales de estudio y preparación',
                'thumbnail': 'templates/thumbnails/study_guide.jpg',
                'content': {
                    'html': """
                    <div class="study-guide">
                        <div class="header">
                            <h1>Guía de Estudio</h1>
                            <h2>Tema: [Nombre del Tema]</h2>
                        </div>
                        <div class="section">
                            <h3>Objetivos de Aprendizaje</h3>
                            <ul class="objectives">
                                <li>Comprender los conceptos básicos de [tema]</li>
                                <li>Identificar las principales características de [tema]</li>
                                <li>Aplicar los conocimientos adquiridos en situaciones prácticas</li>
                            </ul>
                        </div>
                        <div class="section">
                            <h3>Conceptos Clave</h3>
                            <div class="concepts-grid">
                                <div class="concept">
                                    <h4>Concepto 1</h4>
                                    <p>Descripción del concepto y su importancia.</p>
                                </div>
                                <div class="concept">
                                    <h4>Concepto 2</h4>
                                    <p>Descripción del concepto y su importancia.</p>
                                </div>
                                <div class="concept">
                                    <h4>Concepto 3</h4>
                                    <p>Descripción del concepto y su importancia.</p>
                                </div>
                                <div class="concept">
                                    <h4>Concepto 4</h4>
                                    <p>Descripción del concepto y su importancia.</p>
                                </div>
                            </div>
                        </div>
                        <div class="section">
                            <h3>Recursos Adicionales</h3>
                            <ul class="resources">
                                <li><a href="#">Enlace a recurso 1</a></li>
                                <li><a href="#">Enlace a recurso 2</a></li>
                                <li><a href="#">Enlace a recurso 3</a></li>
                            </ul>
                        </div>
                        <div class="footer">
                            <p>Preparado por: [Nombre del Profesor]</p>
                            <p>Fecha: [Fecha de Creación]</p>
                        </div>
                    </div>
                    """,
                    'css': """
                    .study-guide {
                        max-width: 800px;
                        margin: 0 auto;
                        font-family: 'Arial', sans-serif;
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 2rem;
                        border-bottom: 2px solid #6c5ce7;
                        padding-bottom: 1rem;
                    }
                    .header h1 {
                        color: #6c5ce7;
                        margin-bottom: 0.5rem;
                    }
                    .header h2 {
                        color: #636e72;
                        font-weight: normal;
                    }
                    .section {
                        margin-bottom: 2rem;
                        background-color: #f8f9fa;
                        padding: 1.5rem;
                        border-radius: 8px;
                    }
                    .section h3 {
                        color: #6c5ce7;
                        margin-top: 0;
                        border-bottom: 1px solid #dfe6e9;
                        padding-bottom: 0.5rem;
                    }
                    .objectives li {
                        margin-bottom: 0.5rem;
                    }
                    .concepts-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                        gap: 1rem;
                        margin-top: 1.5rem;
                    }
                    .concept {
                        background-color: white;
                        padding: 1rem;
                        border-radius: 6px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .concept h4 {
                        color: #6c5ce7;
                        margin-top: 0;
                    }
                    .resources li {
                        margin-bottom: 0.5rem;
                    }
                    .resources a {
                        color: #6c5ce7;
                        text-decoration: none;
                    }
                    .resources a:hover {
                        text-decoration: underline;
                    }
                    .footer {
                        font-size: 0.9rem;
                        color: #636e72;
                        text-align: center;
                        margin-top: 2rem;
                        padding-top: 1rem;
                        border-top: 1px solid #dfe6e9;
                    }
                    """
                }
            }
        ]

        # Crear directorio para thumbnails si no existe
        thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'templates', 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)

        # Guardar las plantillas en la base de datos
        try:
            from apps.ai_content_generator.models import GrapesJSTemplate
            
            # Crear o actualizar cada plantilla
            for idx, template_data in enumerate(templates):
                template, created = GrapesJSTemplate.objects.update_or_create(
                    name=template_data['name'],
                    defaults={
                        'description': template_data['description'],
                        'thumbnail': template_data['thumbnail'],
                        'html_content': template_data['content']['html'],
                        'css_content': template_data['content']['css'],
                        'order': idx + 1
                    }
                )
                
                action = "Creada" if created else "Actualizada"
                self.stdout.write(self.style.SUCCESS(f"{action} plantilla: {template.name}"))
            
            self.stdout.write(self.style.SUCCESS(f"Proceso completado. Se procesaron {len(templates)} plantillas."))
            
        except ImportError:
            # Si el modelo no existe, guardar plantillas en un archivo JSON
            templates_file = os.path.join(settings.BASE_DIR, 'static', 'ai_content_generator', 'grapesjs_templates.json')
            os.makedirs(os.path.dirname(templates_file), exist_ok=True)
            
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f"Plantillas guardadas en archivo JSON: {templates_file}"))
            self.stdout.write(self.style.WARNING("Para usar estas plantillas con la base de datos, crea el modelo GrapesJSTemplate."))
            
            # Instrucciones para crear el modelo
            self.stdout.write(self.style.WARNING("\nPara crear el modelo GrapesJSTemplate, añade esto a tu archivo models.py:"))
            model_code = """
from django.db import models

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
"""
            self.stdout.write(model_code) 