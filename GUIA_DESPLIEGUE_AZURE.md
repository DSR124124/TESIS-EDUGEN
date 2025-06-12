# 🚀 Guía Completa de Despliegue EduGen en Azure

## 📋 Estado Actual de tu Infraestructura

✅ **Resource Group**: `rg-edugen`  
✅ **PostgreSQL Database**: `edugen-db-2024-01.postgres.database.azure.com`  
✅ **Database Name**: `edugen`  
✅ **App Service**: `edugen-app.azurewebsites.net`  
✅ **App Service Plan**: `plan-edugen` (B1 - Basic)

---

## 🔧 Paso 1: Finalizar Configuración de Variables de Entorno

### Actualizar Variables de Base de Datos
```bash
az webapp config appsettings set --resource-group rg-edugen --name edugen-app \
--settings DATABASE_URL="postgresql://postgres:EduGen123!@edugen-db-2024-01.postgres.database.azure.com:5432/edugen"
```

### Configurar Variables Completas
```bash
az webapp config appsettings set --resource-group rg-edugen --name edugen-app \
--settings \
DJANGO_SETTINGS_MODULE="config.settings.azure_production" \
SECRET_KEY="tu-clave-secreta-super-segura-cambiar" \
ALLOWED_HOSTS="edugen-app.azurewebsites.net,localhost,127.0.0.1" \
DATABASE_NAME="edugen" \
DATABASE_USER="postgres" \
DATABASE_PASSWORD="EduGen123!" \
DATABASE_HOST="edugen-db-2024-01.postgres.database.azure.com" \
DATABASE_PORT="5432" \
DEEPSEEK_API_KEY="sk-tu-deepseek-api-key-real" \
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="tu-google-client-id-real.apps.googleusercontent.com" \
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="tu-google-client-secret-real"
```

---

## 📂 Paso 2: Preparar Repositorio de GitHub

### 2.1 Crear Repositorio en GitHub
1. Ve a [GitHub](https://github.com)
2. Crea un nuevo repositorio llamado `TESIS-EDUGEN`
3. **NO** inicialices con README, .gitignore, o license (ya tienes código)

### 2.2 Subir Código al Repositorio
```bash
# Desde tu directorio F:\TESIS-EDUGEN
git init
git add .
git commit -m "Initial commit - EduGen Sistema Educativo"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TESIS-EDUGEN.git
git push -u origin main
```

---

## 🔗 Paso 3: Configurar Despliegue Automático desde GitHub

### 3.1 Configurar Deployment Source
```bash
az webapp deployment source config --name edugen-app --resource-group rg-edugen \
--repo-url https://github.com/TU-USUARIO/TESIS-EDUGEN \
--branch main --manual-integration
```

### 3.2 Alternativa: Configurar GitHub Actions (Recomendado)
```bash
az webapp deployment github-actions add --resource-group rg-edugen --name edugen-app \
--repo https://github.com/TU-USUARIO/TESIS-EDUGEN --branch main
```

---

## 🛠️ Paso 4: Configurar Python Runtime

```bash
az webapp config set --resource-group rg-edugen --name edugen-app \
--linux-fx-version "PYTHON|3.11" \
--startup-file "startup.sh"
```

---

## 🐛 Paso 5: Verificar y Solucionar Problemas

### 5.1 Ver Logs en Tiempo Real
```bash
az webapp log tail --resource-group rg-edugen --name edugen-app
```

### 5.2 Verificar Estado de la App
```bash
az webapp show --resource-group rg-edugen --name edugen-app --query state
```

### 5.3 Reiniciar la App si es Necesario
```bash
az webapp restart --resource-group rg-edugen --name edugen-app
```

---

## 📊 Paso 6: Configurar Base de Datos PostgreSQL

### 6.1 Crear Base de Datos (si no existe)
```bash
az postgres flexible-server db create \
--resource-group rg-edugen \
--server-name edugen-db-2024-01 \
--database-name edugen
```

### 6.2 Configurar Firewall para Azure Services
```bash
az postgres flexible-server firewall-rule create \
--resource-group rg-edugen \
--name edugen-db-2024-01 \
--rule-name AllowAzureServices \
--start-ip-address 0.0.0.0 \
--end-ip-address 0.0.0.0
```

---

## 🎯 Paso 7: Post-Deployment

### 7.1 Ejecutar Migraciones (Automático via startup.sh)
El script `startup.sh` ejecutará automáticamente:
- `python manage.py migrate`
- `python manage.py collectstatic`
- Creación de superusuario

### 7.2 Acceder a la Aplicación
URL: **https://edugen-app.azurewebsites.net**

### 7.3 Acceso de Administrador
- **Usuario**: `admin`
- **Contraseña**: `EduGenAdmin123!`
- **URL Admin**: `https://edugen-app.azurewebsites.net/admin/`

---

## 🔐 Paso 8: Configurar APIs Externas (Opcional)

### 8.1 DeepSeek API (IA para Contenido)
1. Registrarse en [DeepSeek](https://www.deepseek.com/)
2. Obtener API key
3. Actualizar variable: `DEEPSEEK_API_KEY="sk-tu-key-real"`

### 8.2 Google OAuth (Login Social)
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto y configurar OAuth 2.0
3. Actualizar variables:
   - `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`
   - `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`

---

## 📈 Paso 9: Monitoreo y Optimización

### 9.1 Configurar Application Insights
```bash
az extension add --name application-insights
az monitor app-insights component create \
--app edugen-insights \
--location centralus \
--resource-group rg-edugen \
--application-type web
```

### 9.2 Escalar Aplicación si es Necesario
```bash
# Escalar a plan superior
az appservice plan update --name plan-edugen --resource-group rg-edugen --sku S1

# Escalar número de instancias
az appservice plan update --name plan-edugen --resource-group rg-edugen --number-of-workers 2
```

---

## 🚨 Comandos de Troubleshooting

### Ver Configuración Actual
```bash
az webapp config appsettings list --resource-group rg-edugen --name edugen-app
```

### Conectar a Base de Datos para Testing
```bash
az postgres flexible-server connect \
--name edugen-db-2024-01 \
--resource-group rg-edugen \
--username postgres \
--database edugen
```

### Descargar Logs
```bash
az webapp log download --resource-group rg-edugen --name edugen-app
```

---

## 📝 Checklist Final

- [ ] ✅ Infraestructura Azure creada
- [ ] 📂 Código subido a GitHub  
- [ ] 🔗 Deployment configurado
- [ ] 🔐 Variables de entorno configuradas
- [ ] 🗄️ Base de datos PostgreSQL funcionando
- [ ] 🌐 Aplicación accesible en https://edugen-app.azurewebsites.net
- [ ] 👤 Superusuario creado
- [ ] 🎨 Archivos estáticos servidos correctamente
- [ ] 🤖 APIs externas configuradas (opcional)

---

## 🆘 Contactos de Soporte

- **Azure Status**: https://status.azure.com/
- **Django Docs**: https://docs.djangoproject.com/
- **PostgreSQL Azure**: https://docs.microsoft.com/azure/postgresql/

---

## 💡 Próximos Pasos Recomendados

1. **Configurar Dominio Personalizado** (opcional)
2. **Configurar SSL Certificate** (Let's Encrypt)
3. **Implementar CI/CD con GitHub Actions**
4. **Configurar Backups Automáticos**
5. **Implementar CDN para archivos estáticos**
6. **Configurar alertas de monitoreo**

---

> **⚠️ Nota Importante**: Cambia todas las claves por valores reales y seguros antes del despliegue en producción.

¡Tu aplicación EduGen estará lista para servir estudiantes y profesores! 🎓✨ 