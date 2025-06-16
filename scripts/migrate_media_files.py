#!/usr/bin/env python
"""
Script to migrate media files to Azure production environment
"""
import os
import shutil
import sys
from pathlib import Path

def migrate_media_files():
    """
    Migrate media files from development to production paths
    """
    # Get the base directory (where manage.py is located)
    base_dir = Path(__file__).resolve().parent.parent
    
    # Source and destination paths
    local_media = base_dir / 'media'
    production_media = Path('/home/site/wwwroot/media')
    
    print(f"🔄 Migrando archivos de media...")
    print(f"📁 Origen: {local_media}")
    print(f"📁 Destino: {production_media}")
    
    if not local_media.exists():
        print("❌ No se encontró el directorio media local")
        return False
    
    # Create production media directory if it doesn't exist
    production_media.mkdir(parents=True, exist_ok=True)
    
    # Copy all files maintaining directory structure
    try:
        for root, dirs, files in os.walk(local_media):
            # Calculate relative path from local_media
            rel_path = Path(root).relative_to(local_media)
            dest_dir = production_media / rel_path
            
            # Create destination directory
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            for file in files:
                src_file = Path(root) / file
                dest_file = dest_dir / file
                
                if not dest_file.exists() or src_file.stat().st_mtime > dest_file.stat().st_mtime:
                    print(f"📋 Copiando: {rel_path / file}")
                    shutil.copy2(src_file, dest_file)
                else:
                    print(f"⏭️  Omitiendo: {rel_path / file} (ya existe y está actualizado)")
        
        print("✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def cleanup_temp_media():
    """
    Clean up temporary media files in /tmp/media
    """
    temp_media = Path('/tmp/media')
    if temp_media.exists():
        print(f"🧹 Limpiando archivos temporales en {temp_media}")
        shutil.rmtree(temp_media)
        print("✅ Archivos temporales eliminados")

if __name__ == '__main__':
    print("🚀 Iniciando migración de archivos media para Azure...")
    
    if migrate_media_files():
        cleanup_temp_media()
        print("\n🎉 ¡Migración completada! Los archivos de media ahora deberían estar disponibles en producción.")
    else:
        print("\n❌ Migración fallida. Revisa los errores anteriores.")
        sys.exit(1) 