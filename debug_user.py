#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Teacher, Director
from apps.academic.models import Student

User = get_user_model()

def diagnose_users():
    print("🔍 Diagnóstico de usuarios en el sistema:")
    print("=" * 50)
    
    # Listar todos los usuarios
    users = User.objects.all()
    print(f"📊 Total de usuarios: {users.count()}")
    
    for user in users:
        print(f"\n👤 Usuario: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nombre: {user.first_name} {user.last_name}")
        print(f"   Rol: {user.role}")
        print(f"   Es superusuario: {user.is_superuser}")
        print(f"   Es staff: {user.is_staff}")
        
        # Verificar perfiles
        has_teacher = hasattr(user, 'teacher_profile')
        has_director = hasattr(user, 'director_profile')
        has_student = hasattr(user, 'student_profile')
        
        print(f"   Tiene teacher_profile: {has_teacher}")
        print(f"   Tiene director_profile: {has_director}")
        print(f"   Tiene student_profile: {has_student}")
        
        if has_teacher:
            teacher = user.teacher_profile
            print(f"   📚 Profesor - Código: {teacher.teacher_code}")
        
        if has_director:
            director = user.director_profile
            print(f"   🏛️ Director - DNI: {director.dni}")
            
        if has_student:
            student = user.student_profile
            print(f"   🎓 Estudiante - Código: {student.student_code}")

def create_teacher_profile_for_admin():
    """Crear un perfil de profesor para el usuario admin"""
    try:
        admin_user = User.objects.get(username='admin')
        
        if hasattr(admin_user, 'teacher_profile'):
            print("✅ El usuario admin ya tiene perfil de profesor")
            return
        
        # Crear perfil de profesor
        teacher = Teacher.objects.create(
            user=admin_user,
            dni='12345678',  # DNI temporal
            phone='999999999',
            address='Dirección temporal'
        )
        
        print(f"✅ Perfil de profesor creado para {admin_user.username}")
        print(f"   Código de profesor: {teacher.teacher_code}")
        
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")
    except Exception as e:
        print(f"❌ Error creando perfil de profesor: {str(e)}")

if __name__ == '__main__':
    diagnose_users()
    print("\n" + "=" * 50)
    print("🔧 Creando perfil de profesor para admin...")
    create_teacher_profile_for_admin() 