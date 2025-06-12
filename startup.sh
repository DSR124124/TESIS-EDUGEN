#!/bin/bash

echo "🚀 Iniciando EduGen en Azure App Service"

# Activar entorno virtual si es necesario
if [ -f "antenv/bin/activate" ]; then
  echo "🐍 Activando entorno virtual..."
  source antenv/bin/activate
fi

# Establecer settings de Django para producción
export DJANGO_SETTINGS_MODULE=config.settings.azure_production

# Instalar dependencias si no están presentes
echo "📦 Verificando e instalando dependencias..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Iniciar Gunicorn correctamente
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT --timeout 600
