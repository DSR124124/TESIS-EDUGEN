# 🚀 Manual Completo de Despliegue - Sistema EduGen

## 📋 Guía Paso a Paso desde Cero

Este manual te guiará desde descargar el proyecto de GitHub hasta tenerlo funcionando completamente en una nueva computadora, ya sea en desarrollo local o en producción.

---

## 📚 Tabla de Contenidos

1. [Preparación del Entorno](#1-preparación-del-entorno)
2. [Descarga e Instalación del Proyecto](#2-descarga-e-instalación-del-proyecto)
3. [Configuración de Base de Datos](#3-configuración-de-base-de-datos)
4. [Configuración de Variables de Entorno](#4-configuración-de-variables-de-entorno)
5. [Instalación de Dependencias](#5-instalación-de-dependencias)
6. [Configuración Inicial del Sistema](#6-configuración-inicial-del-sistema)
7. [Carga de Datos Iniciales](#7-carga-de-datos-iniciales)
8. [Pruebas del Sistema](#8-pruebas-del-sistema)
9. [Despliegue en Producción (Azure)](#9-despliegue-en-producción-azure)
10. [Mantenimiento y Solución de Problemas](#10-mantenimiento-y-solución-de-problemas)

---

## 1. 🛠️ Preparación del Entorno

### 1.1 Requisitos del Sistema

#### Windows
```bash
# Descargar e instalar:
- Python 3.11+ (https://python.org/downloads/)
- Git (https://git-scm.com/downloads)
- Visual Studio Code (opcional, recomendado)
- PostgreSQL 15+ (https://postgresql.org/download/)
```

#### Linux/macOS
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3-pip git postgresql postgresql-contrib

# macOS (con Homebrew)
brew install python@3.11 git postgresql
```

### 1.2 Verificar Instalaciones

```bash
# Verificar versiones
python --version    # Debe ser 3.11+
git --version      # Cualquier versión reciente
psql --version     # PostgreSQL 15+
```

---

## 2. 📥 Descarga e Instalación del Proyecto

### 2.1 Clonar el Repositorio

```bash
# Navegar al directorio donde quieres instalar
cd C:\Proyectos  # Windows
cd ~/Proyectos   # Linux/macOS

# Clonar el repositorio
git clone https://github.com/TU-USUARIO/TESIS-EDUGEN.git
cd TESIS-EDUGEN
```

### 2.2 Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Verificar que está activado (debe aparecer (.venv) en el prompt)
```

### 2.3 Estructura del Proyecto

```
TESIS-EDUGEN/
├── 📁 apps/                    # Aplicaciones Django
│   ├── accounts/              # Sistema de usuarios
│   ├── academic/              # Gestión académica
│   ├── ai_content_generator/  # Generador de contenido IA
│   ├── content/               # Gestión de contenidos
│   ├── director/              # Panel de director
│   ├── institutions/          # Instituciones educativas
│   └── portfolios/            # Portafolios de estudiantes
├── 📁 config/                 # Configuración Django
│   ├── settings/              # Configuraciones por entorno
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI para producción
├── 📁 static/                 # Archivos estáticos (CSS, JS, imágenes)
├── 📁 templates/              # Plantillas HTML
├── 📁 media/                  # Archivos subidos por usuarios
├── 📁 scripts/                # Scripts de utilidad
├── 📁 requirements/           # Dependencias por entorno
├── manage.py                  # Comando principal Django
├── app.py                     # Entry point para Azure
└── startup.sh                 # Script de inicio para Azure
```

---

## 3. 🗄️ Configuración de Base de Datos

### 3.1 PostgreSQL Local (Desarrollo)

#### Windows
```bash
# Abrir SQL Shell (psql) como administrador
# Crear base de datos
CREATE DATABASE edugen_db;
CREATE USER edugen_user WITH PASSWORD 'tu_password_segura';
GRANT ALL PRIVILEGES ON DATABASE edugen_db TO edugen_user;
\q
```

#### Linux/macOS
```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE edugen_db;
CREATE USER edugen_user WITH PASSWORD 'tu_password_segura';
GRANT ALL PRIVILEGES ON DATABASE edugen_db TO edugen_user;
\q
```

### 3.2 SQLite (Alternativa Simple)

Si prefieres usar SQLite para desarrollo local:
```bash
# No necesitas configurar nada, Django creará el archivo automáticamente
# El archivo se creará en: db/sistema_educativo_db.sqlite3
```

---

## 4. ⚙️ Configuración de Variables de Entorno

### 4.1 Crear Archivo de Configuración

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Crear archivo .env
# Windows
echo. > .env

# Linux/macOS
touch .env
```

### 4.2 Configurar Variables de Entorno

Edita el archivo `.env` con el siguiente contenido:

```env
# Configuración General
DEBUG=True
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui
DJANGO_SETTINGS_MODULE=config.settings.local

# Base de Datos PostgreSQL (si usas PostgreSQL)
DB_NAME=edugen_db
DB_USER=edugen_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=5432

# OpenAI (para generación de contenido IA)
OPENAI_API_KEY=tu-api-key-de-openai-aqui

# Google OAuth (opcional)
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret

# Email (opcional, para notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion

# Azure (solo para producción)
AZURE_STORAGE_ACCOUNT_NAME=
AZURE_STORAGE_ACCOUNT_KEY=
AZURE_STORAGE_CONTAINER_NAME=media
```

### 4.3 Generar Clave Secreta

```python
# Ejecutar en Python para generar una clave secreta
import secrets
print(secrets.token_urlsafe(50))
```

---

## 5. 📦 Instalación de Dependencias

### 5.1 Instalar Dependencias de Desarrollo

```bash
# Asegúrate de que el entorno virtual esté activado
pip install --upgrade pip

# Instalar dependencias de desarrollo
pip install -r requirements/local.txt

# Si el archivo no existe, instalar manualmente:
pip install django==4.2.7
pip install psycopg2-binary
pip install python-dotenv
pip install pillow
pip install openai
pip install whitenoise
pip install gunicorn
pip install django-allauth
```

### 5.2 Verificar Instalación

```bash
# Verificar que Django está instalado
python -c "import django; print(django.get_version())"

# Listar paquetes instalados
pip list
```

---

## 6. 🔧 Configuración Inicial del Sistema

### 6.1 Configurar Django

```bash
# Crear directorios necesarios
mkdir -p media/uploads
mkdir -p static/uploads
mkdir -p db

# Verificar configuración
python manage.py check
```

### 6.2 Ejecutar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Si hay errores, ejecutar por aplicación:
python manage.py migrate accounts
python manage.py migrate academic
python manage.py migrate institutions
python manage.py migrate portfolios
python manage.py migrate ai_content_generator
python manage.py migrate content
```

### 6.3 Recolectar Archivos Estáticos

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

---

## 7. 📊 Carga de Datos Iniciales

### 7.1 Crear Superusuario

```bash
# Crear superusuario administrador
python manage.py createsuperuser

# Seguir las instrucciones:
# Username: admin
# Email: admin@edugen.com
# Password: (tu password segura)
```

### 7.2 Cargar Datos de Prueba

#### Opción A: Usar Comandos de Gestión
```bash
# Crear institución de prueba
python manage.py shell
```

```python
# Dentro del shell de Django
from apps.institutions.models import Institution

# Crear institución
institution = Institution.objects.create(
    name='TÉCNICO FAP MANUEL POLO JIMÉNEZ',
    code='POLO-JIMENEZ',
    domain='cased.edu.pe',
    address='Lima, Perú',
    phone='01-234-5678',
    email='info@cased.edu.pe',
    type='TECNICO',
    established_year=1980,
    is_active=True
)

print(f"Institución creada: {institution.name}")
exit()
```

#### Opción B: Usar Scripts de Migración
```bash
# Si existen los scripts de estudiantes
python scripts/deploy_production_students.py     # Estudiantes 4F
python scripts/deploy_production_students_5a.py  # Estudiantes 5A
```

### 7.3 Crear Usuarios de Prueba

```bash
# Crear usuarios de prueba manualmente
python manage.py shell
```

```python
# Crear director de prueba
from apps.accounts.models import CustomUser
from apps.academic.models import Teacher

# Crear usuario director
director = CustomUser.objects.create_user(
    username='director_prueba',
    email='director@cased.edu.pe',
    password='director123',
    first_name='Juan',
    last_name='Pérez',
    role='director',
    is_active=True
)

# Crear usuario profesor
profesor = CustomUser.objects.create_user(
    username='profesor_prueba',
    email='profesor@cased.edu.pe',
    password='profesor123',
    first_name='María',
    last_name='García',
    role='teacher',
    is_active=True
)

print("Usuarios de prueba creados")
exit()
```

---

## 8. 🧪 Pruebas del Sistema

### 8.1 Iniciar Servidor de Desarrollo

```bash
# Iniciar servidor
python manage.py runserver

# El servidor estará disponible en:
# http://127.0.0.1:8000/
```

### 8.2 Verificar Funcionalidades

#### Accesos de Prueba
```
🔐 Panel de Administración:
URL: http://127.0.0.1:8000/admin/
Usuario: admin
Password: (el que creaste)

🎓 Sistema Principal:
URL: http://127.0.0.1:8000/
- Director: director@cased.edu.pe / director123
- Profesor: profesor@cased.edu.pe / profesor123
- Estudiante: (usar los creados con scripts)
```

#### Lista de Verificación
- [ ] ✅ Página principal carga correctamente
- [ ] ✅ Login funciona para diferentes roles
- [ ] ✅ Panel de administración accesible
- [ ] ✅ Creación de usuarios funciona
- [ ] ✅ Subida de archivos funciona
- [ ] ✅ Base de datos guarda información
- [ ] ✅ Archivos estáticos se cargan (CSS, JS, imágenes)

### 8.3 Solución de Problemas Comunes

#### Error: "No module named 'config'"
```bash
# Asegúrate de estar en el directorio correcto
pwd  # Debe mostrar la ruta a TESIS-EDUGEN
ls   # Debe mostrar manage.py y config/
```

#### Error: "Database connection failed"
```bash
# Verificar que PostgreSQL esté corriendo
# Windows
services.msc  # Buscar PostgreSQL

# Linux
sudo systemctl status postgresql

# Verificar conexión
psql -h localhost -U edugen_user -d edugen_db
```

#### Error: "Static files not found"
```bash
# Recolectar archivos estáticos nuevamente
python manage.py collectstatic --clear --noinput
```

---

## 9. ☁️ Despliegue en Producción (Azure)

### 9.1 Preparación para Producción

#### Crear archivos de producción
```bash
# Crear requirements/production.txt
cat > requirements/production.txt << EOF
django==4.2.7
psycopg2-binary==2.9.7
gunicorn==21.2.0
whitenoise==6.5.0
python-dotenv==1.0.0
pillow==10.0.1
openai==0.28.1
django-allauth==0.57.0
azure-storage-blob==12.17.0
EOF
```

#### Configurar startup.sh
```bash
#!/bin/bash
echo "🚀 Iniciando EduGen en Azure..."

cd /home/site/wwwroot
export DJANGO_SETTINGS_MODULE=config.settings.azure_production

# Crear directorios
mkdir -p media staticfiles

# Instalar dependencias
pip install -r requirements/production.txt

# Recolectar archivos estáticos
python manage.py collectstatic --noinput --clear

# Ejecutar migraciones
python manage.py migrate --noinput

# Crear superusuario si no existe
python manage.py shell << EOF
from apps.accounts.models import CustomUser
if not CustomUser.objects.filter(is_superuser=True).exists():
    CustomUser.objects.create_superuser('admin', 'admin@edugen.com', 'AdminEduGen2024!')
    print('Superusuario creado')
EOF

echo "✅ Configuración completada"
exec gunicorn --bind=0.0.0.0 --timeout 600 config.wsgi
```

### 9.2 Configuración en Azure

#### Variables de Entorno en Azure
```bash
# En Azure App Service -> Configuration -> Application Settings
DEBUG=False
SECRET_KEY=tu-clave-super-secreta-para-produccion
DJANGO_SETTINGS_MODULE=config.settings.azure_production
DB_NAME=postgres
DB_USER=EDUGEN
DB_PASSWORD=tu-password-postgresql-azure
DB_HOST=edugen-server.postgres.database.azure.com
DB_PORT=5432
OPENAI_API_KEY=tu-api-key-openai
WEBSITE_HOSTNAME=tu-app.azurewebsites.net
```

#### Comandos de Despliegue
```bash
# Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login a Azure
az login

# Crear resource group
az group create --name edugen-rg --location "East US"

# Crear App Service Plan
az appservice plan create --name edugen-plan --resource-group edugen-rg --sku B1 --is-linux

# Crear Web App
az webapp create --resource-group edugen-rg --plan edugen-plan --name tu-app-edugen --runtime "PYTHON|3.11"

# Configurar deployment desde GitHub
az webapp deployment source config --name tu-app-edugen --resource-group edugen-rg --repo-url https://github.com/TU-USUARIO/TESIS-EDUGEN --branch main --manual-integration
```

### 9.3 Base de Datos PostgreSQL en Azure

```bash
# Crear servidor PostgreSQL
az postgres server create \
    --resource-group edugen-rg \
    --name edugen-postgres-server \
    --location eastus \
    --admin-user EDUGEN \
    --admin-password TuPasswordSegura123! \
    --sku-name B_Gen5_1

# Configurar firewall
az postgres server firewall-rule create \
    --resource-group edugen-rg \
    --server edugen-postgres-server \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

---

## 10. 🔧 Mantenimiento y Solución de Problemas

### 10.1 Comandos de Mantenimiento

#### Backup de Base de Datos
```bash
# PostgreSQL local
pg_dump -U edugen_user -h localhost edugen_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U edugen_user -h localhost edugen_db < backup_20240101.sql
```

#### Limpiar Archivos Temporales
```bash
# Limpiar migraciones
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Limpiar archivos Python compilados
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 10.2 Logs y Debugging

#### Ver logs en desarrollo
```bash
# Logs detallados
python manage.py runserver --verbosity=2

# Verificar configuración
python manage.py check --deploy
```

#### Ver logs en Azure
```bash
# Habilitar logs en Azure
az webapp log config --name tu-app-edugen --resource-group edugen-rg --web-server-logging filesystem

# Ver logs en tiempo real
az webapp log tail --name tu-app-edugen --resource-group edugen-rg
```

### 10.3 Solución de Problemas Frecuentes

#### "500 Internal Server Error" en producción
```bash
# 1. Verificar logs
az webapp log tail --name tu-app-edugen --resource-group edugen-rg

# 2. Verificar variables de entorno
az webapp config appsettings list --name tu-app-edugen --resource-group edugen-rg

# 3. Verificar que DEBUG=False
# 4. Verificar ALLOWED_HOSTS
# 5. Verificar conexión a base de datos
```

#### "Static files not loading"
```bash
# 1. Verificar STATIC_ROOT y STATIC_URL
# 2. Ejecutar collectstatic
python manage.py collectstatic --clear --noinput

# 3. Verificar Whitenoise configuración
```

#### "Database connection failed"
```bash
# 1. Verificar variables de entorno de DB
# 2. Verificar firewall rules en Azure PostgreSQL
# 3. Verificar SSL requirements
```

---

## 🎉 ¡Felicidades!

Si has llegado hasta aquí, deberías tener el sistema EduGen funcionando completamente. 

### 📞 Soporte y Recursos

- **Documentación Django**: https://docs.djangoproject.com/
- **Azure App Service**: https://docs.microsoft.com/azure/app-service/
- **PostgreSQL**: https://www.postgresql.org/docs/

### 🔄 Próximos Pasos

1. **Configurar monitoreo** con Azure Application Insights
2. **Implementar backups automáticos**
3. **Configurar dominio personalizado**
4. **Implementar HTTPS con certificado SSL**
5. **Configurar CDN para archivos estáticos**

---

**¿Necesitas ayuda?** Revisa la sección de solución de problemas o consulta los logs del sistema para identificar errores específicos. 