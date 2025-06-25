#!/usr/bin/env python3
"""
Comando de Django para reparar automáticamente materiales SCORM sin procesar.
Se ejecuta automáticamente al iniciar el sistema para garantizar que todos los SCORM funcionen.
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.portfolios.models import PortfolioMaterial
from apps.ai_content_generator.models import ContentRequest, ContentType, GeneratedContent
from apps.scorm_packager.models import SCORMPackage

User = get_user_model()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Repara automáticamente materiales SCORM sin procesar al iniciar el sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--silent',
            action='store_true',
            help='Ejecuta en modo silencioso (solo errores)',
        )

    def handle(self, *args, **options):
        silent = options['silent']
        
        if not silent:
            self.stdout.write("🔍 Verificando materiales SCORM...")
        
        # Buscar materiales SCORM sin SCORMPackage
        broken_materials = PortfolioMaterial.objects.filter(
            material_type='SCORM',
            file__isnull=False,
            scorm_package__isnull=True
        ).order_by('-created_at')
        
        total_found = broken_materials.count()
        
        if total_found == 0:
            if not silent:
                self.stdout.write(self.style.SUCCESS("✅ Todos los materiales SCORM están correctamente configurados"))
            return
            
        if not silent:
            self.stdout.write(f"🔧 Encontrados {total_found} materiales SCORM para reparar automáticamente")
        
        # Reparar cada material
        repaired = 0
        failed = 0
        
        for material in broken_materials:
            try:
                with transaction.atomic():
                    success = self.repair_material(material, silent)
                    if success:
                        repaired += 1
                        if not silent:
                            self.stdout.write(f"  ✅ {material.title}")
                    else:
                        failed += 1
                        if not silent:
                            self.stdout.write(f"  ❌ {material.title} (no es ZIP)")
            except Exception as e:
                failed += 1
                error_msg = f"Error reparando {material.title}: {str(e)}"
                logger.error(error_msg)
                if not silent:
                    self.stdout.write(f"  ❌ {error_msg}")
                
        # Resumen final
        if not silent:
            self.stdout.write("\n" + "="*50)
            self.stdout.write("📊 RESUMEN AUTOMÁTICO:")
            self.stdout.write(f"  🔍 Encontrados: {total_found}")
            self.stdout.write(f"  ✅ Reparados: {repaired}")
            self.stdout.write(f"  ❌ Fallos: {failed}")
            self.stdout.write("="*50)
        
        if repaired > 0:
            logger.info(f"🤖 Auto-reparación completada: {repaired} materiales SCORM configurados automáticamente")

    def repair_material(self, material, silent=False):
        """
        Repara un material SCORM específico
        """
        # Verificar que el archivo sea ZIP
        if not material.file or not material.file.name.lower().endswith('.zip'):
            return False
            
        # Obtener el profesor
        if material.topic:
            teacher = material.topic.teacher
        elif material.course_topic:
            teacher = material.course_topic.teacher
        else:
            # Usar el primer superusuario como fallback
            teacher = User.objects.filter(is_superuser=True).first()
            if not teacher:
                raise Exception("No se encontró un profesor válido")
        
        # Crear o obtener ContentType para SCORM
        content_type, created = ContentType.objects.get_or_create(
            name='SCORM Package',
            defaults={
                'description': 'Paquete SCORM interactivo',
                'template_prompt': 'Contenido SCORM interactivo'
            }
        )
        
        # Crear ContentRequest
        course = None
        if material.topic and material.topic.course:
            course = material.topic.course
        elif material.course_topic and material.course_topic.course:
            course = material.course_topic.course
        else:
            # Usar el primer curso del profesor como fallback
            course = teacher.teacher_courses.first()
            if not course:
                raise Exception("No se encontró un curso válido")
        
        content_request = ContentRequest.objects.create(
            teacher=teacher.user,
            course=course,
            content_type=content_type,
            topic=material.title,
            grade_level='General',
            additional_instructions=material.description or 'Material SCORM auto-reparado',
            status='completed',
            related_topic=material.topic,
            for_class=material.is_class_material
        )
        
        # Crear GeneratedContent
        generated_content = GeneratedContent.objects.create(
            request=content_request,
            title=material.title,
            raw_content=f"Contenido SCORM: {material.title}",
            formatted_content=f"<p>Material SCORM interactivo: {material.title}</p>",
            model_used='auto_repair',
            tokens_used=0
        )
        
        # Crear SCORMPackage
        scorm_package = SCORMPackage.objects.create(
            generated_content=generated_content,
            title=material.title,
            description=material.description or f"Paquete SCORM: {material.title}",
            standard='scorm_2004_4th',
            package_file=material.file,
            is_published=True,
            created_by=teacher.user
        )
        
        # Asociar el SCORMPackage al material
        material.scorm_package = scorm_package
        material.save(update_fields=['scorm_package'])
        
        return True 