# config/settings/azure_production.py
# Configuración optimizada para Azure con PostgreSQL únicamente

import os
from .base import *

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-azure-temp-key-change-in-production')

# Hosts permitidos en Azure
ALLOWED_HOSTS = [
    'edugen-app.azurewebsites.net',
    '*.azurewebsites.net',
    'localhost',
    '127.0.0.1'
]

# Configuración HTTPS para Azure
SECURE_SSL_REDIRECT = False  # Azure maneja SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ==========================================
# BASE DE DATOS - TEMPORALMENTE SQLite para que funcione
# ==========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'azure_production.sqlite3',
    }
}

print("🔧 Usando SQLite temporalmente")

# ==========================================
# AZURE BLOB STORAGE para archivos media
# ==========================================

AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')

if AZURE_STORAGE_CONNECTION_STRING:
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
    
    # Extraer account name del connection string
    account_name = None
    for part in AZURE_STORAGE_CONNECTION_STRING.split(';'):
        if part.startswith('AccountName='):
            account_name = part.split('=')[1]
            break
    
    if account_name:
        AZURE_CUSTOM_DOMAIN = f"{account_name}.blob.core.windows.net"
        MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/"
    print("🔧 Usando Azure Blob Storage")
else:
    # Fallback a almacenamiento local
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    print("🔧 Usando almacenamiento local como fallback")

# Configuración de archivos estáticos para Azure
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ==========================================
# CONFIGURACIÓN DE IA - DEEPSEEK Y OPENAI
# ==========================================

# Configuración DeepSeek (más económico)
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_ENDPOINT = 'https://api.deepseek.com/v1'
DEEPSEEK_MODEL = 'deepseek-chat'

# OpenAI configuration (Backup)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_ENDPOINT = 'https://api.openai.com/v1'
OPENAI_MODEL = 'gpt-3.5-turbo'

# Configuración de IA unificada
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'deepseek')

if AI_PROVIDER == 'deepseek' and DEEPSEEK_API_KEY:
    AI_CONFIG = {
        'api_key': DEEPSEEK_API_KEY,
        'endpoint': DEEPSEEK_ENDPOINT,
        'model': DEEPSEEK_MODEL,
        'provider': 'deepseek'
    }
    print("🔧 Usando DeepSeek como proveedor de IA")
elif OPENAI_API_KEY:
    AI_CONFIG = {
        'api_key': OPENAI_API_KEY,
        'endpoint': OPENAI_ENDPOINT,
        'model': OPENAI_MODEL,
        'provider': 'openai'
    }
    print("🔧 Usando OpenAI como proveedor de IA")
else:
    AI_CONFIG = None
    print("⚠️ No se encontró configuración de IA válida")

# Límites para controlar costos
MAX_TOKENS_PER_REQUEST = 1000
AI_REQUEST_TIMEOUT = 30
MAX_AI_REQUESTS_PER_HOUR = 50
MAX_AI_REQUESTS_PER_DAY = 200

# ==========================================
# CACHE - Redis Azure o Local Memory
# ==========================================

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    # Usar Redis si está disponible
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    print("🔧 Usando Redis para cache")
else:
    # Fallback a memoria local
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
    print("🔧 Usando cache local como fallback")

# Cache para sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = False

# ==========================================
# LOGGING OPTIMIZADO
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
# CONFIGURACIÓN DE EMAIL
# ==========================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Sistema Educativo <noreply@azurewebsites.net>'

# ==========================================
# MIDDLEWARE OPTIMIZADO
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.accounts.middleware.SocialAuthExceptionMiddleware',
    'apps.portfolios.middleware.TopicRelationshipErrorMiddleware',
    'apps.portfolios.middleware.PortfolioErrorRecoveryMiddleware',
]

# Configuración WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_MANIFEST_STRICT = False

# ==========================================
# CONFIGURACIÓN ESPECÍFICA DE AZURE
# ==========================================

if 'WEBSITE_HOSTNAME' in os.environ:
    ALLOWED_HOSTS.append(os.environ['WEBSITE_HOSTNAME'])
    CSRF_TRUSTED_ORIGINS = [
        f"https://{os.environ['WEBSITE_HOSTNAME']}",
    ]

AZURE_DEPLOYMENT = True
WEBSITE_HOSTNAME = os.environ.get('WEBSITE_HOSTNAME', '')

# ==========================================
# CONFIGURACIÓN DE GOOGLE OAUTH
# ==========================================

SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI", 
    f"https://{WEBSITE_HOSTNAME}/auth/complete/google-oauth2/" if WEBSITE_HOSTNAME 
    else "https://sistema-educativo-app.azurewebsites.net/auth/complete/google-oauth2/"
)

# ==========================================
# CONFIGURACIÓN DE CONTENIDO IA
# ==========================================

AI_CONTENT_GENERATION = {
    'max_tokens': MAX_TOKENS_PER_REQUEST,
    'temperature': 0.7,
    'top_p': 0.9,
    'frequency_penalty': 0.1,
    'presence_penalty': 0.1,
    'timeout': AI_REQUEST_TIMEOUT,
    'stream': False,
}

AI_CONTENT_CACHE_TIMEOUT = 3600 * 24  # 24 horas

# ==========================================
# CONFIGURACIÓN DE ARCHIVOS
# ==========================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o644

ALLOWED_UPLOAD_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.pdf', '.doc', '.docx', '.txt',
    '.mp4', '.avi', '.mov',
    '.mp3', '.wav',
]

# ==========================================
# MONITOREO Y DEBUGGING
# ==========================================

APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get('APPINSIGHTS_INSTRUMENTATION_KEY')

if APPINSIGHTS_INSTRUMENTATION_KEY:
    INSTALLED_APPS += ['applicationinsights.django']
    MIDDLEWARE.insert(0, 'applicationinsights.django.ApplicationInsightsMiddleware')

# ==========================================
# CONFIGURACIÓN REGIONAL
# ==========================================

TIME_ZONE = 'America/Lima'
USE_TZ = True
LANGUAGE_CODE = 'es-pe'

# ==========================================
# VERIFICACIÓN DE CONFIGURACIÓN
# ==========================================

# Variables críticas requeridas
REQUIRED_ENV_VARS = [
    'PGPASSWORD',  # PostgreSQL es obligatorio
]

# Variables recomendadas
RECOMMENDED_ENV_VARS = [
    'SECRET_KEY',
    'AZURE_STORAGE_CONNECTION_STRING',
    'DEEPSEEK_API_KEY',
    'WEBSITE_HOSTNAME',
]

# Verificar variables requeridas
missing_required = []
for var in REQUIRED_ENV_VARS:
    if not os.environ.get(var):
        missing_required.append(var)

if missing_required:
    raise ValueError(f"Variables de entorno requeridas no encontradas: {', '.join(missing_required)}")

# Verificar variables recomendadas
missing_recommended = []
for var in RECOMMENDED_ENV_VARS:
    if not os.environ.get(var):
        missing_recommended.append(var)

if missing_recommended:
    print(f"⚠️  Variables de entorno recomendadas no encontradas: {', '.join(missing_recommended)}")

# ==========================================
# CONFIGURACIÓN DE RECUPERACIÓN DE ERRORES
# ==========================================

DATABASE_RETRY_ATTEMPTS = 3
DATABASE_RETRY_DELAY = 5
AI_RETRY_ATTEMPTS = 2
AI_RETRY_DELAY = 3

# ==========================================
# CONFIGURACIÓN FINAL DE DEBUG
# ==========================================

print("🚀 Configuración Azure Production cargada:")
print(f"  • Database: SQLite temporal")
print(f"  • Storage: {'Azure Blob' if AZURE_STORAGE_CONNECTION_STRING else 'Local'}")
print(f"  • Cache: {'Redis' if REDIS_URL else 'Local Memory'}")
print(f"  • AI Provider: {AI_CONFIG['provider'] if AI_CONFIG else 'None'}")
print(f"  • Website: {WEBSITE_HOSTNAME or 'No configurado'}")
