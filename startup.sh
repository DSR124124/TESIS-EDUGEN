#!/bin/bash
echo "🚀 Iniciando aplicación Django en Azure..."

# Configurar PATH de Python
export PATH="/opt/python/3.11/bin:$PATH"

# Mostrar información del entorno
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements-azure.txt

# Crear directorio de archivos temporales
mkdir -p /tmp/sessions
mkdir -p /tmp/backups

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --verbosity=0

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones de base de datos..."
python manage.py migrate --verbosity=0

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Creando superusuario admin/admin...")
    User.objects.create_superuser('admin', 'admin@sistema.edu', 'admin123')
    print("✅ Superusuario creado: admin/admin123")
else:
    print("✅ Superusuario ya existe")
PYTHON

echo "✅ Configuración completada. Iniciando servidor..."

# Iniciar servidor Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT config.wsgi:application 