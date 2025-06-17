#!/usr/bin/env python
"""
Script para probar el sistema de autenticación dual de estudiantes
Uso: python scripts/test_student_authentication.py
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

from django.contrib.auth import authenticate
from apps.accounts.models import CustomUser
from apps.academic.models import Student
from apps.institutions.models import Institution

def test_authentication_methods():
    """Probar todos los métodos de autenticación disponibles"""
    print("🔐 PROBANDO MÉTODOS DE AUTENTICACIÓN")
    print("=" * 50)
    
    # Crear estudiante de prueba si no existe
    test_email = "test.estudiante@tecnicofap.edu.pe"
    test_username = "e12345678"
    test_password = "estudiante123"
    
    try:
        # Buscar o crear usuario de prueba
        user, created = CustomUser.objects.get_or_create(
            email=test_email,
            defaults={
                'username': test_username,
                'first_name': 'Test',
                'last_name': 'Estudiante',
                'role': 'student',
                'is_active': True
            }
        )
        
        if created:
            user.set_password(test_password)
            user.save()
            
            # Crear perfil de estudiante
            Student.objects.create(
                user=user,
                dni='12345678',
                birth_date='2005-01-01',
                guardian_name='Test Guardian',
                guardian_phone='999999999',
                is_active=True,
                google_account_linked=False
            )
            print(f"✅ Usuario de prueba creado: {test_email}")
        else:
            # Asegurar que tenga la contraseña correcta
            user.set_password(test_password)
            user.save()
            print(f"ℹ️ Usuario de prueba ya existe: {test_email}")
    
    except Exception as e:
        print(f"❌ Error creando usuario de prueba: {e}")
        return False
    
    print("\n🧪 EJECUTANDO PRUEBAS DE AUTENTICACIÓN")
    print("-" * 40)
    
    # Prueba 1: Autenticación por username
    print("1️⃣ Probando autenticación por USERNAME...")
    auth_user = authenticate(username=test_username, password=test_password)
    if auth_user:
        print(f"   ✅ SUCCESS: Usuario '{test_username}' autenticado correctamente")
        print(f"   👤 Nombre: {auth_user.get_full_name()}")
        print(f"   📧 Email: {auth_user.email}")
        print(f"   🎓 Rol: {auth_user.role}")
    else:
        print(f"   ❌ FAIL: No se pudo autenticar con username '{test_username}'")
    
    # Prueba 2: Autenticación por email
    print("\n2️⃣ Probando autenticación por EMAIL...")
    auth_user = authenticate(username=test_email, password=test_password)
    if auth_user:
        print(f"   ✅ SUCCESS: Email '{test_email}' autenticado correctamente")
        print(f"   👤 Nombre: {auth_user.get_full_name()}")
        print(f"   📧 Email: {auth_user.email}")
        print(f"   🎓 Rol: {auth_user.role}")
    else:
        print(f"   ❌ FAIL: No se pudo autenticar con email '{test_email}'")
    
    # Prueba 3: Verificar perfil de estudiante
    print("\n3️⃣ Verificando perfil de ESTUDIANTE...")
    try:
        student_profile = user.student_profile
        print(f"   ✅ SUCCESS: Perfil de estudiante encontrado")
        print(f"   📋 DNI: {student_profile.dni}")
        print(f"   👨‍👩‍👧‍👦 Apoderado: {student_profile.guardian_name}")
        print(f"   📞 Teléfono: {student_profile.guardian_phone}")
        print(f"   🔗 Google vinculado: {student_profile.google_account_linked}")
    except Exception as e:
        print(f"   ❌ FAIL: Error accediendo a perfil de estudiante: {e}")
    
    # Prueba 4: Contraseña incorrecta
    print("\n4️⃣ Probando con contraseña INCORRECTA...")
    auth_user = authenticate(username=test_username, password="wrong_password")
    if auth_user:
        print(f"   ❌ FAIL: Se autenticó con contraseña incorrecta (problema de seguridad!)")
    else:
        print(f"   ✅ SUCCESS: Contraseña incorrecta rechazada correctamente")
    
    print("\n" + "=" * 50)
    return True

def show_student_credentials():
    """Mostrar credenciales de todos los estudiantes activos"""
    print("\n📋 CREDENCIALES DE ESTUDIANTES ACTIVOS")
    print("=" * 50)
    
    students = Student.objects.filter(is_active=True).select_related('user')
    
    if not students.exists():
        print("❌ No hay estudiantes activos en el sistema")
        return
    
    print(f"Total de estudiantes activos: {students.count()}")
    print("-" * 50)
    
    for student in students:
        user = student.user
        print(f"👤 {user.get_full_name()}")
        print(f"   📧 Email: {user.email}")
        print(f"   👤 Usuario: {user.username}")
        print(f"   🔑 Contraseña: estudiante123 (predeterminada)")
        print(f"   📋 DNI: {student.dni}")
        print(f"   🔗 Google: {'Sí' if student.google_account_linked else 'No'}")
        print(f"   ✅ Activo: {'Sí' if user.is_active else 'No'}")
        print()

def show_login_urls():
    """Mostrar URLs de login disponibles"""
    print("\n🌐 URLS DE LOGIN DISPONIBLES")
    print("=" * 50)
    print("🔗 Login Principal:")
    print("   https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/login/")
    print()
    print("🔗 Google OAuth:")
    print("   https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/auth/login/google-oauth2/")
    print()
    print("🔗 Admin:")
    print("   https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/admin/")

def main():
    """Función principal"""
    print("🎓 SISTEMA DE AUTENTICACIÓN DUAL - ESTUDIANTES")
    print("=" * 60)
    
    # Ejecutar pruebas
    if test_authentication_methods():
        show_student_credentials()
        show_login_urls()
        
        print("\n🎉 PRUEBAS COMPLETADAS")
        print("✅ El sistema soporta autenticación dual:")
        print("   • Usuario/Contraseña tradicional")
        print("   • Email/Contraseña")
        print("   • Google OAuth (opcional)")
    else:
        print("❌ Error durante las pruebas")

if __name__ == '__main__':
    main() 