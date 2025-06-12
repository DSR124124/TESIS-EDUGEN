#!/bin/bash

# Script de inicio simplificado para Azure App Service
echo "🚀 Iniciando EduGen en Azure..."

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"

# Mostrar información básica
echo "📊 Entorno Django: $DJANGO_SETTINGS_MODULE"
echo "📊 Python: $(python --version)"

# Instalar dependencias (solo si es necesario)
echo "📦 Verificando dependencias..."
pip install -r requirements-azure.txt --quiet --no-warn-script-location

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate

# Crear superusuario automáticamente
echo "👤 Configurando usuario admin..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@edugen.com', 'EduGenAdmin123!')
    print('✅ Superusuario creado')
"

echo "🌐 Iniciando servidor..."
# Usar el puerto que Azure proporciona
exec gunicorn config.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=2 \
    --threads=4 \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info 