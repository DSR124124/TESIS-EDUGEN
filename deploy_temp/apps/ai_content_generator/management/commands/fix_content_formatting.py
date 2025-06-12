"""
Comando para corregir el formateo de contenidos existentes
"""

from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import GeneratedContent
from apps.ai_content_generator.utils.enhanced_text_processor import EnhancedTextProcessor
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige el formateo de contenidos existentes que tengan problemas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--content-id',
            type=int,
            help='ID específico del contenido a corregir'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se corregiría sin hacer cambios'
        )

    def handle(self, *args, **options):
        content_id = options.get('content_id')
        dry_run = options.get('dry_run', False)
        
        processor = EnhancedTextProcessor()
        
        if content_id:
            # Corregir contenido específico
            try:
                content = GeneratedContent.objects.get(id=content_id)
                self.process_single_content(content, processor, dry_run)
            except GeneratedContent.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'No se encontró contenido con ID {content_id}')
                )
                return
        else:
            # Corregir todos los contenidos problemáticos
            self.process_all_contents(processor, dry_run)

    def process_single_content(self, content, processor, dry_run=False):
        """Procesa un contenido individual"""
        self.stdout.write(f"Procesando contenido ID: {content.id}")
        self.stdout.write(f"Título: {content.title}")
        
        # Verificar si el contenido tiene problemas
        if self.has_formatting_issues(content):
            self.stdout.write(
                self.style.WARNING("✗ Contenido tiene problemas de formato")
            )
            
            if not dry_run:
                # Corregir el contenido
                self.fix_content(content, processor)
                self.stdout.write(
                    self.style.SUCCESS("✓ Contenido corregido")
                )
            else:
                self.stdout.write("  (Solo simulación - no se realizaron cambios)")
        else:
            self.stdout.write(
                self.style.SUCCESS("✓ Contenido ya está bien formateado")
            )

    def process_all_contents(self, processor, dry_run=False):
        """Procesa todos los contenidos"""
        self.stdout.write("Buscando contenidos con problemas de formato...")
        
        contents = GeneratedContent.objects.all()
        problematic_contents = []
        
        for content in contents:
            if self.has_formatting_issues(content):
                problematic_contents.append(content)
        
        self.stdout.write(f"Encontrados {len(problematic_contents)} contenidos con problemas")
        
        if not problematic_contents:
            self.stdout.write(
                self.style.SUCCESS("No se encontraron contenidos con problemas")
            )
            return
        
        for content in problematic_contents:
            self.stdout.write(f"\n--- Contenido ID: {content.id} ---")
            self.process_single_content(content, processor, dry_run)

    def has_formatting_issues(self, content):
        """Verifica si un contenido tiene problemas de formato"""
        if not content.formatted_content:
            return True
        
        formatted = content.formatted_content
        
        # Verificar problemas comunes
        issues = [
            '[TÍTULO]' in formatted,
            '[PÁRRAFO]' in formatted,
            '[EJEMPLO]' in formatted,
            '[ACTIVIDAD]' in formatted,
            '[MULTIMEDIA]' in formatted,
            '[EVALUACIÓN]' in formatted,
            'Aquí están las secciones faltantes' in formatted,
            'javascript' in formatted.lower(),
            'iframe' in formatted.lower(),
            'addEventListener' in formatted,
            'querySelector' in formatted,
            'const ' in formatted,
            '=> {' in formatted,
            'loadingIndicator' in formatted,
            not formatted.strip().startswith('<!DOCTYPE html')
        ]
        
        return any(issues)

    def fix_content(self, content, processor):
        """Corrige el formateo de un contenido"""
        try:
            # Usar el contenido raw como fuente
            raw_content = content.raw_content or content.formatted_content
            
            # Procesar con el EnhancedTextProcessor
            corrected_html = processor.process_to_structured_html(
                raw_text=raw_content,
                topic=content.title,
                course=content.request.course.name if content.request.course else "Curso General",
                grade=content.request.grade_level if hasattr(content.request, 'grade_level') else "Grado General"
            )
            
            # Guardar el contenido corregido
            content.formatted_content = corrected_html
            content.save()
            
            logger.info(f"Contenido {content.id} corregido exitosamente")
            
        except Exception as e:
            logger.error(f"Error al corregir contenido {content.id}: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f"Error al corregir: {str(e)}")
            ) 