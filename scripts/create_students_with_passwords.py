#!/usr/bin/env python
"""
Script para crear estudiantes con contraseñas predeterminadas
Uso: python scripts/create_students_with_passwords.py
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')
django.setup()

from apps.accounts.models import CustomUser
from apps.academic.models import Student
from apps.institutions.models import Institution
from django.contrib.auth.hashers import make_password

def create_students_with_passwords():
    """Crear estudiantes con contraseñas predeterminadas"""
    print("🎓 CREANDO ESTUDIANTES CON CONTRASEÑAS")
    print("=" * 50)
    
    # Obtener institución
    try:
        institution = Institution.objects.get(name="TÉCNICO FAP MANUEL POLO JIMÉNEZ")
        print(f"✅ Institución encontrada: {institution.name}")
    except Institution.DoesNotExist:
        print("❌ Error: Institución no encontrada")
        return False
    
    # Lista de estudiantes de ejemplo
    estudiantes = [
        {
            'username': 'estudiante01',
            'first_name': 'Ana',
            'last_name': 'García López',
            'email': 'ana.garcia@tecnicofap.edu.pe',
            'password': 'estudiante123',
            'dni': '12345678',
            'birth_date': '2005-03-15',
            'guardian_name': 'María López',
            'guardian_phone': '987654321'
        },
        {
            'username': 'estudiante02', 
            'first_name': 'Carlos',
            'last_name': 'Mendoza Rivera',
            'email': 'carlos.mendoza@tecnicofap.edu.pe',
            'password': 'estudiante123',
            'dni': '23456789',
            'birth_date': '2005-07-22',
            'guardian_name': 'Pedro Mendoza',
            'guardian_phone': '987654322'
        },
        {
            'username': 'estudiante03',
            'first_name': 'Sofía',
            'last_name': 'Hernández Torres',
            'email': 'sofia.hernandez@tecnicofap.edu.pe', 
            'password': 'estudiante123',
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
            if CustomUser.objects.filter(email=est_data['email']).exists():
                print(f"⏭️ {est_data['first_name']} {est_data['last_name']}: Ya existe")
                continue
            
            # Crear usuario
            user = CustomUser.objects.create_user(
                username=est_data['username'],
                email=est_data['email'],
                password=est_data['password'],
                first_name=est_data['first_name'],
                last_name=est_data['last_name'],
                role='student',
                is_active=True
            )
            
            # Crear perfil de estudiante
            student = Student.objects.create(
                user=user,
                dni=est_data['dni'],
                birth_date=est_data['birth_date'],
                guardian_name=est_data['guardian_name'],
                guardian_phone=est_data['guardian_phone'],
                is_active=True,
                google_account_linked=False
            )
            
            print(f"✅ {est_data['first_name']} {est_data['last_name']}")
            print(f"   📧 Email: {est_data['email']}")
            print(f"   👤 Usuario: {est_data['username']}")
            print(f"   🔑 Contraseña: {est_data['password']}")
            print(f"   📋 DNI: {est_data['dni']}")
            print()
            
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creando {est_data['first_name']}: {e}")
    
    print(f"🎉 {created_count} estudiantes creados exitosamente")
    return True

def show_login_instructions():
    """Mostrar instrucciones de login para estudiantes"""
    print("\n📋 INSTRUCCIONES DE LOGIN PARA ESTUDIANTES")
    print("=" * 50)
    print("Los estudiantes pueden iniciar sesión de dos formas:")
    print()
    print("1️⃣ CON USUARIO Y CONTRASEÑA:")
    print("   • Usuario: estudiante01, estudiante02, estudiante03")
    print("   • Contraseña: estudiante123")
    print("   • URL: https://tu-app.azurewebsites.net/login/")
    print()
    print("2️⃣ CON CORREO Y CONTRASEÑA:")
    print("   • Email: ana.garcia@tecnicofap.edu.pe")
    print("   • Contraseña: estudiante123")
    print()
    print("3️⃣ CON GOOGLE OAUTH (si tienen Gmail):")
    print("   • Hacer clic en 'Iniciar sesión con Google'")
    print()
    print("⚠️ IMPORTANTE: Los estudiantes DEBEN estar matriculados")
    print("   en una sección para acceder al dashboard completo.")

def reset_student_passwords():
    """Resetear contraseñas de estudiantes existentes"""
    print("\n🔄 RESETEANDO CONTRASEÑAS DE ESTUDIANTES")
    print("=" * 50)
    
    students = Student.objects.all()
    reset_count = 0
    
    for student in students:
        try:
            # Establecer contraseña predeterminada
            student.user.set_password('estudiante123')
            student.user.is_active = True
            student.user.save()
            
            print(f"✅ {student.user.first_name} {student.user.last_name}")
            print(f"   📧 Email: {student.user.email}")
            print(f"   🔑 Nueva contraseña: estudiante123")
            
            reset_count += 1
        except Exception as e:
            print(f"❌ Error con {student.user.first_name}: {e}")
    
    print(f"\n🎉 {reset_count} contraseñas reseteadas")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        # Resetear contraseñas existentes
        reset_student_passwords()
    else:
        # Crear nuevos estudiantes
        create_students_with_passwords()
    
    show_login_instructions() 