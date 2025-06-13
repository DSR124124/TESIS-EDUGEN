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

# Ejecutar collectstatic
echo "🔧 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Ejecutar migraciones
echo "🔧 Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear usuario admin si no existe
echo "🔧 Creando usuario administrador..."
python manage.py create_admin

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