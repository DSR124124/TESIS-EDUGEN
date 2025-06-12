# 🔧 Solución para Error OAuth Google: redirect_uri_mismatch

## 🚨 **Problema**
```
Error 400: redirect_uri_mismatch
No puedes iniciar sesión porque esta aplicación ha enviado una solicitud no válida.
```

**URI problemático**: `https://edugen-app.azurewebsites.net/auth/complete/google-oauth2/`

## ✅ **Solución Paso a Paso**

### **Paso 1: Configurar Google Cloud Console**

1. **Acceder a Google Cloud Console**
   - Ve a: https://console.cloud.google.com/
   - Inicia sesión con tu cuenta de Google

2. **Navegar a Credentials**
   - En el menú lateral: **APIs & Services** → **Credentials**
   - Busca tu Client ID: `50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com`

3. **Editar OAuth 2.0 Client**
   - Click en el ícono de editar (lápiz) junto a tu OAuth client
   - En la sección **"Authorized redirect URIs"**

4. **Agregar URIs de Redirección**
   
   **🔧 URIs OBLIGATORIOS que debes agregar:**
   ```
   https://edugen-app.azurewebsites.net/auth/complete/google-oauth2/
   http://localhost:8000/auth/complete/google-oauth2/
   https://127.0.0.1:8000/auth/complete/google-oauth2/
   ```

   **📝 Notas importantes:**
   - ✅ Incluye la barra final `/`
   - ✅ Usa exactamente `https://` para producción
   - ✅ Incluye `http://localhost:8000/` para desarrollo
   - ❌ NO agregues espacios adicionales
   - ❌ NO uses puertos personalizados sin registrarlos

5. **Guardar Cambios**
   - Click en **"Save"** o **"Guardar"**
   - Espera 5-10 minutos para que los cambios se propaguen

### **Paso 2: Verificar Configuración de la Aplicación**

Los URIs están configurados correctamente en:
- `config/settings/azure_production.py`: Para producción en Azure
- `config/settings/__init__.py`: Para desarrollo local

**URI actual configurado:**
```python
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = "https://edugen-app.azurewebsites.net/auth/complete/google-oauth2/"
```

### **Paso 3: Verificar en Producción**

1. **Hacer un nuevo deployment**
   ```bash
   git add .
   git commit -m "Fix OAuth redirect URI configuration"
   git push origin main
   ```

2. **Verificar logs de Azure**
   - Ve a Azure Portal → App Service → Logs
   - Busca líneas que muestren:
     ```
     🔧 OAuth Redirect URI configurado: https://edugen-app.azurewebsites.net/auth/complete/google-oauth2/
     🔧 Website Hostname: edugen-app.azurewebsites.net
     ```

3. **Probar el login**
   - Ve a: https://edugen-app.azurewebsites.net
   - Intenta hacer login con Google
   - Deberías ser redirigido correctamente

## 🔍 **Verificación de Configuración**

### **URLs Importantes:**

| Entorno | URL Base | Redirect URI |
|---------|----------|--------------|
| **Producción** | `https://edugen-app.azurewebsites.net` | `https://edugen-app.azurewebsites.net/auth/complete/google-oauth2/` |
| **Desarrollo** | `http://localhost:8000` | `http://localhost:8000/auth/complete/google-oauth2/` |

### **Información OAuth:**

- **Client ID**: `50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com`
- **Scopes solicitados**:
  - `https://www.googleapis.com/auth/userinfo.email`
  - `https://www.googleapis.com/auth/userinfo.profile`
  - `openid`

## 🚨 **Troubleshooting**

### **Si el error persiste:**

1. **Verificar que los URIs coincidan exactamente**
   - Compara carácter por carácter
   - Asegúrate de incluir la barra final `/`

2. **Esperar propagación**
   - Los cambios en Google Cloud Console pueden tardar hasta 10 minutos

3. **Limpiar caché del navegador**
   - Ctrl+F5 para refrescar sin caché
   - O usar modo incógnito

4. **Verificar variables de entorno en Azure**
   - Azure Portal → App Service → Configuration
   - Verificar que `WEBSITE_HOSTNAME` sea correcto

### **Comandos útiles para debugging:**

```bash
# Ver logs de Azure en tiempo real
az webapp log tail --name edugen-app --resource-group [tu-resource-group]

# Verificar configuración actual
az webapp config appsettings list --name edugen-app --resource-group [tu-resource-group]
```

## ✅ **Confirmación de Éxito**

El problema estará resuelto cuando:
- ✅ Puedas hacer click en "Iniciar sesión con Google"
- ✅ Seas redirigido a Google para autenticación
- ✅ Después de autenticarte, regreses a la aplicación sin errores
- ✅ Veas tu perfil de Google en la aplicación

## 📋 **Próximos Pasos Recomendados**

1. **Cambiar credenciales por defecto**
   - Actualiza `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` por seguridad

2. **Configurar dominio personalizado** (opcional)
   - Si planeas usar un dominio personalizado, agrégalo también a Google Cloud Console

3. **Configurar HTTPS** (ya está configurado)
   - Azure App Service ya incluye certificado SSL automático

## 🔗 **Enlaces Útiles**

- [Google Cloud Console](https://console.cloud.google.com/)
- [Documentación OAuth 2.0 de Google](https://developers.google.com/identity/protocols/oauth2/web-server#authorization-errors-redirect-uri-mismatch)
- [Azure App Service Portal](https://portal.azure.com/) 