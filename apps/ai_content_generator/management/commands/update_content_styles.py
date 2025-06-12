from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import GeneratedContent
from apps.ai_content_generator.services.template_manager import TemplateManager
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza todos los contenidos generados para asegurar compatibilidad con GrapesJS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación (no guarda cambios)',
        )
        
        parser.add_argument(
            '--id',
            type=int,
            help='ID específico de contenido a actualizar',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        specific_id = options.get('id')
        
        if specific_id:
            self.stdout.write(f"Actualizando contenido con ID {specific_id}")
            try:
                content = GeneratedContent.objects.get(id=specific_id)
                self._update_content(content, dry_run)
            except GeneratedContent.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No se encontró contenido con ID {specific_id}"))
                return
        else:
            # Obtener todos los contenidos
            contents = GeneratedContent.objects.all()
            
            self.stdout.write(f"Encontrados {contents.count()} contenidos para actualizar")
            
            updated_count = 0
            skipped_count = 0
            failed_count = 0
            
            for content in contents:
                result = self._update_content(content, dry_run)
                if result == 'updated':
                    updated_count += 1
                elif result == 'skipped':
                    skipped_count += 1
                else:
                    failed_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f"Proceso completado: {updated_count} actualizados, {skipped_count} omitidos, {failed_count} fallidos"
            ))

    def _update_content(self, content, dry_run):
        try:
            # Verificar si el contenido ya tiene estilos GrapesJS
            if content.formatted_content and ("<style>" in content.formatted_content and "gjs-row" in content.formatted_content):
                self.stdout.write(f"Contenido ID {content.id}: Ya tiene estilos GrapesJS - omitiendo")
                return 'skipped'
            
            # Aplicar la compatibilidad con GrapesJS
            if content.formatted_content:
                formatted_content = TemplateManager.ensure_grapesjs_compatibility(content.formatted_content)
                
                if not dry_run:
                    content.formatted_content = formatted_content
                    content.save(update_fields=['formatted_content'])
                    self.stdout.write(f"Contenido ID {content.id}: Actualizado con estilos GrapesJS")
                else:
                    self.stdout.write(f"Contenido ID {content.id}: Se aplicarían estilos GrapesJS (modo simulación)")
                
                return 'updated'
            else:
                self.stdout.write(self.style.WARNING(f"Contenido ID {content.id}: Sin contenido formateado - omitiendo"))
                return 'skipped'
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al actualizar contenido ID {content.id}: {str(e)}"))
            logger.error(f"Error al actualizar contenido ID {content.id}: {str(e)}")
            return 'failed' 