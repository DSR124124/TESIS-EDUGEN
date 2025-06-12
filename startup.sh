#!/bin/bash

echo "🚀 Iniciando aplicación EduGen..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones básicas
echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🌐 Iniciando servidor Gunicorn..."
# Usar el puerto que Azure asigna
gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 config.wsgi:application 