#!/bin/bash

echo "🚀 Iniciando aplicación Django en Azure..."

# Cambiar al directorio de la aplicación
cd /home/site/wwwroot

# Activar el entorno virtual si existe
if [ -d "antenv" ]; then
    echo "📦 Activando entorno virtual..."
    source antenv/bin/activate
fi

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE=config.settings.azure_production

# Crear directorio de media si no existe
echo "📁 Configurando directorio de media..."
mkdir -p /home/site/wwwroot/media
chmod 755 /home/site/wwwroot/media

# Migrar archivos de media existentes
if [ -d "media" ]; then
    echo "📋 Migrando archivos de media..."
    python scripts/migrate_media_files.py
fi

# Ejecutar collectstatic
echo "🔧 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Ejecutar migraciones
echo "🔧 Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear usuario admin si no existe
echo "🔧 Creando usuario administrador..."
python manage.py create_admin

# Crear estudiantes de ejemplo si no existen
echo "🎓 Configurando estudiantes de ejemplo..."
python manage.py manage_students --create

# Verificar archivos estáticos
if [ -d "staticfiles" ]; then
    echo "✅ Directorio staticfiles encontrado"
    echo "📊 Archivos estáticos: $(find staticfiles -type f | wc -l) archivos"
else
    echo "❌ Directorio staticfiles no encontrado"
fi

echo "🎉 Configuración completada. Iniciando servidor..."

# Iniciar Gunicorn
exec gunicorn --bind=0.0.0.0 --timeout 600 config.wsgi 