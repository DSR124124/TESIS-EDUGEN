from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from datetime import date, datetime
import random

from apps.academic.models import Student, Grade, Section, Enrollment
from apps.institutions.models import Institution

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura automáticamente los estudiantes del 4to F - Polo Jiménez para producción'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la recreación de estudiantes existentes',
        )
        parser.add_argument(
            '--verify-only',
            action='store_true',
            help='Solo verifica el estado actual sin hacer cambios',
        )

    def handle(self, *args, **options):
        self.force = options['force']
        self.verify_only = options['verify_only']
        
        # Datos de los estudiantes
        self.estudiantes_data = [
            {'nro': 1, 'apellido': 'Serna Ventura', 'nombre': 'Carlos Eduardo', 'email': '61791657@cased.edu.pe', 'password': '61791657'},
            {'nro': 2, 'apellido': 'Obregón Escudero', 'nombre': 'Gabriela Isabel', 'email': '61912715@cased.edu.pe', 'password': '61912715'},
            {'nro': 3, 'apellido': 'Orejuela Rentería', 'nombre': 'Luciana Brigitte', 'email': '61996238@cased.edu.pe', 'password': '61996238'},
            {'nro': 4, 'apellido': 'Chalco Cardenas', 'nombre': 'Chanel Yazmín', 'email': '73921044@cased.edu.pe', 'password': '73921044'},
            {'nro': 5, 'apellido': 'Ruiz Mera', 'nombre': 'Brunella Alejandra', 'email': '61907427@cased.edu.pe', 'password': '61907427'},
            {'nro': 6, 'apellido': 'Vilca Quiroz', 'nombre': 'Alvaro Fabian', 'email': '61912578@cased.edu.pe', 'password': '61912578'},
            {'nro': 7, 'apellido': 'Sánchez Sullón', 'nombre': 'Mateo Martín', 'email': '73724440@cased.edu.pe', 'password': '73724440'},
            {'nro': 8, 'apellido': 'Edones Castro', 'nombre': 'Gabriela Alexandra', 'email': '61933419@cased.edu.pe', 'password': '61933419'},
            {'nro': 9, 'apellido': 'Saavedra Tavara', 'nombre': 'Valeria Deyanira', 'email': '61851650@cased.edu.pe', 'password': '61851650'},
            {'nro': 10, 'apellido': 'Lazo Adrianzen', 'nombre': 'Nicolás Carlos', 'email': '62544018@cased.edu.pe', 'password': '62544018'},
            {'nro': 11, 'apellido': 'Silupú Chavez', 'nombre': 'Henry Pabbov', 'email': '61912911@cased.edu.pe', 'password': '61912911'},
            {'nro': 12, 'apellido': 'Mori', 'nombre': 'Tiago Arie', 'email': '73846445@cased.edu.pe', 'password': '73846445'},
            {'nro': 13, 'apellido': 'Vera Ortiz', 'nombre': 'Miguel Ángel', 'email': '72583221@cased.edu.pe', 'password': '72583221'},
            {'nro': 14, 'apellido': 'Cardenas Esculonte', 'nombre': 'Luis Fernando', 'email': '61792050@cased.edu.pe', 'password': '61792050'},
            {'nro': 15, 'apellido': 'Beaumont Narro', 'nombre': 'Adrianna Alessandra', 'email': '61851954@cased.edu.pe', 'password': '61851954'},
            {'nro': 16, 'apellido': 'Zaga Toro', 'nombre': 'Dominyk Emmanuel', 'email': '73400838@cased.edu.pe', 'password': '73400838'},
            {'nro': 17, 'apellido': 'Arica Paxi', 'nombre': 'José Alonso', 'email': '73839017@cased.edu.pe', 'password': '73839017'},
            {'nro': 18, 'apellido': 'Reyes Ramos', 'nombre': 'Saul Santiago', 'email': '73718377@cased.edu.pe', 'password': '73718377'},
            {'nro': 19, 'apellido': 'Torres Ramírez', 'nombre': 'Yaritza Thais', 'email': '61792348@cased.edu.pe', 'password': '61792348'},
            {'nro': 20, 'apellido': 'Ortega Falconi', 'nombre': 'Ariana Valentina', 'email': '73914527@cased.edu.pe', 'password': '73914527'},
        ]

        try:
            self.print_banner()
            
            if self.verify_only:
                self.verify_system()
                return
            
            # 1. Crear/verificar institución
            institution = self.setup_institution()
            
            # 2. Crear/verificar estructura académica
            grade, section = self.setup_academic_structure()
            
            # 3. Crear/actualizar estudiantes
            created, updated, errors = self.setup_students(institution, section)
            
            # 4. Actualizar contadores
            self.update_section_counter(section)
            
            # 5. Verificar sistema
            self.verify_system()
            
            # Resumen final
            self.print_summary(created, updated, errors)
            
        except Exception as e:
            raise CommandError(f'Error en la configuración: {str(e)}')

    def print_banner(self):
        """Imprime el banner del comando"""
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("🎓 CONFIGURACIÓN PRODUCCIÓN - ESTUDIANTES 4TO F"))
        self.stdout.write(self.style.WARNING("🏫 Institución: TÉCNICO FAP MANUEL POLO JIMÉNEZ"))
        self.stdout.write(self.style.WARNING("📚 Grado: 4to (CUARTO) - Sección: F"))
        self.stdout.write(self.style.WARNING("👥 Estudiantes: 20"))
        self.stdout.write("=" * 80)

    def setup_institution(self):
        """Crea o obtiene la institución"""
        self.stdout.write("\n🏫 Configurando institución...")
        
        institution, created = Institution.objects.get_or_create(
            name='TÉCNICO FAP MANUEL POLO JIMÉNEZ',
            defaults={
                'code': 'POLO-JIMENEZ',
                'domain': 'cased.edu.pe',
                'address': 'Lima, Perú',
                'phone': '01-234-5678',
                'email': 'info@cased.edu.pe',
                'type': 'TECNICO',
                'established_year': 1980,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f"   ✅ Institución creada: {institution.name}")
        else:
            self.stdout.write(f"   ✅ Institución encontrada: {institution.name}")
        
        return institution

    def setup_academic_structure(self):
        """Crea la estructura académica"""
        self.stdout.write("📚 Configurando estructura académica...")
        
        # Crear grado CUARTO
        grade, created = Grade.objects.get_or_create(
            name='CUARTO',
            defaults={
                'level': 'SECUNDARIA',
                'description': 'Cuarto grado de secundaria',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f"   ✅ Grado creado: {grade.name}")
        else:
            self.stdout.write(f"   ✅ Grado encontrado: {grade.name}")
        
        # Crear sección F
        section, created = Section.objects.get_or_create(
            name='F',
            grade=grade,
            defaults={
                'capacity': 30,
                'current_students': 0,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f"   ✅ Sección creada: {section}")
        else:
            self.stdout.write(f"   ✅ Sección encontrada: {section}")
        
        return grade, section

    def generate_username(self, nombre, apellido):
        """Genera un username único"""
        nombre_clean = nombre.lower().replace(' ', '_')
        apellido_clean = apellido.lower().replace(' ', '_').replace('ñ', 'n')
        
        # Remover acentos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ü': 'u', 'ç': 'c'
        }
        
        for old, new in replacements.items():
            nombre_clean = nombre_clean.replace(old, new)
            apellido_clean = apellido_clean.replace(old, new)
        
        username = f"{nombre_clean}_{apellido_clean}"
        
        if len(username) > 30:
            username = username[:30]
        
        return username

    def generate_dni(self):
        """Genera un DNI único"""
        while True:
            dni = str(random.randint(70000000, 79999999))
            if not Student.objects.filter(dni=dni).exists():
                return dni

    def setup_students(self, institution, section):
        """Crea o actualiza todos los estudiantes"""
        self.stdout.write("\n👥 Configurando estudiantes...")
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for data in self.estudiantes_data:
            try:
                with transaction.atomic():
                    # Verificar si el usuario ya existe
                    user = User.objects.filter(email=data['email']).first()
                    
                    if user and not self.force:
                        # Usuario existe, solo actualizar contraseña
                        user.set_password(data['password'])
                        user.save()
                        updated_count += 1
                        status = "🔄 ACTUALIZADO"
                    else:
                        if user and self.force:
                            # Eliminar usuario existente si se fuerza
                            user.delete()
                        
                        # Crear nuevo usuario
                        nombres = data['nombre'].split()
                        username = self.generate_username(data['nombre'], data['apellido'])
                        
                        user = User.objects.create_user(
                            username=username,
                            email=data['email'],
                            password=data['password'],
                            first_name=nombres[0] if nombres else data['nombre'],
                            last_name=data['apellido'],
                            role='student',
                            is_active=True
                        )
                        
                        # Crear perfil de estudiante
                        student = Student.objects.create(
                            user=user,
                            dni=self.generate_dni(),
                            birth_date=date(random.choice([2008, 2009]), random.randint(1, 12), random.randint(1, 28)),
                            address='Lima, Perú',
                            guardian_name=f'Apoderado de {nombres[0] if nombres else data["nombre"]}',
                            guardian_phone=f'9{random.randint(10000000, 99999999)}',
                            is_active=True,
                            google_account_linked=False
                        )
                        
                        # Crear matrícula
                        enrollment, enrollment_created = Enrollment.objects.get_or_create(
                            student=student,
                            section=section,
                            defaults={
                                'academic_year': str(datetime.now().year),
                                'status': 'ACTIVE',
                                'enrollment_date': date.today(),
                            }
                        )
                        
                        created_count += 1
                        status = "✅ CREADO"
                    
                    # Verificar autenticación
                    auth_result = authenticate(username=data['email'], password=data['password'])
                    login_status = "✅" if auth_result else "❌"
                    
                    self.stdout.write(f"{data['nro']:2d}/20. {data['nombre']} {data['apellido']:<25} {status}")
                    self.stdout.write(f"       📧 {data['email']}")
                    self.stdout.write(f"       🔐 Login: {login_status}")
                    
            except Exception as e:
                error_msg = f"{data['nro']}. {data['nombre']} {data['apellido']} - Error: {str(e)}"
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
        
        return created_count, updated_count, errors

    def update_section_counter(self, section):
        """Actualiza el contador de estudiantes"""
        self.stdout.write("\n🔢 Actualizando contadores...")
        
        active_enrollments = Enrollment.objects.filter(
            section=section,
            status='ACTIVE'
        ).count()
        
        section.current_students = active_enrollments
        section.save()
        
        self.stdout.write(f"   ✅ Sección {section}: {active_enrollments} estudiantes")

    def verify_system(self):
        """Verifica el sistema"""
        self.stdout.write("\n🔍 Verificando sistema...")
        
        # Verificar algunos logins aleatorios
        test_students = random.sample(self.estudiantes_data, min(3, len(self.estudiantes_data)))
        
        for data in test_students:
            auth_result = authenticate(username=data['email'], password=data['password'])
            status = "✅ OK" if auth_result else "❌ FALLA"
            self.stdout.write(f"   🧪 {data['nombre']}: {status}")
        
        # Estadísticas
        total_students = User.objects.filter(role='student', is_active=True).count()
        total_enrollments = Enrollment.objects.filter(status='ACTIVE').count()
        polo_students = User.objects.filter(
            role='student',
            is_active=True,
            email__endswith='@cased.edu.pe'
        ).count()
        
        self.stdout.write(f"   📊 Total estudiantes activos: {total_students}")
        self.stdout.write(f"   📊 Total matrículas activas: {total_enrollments}")
        self.stdout.write(f"   📊 Estudiantes Polo Jiménez: {polo_students}")

    def print_summary(self, created, updated, errors):
        """Imprime el resumen final"""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("🎉 ¡CONFIGURACIÓN COMPLETADA!"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"✅ Estudiantes creados: {created}")
        self.stdout.write(f"🔄 Estudiantes actualizados: {updated}")
        self.stdout.write(f"❌ Errores: {len(errors)}")
        
        if errors:
            self.stdout.write(self.style.WARNING("\n⚠️  Errores encontrados:"))
            for error in errors:
                self.stdout.write(f"   - {error}")
        
        self.stdout.write("\n📋 INFORMACIÓN DE ACCESO:")
        self.stdout.write("   Método: Email + Contraseña")
        self.stdout.write("   Ejemplo: 61791657@cased.edu.pe / 61791657")
        self.stdout.write("\n✅ Sistema listo para producción!")
        self.stdout.write("=" * 80) 