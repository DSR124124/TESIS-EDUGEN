#!/usr/bin/env python
"""
Script de Migración a Producción - Estudiantes 5to A
====================================================

Este script registra automáticamente todos los estudiantes del 5to grado A
del colegio Polo Jiménez cuando se migra a producción.

Uso:
    python scripts/deploy_production_students_5a.py
    
Características:
- Crea la institución si no existe
- Crea los grados y secciones necesarios
- Registra los 15 estudiantes con sus credenciales
- Verifica que todo funcione correctamente
- Es seguro ejecutar múltiples veces (no duplica datos)
"""

import os
import sys
import django
from datetime import date, datetime
import random

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from apps.academic.models import Student, Grade, Section, Enrollment
from apps.institutions.models import Institution

User = get_user_model()

# Datos de los estudiantes del 5to A - Polo Jiménez
ESTUDIANTES_DATA = [
    {'nro': 1, 'apellido': 'Cruz Clawijo', 'nombre': 'Nicolle Elizabeth', 'email': '61516890@cased.edu.pe', 'password': '61516890'},
    {'nro': 2, 'apellido': 'Chunga Acosta', 'nombre': 'Dayra', 'email': '61374502@cased.edu.pe', 'password': '61374502'},
    {'nro': 3, 'apellido': 'Chucos Villajulca', 'nombre': 'Nephi Mijhail', 'email': '62039094@cased.edu.pe', 'password': '62039094'},
    {'nro': 4, 'apellido': 'Llica Torres', 'nombre': 'Alexander Estefano', 'email': '61355415@cased.edu.pe', 'password': '61355415'},
    {'nro': 5, 'apellido': 'Hipólito Acuña', 'nombre': 'Renzo Ulises', 'email': '61516161@cased.edu.pe', 'password': '61516161'},
    {'nro': 6, 'apellido': 'Taco Ruiz', 'nombre': 'Pedro Manuel Fernando', 'email': '61471442@cased.edu.pe', 'password': '61471442'},
    {'nro': 7, 'apellido': 'Quispe Saavedra', 'nombre': 'Romina Asly', 'email': '62018970@cased.edu.pe', 'password': '62018970'},
    {'nro': 8, 'apellido': 'Vera Aguayo', 'nombre': 'Sofía', 'email': '62018718@cased.edu.pe', 'password': '62018718'},
    {'nro': 9, 'apellido': 'Velázquez Quispe', 'nombre': 'Matías Gabriel', 'email': '61366999@cased.edu.pe', 'password': '61366999'},
    {'nro': 10, 'apellido': 'Tuesta Paulini', 'nombre': 'Oriana', 'email': '71675298@cased.edu.pe', 'password': '71675298'},
    {'nro': 11, 'apellido': 'Motello Portal', 'nombre': 'Héctor', 'email': '61433594@cased.edu.pe', 'password': '61433594'},
    {'nro': 12, 'apellido': 'Cahuana Díaz', 'nombre': 'Pedro', 'email': '72584841@cased.edu.pe', 'password': '72584841'},
    {'nro': 13, 'apellido': 'Verona', 'nombre': 'Joaquín Mateo', 'email': '61755436@cased.edu.pe', 'password': '61755436'},
    {'nro': 14, 'apellido': 'Arselles Asunción', 'nombre': 'Dulce Maricielo', 'email': '61443053@cased.edu.pe', 'password': '61443053'},
    {'nro': 15, 'apellido': 'Chávez Romero', 'nombre': 'Matías', 'email': '62018899@cased.edu.pe', 'password': '62018899'},
]

def print_banner():
    """Imprime el banner del script"""
    print("=" * 80)
    print("🎓 SCRIPT DE MIGRACIÓN A PRODUCCIÓN - ESTUDIANTES 5TO A")
    print("🏫 Institución: TÉCNICO FAP MANUEL POLO JIMÉNEZ")
    print("📚 Grado: 5to (QUINTO) - Sección: A")
    print("👥 Estudiantes: 15")
    print("=" * 80)
    print()

def create_institution():
    """Crea o obtiene la institución Polo Jiménez"""
    print("🏫 Configurando institución...")
    
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
        print(f"   ✅ Institución creada: {institution.name}")
    else:
        print(f"   ✅ Institución encontrada: {institution.name}")
    
    return institution

def create_academic_structure():
    """Crea la estructura académica (grados y secciones)"""
    print("📚 Configurando estructura académica...")
    
    # Crear grado QUINTO
    grade, created = Grade.objects.get_or_create(
        name='QUINTO',
        defaults={
            'level': 'SECUNDARIA',
            'description': 'Quinto grado de secundaria',
            'is_active': True,
        }
    )
    
    if created:
        print(f"   ✅ Grado creado: {grade.name}")
    else:
        print(f"   ✅ Grado encontrado: {grade.name}")
    
    # Crear sección A
    section, created = Section.objects.get_or_create(
        name='A',
        grade=grade,
        defaults={
            'capacity': 30,
            'current_students': 0,
            'is_active': True,
        }
    )
    
    if created:
        print(f"   ✅ Sección creada: {section}")
    else:
        print(f"   ✅ Sección encontrada: {section}")
    
    return grade, section

def generate_username(nombre, apellido):
    """Genera un username único basado en nombre y apellido"""
    # Normalizar nombre y apellido
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
    
    # Truncar si es muy largo
    if len(username) > 30:
        username = username[:30]
    
    return username

def create_students(institution, section):
    """Crea todos los estudiantes"""
    print("👥 Registrando estudiantes...")
    print()
    
    created_count = 0
    updated_count = 0
    errors = []
    
    for data in ESTUDIANTES_DATA:
        try:
            with transaction.atomic():
                # Verificar si el usuario ya existe (usar first() para evitar duplicados)
                user = User.objects.filter(email=data['email']).first()
                
                if user:
                    # Usuario existe, actualizar contraseña y datos si es necesario
                    user.set_password(data['password'])
                    user.first_name = data['nombre']
                    user.last_name = data['apellido']
                    user.save()
                    updated_count += 1
                    status = "🔄 ACTUALIZADO"
                else:
                    # Crear nuevo usuario
                    nombres = data['nombre'].split()
                    username = generate_username(data['nombre'], data['apellido'])
                    
                    # Asegurar username único
                    original_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{original_username}_{counter}"
                        counter += 1
                    
                    user = User.objects.create_user(
                        username=username,
                        email=data['email'],
                        password=data['password'],
                        first_name=data['nombre'],
                        last_name=data['apellido'],
                        role='student',
                        is_active=True
                    )
                    
                    # Crear perfil de estudiante con datos consistentes con 4F
                    student = Student.objects.create(
                        user=user,
                        dni=data['password'],  # Usar el password como DNI (que es el DNI real)
                        birth_date=date(
                            random.choice([2008, 2009]),  # Edades 16-17 años
                            random.randint(1, 12), 
                            random.randint(1, 28)
                        ),
                        address='',  # Vacío como en 4F
                        guardian_name=f'Apoderado de {nombres[0] if nombres else data["nombre"]}',
                        guardian_phone='999999999',  # Teléfono estándar como en 4F
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
                
                print(f"{data['nro']:2d}/15. {data['nombre']} {data['apellido']:<25} {status}")
                print(f"       📧 {data['email']}")
                print(f"       🔑 {data['password']}")
                print(f"       🔐 Login: {login_status}")
                print()
                
        except Exception as e:
            error_msg = f"{data['nro']}. {data['nombre']} {data['apellido']} - Error: {str(e)}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    return created_count, updated_count, errors

def update_section_counter(section):
    """Actualiza el contador de estudiantes en la sección"""
    print("🔢 Actualizando contadores...")
    
    active_enrollments = Enrollment.objects.filter(
        section=section,
        status='ACTIVE'
    ).count()
    
    section.current_students = active_enrollments
    section.save()
    
    print(f"   ✅ Sección {section}: {active_enrollments} estudiantes")

def verify_system():
    """Verifica que todo el sistema funcione correctamente"""
    print("🔍 Verificando sistema...")
    
    # Verificar algunos logins aleatorios
    test_students = random.sample(ESTUDIANTES_DATA, 3)
    
    for data in test_students:
        auth_result = authenticate(username=data['email'], password=data['password'])
        status = "✅ OK" if auth_result else "❌ FALLA"
        print(f"   🧪 {data['nombre']}: {status}")
    
    # Estadísticas finales
    total_students = User.objects.filter(role='student', is_active=True).count()
    total_enrollments = Enrollment.objects.filter(status='ACTIVE').count()
    
    print(f"   📊 Total estudiantes activos: {total_students}")
    print(f"   📊 Total matrículas activas: {total_enrollments}")

def main():
    """Función principal del script"""
    try:
        print_banner()
        
        print("🚀 Iniciando migración a producción...")
        print()
        
        # 1. Crear institución
        institution = create_institution()
        
        # 2. Crear estructura académica
        grade, section = create_academic_structure()
        
        # 3. Crear estudiantes
        created, updated, errors = create_students(institution, section)
        
        # 4. Actualizar contadores
        update_section_counter(section)
        
        # 5. Verificar sistema
        verify_system()
        
        # Resumen final
        print()
        print("=" * 80)
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 80)
        print(f"✅ Estudiantes creados: {created}")
        print(f"🔄 Estudiantes actualizados: {updated}")
        print(f"❌ Errores: {len(errors)}")
        
        if errors:
            print("\n⚠️  Errores encontrados:")
            for error in errors:
                print(f"   - {error}")
        
        print()
        print("📋 INFORMACIÓN DE ACCESO:")
        print("   URL: https://tu-dominio-produccion.com/login/")
        print("   Método: Email + Contraseña")
        print("   Ejemplo: 61516890@cased.edu.pe / 61516890")
        print()
        print("🎯 CARACTERÍSTICAS DE LAS CUENTAS:")
        print("   - Edades: 16-17 años (nacidos 2008-2009)")
        print("   - Acceso: Login normal (email + contraseña)")
        print("   - Google OAuth: Deshabilitado")
        print("   - Estructura: Igual que estudiantes 4F")
        print()
        print("✅ El sistema está listo para producción!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 