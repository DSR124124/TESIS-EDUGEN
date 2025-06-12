#!/usr/bin/env python3
"""
Script de Deploy Manual para EduGen en Azure
Prepara todos los archivos y configuraciones necesarias
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_step(step, message):
    print(f"\n🔧 {step}: {message}")
    print("-" * 50)

def run_command(command, description):
    print(f"Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Exitoso")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error:")
        print(e.stderr)
        return False

def main():
    print("🚀 DEPLOY MANUAL DE EDUGEN A AZURE")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ Error: No se encontró manage.py. Ejecuta desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    print_step("1", "Verificando Azure CLI")
    if not run_command("az --version", "Verificación de Azure CLI"):
        print("❌ Azure CLI no está instalado o no funciona correctamente")
        sys.exit(1)
    
    print_step("2", "Verificando login de Azure")
    if not run_command("az account show", "Verificación de login"):
        print("❌ No estás logueado en Azure. Ejecuta 'az login' primero")
        sys.exit(1)
    
    print_step("3", "Creando directorio de deploy")
    deploy_dir = Path("deploy_temp")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    print_step("4", "Copiando archivos necesarios")
    # Lista de archivos y directorios a copiar
    items_to_copy = [
        'apps',
        'config',
        'templates',
        'static',
        'media',
        'manage.py',
        'requirements-azure.txt',
        'startup.sh',
        'web.config',
        '.deployment'
    ]
    
    for item in items_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, deploy_dir / item)
                print(f"✅ Copiado directorio: {item}")
            else:
                shutil.copy2(item, deploy_dir / item)
                print(f"✅ Copiado archivo: {item}")
        else:
            print(f"⚠️  No encontrado: {item}")
    
    print_step("5", "Creando directorio db en deploy")
    (deploy_dir / "db").mkdir(exist_ok=True)
    
    print_step("6", "Configurando permisos de startup.sh")
    startup_path = deploy_dir / "startup.sh"
    if startup_path.exists():
        os.chmod(startup_path, 0o755)
        print("✅ Permisos configurados para startup.sh")
    
    print_step("7", "Preparando para deploy")
    os.chdir(deploy_dir)
    
    print_step("8", "Ejecutando deploy con Azure CLI")
    deploy_command = (
        "az webapp up "
        "--name edugen-app "
        "--resource-group rg-edugen "
        "--runtime PYTHON:3.11 "
        "--sku B1"
    )
    
    print(f"Comando de deploy: {deploy_command}")
    print("\n🚀 Iniciando deploy...")
    
    if run_command(deploy_command, "Deploy a Azure"):
        print("\n🎉 ¡DEPLOY COMPLETADO EXITOSAMENTE!")
        print("🌐 URL: https://edugen-app.azurewebsites.net")
        print("🔧 Admin: https://edugen-app.azurewebsites.net/admin/")
        print("👤 Usuario: admin / EduGenAdmin123!")
    else:
        print("\n❌ Deploy falló. Revisa los errores arriba.")
    
    # Volver al directorio original
    os.chdir("..")
    
    print_step("9", "Limpieza")
    try:
        shutil.rmtree(deploy_dir)
        print("✅ Directorio temporal eliminado")
    except:
        print("⚠️  No se pudo eliminar el directorio temporal")

if __name__ == "__main__":
    main() 