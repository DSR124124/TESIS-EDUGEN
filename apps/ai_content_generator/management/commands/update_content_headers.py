from django.core.management.base import BaseCommand
from django.db import transaction
from apps.ai_content_generator.models import GeneratedContent
from apps.ai_content_generator.utils.enhanced_text_processor import EnhancedTextProcessor
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza todos los contenidos generados con el nuevo encabezado institucional'

    def add_arguments(self, parser):
        parser.add_argument(
            '--content-id',
            type=int,
            help='ID específico del contenido a actualizar (opcional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la actualización sin guardar cambios',
        )

    def handle(self, *args, **options):
        processor = EnhancedTextProcessor()
        
        # Determinar qué contenidos actualizar
        if options['content_id']:
            try:
                contents = [GeneratedContent.objects.get(id=options['content_id'])]
                self.stdout.write(f"🎯 Actualizando contenido específico ID: {options['content_id']}")
            except GeneratedContent.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Contenido con ID {options['content_id']} no encontrado")
                )
                return
        else:
            contents = GeneratedContent.objects.all().select_related('request', 'request__course')
            self.stdout.write(f"🔄 Actualizando {contents.count()} contenidos...")

        updated_count = 0
        error_count = 0

        for content in contents:
            try:
                self.stdout.write(f"\n📝 Procesando: {content.title}")
                
                # Información del curso y grado
                course_name = content.request.course.name if content.request.course else "Curso General"
                grade_name = content.request.grade_level if content.request.grade_level else "Grado General"
                
                self.stdout.write(f"   📚 Curso: {course_name}")
                self.stdout.write(f"   🎓 Grado: {grade_name}")
                
                # Procesar con el nuevo formato
                enhanced_html = processor.process_to_structured_html(
                    raw_text=content.raw_content,
                    topic=content.title,
                    course=course_name,
                    grade=grade_name
                )
                
                if not options['dry_run']:
                    with transaction.atomic():
                        content.formatted_content = enhanced_html
                        content.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Actualizado exitosamente")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"   🔍 Simulado - no se guardaron cambios")
                    )
                
                updated_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error actualizando contenido {content.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Error: {str(e)}")
                )

        # Resumen final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"📊 RESUMEN DE ACTUALIZACIÓN:")
        self.stdout.write(f"   ✅ Contenidos actualizados: {updated_count}")
        self.stdout.write(f"   ❌ Errores: {error_count}")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING("⚠️  Modo simulación - no se guardaron cambios reales")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("🎉 Actualización completada exitosamente!")
            )
            self.stdout.write("🏛️ Todos los contenidos ahora incluyen el encabezado institucional") 