# config/settings/azure_production.py
# Configuración optimizada para Azure con PostgreSQL únicamente

import os
from .base import *

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY o DJANGO_SECRET_KEY debe estar configurado en producción")

# Hosts permitidos para Azure App Service
ALLOWED_HOSTS = []
django_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
if django_allowed_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in django_allowed_hosts.split(',') if host.strip()])

website_hostname = os.environ.get('WEBSITE_HOSTNAME')
if website_hostname:
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

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = []
if website_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{website_hostname}")

# ==========================================
# BASE DE DATOS - POSTGRESQL AZURE
# ==========================================

DB_NAME = os.environ.get('DB_NAME') or os.environ.get('PGDATABASE', 'postgres')
DB_USER = os.environ.get('DB_USER') or os.environ.get('PGUSER', 'EDUGEN')
DB_PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('PGPASSWORD')
DB_HOST = os.environ.get('DB_HOST') or os.environ.get('PGHOST', 'edugenbd.postgres.database.azure.com')
DB_PORT = os.environ.get('DB_PORT') or os.environ.get('PGPORT', '5432')

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD o PGPASSWORD debe estar configurado para PostgreSQL")

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

# ==========================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==========================================

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_MANIFEST_STRICT = False

AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')

if AZURE_STORAGE_CONNECTION_STRING:
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
else:
    MEDIA_ROOT = os.path.join('/home/site/wwwroot', 'media')
    MEDIA_URL = '/media/'
    print("🔧 Usando almacenamiento local")

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ==========================================
# CONFIGURACIÓN DE EMAIL
# ==========================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Sistema Educativo <noreply@azurewebsites.net>')

if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("🔧 Email: Usando console backend (no SMTP configurado)")

# ==========================================
# CONFIGURACIÓN DE CACHE
# ==========================================

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
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
    print("⚠️ IA: No configurada")

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
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
    },
}

# ==========================================
# REGIÓN Y LENGUAJE
# ==========================================

TIME_ZONE = 'America/Lima'
USE_TZ = True
LANGUAGE_CODE = 'es-pe'

# ==========================================
# VERIFICACIÓN FINAL
# ==========================================

REQUIRED_ENV_VARS = [
    ('SECRET_KEY', 'DJANGO_SECRET_KEY'),
    ('DB_PASSWORD', 'PGPASSWORD'),
]

for var_options in REQUIRED_ENV_VARS:
    if not any(os.environ.get(var) for var in var_options):
        missing_vars = ' o '.join(var_options)
        raise ValueError(f"Variable requerida no encontrada: {missing_vars}")

RECOMMENDED_ENV_VARS = [
    'WEBSITE_HOSTNAME',
    'AZURE_STORAGE_CONNECTION_STRING',
    'DEEPSEEK_API_KEY',
    'EMAIL_HOST_USER',
]

missing_recommended = [var for var in RECOMMENDED_ENV_VARS if not os.environ.get(var)]
if missing_recommended:
    print(f"⚠️ Variables recomendadas no encontradas: {', '.join(missing_recommended)}")

print("🚀 Sistema Educativo - Configuración de Producción:")
print(f"  • Base de datos: PostgreSQL ({DB_HOST})")
print(f"  • Cache: {'Redis' if REDIS_URL else 'Local Memory'}")
print(f"  • Storage: {'Azure Blob' if AZURE_STORAGE_CONNECTION_STRING else 'Local'}")
print(f"  • Email: {'SMTP' if EMAIL_HOST_USER else 'Console'}")
print(f"  • IA: {AI_CONFIG['provider'] if AI_CONFIG else 'No configurada'}")
print(f"  • Hostname: {website_hostname or 'No configurado'}")
print(f"  • SSL: {'Habilitado (Azure)' if not SECURE_SSL_REDIRECT else 'Manual'}")
