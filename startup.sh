#!/bin/bash

# Script de inicio optimizado para Azure App Service
echo "🚀 Iniciando EduGen en Azure..."

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Mostrar información básica
echo "📊 Python: $(python --version)"
echo "📊 Django Settings: $DJANGO_SETTINGS_MODULE"

# Verificar que manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py no encontrado"
    exit 1
fi

# Solo verificar Django (no instalar dependencias)
echo "🔍 Verificando Django..."
python -c "import django; print(f'Django version: {django.get_version()}')" || {
    echo "❌ Django no encontrado, instalando dependencias mínimas..."
    pip install -r requirements-azure.txt --no-cache-dir --disable-pip-version-check
}

# Recopilar archivos estáticos (rápido)
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Ejecutar migraciones (puede ser lento pero necesario)
echo "🔄 Ejecutando migraciones..."
python manage.py migrate

# Crear superusuario (rápido)
echo "👤 Configurando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@edugen.com', 'EduGenAdmin123!')
    print('✅ Superusuario creado')
"

echo "🌐 Iniciando servidor en puerto ${PORT:-8000}..."

# Iniciar Gunicorn con configuración optimizada
exec gunicorn config.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=1 \
    --threads=2 \
    --timeout=120 \
    --keep-alive=2 \
    --max-requests=1000 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info 