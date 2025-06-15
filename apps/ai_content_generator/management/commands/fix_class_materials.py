from django.core.management.base import BaseCommand
from django.db import transaction
from apps.portfolios.models import PortfolioMaterial
from apps.academic.models import CourseTopic
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige los materiales de IA que deberían ser material de clase pero están marcados como personalizados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se corregiría sin hacer cambios',
        )
        parser.add_argument(
            '--fix-course-topic-materials',
            action='store_true',
            help='Corregir materiales asociados a CourseTopics',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_course_topics = options.get('fix_course_topic_materials', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Solo se mostrarán los cambios sin aplicarlos'))
        
        # 1. Corregir materiales de IA en CourseTopics que deberían ser material de clase
        if fix_course_topics:
            self.stdout.write('\n📚 Corrigiendo materiales en CourseTopics...')
            course_topic_materials = PortfolioMaterial.objects.filter(
                course_topic__isnull=False,
                ai_generated=True,
                is_class_material=False  # Están marcados como personalizados incorrectamente
            ).select_related('course_topic', 'course_topic__course', 'course_topic__section')
            
            if course_topic_materials.exists():
                self.stdout.write(f'Encontrados {course_topic_materials.count()} materiales en CourseTopics marcados incorrectamente')
                
                for material in course_topic_materials:
                    course_topic = material.course_topic
                    self.stdout.write(
                        f'  • Material: "{material.title}" '
                        f'(ID: {material.id}) - '
                        f'Curso: {course_topic.course.name} - '
                        f'Tema: {course_topic.title} - '
                        f'Sección: {course_topic.section.grade.name}-{course_topic.section.name}'
                    )
                    
                    if not dry_run:
                        material.is_class_material = True
                        material.save(update_fields=['is_class_material'])
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✅ Corregido: ahora marcado como material de clase')
                        )
                        
                if not dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(f'\n✅ {course_topic_materials.count()} materiales corregidos en CourseTopics')
                    )
            else:
                self.stdout.write('✅ No se encontraron materiales en CourseTopics que necesiten corrección')
        
        # 2. Corregir materiales de IA generados para clase que están en PortfolioTopics
        self.stdout.write('\n👥 Analizando materiales de IA en portfolios de estudiantes...')
        
        # Buscar materiales de IA que tienen títulos que sugieren que son para clase
        class_keywords = [
            'Material de clase',
            'Tema:',
            'Sección:',
            'generado con IA',
            'Formato: SCORM'
        ]
        
        # Construir consulta para materiales que parecen ser de clase
        ai_materials_in_portfolios = PortfolioMaterial.objects.filter(
            topic__isnull=False,  # Están en PortfolioTopics
            ai_generated=True,
            is_class_material=False,  # Marcados como personalizados
            material_type='SCORM'  # Los materiales de clase suelen ser SCORM
        ).select_related('topic', 'topic__portfolio', 'topic__portfolio__student', 'topic__portfolio__student__user')
        
        # Filtrar por descripción que contenga palabras clave de clase
        materials_to_fix = []
        for material in ai_materials_in_portfolios:
            description = material.description or ''
            if any(keyword in description for keyword in class_keywords):
                materials_to_fix.append(material)
        
        if materials_to_fix:
            self.stdout.write(f'Encontrados {len(materials_to_fix)} materiales en portfolios que parecen ser de clase')
            
            # Agrupar por tema y sección para mostrar mejor información
            by_topic = {}
            for material in materials_to_fix:
                portfolio = material.topic.portfolio
                topic_title = material.topic.title
                section_info = f"Sin sección"
                
                # Intentar obtener información de sección desde enrollments
                if portfolio.student:
                    from apps.academic.models import Enrollment
                    enrollment = Enrollment.objects.filter(
                        student=portfolio.student,
                        status='ACTIVE'
                    ).first()
                    if enrollment and enrollment.section:
                        section_info = f"{enrollment.section.grade.name}-{enrollment.section.name}"
                
                key = f"{topic_title} ({section_info})"
                if key not in by_topic:
                    by_topic[key] = []
                by_topic[key].append(material)
            
            for topic_key, materials in by_topic.items():
                self.stdout.write(f'\n  📖 {topic_key}:')
                self.stdout.write(f'    - {len(materials)} materiales encontrados')
                
                # Mostrar algunos ejemplos
                for material in materials[:3]:  # Máximo 3 ejemplos por tema
                    student_name = material.topic.portfolio.student.user.get_full_name()
                    self.stdout.write(f'    • "{material.title}" (Estudiante: {student_name})')
                
                if len(materials) > 3:
                    self.stdout.write(f'    • ... y {len(materials) - 3} más')
                
                if not dry_run:
                    # Corregir todos los materiales de este tema
                    with transaction.atomic():
                        for material in materials:
                            material.is_class_material = True
                            material.save(update_fields=['is_class_material'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ {len(materials)} materiales corregidos')
                    )
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Total de {len(materials_to_fix)} materiales corregidos en portfolios')
                )
        else:
            self.stdout.write('✅ No se encontraron materiales en portfolios que necesiten corrección')
        
        # 3. Estadísticas finales
        self.stdout.write('\n📊 Estadísticas finales:')
        
        total_ai_materials = PortfolioMaterial.objects.filter(ai_generated=True).count()
        class_materials = PortfolioMaterial.objects.filter(ai_generated=True, is_class_material=True).count()
        personal_materials = PortfolioMaterial.objects.filter(ai_generated=True, is_class_material=False).count()
        
        self.stdout.write(f'  • Total materiales de IA: {total_ai_materials}')
        self.stdout.write(f'  • Material de clase: {class_materials}')
        self.stdout.write(f'  • Material personalizado: {personal_materials}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️ MODO DRY-RUN: Ningún cambio fue aplicado')
            )
            self.stdout.write('Para aplicar los cambios, ejecuta el comando sin --dry-run')
        else:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Proceso completado exitosamente!')
            ) 