#!/usr/bin/env python3
"""
Comando de Django para reparar materiales SCORM que no tienen asociado un SCORMPackage.
Crea automáticamente GeneratedContent y SCORMPackage para materiales SCORM subidos manualmente.
"""

import os
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
    help = 'Repara materiales SCORM sin SCORMPackage asociado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta sin hacer cambios reales (solo muestra lo que haría)',
        )
        parser.add_argument(
            '--material-id',
            type=int,
            help='ID específico del material a reparar',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        material_id = options.get('material_id')
        
        # Mostrar información de la base de datos
        db_path = getattr(settings, 'DATABASES', {}).get('default', {}).get('NAME', 'No disponible')
        self.stdout.write(f"Base de datos ubicada en: {db_path}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("MODO DRY-RUN: No se harán cambios"))
        
        # Buscar materiales SCORM sin SCORMPackage
        query = PortfolioMaterial.objects.filter(
            material_type='SCORM',
            file__isnull=False,
            scorm_package__isnull=True
        )
        
        if material_id:
            query = query.filter(id=material_id)
            
        materials = query.order_by('-created_at')
        
        self.stdout.write(f"Encontrados {materials.count()} materiales SCORM para reparar")
        
        if not materials.exists():
            self.stdout.write(self.style.SUCCESS("No hay materiales SCORM para reparar"))
            return
            
        # Mostrar lista de materiales encontrados
        for material in materials:
            archivo = material.file.name if material.file else "Sin archivo"
            self.stdout.write(f"  - ID: {material.id}, Título: {material.title}, Archivo: {archivo}")
        
        if dry_run:
            return
            
        # Reparar cada material
        reparados = 0
        fallos = 0
        
        for material in materials:
            try:
                with transaction.atomic():
                    success = self.repair_material(material)
                    if success:
                        reparados += 1
                        self.stdout.write(self.style.SUCCESS(f"✓ Reparado material {material.id}: {material.title}"))
                    else:
                        fallos += 1
                        self.stdout.write(self.style.ERROR(f"✗ Error reparando material {material.id}: No es un archivo ZIP"))
            except Exception as e:
                fallos += 1
                error_msg = f"Error reparando material SCORM {material.id}: {str(e)}"
                logger.error(error_msg)
                self.stdout.write(self.style.ERROR(f"✗ {error_msg}"))
                
        # Resumen final
        self.stdout.write("\n" + "="*50)
        self.stdout.write("RESUMEN:")
        self.stdout.write(f"  Total encontrados: {materials.count()}")
        self.stdout.write(f"  Reparados exitosamente: {reparados}")
        self.stdout.write(f"  Fallos: {fallos}")
        self.stdout.write("="*50)

    def repair_material(self, material):
        """
        Repara un material SCORM específico creando GeneratedContent y SCORMPackage
        """
        # Verificar que el archivo sea ZIP
        if not material.file or not material.file.name.lower().endswith('.zip'):
            self.stdout.write(f"Saltando material {material.id}: no es un archivo ZIP")
            return False
            
        # Obtener el profesor del tópico
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
            additional_instructions=material.description or 'Material SCORM subido manualmente',
            status='completed',
            related_topic=material.topic,
            for_class=material.is_class_material
        )
        
        # Crear GeneratedContent con los campos correctos
        generated_content = GeneratedContent.objects.create(
            request=content_request,
            title=material.title,
            raw_content=f"Contenido SCORM: {material.title}",
            formatted_content=f"<p>Material SCORM interactivo: {material.title}</p>",
            model_used='manual_upload',
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
        material.save()
        
        return True 