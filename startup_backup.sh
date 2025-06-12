#!/bin/bash

echo "🚀 Iniciando EduGen en Azure App Service"

# Configurar variables de entorno
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"
export PYTHONUNBUFFERED=1

# Obtener puerto de Azure
PORT=${PORT:-8000}
echo "🌐 Puerto: $PORT"

# Detectar el directorio correcto donde están los archivos
WORK_DIR="/home/site/wwwroot"

# Si manage.py no está en wwwroot, buscar en el directorio que Azure usa
if [ ! -f "$WORK_DIR/manage.py" ]; then
    echo "⚠️ manage.py no encontrado en $WORK_DIR, buscando..."
    
    # Buscar en directorios temporales de Oryx
    for dir in /tmp/*/; do
        if [ -f "$dir/manage.py" ]; then
            WORK_DIR="$dir"
            echo "✅ Encontrado manage.py en: $WORK_DIR"
            break
        fi
    done
fi

# Cambiar al directorio de trabajo correcto
cd "$WORK_DIR"
echo "📁 Directorio de trabajo: $(pwd)"

# Configurar PYTHONPATH
export PYTHONPATH="$WORK_DIR"

# Verificar que manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py no encontrado en $(pwd)"
    echo "📂 Archivos disponibles:"
    ls -la
    exit 1
fi

echo "✅ manage.py encontrado"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements-azure.txt

# Verificar que Django está instalado
python -c "import django; print(f'Django version: {django.get_version()}')"

# Probar que la aplicación arranque correctamente
echo "🧪 Probando configuración de Django..."
python test_azure_startup.py
if [ $? -ne 0 ]; then
    echo "❌ Error en la configuración de Django"
    exit 1
fi

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
echo "Directorio actual: $(pwd)"
echo "Archivos principales:"
ls -la manage.py config/ apps/ 2>/dev/null || echo "Algunos directorios no encontrados"

# Ejecutar migraciones (opcional)
echo "🔄 Migraciones..."
python manage.py migrate --noinput --settings=config.settings.azure_production || echo "⚠️ Error en migraciones (continuando)"

# Iniciar aplicación
echo "🌐 Iniciando aplicación en $(pwd)..."
exec python manage.py runserver 0.0.0.0:$PORT --settings=config.settings.azure_production
