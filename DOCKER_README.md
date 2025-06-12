# 🐳 EduGen - Configuración Docker

Este documento explica cómo usar Docker para ejecutar la aplicación EduGen - Sistema Educativo con IA.

## 📋 Requisitos Previos

- Docker Engine 20.10+
- Docker Compose 2.0+
- Al menos 2GB de RAM disponible
- Al menos 5GB de espacio en disco

## 🚀 Inicio Rápido

### 1. Construcción y Ejecución con Docker Compose

```bash
# Clonar el repositorio (si no lo has hecho)
git clone <tu-repositorio>
cd TESIS-EDUGEN

# Construir y ejecutar todos los servicios
docker-compose up --build

# O ejecutar en segundo plano
docker-compose up -d --build
```

### 2. Acceso a la Aplicación

- **Aplicación web**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Configuración Inicial

Después de ejecutar los contenedores, necesitarás configurar la aplicación manualmente:

```bash
# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic
```

## 🔧 Configuración

### Variables de Entorno

Puedes personalizar la configuración creando un archivo `.env`:

```bash
# .env
# Base de datos
PGHOST=db
PGPORT=5432
PGDATABASE=edugen
PGUSER=postgres
PGPASSWORD=EduGen123!

# Django
SECRET_KEY=django-insecure-edugen-docker-key-2024-change-in-production-f8k9j2h3g4
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,edugen-app.azurewebsites.net

# Google OAuth (ya configurado)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=AIzaSyDbaO4sVGS5_dCMV1r4yizjzqAoakAnME0

# IA (ya configurado)
DEEPSEEK_API_KEY=sk-f1bfb13127b14daf97788bb0232a5584
AI_PROVIDER=deepseek

# Redis
REDIS_URL=redis://redis:6379/0

# Configuración adicional
WEBSITE_HOSTNAME=localhost:8000
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://localhost:8000

# Azure Storage (opcional)
AZURE_STORAGE_CONNECTION_STRING=tu_connection_string
AZURE_STORAGE_CONTAINER_NAME=media
```

### Configuración de IA

Para habilitar las funciones de IA, necesitas configurar al menos una de estas APIs:

1. **DeepSeek** (recomendado - más económico):
   - Registrarse en https://platform.deepseek.com/
   - Obtener API key
   - Configurar `DEEPSEEK_API_KEY`

2. **OpenAI** (alternativa):
   - Registrarse en https://platform.openai.com/
   - Obtener API key
   - Configurar `OPENAI_API_KEY`

## 📦 Comandos Útiles

### Gestión de Contenedores

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web

# Reiniciar un servicio
docker-compose restart web

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes (¡CUIDADO! Elimina datos)
docker-compose down -v
```

### Comandos Django

```bash
# Ejecutar comandos Django en el contenedor
docker-compose exec web python manage.py <comando>

# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario adicional
docker-compose exec web python manage.py createsuperuser

# Shell de Django
docker-compose exec web python manage.py shell

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U postgres -d edugen

# Backup de la base de datos
docker-compose exec db pg_dump -U postgres edugen > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres -d edugen < backup.sql
```

## 🏗️ Solo Docker (sin Compose)

Si prefieres usar solo Docker:

```bash
# Construir la imagen
docker build -t edugen-app .

# Ejecutar con SQLite (para testing)
docker run -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e DEBUG=False \
  edugen-app

# Ejecutar con PostgreSQL externo
docker run -p 8000:8000 \
  -e PGHOST=tu_host_postgresql \
  -e PGPORT=5432 \
  -e PGDATABASE=edugen_db \
  -e PGUSER=tu_usuario \
  -e PGPASSWORD=tu_password \
  edugen-app
```

## 🔒 Producción

### Con Nginx

Para usar Nginx como proxy reverso:

```bash
# Ejecutar con perfil de producción
docker-compose --profile production up -d
```

### Configuración de Seguridad

Para producción, asegúrate de:

1. **Cambiar credenciales por defecto**
2. **Usar HTTPS** (configurar certificados SSL)
3. **Configurar firewall** apropiadamente
4. **Usar secrets** para variables sensibles
5. **Configurar backups** automáticos

### Variables de Entorno de Producción

```bash
# Ejemplo para producción
SECRET_KEY=tu_secret_key_super_seguro_de_50_caracteres_minimo
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
PGPASSWORD=password_muy_seguro_con_simbolos_123!
```

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Puerto 8000 ocupado**:
   ```bash
   # Cambiar puerto en docker-compose.yml
   ports:
     - "8080:8000"  # Usar puerto 8080 en su lugar
   ```

2. **Error de permisos**:
   ```bash
   # Dar permisos al script de entrada
   chmod +x docker-entrypoint.sh
   ```

3. **Base de datos no conecta**:
   ```bash
   # Verificar que PostgreSQL esté ejecutándose
   docker-compose ps
   
   # Ver logs de la base de datos
   docker-compose logs db
   ```

4. **Módulos Python faltantes**:
   ```bash
   # Reconstruir la imagen
   docker-compose build --no-cache web
   ```

### Logs y Debugging

```bash
# Ver todos los logs
docker-compose logs

# Logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs web

# Entrar al contenedor para debugging
docker-compose exec web bash
```

## 📊 Monitoreo

### Verificar Estado de Servicios

```bash
# Ver estado de contenedores
docker-compose ps

# Ver uso de recursos
docker stats

# Ver logs de salud
docker-compose logs | grep health
```

### Métricas de Rendimiento

Los contenedores incluyen health checks que puedes monitorear:

- **PostgreSQL**: Verifica conectividad cada 10s
- **Redis**: Verifica respuesta cada 10s
- **Django**: Responde en puerto 8000

## 🔄 Actualizaciones

```bash
# Actualizar código y reconstruir
git pull
docker-compose build --no-cache
docker-compose up -d

# Aplicar nuevas migraciones
docker-compose exec web python manage.py migrate
```

## 📝 Notas Adicionales

- Los datos de PostgreSQL y Redis se persisten en volúmenes Docker
- Los archivos media y estáticos se montan como volúmenes para persistencia
- El contenedor ejecuta como usuario no-root para seguridad
- Se incluye configuración de health checks para todos los servicios

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs`
2. Verifica la configuración de variables de entorno
3. Asegúrate de que todos los puertos estén disponibles
4. Verifica que Docker tenga suficientes recursos asignados

---

**¡Tu aplicación EduGen está lista para ejecutarse con Docker! 🎉** 