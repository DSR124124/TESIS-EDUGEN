#!/usr/bin/env python
"""
Script de post-despliegue para Azure App Service
Ejecuta collectstatic y otras tareas necesarias después del despliegue
"""
import os
import sys
import django
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} completado exitosamente")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"❌ Error en {description}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout en {description}")
        return False
    except Exception as e:
        print(f"❌ Excepción en {description}: {str(e)}")
        return False
    return True

def main():
    print("🚀 Iniciando script de post-despliegue...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto.")
        sys.exit(1)
    
    # Configurar Django
    try:
        django.setup()
        print("✅ Django configurado correctamente")
    except Exception as e:
        print(f"❌ Error configurando Django: {str(e)}")
        sys.exit(1)
    
    # Lista de comandos a ejecutar
    commands = [
        ("python manage.py collectstatic --noinput --clear", "Recolectando archivos estáticos"),
        ("python manage.py migrate --noinput", "Ejecutando migraciones de base de datos"),
        ("python manage.py create_admin", "Creando usuario administrador"),
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"⚠️ Falló: {description}")
    
    print(f"\n📊 Resumen: {success_count}/{len(commands)} comandos ejecutados exitosamente")
    
    # Verificar que los archivos estáticos se recolectaron
    staticfiles_dir = 'staticfiles'
    if os.path.exists(staticfiles_dir):
        static_files = []
        for root, dirs, files in os.walk(staticfiles_dir):
            static_files.extend(files)
        print(f"✅ Archivos estáticos recolectados: {len(static_files)} archivos")
        
        # Verificar archivos específicos importantes
        important_files = [
            'admin/css/base.css',
            'admin/css/login.css',
            'admin/js/core.js',
        ]
        
        for file_path in important_files:
            full_path = os.path.join(staticfiles_dir, file_path)
            if os.path.exists(full_path):
                print(f"✅ Encontrado: {file_path}")
            else:
                print(f"❌ Faltante: {file_path}")
    else:
        print("❌ Directorio staticfiles no encontrado")
    
    print("🎉 Script de post-despliegue completado")

if __name__ == '__main__':
    main() 