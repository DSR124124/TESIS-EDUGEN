#!/bin/bash

# Script de inicio robusto para Azure App Service
set -e  # Exit on any error

echo "🚀 Iniciando EduGen en Azure..."
echo "📊 Directorio actual: $(pwd)"
echo "📊 Contenido del directorio:"
ls -la

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Mostrar información del entorno
echo "📊 Python: $(python --version)"
echo "📊 Pip: $(pip --version)"
echo "📊 Django Settings: $DJANGO_SETTINGS_MODULE"
echo "📊 Variables de entorno importantes:"
echo "   - DATABASE_HOST: $DATABASE_HOST"
echo "   - DATABASE_NAME: $DATABASE_NAME"
echo "   - ALLOWED_HOSTS: $ALLOWED_HOSTS"

# Verificar que manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py no encontrado"
    exit 1
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements-azure.txt --no-cache-dir --disable-pip-version-check

# Verificar instalación de Django
echo "🔍 Verificando Django..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Verificar configuración de Django
echo "🔍 Verificando configuración..."
python manage.py check --deploy

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --run-syncdb

# Crear superusuario
echo "👤 Configurando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@edugen.com', 'EduGenAdmin123!')
    print('✅ Superusuario creado: admin/EduGenAdmin123!')
else:
    print('✅ Superusuario ya existe')
"

echo "🌐 Iniciando servidor Gunicorn..."
echo "📊 Puerto: ${PORT:-8000}"

# Iniciar Gunicorn con configuración más conservadora
exec gunicorn config.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=1 \
    --threads=2 \
    --timeout=300 \
    --keep-alive=2 \
    --max-requests=1000 \
    --max-requests-jitter=50 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=debug \
    --capture-output 