from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date
from apps.academic.models import Student, Grade, Section, Enrollment, Institution
import random

class Command(BaseCommand):
    help = 'Registra estudiantes de 5to grado sección A del colegio Polo Jiménez'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write("🎓 Iniciando registro de estudiantes de 5A...")
                
                # Obtener la institución
                institution = Institution.objects.get(name="TÉCNICO FAP MANUEL POLO JIMÉNEZ")
                self.stdout.write(f"✅ Institución encontrada: {institution.name}")
                
                # Obtener o crear el grado QUINTO
                grade, created = Grade.objects.get_or_create(
                    name='QUINTO',
                    defaults={
                        'level': 'SECUNDARIA',
                        'description': 'Quinto grado de secundaria',
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f"✅ Grado creado: {grade.name}")
                else:
                    self.stdout.write(f"✅ Grado encontrado: {grade.name}")
                
                # Obtener o crear la sección A
                section, created = Section.objects.get_or_create(
                    name='A',
                    grade=grade,
                    defaults={
                        'capacity': 30,
                        'current_students': 0,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f"✅ Sección creada: {section}")
                else:
                    self.stdout.write(f"✅ Sección encontrada: {section}")
                
                # Lista de estudiantes (corrigiendo el email duplicado)
                students_data = [
                    {
                        'nombres': 'Nicolle Elizabeth',
                        'apellidos': 'Cruz Clawijo',
                        'email': '61516890@cased.edu.pe',
                        'dni': '61516890',
                        'password': '61516890'
                    },
                    {
                        'nombres': 'Dayra',
                        'apellidos': 'Chunga Acosta',
                        'email': '61374502@cased.edu.pe',
                        'dni': '61374502',
                        'password': '61374502'
                    },
                    {
                        'nombres': 'Nephi Mijhail',
                        'apellidos': 'Chucos Villajulca',
                        'email': '62039094@cased.edu.pe',
                        'dni': '62039094',
                        'password': '62039094'
                    },
                    {
                        'nombres': 'Alexander Estefano',
                        'apellidos': 'Llica Torres',
                        'email': '61355415@cased.edu.pe',
                        'dni': '61355415',
                        'password': '61355415'
                    },
                    {
                        'nombres': 'Renzo Ulises',
                        'apellidos': 'Hipólito Acuña',
                        'email': '61516161@cased.edu.pe',
                        'dni': '61516161',
                        'password': '61516161'
                    },
                    {
                        'nombres': 'Pedro Manuel Fernando',
                        'apellidos': 'Taco Ruiz',
                        'email': '61471442@cased.edu.pe',
                        'dni': '61471442',
                        'password': '61471442'
                    },
                    {
                        'nombres': 'Romina Asly',
                        'apellidos': 'Quispe Saavedra',
                        'email': '62018970@cased.edu.pe',
                        'dni': '62018970',
                        'password': '62018970'
                    },
                    {
                        'nombres': 'Sofía',
                        'apellidos': 'Vera Aguayo',
                        'email': '62018718@cased.edu.pe',
                        'dni': '62018718',
                        'password': '62018718'
                    },
                    {
                        'nombres': 'Matías Gabriel',
                        'apellidos': 'Velázquez Quispe',
                        'email': '61366999@cased.edu.pe',
                        'dni': '61366999',
                        'password': '61366999'
                    },
                    {
                        'nombres': 'Oriana',
                        'apellidos': 'Tuesta Paulini',
                        'email': '71675298@cased.edu.pe',
                        'dni': '71675298',
                        'password': '71675298'
                    },
                    {
                        'nombres': 'Héctor',
                        'apellidos': 'Motello Portal',
                        'email': '61433594@cased.edu.pe',
                        'dni': '61433594',
                        'password': '61433594'
                    },
                    {
                        'nombres': 'Pedro',
                        'apellidos': 'Cahuana Díaz',
                        'email': '72584841@cased.edu.pe',
                        'dni': '72584841',
                        'password': '72584841'
                    },
                    {
                        'nombres': 'Joaquín Mateo',
                        'apellidos': 'Verona',
                        'email': '61755436@cased.edu.pe',
                        'dni': '61755436',
                        'password': '61755436'
                    },
                    {
                        'nombres': 'Dulce Maricielo',
                        'apellidos': 'Arselles Asunción',
                        'email': '61443053@cased.edu.pe',
                        'dni': '61443053',
                        'password': '61443053'
                    },
                    {
                        'nombres': 'Matías',
                        'apellidos': 'Chávez Romero',
                        'email': '62018899@cased.edu.pe',
                        'dni': '62018899',
                        'password': '62018899'
                    }
                ]
                
                # Registrar estudiantes
                created_count = 0
                for student_data in students_data:
                    try:
                        # Generar username único
                        base_username = f"{student_data['nombres'].lower().replace(' ', '_')}_{student_data['apellidos'].lower().replace(' ', '_')}"
                        # Limpiar caracteres especiales
                        base_username = base_username.replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                        
                        username = base_username[:30]  # Limitar longitud
                        counter = 1
                        original_username = username
                        while CustomUser.objects.filter(username=username).exists():
                            username = f"{original_username[:27]}_{counter}"
                            counter += 1
                        
                        # Crear usuario
                        user = CustomUser.objects.create_user(
                            username=username,
                            email=student_data['email'],
                            password=student_data['password'],
                            first_name=student_data['nombres'],
                            last_name=student_data['apellidos'],
                            role='student'
                        )
                        
                        # Generar fecha de nacimiento para edad 16-17 años
                        current_year = datetime.now().year
                        birth_year = current_year - random.choice([16, 17])
                        birth_month = random.randint(1, 12)
                        birth_day = random.randint(1, 28)
                        birth_date = date(birth_year, birth_month, birth_day)
                        
                        # Crear estudiante
                        student = Student.objects.create(
                            user=user,
                            dni=student_data['dni'],
                            birth_date=birth_date,
                            address='',
                            guardian_name='',
                            guardian_phone='',
                            is_active=True,
                            google_account_linked=False  # Acceso por login normal
                        )
                        
                        # Crear matrícula
                        enrollment = Enrollment.objects.create(
                            student=student,
                            section=section,
                            academic_year=str(datetime.now().year),
                            status='ACTIVE',
                            enrollment_date=datetime.now().date()
                        )
                        
                        # Actualizar contador de estudiantes en la sección
                        section.current_students += 1
                        section.save()
                        
                        created_count += 1
                        self.stdout.write(f"✅ Estudiante creado: {student_data['nombres']} {student_data['apellidos']} (Usuario: {username})")
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Error al crear estudiante {student_data['nombres']} {student_data['apellidos']}: {str(e)}")
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(f"\n🎉 Proceso completado exitosamente!")
                )
                self.stdout.write(f"📊 Estadísticas:")
                self.stdout.write(f"   - Estudiantes creados: {created_count}")
                self.stdout.write(f"   - Grado: {grade.name}")
                self.stdout.write(f"   - Sección: {section.name}")
                self.stdout.write(f"   - Institución: {institution.name}")
                self.stdout.write(f"\n💡 Características de las cuentas:")
                self.stdout.write(f"   - Edades: 16-17 años")
                self.stdout.write(f"   - Acceso: Login normal (usuario/contraseña)")
                self.stdout.write(f"   - Google OAuth: Deshabilitado")
                self.stdout.write(f"   - Ejemplo de login: {students_data[0]['email']} / {students_data[0]['password']}")
                
        except Institution.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ Error: No se encontró la institución 'TÉCNICO FAP MANUEL POLO JIMÉNEZ'")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error inesperado: {str(e)}")
            ) 