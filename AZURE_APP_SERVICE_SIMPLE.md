# 🚀 Despliegue EduGen en Azure App Service

Guía simplificada para desplegar tu aplicación EduGen en Azure App Service.

## 🔧 Paso 1: Crear App Service

```bash
# Crear App Service Plan
az appservice plan create \
  --name "edugen-app-plan" \
  --resource-group "rg-edugen-containers" \
  --location "East US" \
  --sku B1 \
  --is-linux

# Crear Web App
az webapp create \
  --resource-group "rg-edugen-containers" \
  --plan "edugen-app-plan" \
  --name "edugen-app-service" \
  --runtime "PYTHON:3.11"
```

## 🔧 Paso 2: Configurar Variables de Entorno

```bash
az webapp config appsettings set \
  --resource-group "rg-edugen-containers" \
  --name "edugen-app-service" \
  --settings \
    DJANGO_SETTINGS_MODULE="config.settings.azure_production" \
    DEBUG="False" \
    SECRET_KEY="tu-secret-key-seguro-aqui" \
    ALLOWED_HOSTS="edugen-app-service.azurewebsites.net" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="tu-google-client-id" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="tu-google-secret" \
    DEEPSEEK_API_KEY="tu-deepseek-api-key" \
    AI_PROVIDER="deepseek" \
    WEBSITE_HOSTNAME="edugen-app-service.azurewebsites.net" \
    CSRF_TRUSTED_ORIGINS="https://edugen-app-service.azurewebsites.net"
```

## 🔧 Paso 3: Configurar Despliegue desde GitHub

```bash
# Configurar GitHub como fuente
az webapp deployment source config \
  --resource-group "rg-edugen-containers" \
  --name "edugen-app-service" \
  --repo-url "https://github.com/DSR124124/TESIS-EDUGEN.git" \
  --branch "main" \
  --manual-integration

# Configurar startup command
az webapp config set \
  --resource-group "rg-edugen-containers" \
  --name "edugen-app-service" \
  --startup-file "startup.sh"
```

## 🌐 Acceso

- **URL**: https://edugen-app-service.azurewebsites.net
- **Admin**: https://edugen-app-service.azurewebsites.net/admin/
- **Credenciales**: admin / EduGenAdmin123!

## 💰 Costo Estimado

- **App Service B1**: ~$15/mes
- **Total**: ~$15-20/mes

## 🔧 Comandos Útiles

```bash
# Ver logs
az webapp log tail --resource-group "rg-edugen-containers" --name "edugen-app-service"

# Reiniciar
az webapp restart --resource-group "rg-edugen-containers" --name "edugen-app-service"

# Ver estado
az webapp show --resource-group "rg-edugen-containers" --name "edugen-app-service"
``` 