# ☁️ Manual de Despliegue Azure - Sistema EduGen

## 🎯 Guía Específica para Azure App Service

> **Nota:** Para instalación desde cero, consulta `MANUAL_DESPLIEGUE_COMPLETO.md`

---

## 📋 Tabla de Contenidos

1. [Preparación para Azure](#1-preparación-para-azure)
2. [Configuración de Azure Resources](#2-configuración-de-azure-resources)
3. [Configuración de Base de Datos PostgreSQL](#3-configuración-de-base-de-datos-postgresql)
4. [Configuración de App Service](#4-configuración-de-app-service)
5. [Variables de Entorno](#5-variables-de-entorno)
6. [Despliegue desde GitHub](#6-despliegue-desde-github)
7. [Configuración Post-Despliegue](#7-configuración-post-despliegue)
8. [Monitoreo y Logs](#8-monitoreo-y-logs)
9. [Solución de Problemas Azure](#9-solución-de-problemas-azure)

---

## 🔧 Requisitos Previos

### Software Necesario
- **Python 3.11+**
- **Git**
- **Azure CLI**
- **PostgreSQL** (para desarrollo local)

### Cuentas Requeridas
- **Cuenta de Azure** con suscripción activa
- **Cuenta de GitHub** para control de versiones
- **Cuenta de Google** para OAuth (opcional)

---

## 🚀 Configuración del Proyecto Django

### 1. Estructura del Proyecto

```
TESIS-EDUGEN/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── azure_production.py
│   │   └── local.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   ├── academic/
│   ├── director/
│   ├── institutions/
│   └── [otros apps]
├── static/
├── media/
├── templates/
├── scripts/
├── startup.sh
├── app.py
└── manage.py
```

### 2. Archivo Principal de Configuración

#### `config/settings/azure_production.py`
```python
import os
from .base import *

# Configuración de seguridad
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')

# Hosts permitidos para Azure
ALLOWED_HOSTS = ['*']
website_hostname = os.environ.get('WEBSITE_HOSTNAME')
if website_hostname:
    ALLOWED_HOSTS.append(website_hostname)
ALLOWED_HOSTS.extend(['.azurewebsites.net', 'localhost', '127.0.0.1'])

# Configuración de seguridad para Azure
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Base de datos PostgreSQL Azure
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'EDUGEN')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST', 'edugenbd.postgres.database.azure.com')
DB_PORT = os.environ.get('DB_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {'sslmode': 'require'},
    }
}

# Archivos estáticos con Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Archivos media
MEDIA_ROOT = os.path.join('/home/site/wwwroot', 'media')
MEDIA_URL = '/media/'
```

### 3. URLs de Media en Producción

#### `config/urls.py` (Fragmento importante)
```python
from django.conf.urls.static import static
from django.conf import settings

# Al final del archivo
# Servir archivos media en todos los entornos
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## ☁️ Configuración de Azure App Service

### 1. Archivos de Configuración

#### `startup.sh`
```bash
#!/bin/bash
echo "🚀 Iniciando aplicación Django en Azure..."

cd /home/site/wwwroot
export DJANGO_SETTINGS_MODULE=config.settings.azure_production

# Crear directorio de media
echo "📁 Configurando directorio de media..."
mkdir -p /home/site/wwwroot/media
chmod 755 /home/site/wwwroot/media

# Migrar archivos de media existentes
if [ -d "media" ]; then
    echo "📋 Migrando archivos de media..."
    python scripts/migrate_media_files.py
fi

# Recolectar archivos estáticos
echo "🔧 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Ejecutar migraciones
echo "🔧 Ejecutando migraciones..."
python manage.py migrate --noinput

echo "🎉 Configuración completada. Iniciando servidor..."
exec gunicorn --bind=0.0.0.0 --timeout 600 config.wsgi
```

#### `app.py`
```python
"""Entry point for Azure App Service"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

from config.wsgi import application
app = application
```

---

## 🗄️ Configuración de Base de Datos PostgreSQL

### Variables de Entorno para PostgreSQL

```bash
DB_NAME=postgres
DB_USER=EDUGEN
DB_PASSWORD=tu_password_segura
DB_HOST=edugenbd.postgres.database.azure.com
DB_PORT=5432
```

### Comando de Creación en Azure

```bash
az postgres server create \
    --resource-group edugen-rg \
    --name edugen-postgres-server \
    --location "Central US" \
    --admin-user EDUGEN \
    --admin-password "TuPasswordSegura123!" \
    --sku-name GP_Gen5_1
```

---

## 📁 Configuración de Archivos Estáticos y Media

### 1. Script de Migración de Media

#### `scripts/migrate_media_files.py`
```python
#!/usr/bin/env python
"""Script to migrate media files to Azure production environment"""
import os
import shutil
from pathlib import Path

def migrate_media_files():
    print("🔄 Migrando archivos de media...")
    
    base_dir = Path(__file__).resolve().parent.parent
    local_media = base_dir / 'media'
    production_media = Path('/home/site/wwwroot/media')
    
    if not local_media.exists():
        print("❌ No se encontró el directorio media local")
        return False
    
    production_media.mkdir(parents=True, exist_ok=True)
    
    try:
        for root, dirs, files in os.walk(local_media):
            rel_path = Path(root).relative_to(local_media)
            dest_dir = production_media / rel_path
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                src_file = Path(root) / file
                dest_file = dest_dir / file
                
                if not dest_file.exists():
                    print(f"📋 Copiando: {rel_path / file}")
                    shutil.copy2(src_file, dest_file)
        
        print("✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == '__main__':
    migrate_media_files()
```

### 2. Script de Diagnóstico

#### `scripts/debug_media.py`
```python
#!/usr/bin/env python
"""Debug script to check media file configuration"""
import os
import sys
from pathlib import Path

def debug_media_configuration():
    print("🔍 DEBUGGING MEDIA CONFIGURATION")
    print("=" * 50)
    
    # Check current working directory
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    # Check media directory
    media_path = Path("/home/site/wwwroot/media")
    print(f"📁 Ruta de media: {media_path}")
    print(f"📂 Media existe: {media_path.exists()}")
    
    if media_path.exists():
        print(f"📊 Contenido de media:")
        for item in media_path.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                print(f"  📄 {item.relative_to(media_path)} ({size} bytes)")

if __name__ == "__main__":
    debug_media_configuration()
```

---

## 🔧 Variables de Entorno

### Variables Críticas en Azure App Service

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.azure_production` | Configuración Django |
| `SECRET_KEY` | `tu-secret-key-segura` | Clave secreta Django |
| `DB_NAME` | `postgres` | Nombre base de datos |
| `DB_USER` | `EDUGEN` | Usuario PostgreSQL |
| `DB_PASSWORD` | `tu-password` | Contraseña PostgreSQL |
| `DB_HOST` | `edugenbd.postgres.database.azure.com` | Host PostgreSQL |
| `DB_PORT` | `5432` | Puerto PostgreSQL |

### Comando para Configurar Variables

```bash
az webapp config appsettings set \
    --name edugen-app \
    --resource-group edugen-rg \
    --settings \
        DJANGO_SETTINGS_MODULE="config.settings.azure_production" \
        SECRET_KEY="tu-secret-key" \
        DB_NAME="postgres" \
        DB_USER="EDUGEN" \
        DB_PASSWORD="tu-password" \
        DB_HOST="edugenbd.postgres.database.azure.com"
```

---

## 🚀 Proceso de Despliegue

### 1. Despliegue Manual

```bash
# Hacer commit de cambios
git add .
git commit -m "Configure Azure production deployment"
git push origin main

# El despliegue automático se activa desde GitHub
```

### 2. Verificación Post-Despliegue

```bash
# Health check
curl https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/health/

# Verificar login
curl https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/login/
```

---

## 👥 Configuración de Usuarios y Permisos

### 1. Crear Usuarios en Producción

#### Script para Configurar Director

```python
# En Azure Console
python3 -c "
import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

import django
django.setup()

from apps.accounts.models import CustomUser, Director
from apps.institutions.models import Institution

# Crear institución
institution, created = Institution.objects.get_or_create(
    code='0000001',
    defaults={
        'name': 'TÉCNICO FAP MANUEL POLO JIMÉNEZ',
        'domain': 'tecnicofap'
    }
)

# Crear usuario director
email = '246810diegosr@gmail.com'
user, created = CustomUser.objects.get_or_create(
    email=email,
    defaults={
        'first_name': 'Diego',
        'last_name': 'Director',
        'role': 'director',
        'is_active': True
    }
)

# Crear perfil director
director, created = Director.objects.get_or_create(
    user=user,
    defaults={
        'institution': institution,
        'is_active': True
    }
)

print(f'✅ Director configurado: {user.email}')
"
```

### 2. Configurar Profesores

```python
# Script para activar profesores
python3 -c "
from apps.accounts.models import Teacher, CustomUser
from django.contrib.auth.hashers import make_password

profesores = [
    {'email': 'dennistesis9@gmail.com', 'nombre': 'Dennis Armando'},
    {'email': 'chacatesis@gmail.com', 'nombre': 'Javier Martin'}
]

for prof in profesores:
    try:
        user = CustomUser.objects.get(email=prof['email'])
        user.password = make_password('profesor123')
        user.is_active = True
        user.save()
        print(f'✅ {prof["nombre"]}: {prof["email"]} - Contraseña: profesor123')
    except:
        print(f'❌ Error con {prof["email"]}')
"
```

### 3. Configurar Estudiantes sin Gmail

```bash
# Crear estudiantes con contraseñas predeterminadas
python scripts/create_students_with_passwords.py

# O resetear contraseñas existentes
python scripts/create_students_with_passwords.py --reset
```

#### Opciones de Login para Estudiantes:

1️⃣ **Con Usuario y Contraseña:**
   - Usuario: `estudiante01`, `estudiante02`, `estudiante03`
   - Contraseña: `estudiante123`

2️⃣ **Con Email y Contraseña:**
   - Email: `ana.garcia@tecnicofap.edu.pe`
   - Contraseña: `estudiante123`

3️⃣ **Con Google OAuth (opcional):**
   - Solo si el estudiante tiene cuenta Gmail

---

## 🔧 Resolución de Problemas Comunes

### 1. Error 404 en Archivos Media

**Síntoma:** Los logos e imágenes no se cargan, error 404.

**Solución:**
```bash
# 1. Verificar ubicación de archivos
cd /tmp/8ddac7092732a7c/
ls -la media/institutions/logos/

# 2. Copiar a ubicación correcta
mkdir -p /home/site/wwwroot/media/institutions/logos/
cp -r media/* /home/site/wwwroot/media/

# 3. Verificar permisos
chmod -R 755 /home/site/wwwroot/media/

# 4. Probar URL
curl https://tu-app.azurewebsites.net/media/institutions/logos/images.jpeg
```

### 2. Error Acceso Denegado para Profesores

**Síntoma:** Profesores no pueden iniciar sesión con Google OAuth.

**Diagnóstico:**
```python
# Verificar estado de profesores
from apps.accounts.models import Teacher
for teacher in Teacher.objects.all():
    print(f"{teacher.user.first_name}: {teacher.user.email} - Activo: {teacher.is_active}")
```

**Solución:**
```python
# Activar todos los profesores
for teacher in Teacher.objects.all():
    teacher.user.is_active = True
    teacher.user.save()
    teacher.is_active = True
    teacher.save()
```

### 3. Error de Conexión a Base de Datos

**Verificación:**
```bash
# Verificar variables de entorno
az webapp config appsettings list --name edugen-app --resource-group edugen-rg

# Verificar conectividad
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='edugenbd.postgres.database.azure.com',
        database='postgres',
        user='EDUGEN',
        password='tu_password'
    )
    print('✅ Conexión exitosa')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### 4. Comandos de Diagnóstico Útiles

```bash
# Ver logs en tiempo real
az webapp log tail --name edugen-app --resource-group edugen-rg

# Reiniciar aplicación
az webapp restart --name edugen-app --resource-group edugen-rg

# Ver configuración
az webapp config show --name edugen-app --resource-group edugen-rg

# SSH a la instancia
az webapp ssh --name edugen-app --resource-group edugen-rg
```

---

## 📊 Mantenimiento y Monitoreo

### 1. Backup de Base de Datos

```bash
# Crear backup
az postgres db export \
    --resource-group edugen-rg \
    --server-name edugen-postgres-server \
    --name postgres \
    --output-file backup-$(date +%Y%m%d).sql
```

### 2. Monitoreo de Logs

```bash
# Logs de aplicación
az webapp log download --name edugen-app --resource-group edugen-rg

# Logs específicos
az webapp log show --name edugen-app --resource-group edugen-rg
```

### 3. Actualizaciones de Código

```bash
# Hacer cambios en código
git add .
git commit -m "Update: descripción del cambio"
git push origin main

# El despliegue automático se activa
# Verificar en: https://portal.azure.com
```

---

## 📝 Checklist de Verificación

### ✅ Pre-Despliegue
- [ ] Código funcionando en local
- [ ] Variables de entorno configuradas
- [ ] Archivos de configuración Azure creados
- [ ] Base de datos PostgreSQL configurada

### ✅ Durante Despliegue
- [ ] App Service creado y configurado
- [ ] Variables de entorno en Azure configuradas
- [ ] Código desplegado desde GitHub
- [ ] Base de datos conectada

### ✅ Post-Despliegue
- [ ] Health check: `GET /health/` retorna 200
- [ ] Login page: `GET /login/` accesible
- [ ] Archivos estáticos funcionando
- [ ] Archivos media funcionando
- [ ] Usuarios pueden iniciar sesión
- [ ] Funciones principales verificadas

---

## 🌐 URLs de Producción

- **Aplicación Principal:** https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/
- **Login:** https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/login/
- **Admin:** https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/admin/
- **Health Check:** https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net/health/

---

## 🆘 Contacto y Soporte

Para problemas específicos:

1. **Verificar logs:** `az webapp log tail --name edugen-app`
2. **Ejecutar diagnósticos:** `python scripts/debug_media.py`
3. **Reiniciar si es necesario:** `az webapp restart --name edugen-app`

---

**✅ Manual completado - Sistema EduGen implementado exitosamente en Azure App Service**

*Fecha de última actualización: Junio 2025*
*Versión: 1.0* 