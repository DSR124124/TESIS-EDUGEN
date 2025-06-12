#!/bin/bash

echo "🚀 Iniciando EduGen en Azure App Service"

# Activar entorno virtual si existe
if [ -f "venv/bin/activate" ]; then
  echo "🐍 Activando entorno virtual..."
  source venv/bin/activate
else
  echo "⚠️ No se encontró entorno virtual llamado 'venv'. Continuando sin activarlo..."
fi

# Establecer variable de entorno de settings de Django
export DJANGO_SETTINGS_MODULE=config.settings.azure_production

# Verificar puerto asignado por Azure (fallback a 8000)
PORT=${PORT:-8000}
echo "🌐 Puerto asignado por Azure: $PORT"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt || {
  echo "❌ Error al instalar dependencias"
  exit 1
}

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput || {
  echo "❌ Error al ejecutar migraciones"
  exit 1
}

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear || {
  echo "❌ Error al recopilar archivos estáticos"
  exit 1
}

# Iniciar servidor Gunicorn
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application --bind=0.0.0.0:$PORT --timeout 600
