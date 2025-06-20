# 🚀 Scripts de Despliegue en Producción - Estudiantes 4to F

Este directorio contiene los scripts necesarios para configurar automáticamente los estudiantes del 4to grado F del colegio Polo Jiménez en el entorno de producción.

## 📋 Archivos Disponibles

### 1. `setup_production_students.py` (Comando Django)
**Recomendado para Azure App Service y servidores con SSH**

```bash
# Configuración normal (crea nuevos, actualiza existentes)
python manage.py setup_production_students

# Solo verificar estado actual (sin cambios)
python manage.py setup_production_students --verify-only

# Forzar recreación de todos los estudiantes
python manage.py setup_production_students --force
```

### 2. `deploy_production_students.py` (Script Python independiente)
**Para ejecución directa sin Django management**

```bash
python scripts/deploy_production_students.py
```

### 3. `deploy_azure_students.sh` (Script Bash para Azure)
**Para Azure App Service con acceso SSH**

```bash
# Configuración normal
bash scripts/deploy_azure_students.sh

# Solo verificar
bash scripts/deploy_azure_students.sh --verify-only

# Forzar recreación
bash scripts/deploy_azure_students.sh --force
```

## 🎯 ¿Cuál Script Usar?

| Entorno | Script Recomendado | Comando |
|---------|-------------------|---------|
| **Azure App Service** | `setup_production_students.py` | `python manage.py setup_production_students` |
| **VPS con SSH** | `deploy_azure_students.sh` | `bash scripts/deploy_azure_students.sh` |
| **Heroku** | `setup_production_students.py` | `heroku run python manage.py setup_production_students` |
| **Docker** | `setup_production_students.py` | `docker exec container python manage.py setup_production_students` |
| **Servidor Local** | Cualquiera | Según preferencia |

## 🏫 Datos que se Configuran

### Institución
- **Nombre**: TÉCNICO FAP MANUEL POLO JIMÉNEZ
- **Código**: POLO-JIMENEZ
- **Dominio**: cased.edu.pe

### Estructura Académica
- **Grado**: CUARTO (4to de secundaria)
- **Sección**: F
- **Capacidad**: 30 estudiantes

### 20 Estudiantes Registrados

| # | Estudiante | Email | Contraseña |
|---|------------|-------|------------|
| 1 | Carlos Eduardo Serna Ventura | 61791657@cased.edu.pe | 61791657 |
| 2 | Gabriela Isabel Obregón Escudero | 61912715@cased.edu.pe | 61912715 |
| 3 | Luciana Brigitte Orejuela Rentería | 61996238@cased.edu.pe | 61996238 |
| 4 | Chanel Yazmín Chalco Cardenas | 73921044@cased.edu.pe | 73921044 |
| 5 | Brunella Alejandra Ruiz Mera | 61907427@cased.edu.pe | 61907427 |
| 6 | Alvaro Fabian Vilca Quiroz | 61912578@cased.edu.pe | 61912578 |
| 7 | Mateo Martín Sánchez Sullón | 73724440@cased.edu.pe | 73724440 |
| 8 | Gabriela Alexandra Edones Castro | 61933419@cased.edu.pe | 61933419 |
| 9 | Valeria Deyanira Saavedra Tavara | 61851650@cased.edu.pe | 61851650 |
| 10 | Nicolás Carlos Lazo Adrianzen | 62544018@cased.edu.pe | 62544018 |
| 11 | Henry Pabbov Silupú Chavez | 61912911@cased.edu.pe | 61912911 |
| 12 | Tiago Arie Mori | 73846445@cased.edu.pe | 73846445 |
| 13 | Miguel Ángel Vera Ortiz | 72583221@cased.edu.pe | 72583221 |
| 14 | Luis Fernando Cardenas Esculonte | 61792050@cased.edu.pe | 61792050 |
| 15 | Adrianna Alessandra Beaumont Narro | 61851954@cased.edu.pe | 61851954 |
| 16 | Dominyk Emmanuel Zaga Toro | 73400838@cased.edu.pe | 73400838 |
| 17 | José Alonso Arica Paxi | 73839017@cased.edu.pe | 73839017 |
| 18 | Saul Santiago Reyes Ramos | 73718377@cased.edu.pe | 73718377 |
| 19 | Yaritza Thais Torres Ramírez | 61792348@cased.edu.pe | 61792348 |
| 20 | Ariana Valentina Ortega Falconi | 73914527@cased.edu.pe | 73914527 |

## 🔧 Instrucciones Paso a Paso

### Para Azure App Service

1. **Acceder via SSH al App Service**
   ```bash
   # En Azure Portal > App Service > SSH
   cd /home/site/wwwroot
   ```

2. **Ejecutar el comando de configuración**
   ```bash
   python manage.py setup_production_students
   ```

3. **Verificar que funcionó**
   ```bash
   python manage.py setup_production_students --verify-only
   ```

### Para VPS/Servidor Dedicado

1. **Conectar via SSH**
   ```bash
   ssh usuario@tu-servidor.com
   cd /ruta/a/tu/proyecto
   ```

2. **Ejecutar script completo**
   ```bash
   bash scripts/deploy_azure_students.sh
   ```

### Para Heroku

1. **Ejecutar comando remoto**
   ```bash
   heroku run python manage.py setup_production_students -a tu-app
   ```

## ⚙️ Variables de Entorno Requeridas

Asegúrate de que estas variables estén configuradas en producción:

```bash
DJANGO_SETTINGS_MODULE=config.settings.azure_production
# o config.settings.production según tu configuración

# Variables de base de datos
DATABASE_URL=postgresql://...
# o las variables específicas de tu BD

# Variables de seguridad
SECRET_KEY=tu-secret-key-super-seguro
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,tu-app.azurewebsites.net
```

## 🔍 Verificación Post-Despliegue

### 1. Verificar Login de Estudiantes
```bash
# Probar algunos logins aleatorios
python manage.py shell
```

```python
from django.contrib.auth import authenticate

# Probar autenticación
user = authenticate(username='61791657@cased.edu.pe', password='61791657')
print(f"Login exitoso: {user is not None}")
```

### 2. Verificar Estadísticas
```bash
python manage.py setup_production_students --verify-only
```

### 3. Acceso Web
- Ir a: `https://tu-dominio.com/login/`
- Probar con: `61791657@cased.edu.pe` / `61791657`

## 🚨 Solución de Problemas

### Error: "Command not found"
```bash
# Verificar que el comando existe
python manage.py help setup_production_students

# Si no existe, verificar que el archivo esté en la ubicación correcta:
# apps/academic/management/commands/setup_production_students.py
```

### Error: "Authentication failed"
```bash
# Verificar que EmailBackend esté configurado
python manage.py shell
```

```python
from django.conf import settings
print(settings.AUTHENTICATION_BACKENDS)
# Debe incluir: 'apps.accounts.backends.EmailBackend'
```

### Error: "Institution not found"
```bash
# El script crea automáticamente la institución
# Si hay error, verificar permisos de base de datos
python manage.py dbshell
```

## 📊 Logs y Monitoreo

### Ver logs en Azure
```bash
# En Azure Portal > App Service > Log stream
# O via SSH:
tail -f /var/log/django.log
```

### Comandos útiles de verificación
```bash
# Ver usuarios creados
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print(f'Total estudiantes: {User.objects.filter(role=\"student\").count()}')
"

# Ver matrículas activas
python manage.py shell -c "
from apps.academic.models import Enrollment
print(f'Matrículas activas: {Enrollment.objects.filter(status=\"ACTIVE\").count()}')
"
```

## 🔄 Re-ejecución Segura

Los scripts están diseñados para ser **idempotentes**, es decir:
- ✅ Se pueden ejecutar múltiples veces sin problemas
- ✅ No duplican datos existentes
- ✅ Solo actualizan contraseñas si el usuario ya existe
- ✅ Crean solo lo que falta

```bash
# Es seguro ejecutar esto múltiples veces
python manage.py setup_production_students
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisar logs** del servidor
2. **Ejecutar en modo verificación** primero: `--verify-only`
3. **Verificar variables de entorno** requeridas
4. **Comprobar permisos** de base de datos
5. **Verificar que las migraciones** estén aplicadas

---

**✅ Una vez ejecutado exitosamente, todos los estudiantes podrán acceder al sistema usando sus emails y contraseñas correspondientes.** 