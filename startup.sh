#!/bin/bash

echo "🚀 Iniciando EduGen en Azure App Service"

# Activar entorno virtual si existe (opcional en Azure, normalmente no se usa virtualenv aquí)
if [ -f "venv/bin/activate" ]; then
  echo "🐍 Activando entorno virtual..."
  source venv/bin/activate
else
  echo "⚠️ Entorno virtual 'venv' no encontrado (normal en contenedores Azure). Continuando..."
fi

# Establecer variable de entorno de settings de Django
export DJANGO_SETTINGS_MODULE=config.settings.azure_production

# Verificar puerto asignado por Azure (usar siempre $PORT, no valor fijo)
PORT=${PORT:-8000}
echo "🌐 Puerto asignado por Azure: $PORT"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
if [ $? -ne 0 ]; then
  echo "❌ Error al instalar dependencias"
  exit 1
fi

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput
if [ $? -ne 0 ]; then
  echo "❌ Error al ejecutar migraciones"
  exit 1
fi

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear
if [ $? -ne 0 ]; then
  echo "❌ Error al recopilar archivos estáticos"
  exit 1
fi

# Iniciar Gunicorn en modo producción
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind=0.0.0.0:$PORT \
  --workers=3 \
  --timeout=600
