#!/bin/bash
echo "🚀 Iniciando EduGen - Sistema Educativo en Azure..."

# Configurar PATH de Python
export PATH="/opt/python/3.11/bin:$PATH"

# Configurar variables de entorno para Django
export DJANGO_SETTINGS_MODULE="config.settings.azure_production"

# Configurar variables de la base de datos desde Azure App Settings
export PGDATABASE="${DATABASE_NAME:-edugen}"
export PGUSER="${DATABASE_USER:-postgres}"
export PGPASSWORD="${DATABASE_PASSWORD:-EduGen123!}"
export PGHOST="${DATABASE_HOST:-edugen-db-2024-01.postgres.database.azure.com}"
export PGPORT="${DATABASE_PORT:-5432}"

# Mostrar información del entorno
echo "📊 Información del entorno:"
echo "   - Python version: $(python --version)"
echo "   - Pip version: $(pip --version)"
echo "   - Django Settings: $DJANGO_SETTINGS_MODULE"
echo "   - Database Host: $PGHOST"
echo "   - Database Name: $PGDATABASE"
echo "   - Allowed Hosts: $ALLOWED_HOSTS"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements-azure.txt

# Crear directorios necesarios
mkdir -p /tmp/sessions
mkdir -p /tmp/backups
mkdir -p /tmp/media

# Verificar conectividad a la base de datos
echo "🔗 Verificando conexión a PostgreSQL..."
python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        database=os.environ['PGDATABASE'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        port=os.environ['PGPORT'],
        sslmode='require'
    )
    print('✅ Conexión a PostgreSQL exitosa')
    conn.close()
except Exception as e:
    print(f'❌ Error de conexión: {e}')
"

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
    print("Creando superusuario admin para EduGen...")
    User.objects.create_superuser('admin', 'admin@edugen.com', 'EduGenAdmin123!')
    print("✅ Superusuario creado: admin/EduGenAdmin123!")
else:
    print("✅ Superusuario ya existe")
PYTHON

# Verificar salud del sistema
echo "🏥 Verificando salud del sistema..."
python manage.py check --deploy --settings=config.settings.azure_production

echo "🌐 Iniciando servidor Gunicorn en puerto ${PORT:-8000}..."

# Iniciar servidor Gunicorn optimizado para Azure
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload 