from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.portfolios.models import PortfolioMaterial, PortfolioTopic
from apps.academic.models import CourseTopic, Student, Enrollment
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige asignaciones incorrectas de materiales en portafolios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría sin hacer cambios reales',
        )
        parser.add_argument(
            '--student-id',
            type=int,
            help='ID específico del estudiante a revisar',
        )
        parser.add_argument(
            '--topic-id',
            type=int,
            help='ID específico del tema a revisar',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        student_id = options.get('student_id')
        topic_id = options.get('topic_id')
        
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando revisión de asignaciones incorrectas de materiales...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🏃 MODO DRY-RUN: No se harán cambios reales'))
        
        # Contadores
        materials_removed = 0
        materials_moved = 0
        duplicates_removed = 0
        orphaned_materials = 0
        
        try:
            with transaction.atomic():
                # 1. Buscar materiales duplicados (mismo título, tipo, y tema)
                self.stdout.write(self.style.HTTP_INFO('\n📋 Paso 1: Detectando materiales duplicados...'))
                
                base_query = PortfolioMaterial.objects.all()
                if student_id:
                    base_query = base_query.filter(topic__portfolio__student_id=student_id)
                if topic_id:
                    base_query = base_query.filter(topic_id=topic_id)
                
                # Buscar duplicados por título y tipo en el mismo tema
                topics_with_materials = PortfolioTopic.objects.filter(
                    materials__in=base_query
                ).distinct()
                
                for topic in topics_with_materials:
                    materials_in_topic = topic.materials.all().order_by('title', 'material_type', 'created_at')
                    
                    # Agrupar por título y tipo
                    material_groups = {}
                    for material in materials_in_topic:
                        key = (material.title, material.material_type)
                        if key not in material_groups:
                            material_groups[key] = []
                        material_groups[key].append(material)
                    
                    # Encontrar duplicados
                    for (title, mat_type), materials in material_groups.items():
                        if len(materials) > 1:
                            # Mantener el más reciente, eliminar el resto
                            materials_to_remove = materials[:-1]  # Todos excepto el último
                            
                            for material_to_remove in materials_to_remove:
                                self.stdout.write(
                                    f'  🗑️  Duplicado encontrado: "{title}" ({mat_type}) en tema "{topic.title}"'
                                )
                                
                                if not dry_run:
                                    material_to_remove.delete()
                                
                                duplicates_removed += 1
                
                # 2. Buscar materiales sin tema o con referencias incorrectas
                self.stdout.write(self.style.HTTP_INFO('\n📋 Paso 2: Detectando materiales huérfanos...'))
                
                orphaned_materials_query = PortfolioMaterial.objects.filter(
                    topic__isnull=True
                )
                
                for orphaned_material in orphaned_materials_query:
                    self.stdout.write(
                        f'  🚨 Material huérfano encontrado: "{orphaned_material.title}" (ID: {orphaned_material.id})'
                    )
                    
                    if not dry_run:
                        orphaned_material.delete()
                    
                    orphaned_materials += 1
                
                # 3. Verificar coherencia entre PortfolioMaterial y CourseTopic
                self.stdout.write(self.style.HTTP_INFO('\n📋 Paso 3: Verificando coherencia curso-tema...'))
                
                materials_with_course_topic = base_query.filter(course_topic__isnull=False)
                
                for material in materials_with_course_topic:
                    if material.topic:
                        # Verificar que el course_topic coincida con el curso del tema
                        if material.course_topic.course != material.topic.course:
                            self.stdout.write(
                                f'  ⚠️  Inconsistencia encontrada: Material "{material.title}" '
                                f'en tema de {material.topic.course.name} pero asociado a CourseTopic de {material.course_topic.course.name}'
                            )
                            
                            # Intentar encontrar el tema correcto
                            correct_topic = PortfolioTopic.objects.filter(
                                portfolio=material.topic.portfolio,
                                course=material.course_topic.course,
                                teacher=material.course_topic.teacher,
                                title=material.course_topic.title
                            ).first()
                            
                            if correct_topic:
                                self.stdout.write(
                                    f'    ✅ Moviendo material al tema correcto: "{correct_topic.title}"'
                                )
                                
                                if not dry_run:
                                    material.topic = correct_topic
                                    material.save()
                                
                                materials_moved += 1
                            else:
                                self.stdout.write(
                                    f'    ❌ No se encontró tema correcto. Eliminando material.'
                                )
                                
                                if not dry_run:
                                    material.delete()
                                
                                materials_removed += 1
                
                # 4. Verificar materiales en temas incorrectos basado en matriculación
                self.stdout.write(self.style.HTTP_INFO('\n📋 Paso 4: Verificando materiales según matriculación...'))
                
                for material in base_query.filter(topic__isnull=False):
                    student = material.topic.portfolio.student
                    course = material.topic.course
                    
                    # Verificar que el estudiante esté matriculado en este curso
                    is_enrolled = Enrollment.objects.filter(
                        student=student,
                        section__course_assignments__course=course,
                        status='ACTIVE'
                    ).exists()
                    
                    if not is_enrolled:
                        self.stdout.write(
                            f'  🚫 Material en tema incorrecto: "{material.title}" - '
                            f'Estudiante {student.user.get_full_name()} no está matriculado en {course.name}'
                        )
                        
                        if not dry_run:
                            material.delete()
                        
                        materials_removed += 1
                
                # 5. Resumen final
                self.stdout.write(self.style.SUCCESS('\n📊 RESUMEN DE LA OPERACIÓN:'))
                self.stdout.write(f'  🗑️  Materiales duplicados eliminados: {duplicates_removed}')
                self.stdout.write(f'  🚨 Materiales huérfanos eliminados: {orphaned_materials}')
                self.stdout.write(f'  📦 Materiales movidos a tema correcto: {materials_moved}')
                self.stdout.write(f'  ❌ Materiales eliminados por inconsistencia: {materials_removed}')
                
                total_changes = duplicates_removed + orphaned_materials + materials_moved + materials_removed
                
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'\n🏃 DRY-RUN: Se habrían hecho {total_changes} cambios'))
                    # Hacer rollback en dry-run
                    transaction.set_rollback(True)
                else:
                    self.stdout.write(self.style.SUCCESS(f'\n✅ Operación completada: {total_changes} cambios realizados'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la operación: {str(e)}')
            )
            raise
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Proceso de corrección finalizado.'))
