#!/usr/bin/env python
"""
Quick check script for media files in production
Run this in Azure App Service console to diagnose media issues
"""
import os
import sys
from pathlib import Path

def quick_media_check():
    """Quick diagnosis of media file issues"""
    print("🔍 DIAGNÓSTICO RÁPIDO - ARCHIVOS MEDIA")
    print("=" * 50)
    
    # Check current working directory
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    # Check if we're in the right location
    if "/home/site/wwwroot" in os.getcwd():
        print("✅ Estamos en Azure App Service")
        base_path = Path("/home/site/wwwroot")
    else:
        print("ℹ️ Corriendo localmente")
        base_path = Path.cwd()
    
    # Check media directory
    media_path = base_path / "media"
    print(f"📁 Ruta de media: {media_path}")
    print(f"📂 Media existe: {media_path.exists()}")
    
    if media_path.exists():
        print(f"📊 Contenido de media:")
        for item in media_path.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                print(f"  📄 {item.relative_to(media_path)} ({size} bytes)")
    
    # Check specific logo file
    logo_path = media_path / "institutions" / "logos" / "images.jpeg"
    print(f"\n🖼️ LOGO ESPECÍFICO:")
    print(f"📍 Ruta completa: {logo_path}")
    print(f"📂 Archivo existe: {logo_path.exists()}")
    
    if logo_path.exists():
        size = logo_path.stat().st_size
        print(f"📊 Tamaño: {size} bytes")
    
    # Check source media directory (in case migration didn't work)
    source_media = base_path / "media"
    if source_media != media_path:
        print(f"\n📁 Directorio fuente alternativo: {source_media}")
        if (source_media / "institutions" / "logos" / "images.jpeg").exists():
            print("✅ Archivo encontrado en ubicación fuente")
    
    # Check permissions
    if media_path.exists():
        stat = media_path.stat()
        print(f"\n🔐 Permisos del directorio media: {oct(stat.st_mode)[-3:]}")
    
    print(f"\n💡 RECOMENDACIONES:")
    if not media_path.exists():
        print("1. Crear directorio media:")
        print(f"   mkdir -p {media_path}")
    
    if not logo_path.exists():
        print("2. El archivo logo no existe. Opciones:")
        print("   - Subir nuevo logo desde la interfaz de administración")
        print("   - Copiar archivo desde backup")
        print("   - Verificar ruta en base de datos")

if __name__ == "__main__":
    quick_media_check() 