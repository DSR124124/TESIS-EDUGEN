# 🔑 Configuración Google OAuth para Azure
## Sistema Educativo - Autenticación Gratuita

Esta guía te ayudará a configurar Google OAuth 2.0 para tu Sistema Educativo desplegado en Azure App Service.

## 📋 Pasos para Configurar Google OAuth

### **1. Crear Proyecto en Google Cloud Console**

1. **Ve a Google Cloud Console**:
   ```
   https://console.cloud.google.com/
   ```

2. **Crear nuevo proyecto**:
   - Haz clic en "Nuevo Proyecto"
   - Nombre: `Sistema Educativo OAuth`
   - Organización: Tu institución educativa
   - Haz clic en "Crear"

### **2. Habilitar Google+ API**

1. **Ve a APIs y Servicios**:
   ```
   Navigation Menu > APIs & Services > Library
   ```

2. **Buscar y habilitar**:
   - Busca: "Google+ API"
   - Haz clic en "Google+ API"
   - Haz clic en "Habilitar"

### **3. Configurar Pantalla de Consentimiento**

1. **Ve a OAuth consent screen**:
   ```
   APIs & Services > OAuth consent screen
   ```

2. **Configurar información básica**:
   ```
   User Type: External
   Application name: Sistema Educativo
   User support email: tu-email@universidad.edu
   Application home page: https://tu-app.azurewebsites.net
   Application privacy policy: https://tu-app.azurewebsites.net/privacy/
   Application terms of service: https://tu-app.azurewebsites.net/terms/
   Authorized domains: azurewebsites.net
   Developer contact email: tu-email@universidad.edu
   ```

3. **Scopes (Alcances)**:
   ```
   Add or remove scopes:
   - ../auth/userinfo.email
   - ../auth/userinfo.profile
   - openid
   ```

4. **Test users (Para desarrollo)**:
   - Agrega tu email universitario
   - Agrega emails de otros usuarios de prueba

### **4. Crear Credenciales OAuth 2.0**

1. **Ve a Credenciales**:
   ```
   APIs & Services > Credentials
   ```

2. **Crear credenciales**:
   - Haz clic en "Create Credentials"
   - Selecciona "OAuth 2.0 Client IDs"

3. **Configurar aplicación web**:
   ```
   Application type: Web application
   Name: Sistema Educativo Web Client
   
   Authorized JavaScript origins:
   - https://tu-app-name.azurewebsites.net
   - http://localhost:8000 (para desarrollo)
   
   Authorized redirect URIs:
   - https://tu-app-name.azurewebsites.net/accounts/google/login/callback/
   - http://localhost:8000/accounts/google/login/callback/
   ```

4. **Descargar credenciales**:
   - Guarda el `Client ID` y `Client Secret`

## ⚙️ Configurar en Azure App Service

### **1. Agregar Variables de Entorno**

```bash
# Usando Azure CLI
az webapp config appsettings set \
  --name tu-app-name \
  --resource-group sistema-educativo-rg \
  --settings \
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="tu-client-id.googleusercontent.com" \
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="tu-client-secret"
```

### **2. Configurar en el Portal Azure**

1. **Ve a tu App Service** en Azure Portal
2. **Configuration > Application Settings**
3. **Agregar nuevas configuraciones**:
   ```
   Name: SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
   Value: 123456789-abc123.apps.googleusercontent.com
   
   Name: SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
   Value: GOCSPX-tu-client-secret-aqui
   ```

## 🔧 Configuración en Django

### **1. Verificar settings.py**

Tu configuración de producción ya debería incluir:

```python
# config/settings/azure_production.py

# Google OAuth2 Configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

# Scopes que solicitar
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

# Configuración de redirect URI
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = f"https://{WEBSITE_HOSTNAME}/accounts/google/login/callback/"

# Extra data a obtener del perfil
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['first_name', 'last_name']
```

### **2. URLs configuradas**

Ya deberías tener en `urls.py`:

```python
# proyecto/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Incluye Google OAuth
    path('', include('apps.core.urls')),
    # ... otras URLs
]
```

## 🧪 Probar la Configuración

### **1. Verificar en desarrollo local**

```bash
# Configurar variables locales
export SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="tu-client-id"
export SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET="tu-client-secret"

# Ejecutar servidor
python manage.py runserver
```

Visita: `http://localhost:8000/accounts/google/login/`

### **2. Verificar en Azure**

1. **Ve a tu app**: `https://tu-app.azurewebsites.net`
2. **Haz clic en "Iniciar sesión con Google"**
3. **Completa el flujo de OAuth**
4. **Verifica que se cree el usuario en Django Admin**

## 🔍 Troubleshooting Común

### **Error: redirect_uri_mismatch**

```bash
# Solución: Verificar que las URIs coincidan exactamente
Configuradas en Google: https://tu-app.azurewebsites.net/accounts/google/login/callback/
Configuradas en Django: https://tu-app.azurewebsites.net/accounts/google/login/callback/
```

### **Error: invalid_client**

```bash
# Verificar variables de entorno
az webapp config appsettings list \
  --name tu-app \
  --resource-group sistema-educativo-rg \
  --query "[?name=='SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']"
```

### **Error: access_denied**

- Verifica que el usuario esté en "Test users" (modo desarrollo)
- O publica la app para usuarios externos

## 📊 Verificar Configuración

### **1. Comando de verificación**

```python
# Django shell
python manage.py shell

# Verificar configuración
from django.conf import settings
print("Google OAuth Key:", settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY[:20] + "...")
print("Google OAuth Secret:", "Configurado" if settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET else "No configurado")
```

### **2. Logs de Azure**

```bash
# Ver logs en tiempo real
az webapp log tail --name tu-app --resource-group sistema-educativo-rg
```

## 🎯 Checklist de Configuración

- [ ] ✅ Proyecto creado en Google Cloud Console
- [ ] ✅ Google+ API habilitada
- [ ] ✅ OAuth consent screen configurada
- [ ] ✅ Credenciales OAuth 2.0 creadas
- [ ] ✅ URIs de redirect configuradas correctamente
- [ ] ✅ Variables de entorno configuradas en Azure
- [ ] ✅ Configuración de Django verificada
- [ ] ✅ Flujo de login probado y funcionando

## 🔒 Seguridad y Mejores Prácticas

### **1. Producción**

- ✅ Usa HTTPS siempre
- ✅ Mantén el Client Secret seguro
- ✅ Configura dominios autorizados específicos
- ✅ Limita scopes a lo mínimo necesario

### **2. Desarrollo**

- ✅ Usa usuarios de prueba durante desarrollo
- ✅ Mantén credenciales de dev separadas de prod
- ✅ No hagas commit de credenciales al código

## 📝 URLs de Referencia

- **Google Cloud Console**: https://console.cloud.google.com/
- **Django Allauth Docs**: https://django-allauth.readthedocs.io/
- **Google OAuth 2.0 Docs**: https://developers.google.com/identity/protocols/oauth2

¡Con esta configuración tendrás autenticación Google completamente funcional y gratuita! 🔑✅ 