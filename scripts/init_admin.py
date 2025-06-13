#!/usr/bin/env python
"""
Script para inicializar el usuario administrador del sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_admin_user():
    """Crear usuario administrador si no existe"""
    
    # Credenciales por defecto
    username = 'admin'
    email = 'admin@edugen.com'
    password = 'EduGen2024!'  # Contraseña más segura
    
    try:
        with transaction.atomic():
            # Verificar si ya existe un superusuario
            if User.objects.filter(is_superuser=True).exists():
                print("✅ Ya existe un superusuario en el sistema.")
                return
            
            # Verificar si ya existe el usuario
            if User.objects.filter(username=username).exists():
                print(f"❌ El usuario '{username}' ya existe.")
                return
            
            # Crear el superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema',
                role='director'
            )
            
            print("🎉 Superusuario creado exitosamente!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print("   ⚠️  IMPORTANTE: Cambia la contraseña después del primer login!")
            
    except Exception as e:
        print(f"❌ Error al crear el superusuario: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    create_admin_user() 