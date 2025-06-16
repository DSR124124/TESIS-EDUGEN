#!/usr/bin/env python
"""
Debug script to check media file configuration in production
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

import django
django.setup()

from django.conf import settings
from apps.institutions.models import Institution

def debug_media_configuration():
    """Debug media file configuration"""
    print("🔍 DEBUGGING MEDIA CONFIGURATION")
    print("=" * 50)
    
    # Django settings
    print(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"🌐 MEDIA_URL: {settings.MEDIA_URL}")
    print(f"📦 DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Default')}")
    
    # Check if media root exists
    media_root = Path(settings.MEDIA_ROOT)
    print(f"📂 Media root exists: {media_root.exists()}")
    
    if media_root.exists():
        print(f"📊 Media root contents:")
        for item in media_root.iterdir():
            if item.is_dir():
                file_count = len(list(item.rglob('*')))
                print(f"  📁 {item.name}/ ({file_count} files)")
            else:
                print(f"  📄 {item.name}")
    
    # Check Azure Blob Storage configuration
    azure_connection = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    azure_container = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')
    
    print(f"\n☁️  AZURE BLOB STORAGE:")
    print(f"🔗 Connection string configured: {'Yes' if azure_connection else 'No'}")
    print(f"📦 Container name: {azure_container}")
    
    # Check institutions with logos
    print(f"\n🏫 INSTITUTIONS WITH LOGOS:")
    institutions = Institution.objects.filter(logo__isnull=False).exclude(logo='')
    
    for institution in institutions:
        print(f"🏛️  {institution.name}")
        print(f"   Logo path: {institution.logo}")
        if institution.logo:
            logo_path = Path(settings.MEDIA_ROOT) / str(institution.logo)
            print(f"   Full path: {logo_path}")
            print(f"   File exists: {logo_path.exists()}")
            if logo_path.exists():
                print(f"   File size: {logo_path.stat().st_size} bytes")
    
    # Check URL patterns
    print(f"\n🔗 URL CONFIGURATION:")
    from django.urls import get_resolver
    from django.conf.urls.static import static
    
    resolver = get_resolver()
    print(f"Root URLconf: {resolver.url_patterns}")
    
    # Check if media URLs are configured
    media_patterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print(f"Media URL patterns: {len(media_patterns)} patterns")
    
    return {
        'media_root': str(settings.MEDIA_ROOT),
        'media_url': settings.MEDIA_URL,
        'media_root_exists': media_root.exists(),
        'azure_configured': bool(azure_connection),
        'institutions_with_logos': institutions.count()
    }

if __name__ == '__main__':
    try:
        debug_info = debug_media_configuration()
        print(f"\n✅ Debug completed successfully")
        
        # Suggestions
        print(f"\n💡 SUGGESTIONS:")
        if not debug_info['azure_configured']:
            print("1. Configure Azure Blob Storage for production")
            print("   Set AZURE_STORAGE_CONNECTION_STRING environment variable")
        
        if not debug_info['media_root_exists']:
            print("2. Create media directory:")
            print(f"   mkdir -p {debug_info['media_root']}")
        
        if debug_info['institutions_with_logos'] == 0:
            print("3. No institutions have logos configured")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 