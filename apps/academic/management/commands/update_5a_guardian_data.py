from django.core.management.base import BaseCommand
from django.db import transaction
from apps.academic.models import Student, Grade, Section, Enrollment

class Command(BaseCommand):
    help = 'Actualiza los datos de apoderado de estudiantes de 5A siguiendo la estructura de 4F'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write("📝 Actualizando datos de apoderado de estudiantes 5A...")
                
                # Obtener estudiantes de 5A
                grade_5 = Grade.objects.get(name='QUINTO')
                section_a = Section.objects.get(grade=grade_5, name='A')
                enrollments_5a = Enrollment.objects.filter(section=section_a, status='ACTIVE')
                
                self.stdout.write(f"✅ Encontrados {enrollments_5a.count()} estudiantes en 5A")
                
                updated_count = 0
                for enrollment in enrollments_5a:
                    student = enrollment.student
                    user = student.user
                    
                    # Generar datos de apoderado basados en el nombre del estudiante
                    first_name = user.first_name.split()[0]  # Primer nombre
                    guardian_name = f"Apoderado de {first_name}"
                    guardian_phone = "999999999"  # Teléfono estándar como en 4F
                    
                    # Actualizar datos del estudiante
                    student.guardian_name = guardian_name
                    student.guardian_phone = guardian_phone
                    # La dirección se mantiene vacía como en 4F
                    student.save()
                    
                    updated_count += 1
                    self.stdout.write(f"✅ Actualizado: {user.first_name} {user.last_name} -> Apoderado: {guardian_name}")
                
                self.stdout.write(
                    self.style.SUCCESS(f"\n🎉 Proceso completado exitosamente!")
                )
                self.stdout.write(f"📊 Estadísticas:")
                self.stdout.write(f"   - Estudiantes actualizados: {updated_count}")
                self.stdout.write(f"   - Grado: {grade_5.name}")
                self.stdout.write(f"   - Sección: {section_a.name}")
                self.stdout.write(f"\n💡 Estructura aplicada (igual que 4F):")
                self.stdout.write(f"   - Dirección: Vacía")
                self.stdout.write(f"   - Apoderado: 'Apoderado de [Primer nombre]'")
                self.stdout.write(f"   - Teléfono apoderado: '999999999'")
                
        except Grade.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Error: No se encontró el grado 'QUINTO'")
            )
        except Section.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Error: No se encontró la sección 'A' en el grado QUINTO")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error inesperado: {str(e)}")
            ) 