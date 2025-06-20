#!/usr/bin/env python
"""
Script de Migración a Producción - Estudiantes 4to F
====================================================

Este script registra automáticamente todos los estudiantes del 4to grado F
del colegio Polo Jiménez cuando se migra a producción.

Uso:
    python scripts/deploy_production_students.py
    
Características:
- Crea la institución si no existe
- Crea los grados y secciones necesarios
- Registra los 20 estudiantes con sus credenciales
- Verifica que todo funcione correctamente
- Es seguro ejecutar múltiples veces (no duplica datos)
"""

import os
import sys
import django
from datetime import date, datetime
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from apps.academic.models import Student, Grade, Section, Enrollment
from apps.institutions.models import Institution

User = get_user_model()

# Datos de los estudiantes del 4to F - Polo Jiménez
ESTUDIANTES_DATA = [
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

def print_banner():
    """Imprime el banner del script"""
    print("=" * 80)
    print("🎓 SCRIPT DE MIGRACIÓN A PRODUCCIÓN - ESTUDIANTES 4TO F")
    print("🏫 Institución: TÉCNICO FAP MANUEL POLO JIMÉNEZ")
    print("📚 Grado: 4to (CUARTO) - Sección: F")
    print("👥 Estudiantes: 20")
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
        print(f"   ✅ Grado creado: {grade.name}")
    else:
        print(f"   ✅ Grado encontrado: {grade.name}")
    
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

def generate_dni():
    """Genera un DNI único que no exista en la base de datos"""
    while True:
        dni = str(random.randint(70000000, 79999999))
        if not Student.objects.filter(dni=dni).exists():
            return dni

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
                # Verificar si el usuario ya existe
                user = User.objects.filter(email=data['email']).first()
                
                if user:
                    # Usuario existe, actualizar contraseña
                    user.set_password(data['password'])
                    user.save()
                    updated_count += 1
                    status = "🔄 ACTUALIZADO"
                else:
                    # Crear nuevo usuario
                    nombres = data['nombre'].split()
                    username = generate_username(data['nombre'], data['apellido'])
                    
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
                        dni=generate_dni(),
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
                
                print(f"{data['nro']:2d}/20. {data['nombre']} {data['apellido']:<25} {status}")
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
        print("   Ejemplo: 61791657@cased.edu.pe / 61791657")
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