#!/bin/bash

echo "🚀 Iniciando EduGen en Azure App Service"

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"
export PYTHONPATH="/home/site/wwwroot"
export PYTHONUNBUFFERED=1

# Obtener puerto de Azure
PORT=${PORT:-8000}
echo "🌐 Puerto: $PORT"

# Verificar que estamos en el directorio correcto
cd /home/site/wwwroot
echo "📁 Directorio de trabajo: $(pwd)"

# Verificar que manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py no encontrado"
    exit 1
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements-azure.txt

# Verificar que Django está instalado
python -c "import django; print(f'Django version: {django.get_version()}')"

# Verificar la configuración de Django
echo "🔧 Verificando configuración de Django..."
python manage.py check --deploy --settings=config.settings.azure_production

# Recopilar archivos estáticos (opcional)
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear --settings=config.settings.azure_production || echo "⚠️ Error en collectstatic (continuando)"

# Mostrar información del sistema
echo "🔍 Información del sistema:"
python --version
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "PYTHONPATH: $PYTHONPATH"
echo "Archivos en directorio:"
ls -la

# Ejecutar migraciones (opcional)
echo "🔄 Migraciones..."
python manage.py migrate --noinput --settings=config.settings.azure_production || echo "⚠️ Error en migraciones (continuando)"

# Iniciar aplicación
echo "🌐 Iniciando aplicación..."
exec python manage.py runserver 0.0.0.0:$PORT --settings=config.settings.azure_production
