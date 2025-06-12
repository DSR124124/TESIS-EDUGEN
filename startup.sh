#!/bin/bash

# Script de inicio para entorno pre-construido
echo "🚀 Iniciando EduGen (Pre-built) en Azure..."

# Activar entorno virtual si existe
if [ -f "/home/site/wwwroot/venv/bin/activate" ]; then
    echo "📦 Activando entorno virtual pre-construido..."
    source /home/site/wwwroot/venv/bin/activate
    export PATH="/home/site/wwwroot/venv/bin:$PATH"
    export VIRTUAL_ENV="/home/site/wwwroot/venv"
else
    echo "⚠️ Entorno virtual no encontrado, usando Python del sistema..."
fi

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Mostrar información del entorno
echo "📊 Python: $(python --version)"
echo "📊 Pip: $(pip --version)"
echo "📊 Django Settings: $DJANGO_SETTINGS_MODULE"

# Verificar que manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py no encontrado"
    exit 1
fi

# Verificar Django (debería estar pre-instalado)
echo "🔍 Verificando Django..."
python -c "import django; print(f'✅ Django version: {django.get_version()}')" || {
    echo "❌ Django no encontrado, instalando..."
    pip install -r requirements-azure.txt --no-cache-dir
}

# Los archivos estáticos ya deberían estar recopilados, pero por seguridad
echo "📁 Verificando archivos estáticos..."
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles)" ]; then
    echo "📁 Recopilando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
else
    echo "✅ Archivos estáticos ya disponibles"
fi

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear tablas de sesiones específicamente
echo "🔄 Asegurando tablas de sesiones..."
python manage.py migrate sessions

# Limpiar sesiones expiradas
echo "🧹 Limpiando sesiones expiradas..."
python manage.py clearsessions || echo "⚠️ No se pudieron limpiar sesiones (normal en primera ejecución)"

# Crear superusuario si no existe
echo "👤 Configurando superusuario..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@edugen.com', 'EduGen123!')" | python manage.py shell

echo "🌐 Iniciando servidor Gunicorn en puerto ${PORT:-8000}..."

# Iniciar Gunicorn
exec gunicorn config.wsgi:application \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=2 \
    --threads=2 \
    --timeout=120 \
    --keep-alive=2 \
    --max-requests=1000 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info \
    --preload 