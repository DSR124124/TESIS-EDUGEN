# 🔧 Solución para Problemas de Sesiones en Azure

## 🚨 **Problema Identificado**
Las sesiones se pierden al hacer F5 (refresh) en Azure, causando que el usuario tenga que volver a iniciar sesión constantemente.

**Síntomas:**
- ✅ Login inicial funciona correctamente
- ❌ Al hacer F5, la sesión se pierde
- ❌ Las cookies se eliminan del navegador
- ❌ Hay que volver a hacer login constantemente

## 🔍 **Causa Raíz**
El problema era que la aplicación estaba configurada para usar **cache en memoria** para las sesiones:
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # ❌ Problemático en Azure
```

En Azure App Service, el cache en memoria es volátil y se reinicia frecuentemente, causando pérdida de sesiones.

## ✅ **Solución Implementada**

### **1. Cambio a Sesiones en Base de Datos**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # ✅ Persistente
```

### **2. Configuración de Cookies Mejorada**
```python
SESSION_COOKIE_SECURE = True          # HTTPS obligatorio
SESSION_COOKIE_HTTPONLY = True        # Prevenir XSS
SESSION_COOKIE_SAMESITE = 'Lax'      # Permitir navegación normal
SESSION_COOKIE_NAME = 'edugen_sessionid'  # Nombre personalizado
SESSION_COOKIE_AGE = 86400           # 24 horas
```

### **3. Configuración CSRF Mejorada**
```python
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://edugen-app.azurewebsites.net']
```

### **4. Migraciones de Sesiones**
Se agregaron comandos al startup script para asegurar las tablas de sesiones:
```bash
python manage.py migrate sessions
python manage.py clearsessions
```

## 🚀 **Deployment de la Solución**

Para aplicar los cambios:

```bash
git add .
git commit -m "Fix: Solucionar problema de sesiones en Azure - cambiar de cache a database"
git push origin main
```

## 🔍 **Verificación de la Solución**

### **1. Verificar Configuración (Comando personalizado)**
Después del deployment, ejecutar:
```bash
python manage.py check_sessions
```

### **2. Pruebas Manuales**
1. ✅ **Login**: Ve a https://edugen-app.azurewebsites.net/admin/
2. ✅ **Credenciales**: `admin` / `EduGenAdmin123!`
3. ✅ **Refresh**: Hacer F5 múltiples veces
4. ✅ **Navegación**: Cambiar entre páginas
5. ✅ **Persistencia**: Cerrar y abrir navegador

### **3. Verificar Cookies en Navegador**
1. F12 → Application → Cookies
2. Buscar: `edugen_sessionid`
3. Verificar que persiste después de F5

## 📋 **Configuración Antes vs Después**

| Aspecto | ❌ Antes (Problemático) | ✅ Después (Solucionado) |
|---------|---------------------|----------------------|
| **Engine** | `cache` (volátil) | `db` (persistente) |
| **Persistencia** | Se pierde en restart | Sobrevive a restarts |
| **Cookies** | Configuración básica | Configuración segura |
| **CSRF** | Configuración mínima | Configuración completa |
| **Debugging** | Sin herramientas | Comando `check_sessions` |

## 🔧 **Comandos de Troubleshooting**

### **Diagnosticar Sesiones**
```bash
python manage.py check_sessions
```

### **Limpiar Sesiones Expiradas**
```bash
python manage.py clearsessions
```

### **Ver Logs de Azure**
```bash
az webapp log tail --name edugen-app --resource-group [tu-resource-group]
```

### **Reiniciar App Service (si es necesario)**
```bash
az webapp restart --name edugen-app --resource-group [tu-resource-group]
```

## 🛡️ **Configuración de Seguridad**

Las nuevas configuraciones mejoran la seguridad:

- **HTTPS Obligatorio**: `SESSION_COOKIE_SECURE = True`
- **Protección XSS**: `SESSION_COOKIE_HTTPONLY = True`
- **SameSite Policy**: `SESSION_COOKIE_SAMESITE = 'Lax'`
- **CSRF Protection**: Configuración completa

## 📊 **Monitoreo Continuo**

### **Verificar Salud de Sesiones**
```python
# En Django shell
from django.contrib.sessions.models import Session
from django.utils import timezone

# Sesiones activas
active = Session.objects.filter(expire_date__gt=timezone.now()).count()
print(f"Sesiones activas: {active}")
```

### **Logs a Monitorear**
- `✅ Sesiones activas: X` (en check_sessions)
- `🔄 Asegurando tablas de sesiones...` (en startup)
- `🧹 Limpiando sesiones expiradas...` (en startup)

## 🎯 **Confirmación de Éxito**

La solución funciona cuando:
- ✅ Login con `admin/EduGenAdmin123!` funciona
- ✅ F5 no cierra la sesión
- ✅ Navegación entre páginas mantiene la sesión
- ✅ Cookie `edugen_sessionid` persiste en el navegador
- ✅ Sesiones se guardan en la base de datos

## 📞 **Soporte Adicional**

Si el problema persiste:
1. **Verificar HTTPS**: Azure debe estar sirviendo con SSL
2. **Limpiar cookies**: Borrar todas las cookies del sitio
3. **Verificar red**: Asegurar que no hay proxy/firewall bloqueando
4. **Navegador**: Probar en modo incógnito
5. **Logs**: Revisar logs de Azure para errores

## 🔗 **Enlaces Útiles**

- [Django Sessions Documentation](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
- [Azure App Service Configuration](https://docs.microsoft.com/en-us/azure/app-service/)
- [Cookie Security Best Practices](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) 