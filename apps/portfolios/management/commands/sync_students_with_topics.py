from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import logging

from apps.academic.models import Enrollment, Section
from apps.portfolios.signals import manually_sync_student_with_section

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sincroniza automáticamente estudiantes existentes con temas y materiales de su sección'

    def add_arguments(self, parser):
        parser.add_argument(
            '--section',
            type=str,
            help='Sincronizar solo estudiantes de una sección específica (formato: "GradoX-SeccionY")'
        )
        parser.add_argument(
            '--student-dni',
            type=str,
            help='Sincronizar solo un estudiante específico por DNI'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo de prueba sin hacer cambios reales'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎓 Iniciando sincronización automática de estudiantes...'))
        
        # Filtros opcionales
        section_filter = options.get('section')
        student_dni = options.get('student_dni')
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️ MODO PRUEBA - No se harán cambios reales'))
        
        try:
            # Obtener matrículas activas
            enrollments = Enrollment.objects.filter(status='ACTIVE').select_related(
                'student', 'student__user', 'section', 'section__grade'
            )
            
            # Aplicar filtros
            if section_filter:
                try:
                    grade_name, section_name = section_filter.split('-')
                    enrollments = enrollments.filter(
                        section__grade__name=grade_name,
                        section__name=section_name
                    )
                    self.stdout.write(f"🎯 Filtrando por sección: {section_filter}")
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR('❌ Formato de sección inválido. Use: "GradoX-SeccionY"')
                    )
                    return
            
            if student_dni:
                enrollments = enrollments.filter(student__dni=student_dni)
                self.stdout.write(f"🎯 Filtrando por estudiante DNI: {student_dni}")
            
            if not enrollments.exists():
                self.stdout.write(self.style.WARNING('⚠️ No se encontraron estudiantes para sincronizar'))
                return
            
            total_students = enrollments.count()
            self.stdout.write(f"📊 Estudiantes a sincronizar: {total_students}")
            
            successful_syncs = 0
            failed_syncs = 0
            
            for enrollment in enrollments:
                student = enrollment.student
                section = enrollment.section
                
                self.stdout.write(
                    f"🔄 Procesando: {student.user.get_full_name()} "
                    f"({student.dni}) - Sección: {section.grade.name}-{section.name}"
                )
                
                if not dry_run:
                    try:
                        success = manually_sync_student_with_section(student, section)
                        if success:
                            successful_syncs += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"  ✅ Sincronizado exitosamente")
                            )
                        else:
                            failed_syncs += 1
                            self.stdout.write(
                                self.style.ERROR(f"  ❌ Error en sincronización")
                            )
                    except Exception as e:
                        failed_syncs += 1
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Error: {str(e)}")
                        )
                else:
                    self.stdout.write("  🔍 (Modo prueba - no se realizarán cambios)")
            
            # Resumen final
            self.stdout.write("\n" + "="*50)
            self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE SINCRONIZACIÓN"))
            self.stdout.write(f"👥 Total estudiantes procesados: {total_students}")
            
            if not dry_run:
                self.stdout.write(f"✅ Sincronizaciones exitosas: {successful_syncs}")
                self.stdout.write(f"❌ Sincronizaciones fallidas: {failed_syncs}")
                
                if successful_syncs > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"🎉 ¡Sincronización completada! {successful_syncs} estudiantes "
                            f"ahora tienen sus temas y materiales asignados automáticamente."
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING("ℹ️ Ejecute sin --dry-run para realizar los cambios reales")
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error general en sincronización: {str(e)}")
            )
            
        self.stdout.write("\n🎓 Proceso de sincronización finalizado.")

    def show_section_info(self):
        """Muestra información sobre las secciones disponibles"""
        self.stdout.write("\n📚 SECCIONES DISPONIBLES:")
        sections = Section.objects.select_related('grade').order_by('grade__name', 'name')
        
        for section in sections:
            student_count = Enrollment.objects.filter(
                section=section, 
                status='ACTIVE'
            ).count()
            
            self.stdout.write(
                f"  • {section.grade.name}-{section.name} "
                f"({student_count} estudiantes activos)"
            ) 