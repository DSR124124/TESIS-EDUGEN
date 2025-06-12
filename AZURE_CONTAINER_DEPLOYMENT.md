# 🚀 Despliegue Manual de EduGen en Azure Container Instances

Esta guía te llevará paso a paso para desplegar tu aplicación EduGen en Azure usando Container Instances de forma manual.

## 📋 Requisitos Previos

- **Azure CLI** instalado y configurado
- **Docker** instalado localmente
- **Cuenta de Azure** activa
- **Azure Container Registry** (ACR) o **Docker Hub**
- **Base de datos PostgreSQL** en Azure

## 🔧 Paso 1: Preparar el Entorno Local

### 1.1 Instalar Azure CLI (si no lo tienes)

```bash
# Windows (PowerShell como administrador)
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; rm .\AzureCLI.msi

# O descargar desde: https://aka.ms/installazurecliwindows
```

### 1.2 Iniciar sesión en Azure

```bash
# Iniciar sesión
az login

# Verificar suscripción
az account show

# Cambiar suscripción si es necesario
az account set --subscription "tu-subscription-id"
```

### 1.3 Configurar variables de entorno

```bash
# Configurar variables (ajusta según tus necesidades)
$RESOURCE_GROUP = "rg-edugen-containers"
$LOCATION = "East US"
$ACR_NAME = "acredugen"
$CONTAINER_NAME = "edugen-app"
$IMAGE_NAME = "edugen-web"
$DNS_LABEL = "edugen-app-unique"  # Debe ser único globalmente
```

## 🏗️ Paso 2: Crear Recursos en Azure

### 2.1 Crear Resource Group

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 2.2 Crear Azure Container Registry (ACR)

```bash
# Crear ACR
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Obtener credenciales del ACR
az acr credential show --name $ACR_NAME
```

**📝 Anota las credenciales del ACR:**
- Username: `acredugen`
- Password: `[contraseña generada]`

### 2.3 Crear Base de Datos PostgreSQL

```bash
# Crear servidor PostgreSQL
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name "edugen-postgres-server" \
  --location $LOCATION \
  --admin-user postgres \
  --admin-password "EduGen123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32

# Crear base de datos
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name "edugen-postgres-server" \
  --database-name edugen
```

**📝 Anota la cadena de conexión:**
- Host: `edugen-postgres-server.postgres.database.azure.com`
- Database: `edugen`
- User: `postgres`
- Password: `EduGen123!`

## 🐳 Paso 3: Construir y Subir la Imagen Docker

### 3.1 Iniciar sesión en ACR

```bash
az acr login --name $ACR_NAME
```

### 3.2 Construir la imagen localmente

```bash
# Navegar al directorio del proyecto
cd F:\TESIS-EDUGEN

# Construir la imagen
docker build -t $IMAGE_NAME .

# Etiquetar para ACR
docker tag $IMAGE_NAME "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest"
```

### 3.3 Subir imagen a ACR

```bash
# Subir imagen
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest"

# Verificar que se subió
az acr repository list --name $ACR_NAME
```

## 🚀 Paso 4: Desplegar Container Instance

### 4.1 Crear archivo de configuración YAML

Crea un archivo `azure-container-config.yaml`:

```yaml
apiVersion: 2021-03-01
location: eastus
name: edugen-container-group
properties:
  containers:
  - name: edugen-web
    properties:
      image: acredugen.azurecr.io/edugen-web:latest
      resources:
        requests:
          cpu: 1.0
          memoryInGb: 2.0
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      # Base de datos
      - name: PGHOST
        value: "edugen-postgres-server.postgres.database.azure.com"
      - name: PGPORT
        value: "5432"
      - name: PGDATABASE
        value: "edugen"
      - name: PGUSER
        value: "postgres"
      - name: PGPASSWORD
        secureValue: "EduGen123!"
      
      # Django
      - name: DJANGO_SETTINGS_MODULE
        value: "config.settings.azure_production"
      - name: DEBUG
        value: "False"
      - name: SECRET_KEY
        secureValue: "django-insecure-azure-container-key-2024-change-in-production-x9k8j7h6g5"
      - name: ALLOWED_HOSTS
        value: "edugen-app-unique.eastus.azurecontainer.io,localhost,127.0.0.1"
      
      # Google OAuth
      - name: SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        value: "50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com"
      - name: SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        secureValue: "AIzaSyDbaO4sVGS5_dCMV1r4yizjzqAoakAnME0"
      
      # IA
      - name: DEEPSEEK_API_KEY
        secureValue: "sk-f1bfb13127b14daf97788bb0232a5584"
      - name: AI_PROVIDER
        value: "deepseek"
      
      # Configuración adicional
      - name: WEBSITE_HOSTNAME
        value: "edugen-app-unique.eastus.azurecontainer.io"
      - name: CSRF_TRUSTED_ORIGINS
        value: "https://edugen-app-unique.eastus.azurecontainer.io"
        
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 8000
    dnsNameLabel: edugen-app-unique
  imageRegistryCredentials:
  - server: acredugen.azurecr.io
    username: acredugen
    password: "[tu-password-del-acr]"
tags:
  Environment: Production
  Application: EduGen
```

### 4.2 Desplegar usando Azure CLI

```bash
# Opción 1: Usando archivo YAML
az container create --resource-group $RESOURCE_GROUP --file azure-container-config.yaml

# Opción 2: Usando comando directo (alternativa)
az container create \
  --resource-group $RESOURCE_GROUP \
  --name edugen-container-group \
  --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:latest" \
  --registry-login-server "$ACR_NAME.azurecr.io" \
  --registry-username $ACR_NAME \
  --registry-password "[password-del-acr]" \
  --dns-name-label $DNS_LABEL \
  --ports 8000 \
  --cpu 1 \
  --memory 2 \
  --environment-variables \
    PGHOST="edugen-postgres-server.postgres.database.azure.com" \
    PGPORT="5432" \
    PGDATABASE="edugen" \
    PGUSER="postgres" \
    DJANGO_SETTINGS_MODULE="config.settings.azure_production" \
    DEBUG="False" \
    ALLOWED_HOSTS="$DNS_LABEL.eastus.azurecontainer.io,localhost" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com" \
    AI_PROVIDER="deepseek" \
    WEBSITE_HOSTNAME="$DNS_LABEL.eastus.azurecontainer.io" \
  --secure-environment-variables \
    PGPASSWORD="EduGen123!" \
    SECRET_KEY="django-insecure-azure-container-key-2024-x9k8j7h6g5" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="AIzaSyDbaO4sVGS5_dCMV1r4yizjzqAoakAnME0" \
    DEEPSEEK_API_KEY="sk-f1bfb13127b14daf97788bb0232a5584"
```

## ⚙️ Paso 5: Configurar la Aplicación

### 5.1 Verificar el despliegue

```bash
# Ver estado del contenedor
az container show --resource-group $RESOURCE_GROUP --name edugen-container-group --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" --out table

# Ver logs
az container logs --resource-group $RESOURCE_GROUP --name edugen-container-group
```

### 5.2 Ejecutar migraciones

```bash
# Ejecutar comando en el contenedor
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "python manage.py migrate"

# Crear superusuario (interactivo)
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "python manage.py createsuperuser"

# Recopilar archivos estáticos
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "python manage.py collectstatic --noinput"
```

## 🌐 Paso 6: Configurar Dominio y SSL (Opcional)

### 6.1 Configurar dominio personalizado

Si tienes un dominio propio:

```bash
# Obtener IP pública
az container show --resource-group $RESOURCE_GROUP --name edugen-container-group --query ipAddress.ip --output tsv

# Configurar registro DNS A en tu proveedor de dominio
# Ejemplo: edugen.tudominio.com -> [IP obtenida]
```

### 6.2 Configurar SSL con Azure Application Gateway (Avanzado)

Para SSL personalizado, necesitarías configurar Azure Application Gateway o usar Azure Front Door.

## 📊 Paso 7: Monitoreo y Mantenimiento

### 7.1 Comandos útiles de monitoreo

```bash
# Ver estado del contenedor
az container show --resource-group $RESOURCE_GROUP --name edugen-container-group

# Ver logs en tiempo real
az container logs --resource-group $RESOURCE_GROUP --name edugen-container-group --follow

# Ver métricas de uso
az monitor metrics list --resource "/subscriptions/[subscription-id]/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/edugen-container-group" --metric "CpuUsage,MemoryUsage"

# Reiniciar contenedor
az container restart --resource-group $RESOURCE_GROUP --name edugen-container-group
```

### 7.2 Actualizar la aplicación

```bash
# 1. Construir nueva imagen
docker build -t $IMAGE_NAME .
docker tag $IMAGE_NAME "$ACR_NAME.azurecr.io/$IMAGE_NAME:v2"
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME:v2"

# 2. Actualizar contenedor
az container delete --resource-group $RESOURCE_GROUP --name edugen-container-group --yes

# 3. Recrear con nueva imagen (modificar YAML con :v2)
az container create --resource-group $RESOURCE_GROUP --file azure-container-config.yaml
```

## 🔒 Paso 8: Configuración de Seguridad

### 8.1 Configurar Network Security Group

```bash
# Crear NSG (si necesitas restricciones de red)
az network nsg create --resource-group $RESOURCE_GROUP --name edugen-nsg

# Agregar regla para HTTP/HTTPS
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name edugen-nsg \
  --name AllowHTTP \
  --protocol Tcp \
  --priority 1000 \
  --destination-port-range 8000 \
  --access Allow
```

### 8.2 Configurar Azure Key Vault (Recomendado)

```bash
# Crear Key Vault
az keyvault create --name "edugen-keyvault" --resource-group $RESOURCE_GROUP --location $LOCATION

# Agregar secretos
az keyvault secret set --vault-name "edugen-keyvault" --name "database-password" --value "EduGen123!"
az keyvault secret set --vault-name "edugen-keyvault" --name "secret-key" --value "tu-secret-key-seguro"
az keyvault secret set --vault-name "edugen-keyvault" --name "deepseek-api-key" --value "sk-f1bfb13127b14daf97788bb0232a5584"
```

## 🌍 URLs de Acceso

Después del despliegue exitoso, tu aplicación estará disponible en:

- **URL Principal**: `https://edugen-app-unique.eastus.azurecontainer.io:8000`
- **Admin Django**: `https://edugen-app-unique.eastus.azurecontainer.io:8000/admin/`
- **Login Google**: Funcionará con las credenciales OAuth configuradas

## 💰 Estimación de Costos

**Azure Container Instances:**
- 1 vCPU, 2GB RAM: ~$30-50/mes
- Tráfico de red: ~$5-10/mes

**Azure Database for PostgreSQL:**
- Burstable B1ms: ~$15-25/mes

**Azure Container Registry:**
- Basic: ~$5/mes

**Total estimado: $55-90/mes**

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Contenedor no inicia:**
   ```bash
   az container logs --resource-group $RESOURCE_GROUP --name edugen-container-group
   ```

2. **Error de conexión a base de datos:**
   - Verificar firewall de PostgreSQL
   - Verificar cadena de conexión

3. **Error 502/503:**
   - Verificar que el puerto 8000 esté expuesto
   - Verificar logs de la aplicación

4. **Problemas de autenticación ACR:**
   ```bash
   az acr credential show --name $ACR_NAME
   ```

### Comandos de Debugging

```bash
# Entrar al contenedor
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "/bin/bash"

# Ver variables de entorno
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "env"

# Verificar conectividad a base de datos
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "python manage.py dbshell"
```

## 🔄 Backup y Recuperación

### Backup de Base de Datos

```bash
# Backup automático (ya configurado en Azure PostgreSQL)
az postgres flexible-server backup list --resource-group $RESOURCE_GROUP --server-name "edugen-postgres-server"

# Backup manual
az container exec --resource-group $RESOURCE_GROUP --name edugen-container-group --exec-command "python manage.py dumpdata > backup.json"
```

## 📝 Notas Importantes

1. **Cambia las contraseñas por defecto** antes de producción
2. **Configura SSL** para producción
3. **Monitorea los costos** regularmente
4. **Configura alertas** de Azure Monitor
5. **Implementa CI/CD** para actualizaciones automáticas

---

**¡Tu aplicación EduGen está lista para ejecutarse en Azure Container Instances! 🎉**

Para soporte adicional, revisa los logs y la documentación oficial de Azure Container Instances. 