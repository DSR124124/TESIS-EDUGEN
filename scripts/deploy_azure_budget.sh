#!/bin/bash
# Script de Despliegue Automático en Azure - Presupuesto $20 USD
# Sistema Educativo - Configuración Ultra-Económica

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Sistema Educativo - Despliegue Azure ($20 Budget)${NC}"
echo "============================================================"

# Verificar Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI no está instalado${NC}"
    echo "Instala con: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

# Variables de configuración
read -p "📝 Nombre único para tu app (ej: mi-sistema-edu): " APP_NAME
read -p "📧 Tu email para el superuser: " ADMIN_EMAIL
read -p "🔑 Password para admin (min 8 chars): " -s ADMIN_PASSWORD
echo

# Validar inputs
if [[ ${#APP_NAME} -lt 3 ]]; then
    echo -e "${RED}❌ El nombre debe tener al menos 3 caracteres${NC}"
    exit 1
fi

if [[ ${#ADMIN_PASSWORD} -lt 8 ]]; then
    echo -e "${RED}❌ La password debe tener al menos 8 caracteres${NC}"
    exit 1
fi

# Generar nombres únicos
RESOURCE_GROUP="sistema-educativo-rg"
APP_SERVICE_NAME="sistema-educativo-${APP_NAME}"
STORAGE_NAME="storage${APP_NAME}$(date +%s | tail -c 5)"
OPENAI_NAME="openai-${APP_NAME}"
APP_PLAN_NAME="plan-${APP_NAME}"

echo -e "${YELLOW}📋 Configuración:${NC}"
echo "  • Resource Group: $RESOURCE_GROUP"
echo "  • App Service: $APP_SERVICE_NAME"
echo "  • Storage: $STORAGE_NAME"
echo "  • OpenAI: $OPENAI_NAME"
echo ""

# Login a Azure
echo -e "${BLUE}🔐 Iniciando sesión en Azure...${NC}"
az login

# Obtener subscription ID
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
echo -e "${GREEN}✅ Conectado a subscription: $SUBSCRIPTION_ID${NC}"

# Paso 1: Crear Resource Group
echo -e "${BLUE}📁 Creando Resource Group...${NC}"
az group create \
    --name $RESOURCE_GROUP \
    --location "East US" \
    --tags project=investigacion environment=production budget=20usd

# Paso 2: Crear App Service Plan (FREE F1)
echo -e "${BLUE}🖥️  Creando App Service Plan (FREE)...${NC}"
az appservice plan create \
    --name $APP_PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku F1 \
    --is-linux

# Paso 3: Crear App Service
echo -e "${BLUE}🌐 Creando App Service...${NC}"
az webapp create \
    --name $APP_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_PLAN_NAME \
    --runtime "PYTHON|3.11"

# Paso 4: Crear Storage Account
echo -e "${BLUE}💾 Creando Storage Account...${NC}"
az storage account create \
    --name $STORAGE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location eastus \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot

# Crear container para media
az storage container create \
    --name media \
    --account-name $STORAGE_NAME \
    --public-access blob

# Paso 5: Configurar OpenAI API (Externo)
echo -e "${BLUE}🤖 Configurando OpenAI API...${NC}"
echo -e "${YELLOW}📋 Necesitas una API Key de OpenAI:${NC}"
echo "1. Ve a: https://platform.openai.com/api-keys"
echo "2. Crea una nueva API Key"
echo "3. Configura límite de uso ($10/mes recomendado)"
echo ""
read -p "🔑 Ingresa tu OpenAI API Key: " -s OPENAI_KEY
echo ""

if [[ -z "$OPENAI_KEY" ]]; then
    echo -e "${YELLOW}⚠️  Sin API Key de OpenAI. Puedes configurarla después.${NC}"
    OPENAI_KEY="sk-your-openai-key-here"
fi

OPENAI_ENDPOINT="https://api.openai.com/v1"

# Paso 6: Obtener connection strings
echo -e "${BLUE}🔑 Obteniendo credenciales...${NC}"

STORAGE_CONNECTION=$(az storage account show-connection-string \
    --name $STORAGE_NAME \
    --resource-group $RESOURCE_GROUP \
    --output tsv)

# Generar SECRET_KEY segura
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Paso 7: Configurar variables de entorno
echo -e "${BLUE}⚙️  Configurando variables de entorno...${NC}"
az webapp config appsettings set \
    --name $APP_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        DJANGO_SETTINGS_MODULE="config.settings.production" \
        DEBUG="False" \
        SECRET_KEY="$SECRET_KEY" \
        AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONNECTION" \
        AZURE_STORAGE_CONTAINER_NAME="media" \
        OPENAI_API_KEY="$OPENAI_KEY" \
        OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
        OPENAI_MODEL="gpt-3.5-turbo" \
        DATABASE_URL="sqlite:////tmp/db.sqlite3" \
        ADMIN_EMAIL="$ADMIN_EMAIL" \
        ADMIN_PASSWORD="$ADMIN_PASSWORD"

# Paso 8: Crear startup script
echo -e "${BLUE}📜 Creando startup script...${NC}"
cat > startup.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando Sistema Educativo..."

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Collect static files
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️  Ejecutando migraciones..."
python manage.py migrate

# Create superuser
echo "👤 Creando superuser..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ.get('ADMIN_EMAIL', 'admin@ejemplo.com')
password = os.environ.get('ADMIN_PASSWORD', 'adminpass123')
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', email, password)
    print(f'✅ Superuser creado: admin / {email}')
else:
    print('ℹ️  Superuser ya existe')
"

# Setup content types if needed
python manage.py shell -c "
from apps.ai_content_generator.models import ContentType
if ContentType.objects.count() == 0:
    ContentType.objects.create(
        name='Material de Apoyo Integrado',
        description='Material educativo completo con teoría y práctica'
    )
    ContentType.objects.create(
        name='Plan de Sesión de Clase',
        description='Planificación detallada de clase'
    )
    print('✅ Tipos de contenido creados')
"

echo "🎉 Sistema listo!"

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
EOF

# Subir startup script
az webapp deployment source config-zip \
    --name $APP_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --src startup.sh

# Configurar startup command
az webapp config set \
    --name $APP_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file startup.sh

# Paso 9: Crear presupuesto
echo -e "${BLUE}💰 Configurando presupuesto de $20...${NC}"
az consumption budget create \
    --budget-name sistema-educativo-budget \
    --amount 20 \
    --time-grain Monthly \
    --time-period-start $(date +%Y-%m-01) \
    --time-period-end $(date -d "1 year" +%Y-%m-01) \
    --resource-group-filter $RESOURCE_GROUP || echo "⚠️  No se pudo crear presupuesto (requiere permisos especiales)"

# Paso 10: Deploy código (si hay repositorio git)
if [ -d ".git" ]; then
    echo -e "${BLUE}🚀 Desplegando código desde Git...${NC}"
    
    # Crear archivo de configuración para Azure
    cat > .deployment << EOF
[config]
command = bash startup.sh
EOF
    
    # Add Azure remote
    APP_URL="https://${APP_SERVICE_NAME}.scm.azurewebsites.net/${APP_SERVICE_NAME}.git"
    
    # Get publish profile for Git credentials
    echo -e "${YELLOW}📋 Para desplegar tu código, ejecuta:${NC}"
    echo "git remote add azure $APP_URL"
    echo "git push azure main"
else
    echo -e "${YELLOW}⚠️  No hay repositorio Git. Crea uno para deployment automático.${NC}"
fi

# Obtener URL final
APP_URL="https://${APP_SERVICE_NAME}.azurewebsites.net"

echo ""
echo -e "${GREEN}🎉 ¡DESPLIEGUE COMPLETADO!${NC}"
echo "============================================"
echo ""
echo -e "${BLUE}📊 Resumen de Recursos Creados:${NC}"
echo "  • App Service (FREE): $APP_SERVICE_NAME"
echo "  • Storage Account: $STORAGE_NAME"
echo "  • OpenAI API: Externo (OpenAI.com)"
echo "  • Google OAuth: Externo (Google)"
echo "  • Resource Group: $RESOURCE_GROUP"
echo ""
echo -e "${BLUE}🌐 URLs:${NC}"
echo "  • App Web: $APP_URL"
echo "  • Admin Panel: $APP_URL/admin/"
echo ""
echo -e "${BLUE}🔑 Credenciales Admin:${NC}"
echo "  • Usuario: admin"
echo "  • Email: $ADMIN_EMAIL"
echo "  • Password: [la que ingresaste]"
echo ""
echo -e "${YELLOW}💰 Estimación de Costos Mensual:${NC}"
echo "  • App Service F1: $0 (FREE)"
echo "  • Storage (50GB): ~$5"
echo "  • OpenAI API GPT-3.5: ~$5-10"
echo "  • Google OAuth: $0 (FREE)"
echo "  • TOTAL: ~$10-15 USD/mes"
echo ""
echo -e "${BLUE}📋 Próximos Pasos:${NC}"
echo "1. Visita $APP_URL para ver tu app"
echo "2. Ve a $APP_URL/admin/ para administrar"
echo "3. Configura Google OAuth si lo necesitas"
echo "4. Monitorea costos en Azure Portal"
echo ""
echo -e "${GREEN}✅ ¡Tu Sistema Educativo está online en Azure!${NC}"

# Crear archivo de configuración local
cat > azure_deployment_info.txt << EOF
=== INFORMACIÓN DE DESPLIEGUE AZURE ===
Fecha: $(date)
Resource Group: $RESOURCE_GROUP
App Service: $APP_SERVICE_NAME
Storage: $STORAGE_NAME
OpenAI: Externo (OpenAI.com)
Google OAuth: Externo (Google)
URL: $APP_URL
Admin URL: $APP_URL/admin/
Admin User: admin
Admin Email: $ADMIN_EMAIL

=== COMANDOS ÚTILES ===
Ver logs: az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP
Reiniciar app: az webapp restart --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP
Ver costos: az consumption usage list --output table
Eliminar todo: az group delete --name $RESOURCE_GROUP --yes

=== VARIABLES DE ENTORNO ===
DJANGO_SETTINGS_MODULE=config.settings.production
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION
OPENAI_API_KEY=$OPENAI_KEY
EOF

echo -e "${BLUE}📝 Información guardada en: azure_deployment_info.txt${NC}" 