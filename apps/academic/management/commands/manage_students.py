from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.academic.models import Student
from apps.institutions.models import Institution
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Gestiona estudiantes con autenticación dual (contraseña + Google OAuth)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create', 
            action='store_true',
            help='Crear estudiantes de ejemplo'
        )
        parser.add_argument(
            '--list', 
            action='store_true',
            help='Listar todos los estudiantes'
        )
        parser.add_argument(
            '--reset-passwords', 
            action='store_true',
            help='Resetear contraseñas de estudiantes'
        )
        parser.add_argument(
            '--enable-google', 
            type=str,
            help='Habilitar Google OAuth para un estudiante (por email)'
        )
        parser.add_argument(
            '--disable-google', 
            type=str,
            help='Deshabilitar Google OAuth para un estudiante (por email)'
        )

    def handle(self, *args, **options):
        if options['create']:
            self.create_example_students()
        elif options['list']:
            self.list_students()
        elif options['reset_passwords']:
            self.reset_passwords()
        elif options['enable_google']:
            self.enable_google_oauth(options['enable_google'])
        elif options['disable_google']:
            self.disable_google_oauth(options['disable_google'])
        else:
            self.stdout.write(
                self.style.WARNING('Usa --help para ver las opciones disponibles')
            )

    def create_example_students(self):
        """Crear estudiantes de ejemplo"""
        self.stdout.write("🎓 Creando estudiantes de ejemplo...")
        
        # Obtener institución
        try:
            institution = Institution.objects.first()
            if not institution:
                self.stdout.write(
                    self.style.ERROR('❌ No hay instituciones disponibles')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error obteniendo institución: {e}')
            )
            return

        estudiantes = [
            {
                'username': 'ana_garcia',
                'first_name': 'Ana',
                'last_name': 'García López',
                'email': 'ana.garcia@tecnicofap.edu.pe',
                'dni': '12345678',
                'birth_date': '2005-03-15',
                'guardian_name': 'María López',
                'guardian_phone': '987654321'
            },
            {
                'username': 'carlos_mendoza',
                'first_name': 'Carlos',
                'last_name': 'Mendoza Rivera',
                'email': 'carlos.mendoza@tecnicofap.edu.pe',
                'dni': '23456789',
                'birth_date': '2005-07-22',
                'guardian_name': 'Pedro Mendoza',
                'guardian_phone': '987654322'
            },
            {
                'username': 'sofia_hernandez',
                'first_name': 'Sofía',
                'last_name': 'Hernández Torres',
                'email': 'sofia.hernandez@tecnicofap.edu.pe',
                'dni': '34567890',
                'birth_date': '2005-11-08',
                'guardian_name': 'Carmen Torres',
                'guardian_phone': '987654323'
            }
        ]

        created_count = 0
        for est_data in estudiantes:
            try:
                # Verificar si ya existe
                if User.objects.filter(email=est_data['email']).exists():
                    self.stdout.write(f"⏭️ {est_data['first_name']} {est_data['last_name']}: Ya existe")
                    continue

                # Crear usuario
                user = User.objects.create_user(
                    username=est_data['username'],
                    email=est_data['email'],
                    password='estudiante123',
                    first_name=est_data['first_name'],
                    last_name=est_data['last_name'],
                    role='student',
                    is_active=True
                )

                # Crear perfil de estudiante
                Student.objects.create(
                    user=user,
                    dni=est_data['dni'],
                    birth_date=est_data['birth_date'],
                    guardian_name=est_data['guardian_name'],
                    guardian_phone=est_data['guardian_phone'],
                    is_active=True,
                    google_account_linked=False
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {est_data['first_name']} {est_data['last_name']} - Usuario: {est_data['username']}"
                    )
                )
                created_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error creando {est_data['first_name']}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"🎉 {created_count} estudiantes creados exitosamente")
        )

    def list_students(self):
        """Listar todos los estudiantes"""
        self.stdout.write("👥 LISTA DE ESTUDIANTES")
        self.stdout.write("=" * 50)
        
        students = Student.objects.all().select_related('user').order_by('user__first_name')
        
        if not students.exists():
            self.stdout.write(self.style.WARNING("❌ No hay estudiantes registrados"))
            return

        for student in students:
            user = student.user
            google_status = "🔗 Sí" if student.google_account_linked else "❌ No"
            active_status = "✅ Activo" if user.is_active else "❌ Inactivo"
            
            self.stdout.write(f"👤 {user.get_full_name()}")
            self.stdout.write(f"   📧 Email: {user.email}")
            self.stdout.write(f"   🔑 Usuario: {user.username}")
            self.stdout.write(f"   📋 DNI: {student.dni}")
            self.stdout.write(f"   🔗 Google: {google_status}")
            self.stdout.write(f"   📱 Estado: {active_status}")
            self.stdout.write("")

    def reset_passwords(self):
        """Resetear contraseñas de todos los estudiantes"""
        self.stdout.write("🔄 Reseteando contraseñas de estudiantes...")
        
        students = Student.objects.all().select_related('user')
        reset_count = 0
        
        for student in students:
            try:
                student.user.set_password('estudiante123')
                student.user.is_active = True
                student.user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {student.user.get_full_name()} - Nueva contraseña: estudiante123"
                    )
                )
                reset_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error con {student.user.get_full_name()}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎉 {reset_count} contraseñas reseteadas")
        )

    def enable_google_oauth(self, email):
        """Habilitar Google OAuth para un estudiante"""
        try:
            user = User.objects.get(email=email)
            student = user.student_profile
            
            student.google_account = email
            student.google_account_linked = True
            student.google_linked_at = timezone.now()
            student.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Google OAuth habilitado para {user.get_full_name()}"
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ No se encontró estudiante con email: {email}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error: {e}")
            )

    def disable_google_oauth(self, email):
        """Deshabilitar Google OAuth para un estudiante"""
        try:
            user = User.objects.get(email=email)
            student = user.student_profile
            
            student.google_account = None
            student.google_account_linked = False
            student.google_linked_at = None
            student.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Google OAuth deshabilitado para {user.get_full_name()}"
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ No se encontró estudiante con email: {email}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error: {e}")
            ) 