# 🚀 Guía Completa de Despliegue en Azure Web Apps ($20 USD/mes)

## 📋 Resumen del Proyecto

**Sistema Educativo Django** - Plataforma educativa con editor WYSIWYG, generación de contenido con IA, gestión de portafolios y autenticación social.

### 🏗️ Arquitectura del Proyecto
- **Framework**: Django 4.2.10
- **Base de datos**: SQLite3 (optimizada para bajo costo)
- **IA**: DeepSeek API (compatible con OpenAI)
- **Autenticación**: Google OAuth2 + Django Auth
- **Editor**: TinyMCE con capacidades WYSIWYG avanzadas
- **Archivos**: Azure Blob Storage + WhiteNoise para estáticos

---

## 💰 Presupuesto Optimizado ($20 USD/mes)

### Distribución de Costos:
- **Azure App Service B1**: ~$13.40/mes
- **Azure Storage Account**: ~$2-3/mes
- **DeepSeek API**: ~$3-4/mes
- **Total estimado**: $18-20/mes

---

## 🛠️ FASE 1: Preparación Previa

### 1.1. Requisitos Previos
```bash
# Verificar instalaciones locales
python --version    # >= 3.8
pip --version
git --version
```

### 1.2. Cuentas Necesarias
- [ ] **Cuenta de Azure** (con créditos gratuitos si es primera vez)
- [ ] **Cuenta de Google Cloud** (para OAuth2)
- [ ] **Cuenta de DeepSeek** (para API de IA)

### 1.3. Herramientas
- [ ] **Azure CLI** - [Descargar aquí](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [ ] **Git** (ya instalado)
- [ ] **Editor de código** (VS Code recomendado)

---

## 🔧 FASE 2: Configuración de Azure

### 2.1. Instalación y Login de Azure CLI
```bash
# Instalar Azure CLI (si no está instalado)
# Descargar de: https://aka.ms/installazurecliwindows

# Login en Azure
az login

# Verificar suscripción
az account show
```

### 2.2. Crear Grupo de Recursos
```bash
# Crear grupo de recursos en región de bajo costo
az group create \
  --name rg-sistema-educativo \
  --location "East US"
```

### 2.3. Crear Azure Storage Account
```bash
# Crear storage account para archivos media
az storage account create \
  --name sistemeducativofiles \
  --resource-group rg-sistema-educativo \
  --location "East US" \
  --sku Standard_LRS \
  --kind StorageV2

# Crear container para archivos media
az storage container create \
  --name media \
  --account-name sistemeducativofiles \
  --public-access blob

# Obtener connection string (IMPORTANTE: guardar este valor)
az storage account show-connection-string \
  --name sistemeducativofiles \
  --resource-group rg-sistema-educativo
```

### 2.4. Crear App Service Plan (B1 - Básico)
```bash
# Crear plan de servicio básico B1
az appservice plan create \
  --name plan-sistema-educativo \
  --resource-group rg-sistema-educativo \
  --sku B1 \
  --is-linux
```

### 2.5. Crear Web App
```bash
# Crear la aplicación web
az webapp create \
  --resource-group rg-sistema-educativo \
  --plan plan-sistema-educativo \
  --name sistema-educativo-app \
  --runtime "PYTHON|3.11" \
  --startup-file "config/wsgi.py"
```

---

## 🔐 FASE 3: Configuración de APIs Externas

### 3.1. Configurar Google OAuth2

#### Paso 1: Google Cloud Console
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear nuevo proyecto o seleccionar existente
3. Habilitar **Google+ API** y **OAuth2**

#### Paso 2: Crear Credenciales OAuth2
1. Ir a **APIs & Services > Credentials**
2. Crear **OAuth 2.0 Client ID**
3. Tipo: **Web Application**
4. **Authorized redirect URIs**:
   ```
   https://sistema-educativo-app.azurewebsites.net/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

#### Paso 3: Obtener Credenciales (GUARDAR ESTOS VALORES)
- **Client ID**: `tu-client-id.apps.googleusercontent.com`
- **Client Secret**: `tu-client-secret`

### 3.2. Configurar DeepSeek API

#### Paso 1: Crear Cuenta en DeepSeek
1. Ir a [DeepSeek Platform](https://platform.deepseek.com/)
2. Registrarse con email
3. Verificar cuenta

#### Paso 2: Obtener API Key
1. Ir a **API Keys**
2. Crear nueva clave
3. **GUARDAR**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🌐 FASE 4: Variables de Entorno en Azure

### 4.1. Configurar Variables de Entorno Críticas
```bash
# SECRET_KEY para Django (GENERAR UNA NUEVA)
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings SECRET_KEY="tu-nueva-secret-key-muy-segura-aqui-123456789"

# DeepSeek API
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings DEEPSEEK_API_KEY="tu-deepseek-api-key-aqui"

az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings DEEPSEEK_MODEL="deepseek-chat"

# Google OAuth2
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="tu-google-client-id.apps.googleusercontent.com"

az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="tu-google-client-secret"

# Azure Storage (usar el connection string obtenido anteriormente)
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=sistemeducativofiles;AccountKey=tu-key-aqui"

az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings AZURE_STORAGE_CONTAINER_NAME="media"

# Django Settings
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings DJANGO_SETTINGS_MODULE="config.settings.azure_production"

az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings WEBSITE_HOSTNAME="sistema-educativo-app.azurewebsites.net"
```

### 4.2. Variables Opcionales (Mejoras)
```bash
# Application Insights (monitoreo gratuito básico)
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings APPINSIGHTS_INSTRUMENTATION_KEY="opcional-si-quieres-monitoreo"

# Timezone
az webapp config appsettings set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --settings TZ="America/Lima"
```

---

## 📁 FASE 5: Preparación del Código

### 5.1. Crear Archivos de Configuración Azure

#### Crear `requirements-azure.txt`:
```bash
# En tu proyecto local, crear requirements-azure.txt
cat > requirements-azure.txt << EOF
Django>=4.2.0,<4.3.0
djangorestframework>=3.14.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
Pillow>=9.5.0
python-dotenv>=1.0.0
django-cors-headers>=4.3.1
requests>=2.30.0
tqdm>=4.65.0
django-tinymce==3.7.1
django-allauth==0.61.1
social-auth-app-django==5.4.0
beautifulsoup4==4.12.3
django-extensions==3.2.3
PyPDF2==3.0.1
# Azure dependencies
azure-storage-blob>=12.14.0
django-storages[azure]>=1.13.2
whitenoise>=6.4.0
gunicorn>=20.1.0
psycopg2>=2.9.5
dnspython>=2.3.0
EOF
```

#### Crear `startup.sh` para Azure:
```bash
cat > startup.sh << 'EOF'
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
EOF

chmod +x startup.sh
```

### 5.2. Actualizar `config/wsgi.py` para Azure:
```python
# config/wsgi.py
import os
import logging
from django.core.wsgi import get_wsgi_application

# Configuración para Azure
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

# Desactivar logs innecesarios en producción
logging.getLogger('django.db.backends').disabled = True
logging.getLogger('django.server').disabled = True

application = get_wsgi_application()
```

---

## 🚀 FASE 6: Despliegue

### 6.1. Configurar Despliegue desde Git

#### Opción A: Desde repositorio local
```bash
# En tu proyecto local
git add .
git commit -m "Configuración para Azure deployment"

# Configurar despliegue local
az webapp deployment source config-local-git \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app

# Obtener URL de Git remoto
az webapp deployment list-publishing-credentials \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --query scmUri

# Agregar remote de Azure
git remote add azure <URL_obtenida_arriba>

# Desplegar
git push azure main
```

#### Opción B: Desde GitHub (Recomendado)
```bash
# 1. Subir código a GitHub (si no lo has hecho)
git remote add origin https://github.com/tu-usuario/sistema-educativo.git
git push -u origin main

# 2. Configurar despliegue desde GitHub
az webapp deployment source config \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --repo-url https://github.com/tu-usuario/sistema-educativo \
  --branch main \
  --manual-integration
```

### 6.2. Configurar Startup Command
```bash
az webapp config set \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --startup-file "startup.sh"
```

---

## 🔍 FASE 7: Verificación y Testing

### 7.1. Verificar Despliegue
```bash
# Ver logs de despliegue
az webapp log tail \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app

# Verificar estado de la app
az webapp show \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --query "state"
```

### 7.2. URLs Importantes
- **Aplicación**: https://sistema-educativo-app.azurewebsites.net/
- **Admin**: https://sistema-educativo-app.azurewebsites.net/admin/
- **Login**: https://sistema-educativo-app.azurewebsites.net/accounts/login/

### 7.3. Testing Básico
1. ✅ **Acceso general**: Abrir URL principal
2. ✅ **Admin panel**: Acceder con admin/admin123
3. ✅ **Google OAuth**: Probar login con Google
4. ✅ **Editor WYSIWYG**: Crear contenido educativo
5. ✅ **IA Content**: Generar contenido con DeepSeek
6. ✅ **File upload**: Subir archivos al Blob Storage

---

## 🔧 FASE 8: Optimizaciones y Mantenimiento

### 8.1. Monitoreo de Costos
```bash
# Ver costos actuales
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --resource-group rg-sistema-educativo
```

### 8.2. Backup Automático de BD
```bash
# Crear script de backup (ejecutar semanalmente)
cat > backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
az webapp ssh --resource-group rg-sistema-educativo --name sistema-educativo-app << 'REMOTE'
cp /tmp/db.sqlite3 /tmp/backups/db_backup_$DATE.sqlite3
echo "Backup creado: db_backup_$DATE.sqlite3"
REMOTE
EOF
```

### 8.3. Configuración de SSL/Dominio Personalizado (Opcional)
```bash
# Si tienes dominio propio
az webapp config hostname add \
  --resource-group rg-sistema-educativo \
  --webapp-name sistema-educativo-app \
  --hostname tu-dominio.com

# SSL gratuito con Let's Encrypt
az webapp config ssl bind \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

---

## 🚨 RESOLUCIÓN DE PROBLEMAS

### Problema 1: Error de Migración
```bash
# Conectarse por SSH y ejecutar
az webapp ssh --resource-group rg-sistema-educativo --name sistema-educativo-app
python manage.py migrate --verbosity=2
```

### Problema 2: Archivos Estáticos no Cargan
```bash
# Verificar configuración de WhiteNoise
python manage.py collectstatic --clear --noinput
```

### Problema 3: Error de Google OAuth
1. Verificar Redirect URI en Google Console
2. Confirmar variables de entorno en Azure
3. Verificar dominio en ALLOWED_HOSTS

### Problema 4: API de IA no Responde
```bash
# Verificar API key
az webapp config appsettings list \
  --resource-group rg-sistema-educativo \
  --name sistema-educativo-app \
  --query "[?name=='DEEPSEEK_API_KEY']"
```

---

## 📊 VARIABLES DE ENTORNO COMPLETAS

### Variables Obligatorias
```bash
SECRET_KEY="django-insecure-CAMBIAR-EN-PRODUCCION-123456789"
DJANGO_SETTINGS_MODULE="config.settings.azure_production"
WEBSITE_HOSTNAME="sistema-educativo-app.azurewebsites.net"
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
AZURE_STORAGE_CONTAINER_NAME="media"
DEEPSEEK_API_KEY="sk-..."
DEEPSEEK_MODEL="deepseek-chat"
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="....apps.googleusercontent.com"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="GOCSPX-..."
```

### Variables Opcionales
```bash
APPINSIGHTS_INSTRUMENTATION_KEY="opcional-para-monitoreo"
TZ="America/Lima"
OPENAI_API_KEY="$DEEPSEEK_API_KEY"  # Compatibilidad
OPENAI_MODEL="$DEEPSEEK_MODEL"      # Compatibilidad
```

---

## 🎯 CHECKLIST FINAL

### Pre-Deploy
- [ ] Azure CLI instalado y configurado
- [ ] Grupo de recursos creado
- [ ] Storage Account configurado  
- [ ] App Service Plan B1 creado
- [ ] Web App creada
- [ ] Google OAuth2 configurado
- [ ] DeepSeek API key obtenida
- [ ] Variables de entorno configuradas

### Deploy
- [ ] Código preparado con archivos Azure
- [ ] requirements-azure.txt creado
- [ ] startup.sh configurado
- [ ] Despliegue ejecutado exitosamente
- [ ] Logs revisados sin errores

### Post-Deploy
- [ ] Aplicación accesible en URL
- [ ] Admin panel funcional
- [ ] Google OAuth operativo
- [ ] Editor WYSIWYG funcionando
- [ ] Generación de contenido IA activa
- [ ] Carga de archivos a Blob Storage
- [ ] Monitoreo de costos configurado

---

## 💡 CONSEJOS DE OPTIMIZACIÓN DE COSTOS

1. **Usar B1 en horarios de desarrollo**: Cambiar a Free tier fuera de horario
2. **Monitorear Storage**: Limpiar archivos antiguos regularmente
3. **Limitar requests de IA**: Implementar cache y límites por usuario
4. **Optimizar imágenes**: Comprimir antes de subir
5. **Review mensual**: Verificar usage y optimizar recursos

---

## 📞 SOPORTE Y RECURSOS

- **Documentación Azure**: https://docs.microsoft.com/azure/app-service/
- **Django on Azure**: https://docs.microsoft.com/azure/app-service/configure-language-python
- **Storage Pricing**: https://azure.microsoft.com/pricing/details/storage/
- **DeepSeek Docs**: https://platform.deepseek.com/docs

---

**🚀 ¡Tu Sistema Educativo está listo para producción en Azure con presupuesto optimizado de $20/mes!** 