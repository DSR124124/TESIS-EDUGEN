#!/usr/bin/env python
"""
Manual logo upload script for Azure production
"""
import os
import shutil
from pathlib import Path

def upload_logo_manual():
    """Manually copy the logo file to production location"""
    print("🔧 SUBIDA MANUAL DE LOGO")
    print("=" * 40)
    
    # Determine paths
    if "/home/site/wwwroot" in os.getcwd():
        # Running in Azure
        base_path = Path("/home/site/wwwroot")
        source_logo = base_path / "media" / "institutions" / "logos" / "images.jpeg"
        print("✅ Ejecutando en Azure App Service")
    else:
        # Running locally - simulate
        base_path = Path.cwd()
        source_logo = base_path / "media" / "institutions" / "logos" / "images.jpeg"
        print("ℹ️ Simulando desde entorno local")
    
    # Target path in production
    target_dir = Path("/home/site/wwwroot/media/institutions/logos/")
    target_logo = target_dir / "images.jpeg"
    
    print(f"📁 Archivo fuente: {source_logo}")
    print(f"📁 Destino: {target_logo}")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directorio creado: {target_dir}")
    
    # Check if source exists
    if source_logo.exists():
        print(f"✅ Archivo fuente encontrado ({source_logo.stat().st_size} bytes)")
        
        # Copy file
        try:
            shutil.copy2(source_logo, target_logo)
            print(f"✅ Archivo copiado exitosamente")
            print(f"📊 Tamaño del archivo destino: {target_logo.stat().st_size} bytes")
            
            # Set permissions
            os.chmod(target_logo, 0o644)
            print(f"✅ Permisos establecidos")
            
            return True
            
        except Exception as e:
            print(f"❌ Error copiando archivo: {e}")
            return False
    else:
        print(f"❌ Archivo fuente no encontrado: {source_logo}")
        
        # Try to find it in current directory
        local_logo = base_path / "media" / "institutions" / "logos" / "images.jpeg"
        if local_logo.exists():
            print(f"✅ Encontrado en ubicación alternativa: {local_logo}")
            try:
                shutil.copy2(local_logo, target_logo)
                print(f"✅ Archivo copiado desde ubicación alternativa")
                return True
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
        
        return False

if __name__ == "__main__":
    if upload_logo_manual():
        print("\n🎉 ¡Logo subido exitosamente!")
        print("Ahora prueba la URL: https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/media/institutions/logos/images.jpeg")
    else:
        print("\n❌ Falló la subida del logo") 