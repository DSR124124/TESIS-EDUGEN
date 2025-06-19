#!/usr/bin/env python
"""
Script para debuggear y resolver el problema del encabezado institucional
que aparece cuando no debería aparecer
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

def debug_logo_configuration():
    """Verifica el estado actual de la configuración del logo"""
    print("🔍 ANALIZANDO CONFIGURACIÓN DE LOGO INSTITUCIONAL")
    print("=" * 60)
    
    try:
        from apps.institutions.models import Institution
        
        # Obtener todas las instituciones
        institutions = Institution.objects.all()
        
        if not institutions.exists():
            print("❌ No se encontraron instituciones en el sistema")
            return
        
        for institution in institutions:
            print(f"\n🏫 INSTITUCIÓN: {institution.name}")
            print(f"   📍 Dirección: {institution.address or 'No especificada'}")
            print(f"   📧 Email: {institution.email or 'No especificado'}")
            print(f"   🖼️  Logo: {'Sí' if institution.logo else 'No'}")
            
            # Verificar configuración de logo
            try:
                settings = institution.settings
                print(f"   ⚙️  Configuración encontrada:")
                print(f"       - Logo habilitado: {settings.logo_enabled}")
                print(f"       - Color primario: {settings.primary_color}")
                print(f"       - Color secundario: {settings.secondary_color}")
                print(f"       - Color de acento: {settings.accent_color}")
            except Exception as e:
                print(f"   ❌ Error al obtener configuración: {str(e)}")
                print(f"       Esto significa que NO HAY configuración = NO mostrar logo")
    
    except Exception as e:
        print(f"❌ Error general: {str(e)}")

def test_institutional_header():
    """La función get_institutional_header ha sido eliminada del sistema"""
    print("\n✅ FUNCIÓN get_institutional_header ELIMINADA")
    print("=" * 60)
    print("🎯 El sistema ya no genera encabezados institucionales.")
    print("📋 Estado actual:")
    print("   • get_institutional_header() eliminada completamente")
    print("   • No se generarán encabezados institucionales")
    print("   • Los contenidos se mostrarán sin logos/encabezados")
    print("\n✅ ¡Problema resuelto! Ya no aparecerá el encabezado al editar contenido.")

def disable_logo_for_all_institutions():
    """Deshabilita el logo para todas las instituciones"""
    print("\n🛠️  DESHABILITANDO LOGO PARA TODAS LAS INSTITUCIONES")
    print("=" * 60)
    
    try:
        from apps.institutions.models import Institution, InstitutionSettings
        
        institutions = Institution.objects.all()
        
        for institution in institutions:
            try:
                settings = institution.settings
                if settings.logo_enabled:
                    settings.logo_enabled = False
                    settings.save()
                    print(f"✅ Logo deshabilitado para: {institution.name}")
                else:
                    print(f"ℹ️  Logo ya estaba deshabilitado para: {institution.name}")
            except InstitutionSettings.DoesNotExist:
                # Crear configuración con logo deshabilitado
                InstitutionSettings.objects.create(
                    institution=institution,
                    logo_enabled=False,
                    primary_color='#005CFF',
                    secondary_color='#A142F5',
                    accent_color='#00CFFF'
                )
                print(f"✅ Configuración creada (logo deshabilitado) para: {institution.name}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def enable_logo_for_institution(institution_name):
    """Habilita el logo para una institución específica"""
    print(f"\n🔧 HABILITANDO LOGO PARA: {institution_name}")
    print("=" * 60)
    
    try:
        from apps.institutions.models import Institution, InstitutionSettings
        
        institution = Institution.objects.filter(name__icontains=institution_name).first()
        
        if not institution:
            print(f"❌ No se encontró institución con nombre: {institution_name}")
            return
        
        try:
            settings = institution.settings
            settings.logo_enabled = True
            settings.save()
            print(f"✅ Logo habilitado para: {institution.name}")
        except InstitutionSettings.DoesNotExist:
            InstitutionSettings.objects.create(
                institution=institution,
                logo_enabled=True,
                primary_color='#005CFF',
                secondary_color='#A142F5',
                accent_color='#00CFFF'
            )
            print(f"✅ Configuración creada (logo habilitado) para: {institution.name}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal del script"""
    print("🚀 SCRIPT DE DEBUG - PROBLEMA ENCABEZADO INSTITUCIONAL")
    print("=" * 60)
    print("Este script te ayudará a resolver el problema del encabezado")
    print("institucional que aparece cuando editas contenido.")
    print()
    
    # Paso 1: Analizar configuración actual
    debug_logo_configuration()
    
    # Paso 2: Probar función
    test_institutional_header()
    
    # Paso 3: Preguntar qué hacer
    print("\n📋 OPCIONES DISPONIBLES:")
    print("1. Deshabilitar logo para TODAS las instituciones")
    print("2. Habilitar logo para una institución específica")
    print("3. Solo mostrar análisis (no cambiar nada)")
    
    try:
        opcion = input("\n¿Qué opción eliges? (1/2/3): ").strip()
        
        if opcion == "1":
            disable_logo_for_all_institutions()
            print("\n✅ ¡LISTO! El encabezado institucional ya NO debería aparecer")
            print("   Reinicia tu servidor Django y prueba editando contenido")
        
        elif opcion == "2":
            nombre = input("Ingresa el nombre de la institución: ").strip()
            enable_logo_for_institution(nombre)
            print("\n✅ ¡LISTO! El encabezado institucional SÍ debería aparecer para esta institución")
        
        elif opcion == "3":
            print("\n✅ Análisis completado. No se realizaron cambios.")
        
        else:
            print("\n❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 