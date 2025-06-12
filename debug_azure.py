#!/usr/bin/env python
"""
Script de diagnóstico para Azure App Service
Ayuda a identificar problemas de configuración de Django
"""

import os
import sys
import traceback
from pathlib import Path

def test_django_setup():
    """Prueba la configuración básica de Django"""
    print("🔍 Iniciando diagnóstico de Django...")
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')
        
        # Importar Django
        import django
        print(f"✅ Django importado correctamente (versión: {django.get_version()})")
        
        # Configurar Django
        django.setup()
        print("✅ Django configurado correctamente")
        
        # Probar conexión a base de datos
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Conexión a base de datos exitosa: {result}")
            
        # Probar importación de modelos
        from django.contrib.auth.models import User
        print("✅ Modelos importados correctamente")
        
        # Probar URLs
        from django.urls import reverse
        try:
            admin_url = reverse('admin:index')
            print(f"✅ URLs configuradas correctamente: {admin_url}")
        except Exception as e:
            print(f"⚠️ Problema con URLs: {e}")
        
        print("🎉 Django está configurado correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración de Django:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()
        return False

def check_environment():
    """Verifica las variables de entorno importantes"""
    print("\n🔍 Verificando variables de entorno...")
    
    important_vars = [
        'DJANGO_SECRET_KEY',
        'DEEPSEEK_API_KEY',
        'DB_NAME',
        'DB_USER', 
        'DB_PASSWORD',
        'DB_HOST',
        'WEBSITE_HOSTNAME',
        'PORT',
        'PYTHONPATH'
    ]
    
    for var in important_vars:
        value = os.environ.get(var)
        if value:
            # Ocultar valores sensibles
            if 'KEY' in var or 'PASSWORD' in var:
                display_value = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: No configurada")

def check_files():
    """Verifica que los archivos importantes existan"""
    print("\n🔍 Verificando archivos importantes...")
    
    important_files = [
        'manage.py',
        'config/wsgi.py',
        'config/settings/azure_production.py',
        'requirements.txt',
        'app.py',
        'gunicorn.conf.py'
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}: Existe")
        else:
            print(f"❌ {file_path}: No encontrado")

if __name__ == "__main__":
    print("🚀 Diagnóstico de Azure App Service - Django")
    print("=" * 50)
    
    # Verificar entorno
    check_environment()
    
    # Verificar archivos
    check_files()
    
    # Probar Django
    success = test_django_setup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Diagnóstico completado: Django está funcionando correctamente")
    else:
        print("❌ Diagnóstico completado: Se encontraron problemas")
    
    sys.exit(0 if success else 1) 