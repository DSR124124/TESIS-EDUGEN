from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import transaction, connection
from apps.ai_content_generator.models import ContentRequest
from apps.academic.models import Section, Grade, Course
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige problemas de generación de contenido y limpia caché'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Limpiar toda la caché de Django',
        )
        parser.add_argument(
            '--reset-processing',
            action='store_true',
            help='Resetear requests que están stuck en processing',
        )
        parser.add_argument(
            '--verify-db',
            action='store_true',
            help='Verificar integridad de la base de datos',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            self.clear_cache()
        
        if options['reset_processing']:
            self.reset_processing_requests()
        
        if options['verify_db']:
            self.verify_database_integrity()
        
        # Si no se especifica ninguna opción, ejecutar todas
        if not any([options['clear_cache'], options['reset_processing'], options['verify_db']]):
            self.clear_cache()
            self.reset_processing_requests()
            self.verify_database_integrity()

    def clear_cache(self):
        """Limpia toda la caché de Django"""
        try:
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('✅ Caché limpiada exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al limpiar caché: {str(e)}')
            )

    def reset_processing_requests(self):
        """Resetea requests que están atascados en processing"""
        try:
            with transaction.atomic():
                stuck_requests = ContentRequest.objects.filter(status='processing')
                count = stuck_requests.count()
                
                if count > 0:
                    stuck_requests.update(status='pending')
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {count} solicitudes reseteadas de processing a pending')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('✅ No hay solicitudes atascadas en processing')
                    )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al resetear requests: {str(e)}')
            )

    def verify_database_integrity(self):
        """Verifica la integridad de la base de datos"""
        try:
            # Verificar ContentRequest
            self.stdout.write('🔍 Verificando tabla ContentRequest...')
            
            # Verificar campos existentes
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(ai_content_generator_contentrequest)")
                columns = [row[1] for row in cursor.fetchall()]
                
                expected_columns = [
                    'id', 'topic', 'grade_level', 'additional_instructions', 
                    'status', 'created_at', 'updated_at', 'teacher_id', 
                    'course_id', 'content_type_id', 'related_topic_id', 'for_class'
                ]
                
                missing_columns = [col for col in expected_columns if col not in columns]
                extra_columns = [col for col in columns if col not in expected_columns]
                
                if missing_columns:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Columnas faltantes: {missing_columns}')
                    )
                
                if extra_columns:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Columnas extra: {extra_columns}')
                    )
                
                if 'grade_level' in columns:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Campo grade_level existe correctamente')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Campo grade_level NO EXISTE')
                    )

            # Verificar relaciones
            self.stdout.write('🔍 Verificando relaciones...')
            
            # Contar registros con problemas
            broken_teacher_refs = ContentRequest.objects.filter(teacher__isnull=True).count()
            broken_course_refs = ContentRequest.objects.filter(course__isnull=True).count()
            broken_content_type_refs = ContentRequest.objects.filter(content_type__isnull=True).count()
            
            if broken_teacher_refs > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ {broken_teacher_refs} requests con referencias de teacher rotas')
                )
            
            if broken_course_refs > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ {broken_course_refs} requests con referencias de course rotas')
                )
            
            if broken_content_type_refs > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ {broken_content_type_refs} requests con referencias de content_type rotas')
                )
            
            if all([broken_teacher_refs == 0, broken_course_refs == 0, broken_content_type_refs == 0]):
                self.stdout.write(
                    self.style.SUCCESS('✅ Todas las relaciones están intactas')
                )

            # Verificar modelos académicos
            self.stdout.write('🔍 Verificando modelos académicos...')
            
            grades_count = Grade.objects.count()
            sections_count = Section.objects.count()
            courses_count = Course.objects.count()
            
            self.stdout.write(f'📊 Estadísticas:')
            self.stdout.write(f'   - Grados: {grades_count}')
            self.stdout.write(f'   - Secciones: {sections_count}')
            self.stdout.write(f'   - Cursos: {courses_count}')

            # Verificar grados activos
            active_grades = Grade.objects.filter(is_active=True)
            self.stdout.write(f'   - Grados activos: {active_grades.count()}')
            
            for grade in active_grades:
                self.stdout.write(f'     * {grade.name} ({grade.level})')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error verificando base de datos: {str(e)}')
            )
            logger.exception("Error en verificación de base de datos") 