#!/usr/bin/env python3
"""
Script para limpiar archivos obsoletos del proyecto EduGen
"""

import os
import shutil
from pathlib import Path

# Archivos obsoletos que se pueden eliminar
OBSOLETE_FILES = [
    'debug_user.py',           # Script temporal de debug
    'ai_content.log',          # Log vacío
    'debug.log',               # Log vacío  
    'requirements-azure.txt',  # Duplicado de requirements/production.txt
    'requirements.txt',        # Duplicado de requirements/base.txt
    'deploy_simple.bat',       # Reemplazado por manuales nuevos
    'activate.sh',             # Innecesario con entorno virtual estándar
    'wsgi.py',                 # Duplicado de config/wsgi.py
    'Procfile',                # Para Heroku, no Azure
    '.deployment',             # Configuración vieja de Azure
    'oryx-manifest.toml',      # Generado automáticamente
]

# Directorios obsoletos
OBSOLETE_DIRS = [
    'sistema_educativo',       # Configuración vieja, reemplazada por config/
    'doc',                     # Documentación vieja, reemplazada por manuales
]

def main():
    print("🧹 LIMPIEZA DE ARCHIVOS OBSOLETOS - Sistema EduGen")
    print("=" * 60)
    
    current_dir = Path.cwd()
    print(f"📁 Directorio actual: {current_dir}")
    print()
    
    # Verificar archivos obsoletos
    print("📋 ARCHIVOS OBSOLETOS ENCONTRADOS:")
    found_files = []
    
    for file_name in OBSOLETE_FILES:
        file_path = current_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size if file_path.is_file() else 0
            print(f"  ❌ {file_name} ({size} bytes)")
            found_files.append(file_path)
        else:
            print(f"  ✅ {file_name} (ya no existe)")
    
    print()
    print("📂 DIRECTORIOS OBSOLETOS ENCONTRADOS:")
    found_dirs = []
    
    for dir_name in OBSOLETE_DIRS:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            try:
                items = len(list(dir_path.rglob('*')))
                print(f"  ❌ {dir_name}/ ({items} elementos)")
                found_dirs.append(dir_path)
            except:
                print(f"  ❌ {dir_name}/ (no se puede acceder)")
                found_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_name}/ (ya no existe)")
    
    print()
    
    if not found_files and not found_dirs:
        print("🎉 ¡No se encontraron archivos obsoletos!")
        print("✨ El proyecto ya está limpio.")
        return
    
    # Preguntar si eliminar
    print(f"🗑️  Se encontraron {len(found_files)} archivos y {len(found_dirs)} directorios obsoletos.")
    response = input("¿Deseas eliminarlos? (s/N): ").lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        print("\n🧹 Eliminando archivos obsoletos...")
        
        # Eliminar archivos
        for file_path in found_files:
            try:
                file_path.unlink()
                print(f"  ✅ Eliminado: {file_path.name}")
            except Exception as e:
                print(f"  ❌ Error eliminando {file_path.name}: {e}")
        
        # Eliminar directorios
        for dir_path in found_dirs:
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Eliminado: {dir_path.name}/")
            except Exception as e:
                print(f"  ❌ Error eliminando {dir_path.name}/: {e}")
        
        print("\n✨ Limpieza completada!")
    else:
        print("\n🔄 Limpieza cancelada. Los archivos se mantienen.")
    
    print()
    print("📚 ARCHIVOS IMPORTANTES QUE SE MANTIENEN:")
    important_files = [
        'MANUAL_DESPLIEGUE_COMPLETO.md',
        'MANUAL_DESPLIEGUE_AZURE.md', 
        'README_MANUALES.md',
        'manage.py',
        'app.py',
        'startup.sh',
        'requirements/',
        'config/',
        'apps/',
        'static/',
        'templates/',
        'media/',
    ]
    
    for item in important_files:
        item_path = current_dir / item
        if item_path.exists():
            print(f"  ✅ {item}")
        else:
            print(f"  ⚠️  {item} (no encontrado)")
    
    print()
    print("💡 RECOMENDACIONES:")
    print("  - Los manuales nuevos reemplazan la documentación anterior")
    print("  - Usa requirements/local.txt para desarrollo")
    print("  - Usa requirements/production.txt para Azure")
    print("  - El archivo app.py es necesario para Azure")
    print("  - Los archivos de configuración están en config/")

if __name__ == "__main__":
    main() 