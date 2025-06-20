#!/bin/bash

# Script de Despliegue Azure - Estudiantes 4to F Polo Jiménez
# ============================================================
# 
# Este script configura automáticamente los estudiantes en Azure App Service
# Debe ejecutarse después del despliegue inicial de la aplicación
#
# Uso:
#   bash scripts/deploy_azure_students.sh
#   bash scripts/deploy_azure_students.sh --force
#   bash scripts/deploy_azure_students.sh --verify-only

set -e  # Salir si hay algún error

echo "========================================================================"
echo "🚀 SCRIPT DE DESPLIEGUE AZURE - ESTUDIANTES 4TO F POLO JIMÉNEZ"
echo "========================================================================"
echo "📅 Fecha: $(date)"
echo "🌐 Entorno: Azure App Service"
echo "========================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    log_error "No se encontró manage.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Configurar variables de entorno para producción
log_info "Configurando variables de entorno..."

# Azure App Service debería tener estas configuradas, pero las verificamos
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    export DJANGO_SETTINGS_MODULE="config.settings.azure_production"
    log_warning "DJANGO_SETTINGS_MODULE no estaba configurado. Usando: $DJANGO_SETTINGS_MODULE"
else
    log_success "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
fi

# Verificar que Python está disponible
if ! command -v python &> /dev/null; then
    log_error "Python no está disponible en el PATH"
    exit 1
fi

log_success "Python encontrado: $(python --version)"

# Verificar que Django está instalado
if ! python -c "import django" &> /dev/null; then
    log_error "Django no está instalado o no es accesible"
    exit 1
fi

log_success "Django disponible"

# Parsear argumentos
FORCE_FLAG=""
VERIFY_ONLY_FLAG=""

for arg in "$@"; do
    case $arg in
        --force)
            FORCE_FLAG="--force"
            log_warning "Modo FORCE activado - recreará estudiantes existentes"
            ;;
        --verify-only)
            VERIFY_ONLY_FLAG="--verify-only"
            log_info "Modo VERIFY-ONLY activado - solo verificará el estado actual"
            ;;
        *)
            log_warning "Argumento desconocido: $arg"
            ;;
    esac
done

# Ejecutar migraciones primero (por seguridad)
log_info "Ejecutando migraciones de Django..."
if python manage.py migrate --noinput; then
    log_success "Migraciones completadas exitosamente"
else
    log_error "Error en las migraciones. Abortando."
    exit 1
fi

# Recopilar archivos estáticos (para Azure)
log_info "Recopilando archivos estáticos..."
if python manage.py collectstatic --noinput --clear; then
    log_success "Archivos estáticos recopilados"
else
    log_warning "Error al recopilar archivos estáticos (continuando...)"
fi

# Verificar que el comando personalizado existe
log_info "Verificando comando personalizado..."
if python manage.py help setup_production_students &> /dev/null; then
    log_success "Comando setup_production_students disponible"
else
    log_error "El comando setup_production_students no está disponible"
    exit 1
fi

# Ejecutar el comando de configuración de estudiantes
log_info "Ejecutando configuración de estudiantes..."
echo "========================================================================"

COMMAND="python manage.py setup_production_students $FORCE_FLAG $VERIFY_ONLY_FLAG"
log_info "Ejecutando: $COMMAND"

if eval $COMMAND; then
    echo "========================================================================"
    log_success "¡Configuración de estudiantes completada exitosamente!"
else
    echo "========================================================================"
    log_error "Error en la configuración de estudiantes"
    exit 1
fi

# Verificación final del sistema
log_info "Realizando verificación final del sistema..."

# Verificar que la aplicación responde
log_info "Verificando que Django esté funcionando..."
if python manage.py check --deploy; then
    log_success "Verificación de Django exitosa"
else
    log_warning "Advertencias en la verificación de Django"
fi

# Mostrar estadísticas finales
log_info "Obteniendo estadísticas finales..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
django.setup()

from django.contrib.auth import get_user_model
from apps.academic.models import Student, Enrollment

User = get_user_model()

total_users = User.objects.count()
total_students = User.objects.filter(role='student').count()
active_students = User.objects.filter(role='student', is_active=True).count()
polo_students = User.objects.filter(role='student', email__endswith='@cased.edu.pe').count()
active_enrollments = Enrollment.objects.filter(status='ACTIVE').count()

print(f'📊 ESTADÍSTICAS FINALES:')
print(f'   👥 Total usuarios: {total_users}')
print(f'   🎓 Total estudiantes: {total_students}')
print(f'   ✅ Estudiantes activos: {active_students}')
print(f'   🏫 Estudiantes Polo Jiménez: {polo_students}')
print(f'   📚 Matrículas activas: {active_enrollments}')
"

echo "========================================================================"
log_success "🎉 ¡DESPLIEGUE AZURE COMPLETADO EXITOSAMENTE!"
echo "========================================================================"
log_info "📋 INFORMACIÓN DE ACCESO:"
log_info "   🌐 URL: https://tu-app.azurewebsites.net/login/"
log_info "   📧 Método: Email + Contraseña"
log_info "   🔑 Ejemplo: 61791657@cased.edu.pe / 61791657"
echo "========================================================================"
log_success "✅ El sistema está listo para ser usado por los estudiantes!"
echo "========================================================================"

# Limpiar variables de entorno temporales si las configuramos nosotros
# (En Azure App Service, las variables permanentes se configuran en el portal)

echo "📝 Script completado en: $(date)" 