# 🚀 Configuración de Azure App Service para EduGen

## 📋 Variables de Entorno Requeridas

Configure las siguientes variables de entorno en Azure App Service:

### 🔑 Variables Básicas (REQUERIDAS)
```bash
DJANGO_SECRET_KEY=tu-clave-secreta-aqui-muy-larga-y-segura
# NOTA: WEBSITE_HOSTNAME es configurada automáticamente por Azure - NO la agregues manualmente

### 🗄️ Base de Datos PostgreSQL (RECOMENDADO)
```bash
DB_NAME=nombre_de_tu_base_de_datos
DB_USER=usuario_postgres
DB_PASSWORD=password_muy_seguro
DB_HOST=tu-servidor.postgres.database.azure.com
DB_PORT=5432
```

### 🎨 Variables Opcionales
```bash
# IA - DeepSeek (Recomendado)
DEEPSEEK_API_KEY=tu-api-key-deepseek
AI_PROVIDER=deepseek

# O OpenAI (Alternativo)
OPENAI_API_KEY=tu-api-key-openai
AI_PROVIDER=openai

# Cache Redis (Opcional)
REDIS_URL=rediss://tu-redis-server:6380

# Storage Azure Blob (Opcional)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# Email SMTP (Opcional)
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app
```

## ⚙️ Configuración de Azure App Service

### 1. Configuración General
- **Runtime stack**: Python 3.11
- **Operating System**: Linux
- **Pricing tier**: B1 o superior (recomendado B2)

### 2. Configuración de Implementación
- **Startup Command**: `startup.sh`
- **Python Version**: 3.11
- **Always On**: Habilitado

### 3. Configuración de Aplicación
En el portal de Azure, vaya a:
`App Service > Configuración > Configuración de aplicación`

Agregue todas las variables de entorno listadas arriba.

## 🔧 Comandos de Diagnóstico

Si la aplicación falla, puede usar estos comandos en la consola SSH de Azure:

```bash
# Verificar archivos
ls -la /home/site/wwwroot/

# Verificar instalación de Python
python --version

# Verificar Django
python -c "import django; print(django.get_version())"

# Probar configuración
cd /home/site/wwwroot
python manage.py check --settings=config.settings.azure_production

# Ver logs
tail -f /home/LogFiles/Application/console.log
```

## 🚨 Solución de Problemas Comunes

### Error 500 - Internal Server Error
1. Verificar que todas las variables de entorno estén configuradas
2. Revisar logs en `/home/LogFiles/`
3. Verificar que `startup.sh` sea ejecutable
4. Comprobar que `requirements-azure.txt` esté completo

### Error de Base de Datos
1. Verificar conectividad a PostgreSQL
2. Comprobar reglas de firewall en Azure Database
3. Verificar credenciales de base de datos
4. La aplicación usará SQLite como fallback si PostgreSQL no está disponible

### Error de Archivos Estáticos
1. Los archivos estáticos se sirven con WhiteNoise
2. No es necesario configurar servidor web adicional
3. Azure App Service maneja automáticamente los archivos estáticos

## 📝 Archivos de Configuración

### startup.sh
Script de inicio que:
- Instala dependencias
- Ejecuta migraciones
- Recopila archivos estáticos
- Inicia el servidor Django

### requirements-azure.txt
Contiene todas las dependencias necesarias para Azure, incluyendo:
- Django y extensiones
- PostgreSQL driver
- WhiteNoise para archivos estáticos
- Dependencias de Azure

### config/settings/azure_production.py
Configuración optimizada para Azure con:
- Fallbacks para variables faltantes
- Configuración de seguridad para Azure
- Soporte para múltiples servicios (PostgreSQL, Redis, Storage)

## 🎯 Estado de la Aplicación

La aplicación funcionará en diferentes niveles según la configuración:

### ✅ Mínimo (Solo SECRET_KEY)
- Funciona con SQLite
- Sin IA
- Sin cache Redis
- Sin almacenamiento en blob

### 🟨 Recomendado (+ PostgreSQL)
- Base de datos robusta
- Mejor rendimiento
- Datos persistentes

### 🟩 Completo (+ IA + Redis + Storage)
- Funcionalidad completa de IA
- Cache optimizado
- Almacenamiento escalable

## 📞 Soporte

Si tiene problemas:
1. Revise los logs en Azure Portal
2. Verifique las variables de entorno
3. Use la consola SSH para diagnóstico
4. Contacte al equipo de desarrollo

---

**Nota**: Esta configuración está optimizada para Azure App Service y no requiere Docker. 