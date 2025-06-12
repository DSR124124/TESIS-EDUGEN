# 🚀 Despliegue Manual de EduGen en Azure Container Instances

Esta guía te llevará paso a paso para desplegar tu aplicación EduGen en Azure usando Container Instances de forma manual.

## 📋 Requisitos Previos

- **Azure CLI** instalado y configurado
- **Docker** instalado localmente
- **Cuenta de Azure** activa
- **Azure Container Registry** (ACR)
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



## 🏗️ Paso 2: Crear Recursos en Azure

### 2.1 Crear Resource Group

```bash
# Crear grupo de recursos
az group create --name "rg-edugen-containers" --location "Central US"

# Verificar que se creó
az group show --name "rg-edugen-containers"
```

### 2.2 Crear Azure Container Registry (ACR)

```bash
# Crear ACR
az acr create --resource-group "rg-edugen-containers" --name "acredugen" --sku Basic --admin-enabled true

# Obtener credenciales del ACR
az acr credential show --name "acredugen"
```

**📝 Anota las credenciales del ACR:**
- Username: `acredugen`
- Password: `[contraseña generada]`

### 2.3 Crear Base de Datos PostgreSQL

```bash
# Crear servidor PostgreSQL
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

# Crear base de datos
az postgres flexible-server db create \
  --resource-group "rg-edugen-containers" \
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
az acr login --name "acredugen"
```

### 3.2 Construir la imagen localmente

```bash
# Navegar al directorio del proyecto
cd F:\TESIS-EDUGEN

# Construir la imagen
docker build -t edugen-web .

# Etiquetar para ACR
docker tag edugen-web "acredugen.azurecr.io/edugen-web:latest"
```

### 3.3 Subir imagen a ACR

```bash
# Subir imagen
docker push "acredugen.azurecr.io/edugen-web:latest"

# Verificar que se subió
az acr repository list --name "acredugen"
```

## 🚀 Paso 4: Crear Archivo de Configuración YAML

### 4.1 Crear `azure-container-config.yaml`

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
    password: "[REEMPLAZAR-CON-PASSWORD-DEL-ACR]"
tags:
  Environment: Production
  Application: EduGen
```

### 4.2 Actualizar credenciales en YAML

**IMPORTANTE**: Reemplaza `[REEMPLAZAR-CON-PASSWORD-DEL-ACR]` con la contraseña real obtenida en el paso 2.2.

## 🚀 Paso 5: Desplegar Container Instance

### 5.1 Desplegar usando Azure CLI

```bash
# Opción 1: Usando archivo YAML
az container create --resource-group "rg-edugen-containers" --file azure-container-config.yaml

# Opción 2: Usando comando directo (alternativa)
az container create \
  --resource-group "rg-edugen-containers" \
  --name edugen-container-group \
  --image "acredugen.azurecr.io/edugen-web:latest" \
  --registry-login-server "acredugen.azurecr.io" \
  --registry-username "acredugen" \
  --registry-password "[password-del-acr]" \
  --dns-name-label "edugen-app-unique" \
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
    ALLOWED_HOSTS="edugen-app-unique.centralus.azurecontainer.io,localhost" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com" \
    AI_PROVIDER="deepseek" \
    WEBSITE_HOSTNAME="edugen-app-unique.centralus.azurecontainer.io" \
  --secure-environment-variables \
    PGPASSWORD="EduGen123!" \
    SECRET_KEY="django-insecure-azure-container-key-2024-x9k8j7h6g5" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="AIzaSyDbaO4sVGS5_dCMV1r4yizjzqAoakAnME0" \
    DEEPSEEK_API_KEY="sk-f1bfb13127b14daf97788bb0232a5584"
```

## ⚙️ Paso 6: Configurar la Aplicación

### 6.1 Verificar el despliegue

```bash
# Ver estado del contenedor
az container show --resource-group "rg-edugen-containers" --name edugen-container-group --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" --out table

# Ver logs
az container logs --resource-group "rg-edugen-containers" --name edugen-container-group
```

### 6.2 Ejecutar migraciones

```bash
# Ejecutar comando en el contenedor
az container exec --resource-group "rg-edugen-containers" --name edugen-container-group --exec-command "python manage.py migrate"

# Crear superusuario (interactivo)
az container exec --resource-group "rg-edugen-containers" --name edugen-container-group --exec-command "python manage.py createsuperuser"

# Recopilar archivos estáticos
az container exec --resource-group "rg-edugen-containers" --name edugen-container-group --exec-command "python manage.py collectstatic --noinput"
```

## 🌐 Paso 7: Verificar Acceso

Después del despliegue exitoso, tu aplicación estará disponible en:

- **URL Principal**: `https://edugen-app-unique.centralus.azurecontainer.io:8000`
- **Admin Django**: `https://edugen-app-unique.centralus.azurecontainer.io:8000/admin/`
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

## 🔧 Comandos Útiles de Monitoreo

### Ver logs en tiempo real
```bash
az container logs --resource-group "rg-edugen-containers" --name edugen-container-group --follow
```

### Reiniciar contenedor
```bash
az container restart --resource-group "rg-edugen-containers" --name edugen-container-group
```

### Ver métricas de uso
```bash
az monitor metrics list --resource "/subscriptions/[subscription-id]/resourceGroups/rg-edugen-containers/providers/Microsoft.ContainerInstance/containerGroups/edugen-container-group" --metric "CpuUsage,MemoryUsage"
```

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Contenedor no inicia:**
   ```bash
   az container logs --resource-group "rg-edugen-containers" --name edugen-container-group
   ```

2. **Error de conexión a base de datos:**
   - Verificar firewall de PostgreSQL
   - Verificar cadena de conexión

3. **Error 502/503:**
   - Verificar que el puerto 8000 esté expuesto
   - Verificar logs de la aplicación

4. **Problemas de autenticación ACR:**
   ```bash
   az acr credential show --name "acredugen"
   ```

### Comandos de Debugging

```bash
# Entrar al contenedor
az container exec --resource-group "rg-edugen-containers" --name edugen-container-group --exec-command "/bin/bash"

# Ver variables de entorno
az container exec --resource-group "rg-edugen-containers" --name edugen-container-group --exec-command "env"

# Verificar conectividad a base de datos
az container exec --resource-group "rg-edugen-containers" --name edugen-container-group --exec-command "python manage.py dbshell"
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