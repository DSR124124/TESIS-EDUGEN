#!/usr/bin/env python3
"""
Script de Deploy Fix para EduGen - Solución al problema de dependencias
"""

import subprocess
import sys

def run_command(command, description):
    print(f"\n🔧 {description}")
    print(f"Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(f"✅ {description} - Exitoso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print("🚀 DEPLOY FIX - SOLUCIONANDO PROBLEMA DE DEPENDENCIAS")
    print("=" * 60)
    
    # 1. Configurar variables de entorno críticas
    print("\n🔧 Paso 1: Configurando variables de entorno críticas...")
    env_command = """az webapp config appsettings set --resource-group rg-edugen --name edugen-app --settings \
        DJANGO_SETTINGS_MODULE="config.settings.azure_production" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        ENABLE_ORYX_BUILD="true" \
        WEBSITES_CONTAINER_START_TIME_LIMIT="1800" \
        WEBSITE_RUN_FROM_PACKAGE="0" \
        SECRET_KEY="django-insecure-fix-key-for-deploy" \
        ALLOWED_HOSTS="edugen-app.azurewebsites.net,*.azurewebsites.net" \
        DATABASE_NAME="edugen" \
        DATABASE_USER="postgres" \
        DATABASE_PASSWORD="EduGen123!" \
        DATABASE_HOST="edugen-db-2024-01.postgres.database.azure.com" \
        DATABASE_PORT="5432" """
    
    if not run_command(env_command, "Configuración de variables de entorno"):
        return False
    
    # 2. Deploy usando requirements.txt principal
    print("\n🔧 Paso 2: Deploy con requirements.txt principal...")
    deploy_command = """az webapp up \
        --name edugen-app \
        --resource-group rg-edugen \
        --runtime "PYTHON:3.11" \
        --sku B1"""
    
    if not run_command(deploy_command, "Deploy a Azure"):
        return False
    
    # 3. Forzar rebuild
    print("\n🔧 Paso 3: Forzando rebuild...")
    if not run_command("az webapp deployment source sync --name edugen-app --resource-group rg-edugen", "Sync deployment"):
        print("⚠️ Sync falló, pero continuando...")
    
    # 4. Reiniciar aplicación
    print("\n🔧 Paso 4: Reiniciando aplicación...")
    if not run_command("az webapp restart --name edugen-app --resource-group rg-edugen", "Reinicio de aplicación"):
        return False
    
    print("\n🎉 ¡DEPLOY FIX COMPLETADO!")
    print("🌐 URL: https://edugen-app.azurewebsites.net")
    print("🔧 Logs: az webapp log tail --name edugen-app --resource-group rg-edugen")
    print("\n⏳ Espera 2-3 minutos para que la aplicación arranque completamente.")
    
    return True

if __name__ == "__main__":
    if main():
        print("\n✅ Script completado exitosamente")
    else:
        print("\n❌ Script falló - revisa los errores arriba")
        sys.exit(1) 