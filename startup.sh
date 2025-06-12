#!/bin/bash

echo "🚀 Iniciando EduGen en Azure App Service"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🌐 Iniciando servidor Gunicorn..."
# Usar config.wsgi como se recomienda
gunicorn --bind 0.0.0.0:8000 config.wsgi:application 