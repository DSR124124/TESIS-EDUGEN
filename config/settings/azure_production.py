# config/settings/azure_production.py
# Configuración optimizada para Azure con PostgreSQL únicamente

import os
from .base import *

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================

DEBUG = False

# SECRET_KEY con fallback más flexible
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Usar un valor temporal para pruebas (NO recomendado para producción real)
    SECRET_KEY = 'django-insecure-azure-temp-key-change-in-production-f8k9j2h3g4x7z1m5'
    print("⚠️ WARNING: Usando SECRET_KEY temporal. Configure DJANGO_SECRET_KEY en producción.")

# Hosts permitidos para Azure App Service
ALLOWED_HOSTS = ['*']  # Temporal para debugging
django_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
if django_allowed_hosts:
    ALLOWED_HOSTS = [host.strip() for host in django_allowed_hosts.split(',') if host.strip()]

# Azure proporciona automáticamente WEBSITE_HOSTNAME, no la configures manualmente
website_hostname = os.environ.get('WEBSITE_HOSTNAME')  # Azure la configura automáticamente
if website_hostname and website_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(website_hostname)

ALLOWED_HOSTS.extend([
    '.azurewebsites.net',
    'localhost',
    '127.0.0.1',
])

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

SESSION_COOKIE_SECURE = False  # Cambiar a True cuando HTTPS esté configurado
CSRF_COOKIE_SECURE = False     # Cambiar a True cuando HTTPS esté configurado
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF Origins - Azure configura automáticamente muchas de estas
CSRF_TRUSTED_ORIGINS = [
    'https://*.azurewebsites.net', 
    'http://localhost:8000',
    'https://edugen-app-d8ddd4cwfve7bhca.centralus-01.azurewebsites.net',  # Tu hostname específico
]
if website_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{website_hostname}")
    CSRF_TRUSTED_ORIGINS.append(f"http://{website_hostname}")

# ==========================================
# BASE DE DATOS - POSTGRESQL AZURE
# ==========================================

DB_NAME = os.environ.get('DB_NAME') or os.environ.get('PGDATABASE', 'postgres')
DB_USER = os.environ.get('DB_USER') or os.environ.get('PGUSER', 'EDUGEN')
DB_PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('PGPASSWORD')
DB_HOST = os.environ.get('DB_HOST') or os.environ.get('PGHOST', 'edugenbd.postgres.database.azure.com')
DB_PORT = os.environ.get('DB_PORT') or os.environ.get('PGPORT', '5432')

if DB_PASSWORD:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 30,
                'application_name': 'sistema_educativo',
            },
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }
    print(f"🔧 PostgreSQL configurado: {DB_HOST}:{DB_PORT}/{DB_NAME}")
else:
    # Usar SQLite como fallback para debugging
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("⚠️ WARNING: Usando SQLite como fallback. Configure variables de PostgreSQL.")

# ==========================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==========================================

# Configuración simplificada de archivos estáticos para Azure
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Usar configuración básica de archivos estáticos
try:
    # Intentar usar whitenoise si está disponible
    import whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = False
    WHITENOISE_MANIFEST_STRICT = False
    print("🔧 Archivos estáticos: Usando Whitenoise")
except ImportError:
    # Fallback a configuración básica de Django
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    print("🔧 Archivos estáticos: Usando configuración básica de Django")

AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')

if AZURE_STORAGE_CONNECTION_STRING:
    try:
        DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
        account_name = None
        for part in AZURE_STORAGE_CONNECTION_STRING.split(';'):
            if part.startswith('AccountName='):
                account_name = part.split('=')[1]
                break
        if account_name:
            AZURE_CUSTOM_DOMAIN = f"{account_name}.blob.core.windows.net"
            MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/"
        print("🔧 Azure Blob Storage configurado")
    except Exception as e:
        print(f"⚠️ Error configurando Azure Storage: {e}")
        MEDIA_ROOT = os.path.join('/tmp', 'media')
        MEDIA_URL = '/media/'
else:
    MEDIA_ROOT = os.path.join('/tmp', 'media')
    MEDIA_URL = '/media/'
    print("🔧 Usando almacenamiento local temporal")

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ==========================================
# CONFIGURACIÓN DE EMAIL
# ==========================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Temporal para debugging
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Sistema Educativo <noreply@azurewebsites.net>')

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    print("🔧 Email: Usando SMTP")
else:
    print("🔧 Email: Usando console backend (no SMTP configurado)")

# ==========================================
# CONFIGURACIÓN DE CACHE
# ==========================================

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    try:
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'CONNECTION_POOL_KWARGS': {
                        'max_connections': 50,
                        'retry_on_timeout': True,
                    },
                },
                'TIMEOUT': 300,
                'KEY_PREFIX': 'sistema_educativo',
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
        print("🔧 Cache: Usando Redis")
    except Exception as e:
        print(f"⚠️ Error configurando Redis: {e}")
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'sistema-educativo-cache',
                'OPTIONS': {
                    'MAX_ENTRIES': 1000,
                    'CULL_FREQUENCY': 3,
                }
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        SESSION_FILE_PATH = '/tmp/sessions'
        print("🔧 Cache: Fallback a memoria local")
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'sistema-educativo-cache',
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
                'CULL_FREQUENCY': 3,
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    SESSION_FILE_PATH = '/tmp/sessions'
    print("🔧 Cache: Usando memoria local")

SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ==========================================
# CONFIGURACIÓN DE IA
# ==========================================

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_ENDPOINT = 'https://api.deepseek.com/v1'
DEEPSEEK_MODEL = 'deepseek-chat'

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_ENDPOINT = 'https://api.openai.com/v1'
OPENAI_MODEL = 'gpt-3.5-turbo'

AI_PROVIDER = os.environ.get('AI_PROVIDER', 'deepseek')

if AI_PROVIDER == 'deepseek' and DEEPSEEK_API_KEY:
    AI_CONFIG = {
        'api_key': DEEPSEEK_API_KEY,
        'endpoint': DEEPSEEK_ENDPOINT,
        'model': DEEPSEEK_MODEL,
        'provider': 'deepseek'
    }
    print("🔧 IA: Usando DeepSeek")
elif OPENAI_API_KEY:
    AI_CONFIG = {
        'api_key': OPENAI_API_KEY,
        'endpoint': OPENAI_ENDPOINT,
        'model': OPENAI_MODEL,
        'provider': 'openai'
    }
    print("🔧 IA: Usando OpenAI")
else:
    AI_CONFIG = None
    print("⚠️ IA: No configurada (funcional sin IA)")

MAX_TOKENS_PER_REQUEST = 1000
AI_REQUEST_TIMEOUT = 30
MAX_AI_REQUESTS_PER_HOUR = 50
MAX_AI_REQUESTS_PER_DAY = 200

# ==========================================
# LOGGING
# ==========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'sistema_educativo': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ==========================================
# REGIÓN Y LENGUAJE
# ==========================================

TIME_ZONE = 'America/Lima'
USE_TZ = True
LANGUAGE_CODE = 'es-pe'

# ==========================================
# VERIFICACIÓN FINAL (OPCIONAL)
# ==========================================

print("🚀 Sistema Educativo - Configuración de Producción Azure:")
print(f"  • Base de datos: {'PostgreSQL' if DB_PASSWORD else 'SQLite (fallback)'} ({DB_HOST if DB_PASSWORD else 'local'})")
print(f"  • Cache: {'Redis' if REDIS_URL else 'Local Memory'}")
print(f"  • Storage: {'Azure Blob' if AZURE_STORAGE_CONNECTION_STRING else 'Local'}")
print(f"  • Email: {'SMTP' if EMAIL_HOST_USER else 'Console'}")
print(f"  • IA: {AI_CONFIG['provider'] if AI_CONFIG else 'No configurada'}")
print(f"  • Hostname: {website_hostname or 'No configurado'}")
print(f"  • SSL: {'Configurado para Azure' if not SECURE_SSL_REDIRECT else 'Manual'}")
print(f"  • Debug: {DEBUG}")
print(f"  • Allowed Hosts: {ALLOWED_HOSTS[:3]}{'...' if len(ALLOWED_HOSTS) > 3 else ''}")

# Mensaje de estado
if not DB_PASSWORD:
    print("⚠️ IMPORTANTE: Configure las variables de base de datos PostgreSQL en Azure App Service")
if not DEEPSEEK_API_KEY and not OPENAI_API_KEY:
    print("⚠️ AVISO: La funcionalidad de IA no estará disponible sin API keys")
