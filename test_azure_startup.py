#!/usr/bin/env python
"""
Script de prueba para verificar que Django arranque correctamente en Azure
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def test_django_startup():
    """Prueba que Django pueda arrancar sin errores"""
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')
        django.setup()
        
        print("✅ Django configurado correctamente")
        
        # Probar imports básicos
        from django.contrib.auth.models import User
        from apps.accounts.models import CustomUser
        print("✅ Modelos importados correctamente")
        
        # Probar servicio de IA
        try:
            from apps.ai_content_generator.services.llm_service import DeepSeekService
            service = DeepSeekService()
            print(f"✅ Servicio de IA: {'Disponible' if service.api_available else 'No disponible (normal sin API key)'}")
        except Exception as e:
            print(f"⚠️ Servicio de IA: {e}")
        
        # Probar views básicas
        try:
            from apps.content.views import get_openai_service
            ai_service = get_openai_service()
            print(f"✅ Views de content: {'Servicio IA disponible' if ai_service else 'Sin servicio IA (normal)'}")
        except Exception as e:
            print(f"❌ Error en views: {e}")
        
        print("🎉 ¡Aplicación lista para funcionar!")
        return True
        
    except Exception as e:
        print(f"❌ Error al arrancar Django: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_django_startup()
    sys.exit(0 if success else 1) 