#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Crear superusuario
username = 'admin'
email = 'admin@edugen.com'
password = 'EduGen2024!'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Administrador',
        last_name='Sistema',
        role='director'
    )
    print(f"✅ Superusuario creado: {username}")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
else:
    print(f"⚠️ El usuario {username} ya existe") 