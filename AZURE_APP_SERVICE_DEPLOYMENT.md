# 🚀 Despliegue EduGen en Azure App Service

## 📋 Información del Proyecto
- **Aplicación**: EduGen (Django)
- **Método**: Azure App Service (Linux + Python 3.11)
- **Costo estimado**: ~$20-30/mes
- **Ventajas**: Más simple, sin Docker, compatible con cuentas educativas

## 🔧 Prerrequisitos

1. **Azure CLI instalado y autenticado**
2. **Cuenta de Azure activa** (Azure for Students funciona)
3. **Código fuente del proyecto EduGen**

## 🏗️ Paso 1: Crear Recursos Base

### 1.1 Crear Resource Group (si no existe)
```bash
az group create --name "rg-edugen-containers" --location "Central US"
```

### 1.2 Crear App Service Plan
```bash
az appservice plan create \
  --resource-group "rg-edugen-containers" \
  --name "edugen-app-plan" \
  --location "Central US" \
  --sku B1 \
  --is-linux
```

### 1.3 Crear Web App
```bash
az webapp create \
  --resource-group "rg-edugen-containers" \
  --plan "edugen-app-plan" \
  --name "edugen-diego-2025" \
  --runtime "PYTHON:3.11" \
  --deployment-local-git
```

## 🗄️ Paso 2: Crear Base de Datos PostgreSQL

### 2.1 Crear servidor PostgreSQL
```bash
az postgres flexible-server create \
  --resource-group "rg-edugen-containers" \
  --name "edugen-postgres-server" \
  --location "Central US" \
  --admin-user postgres \
  --admin-password "EduGen123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32
```

### 2.2 Crear base de datos
```bash
az postgres flexible-server db create \
  --resource-group "rg-edugen-containers" \
  --server-name "edugen-postgres-server" \
  --database-name edugen
```

### 2.3 Configurar firewall para App Service
```bash
az postgres flexible-server firewall-rule create \
  --resource-group "rg-edugen-containers" \
  --name "edugen-postgres-server" \
  --rule-name "AllowAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

## ⚙️ Paso 3: Configurar Variables de Entorno

### 3.1 Configurar variables de la aplicación
```bash
az webapp config appsettings set \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025" \
  --settings \
    DJANGO_SETTINGS_MODULE="config.settings.azure_production" \
    DEBUG="False" \
    ALLOWED_HOSTS="edugen-diego-2025.azurewebsites.net,localhost,127.0.0.1" \
    WEBSITE_HOSTNAME="edugen-diego-2025.azurewebsites.net" \
    CSRF_TRUSTED_ORIGINS="https://edugen-diego-2025.azurewebsites.net" \
    PGHOST="edugen-postgres-server.postgres.database.azure.com" \
    PGPORT="5432" \
    PGDATABASE="edugen" \
    PGUSER="postgres" \
    PGPASSWORD="EduGen123!" \
    SECRET_KEY="django-insecure-azure-app-service-key-2025-change-in-production" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="AIzaSyDbaO4sVGS5_dCMV1r4yizjzqAoakAnME0" \
    DEEPSEEK_API_KEY="sk-f1bfb13127b14daf97788bb0232a5584" \
    AI_PROVIDER="deepseek"
```

### 3.2 Configurar comando de inicio
```bash
az webapp config set \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025" \
  --startup-file "startup.sh"
```

## 📁 Paso 4: Preparar Archivos de Configuración

### 4.1 Crear startup.sh
```bash
#!/bin/bash

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate --noinput

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario si no existe
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@edugen.com', 'EduGen123!')" | python manage.py shell

# Iniciar servidor Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 2 config.wsgi:application
```

### 4.2 Actualizar requirements.txt
Asegurar que incluya:
```
gunicorn>=20.1.0
psycopg2-binary>=2.9.0
whitenoise>=6.0.0
```

## 🚀 Paso 5: Desplegar Código

### 5.1 Configurar Git para despliegue
```bash
# Obtener URL de Git
az webapp deployment source config-local-git \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025" \
  --query url \
  --output tsv
```

### 5.2 Obtener credenciales de despliegue
```bash
az webapp deployment list-publishing-credentials \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025" \
  --query "{Username:publishingUserName,Password:publishingPassword}" \
  --output table
```

### 5.3 Desplegar código
```bash
# Agregar remote de Azure
git remote add azure [URL-obtenida-en-5.1]

# Hacer push a Azure
git push azure main
```

## 🔍 Paso 6: Verificar Despliegue

### 6.1 Ver logs de la aplicación
```bash
az webapp log tail \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025"
```

### 6.2 Verificar estado de la aplicación
```bash
az webapp show \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025" \
  --query "{Name:name,State:state,DefaultHostName:defaultHostName}" \
  --output table
```

### 6.3 Acceder a la aplicación
- **URL Principal**: `https://edugen-diego-2025.azurewebsites.net`
- **Admin Django**: `https://edugen-diego-2025.azurewebsites.net/admin/`
- **Credenciales Admin**: usuario: `admin`, contraseña: `EduGen123!`

## 💰 Estimación de Costos

**Azure App Service (Basic B1):**
- Costo base: ~$15-20/mes
- Tráfico incluido: 165 GB/mes

**Azure Database for PostgreSQL (Burstable B1ms):**
- Costo base: ~$15-25/mes
- Almacenamiento: 32 GB incluidos

**Total estimado: $30-45/mes**

## 🔧 Comandos Útiles

### Reiniciar aplicación
```bash
az webapp restart \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025"
```

### Ver configuración actual
```bash
az webapp config appsettings list \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025" \
  --output table
```

### Ejecutar comandos Django remotamente
```bash
az webapp ssh \
  --resource-group "rg-edugen-containers" \
  --name "edugen-diego-2025"
```

## 🐛 Solución de Problemas

### 1. Error 500 - Internal Server Error
```bash
# Ver logs detallados
az webapp log tail --resource-group "rg-edugen-containers" --name "edugen-diego-2025"

# Verificar variables de entorno
az webapp config appsettings list --resource-group "rg-edugen-containers" --name "edugen-diego-2025"
```

### 2. Error de conexión a base de datos
```bash
# Verificar firewall de PostgreSQL
az postgres flexible-server firewall-rule list \
  --resource-group "rg-edugen-containers" \
  --name "edugen-postgres-server"
```

### 3. Problemas con archivos estáticos
- Verificar que `whitenoise` esté en requirements.txt
- Verificar configuración de `STATIC_ROOT` en settings

### 4. Error de migraciones
```bash
# Conectar por SSH y ejecutar manualmente
az webapp ssh --resource-group "rg-edugen-containers" --name "edugen-diego-2025"
python manage.py migrate --noinput
```

## 📝 Notas Importantes

1. **Cambiar contraseñas por defecto** antes de producción
2. **Configurar dominio personalizado** si es necesario
3. **Habilitar HTTPS** (incluido por defecto en App Service)
4. **Configurar backup automático** de la base de datos
5. **Monitorear costos** regularmente en Azure Portal

---

**¡Tu aplicación EduGen estará lista en Azure App Service! 🎉**

Este método es más simple y económico que Container Instances, perfecto para cuentas educativas de Azure. 