#!/usr/bin/env python3
"""
Deploy Simple Fix - Solo lo esencial para que funcione
"""

import subprocess
import sys

def run_cmd(cmd):
    print(f"🔧 Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Exitoso")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False

def main():
    print("🚀 DEPLOY SIMPLE FIX")
    print("=" * 30)
    
    # 1. Configurar variables mínimas
    print("\n1. Configurando variables básicas...")
    if not run_cmd('az webapp config appsettings set --resource-group rg-edugen --name edugen-app --settings DJANGO_SETTINGS_MODULE="config.settings.azure_production" SCM_DO_BUILD_DURING_DEPLOYMENT="true"'):
        return False
    
    # 2. Deploy directo
    print("\n2. Deploy directo...")
    if not run_cmd('az webapp deployment source config-zip --resource-group rg-edugen --name edugen-app --src deploy.zip'):
        # Si falla, crear el zip primero
        print("Creando zip...")
        run_cmd('powershell Compress-Archive -Path * -DestinationPath deploy.zip -Force')
        if not run_cmd('az webapp deployment source config-zip --resource-group rg-edugen --name edugen-app --src deploy.zip'):
            return False
    
    # 3. Reiniciar
    print("\n3. Reiniciando...")
    run_cmd('az webapp restart --name edugen-app --resource-group rg-edugen')
    
    print("\n🎉 ¡Deploy completado!")
    print("🌐 URL: https://edugen-app.azurewebsites.net")
    
    return True

if __name__ == "__main__":
    main() 