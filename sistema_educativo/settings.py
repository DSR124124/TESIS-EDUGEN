import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Asegurar que las apps están en el path
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# DeepSeek API Configuration
# Leer de variables de entorno para mayor seguridad
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-f1bfb13127b14daf97788bb0232a5584")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# Configuración de DeepSeek - Modelo de IA avanzado
# API Key configurada directamente para desarrollo
DEEPSEEK_API_KEY = "sk-f1bfb13127b14daf97788bb0232a5584"

# Mantener compatibilidad con código existente (OpenAI variables apuntan a DeepSeek)
OPENAI_API_KEY = DEEPSEEK_API_KEY  # Para compatibilidad con código existente
OPENAI_MODEL = DEEPSEEK_MODEL     # Para compatibilidad con código existente 

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a!7lz6(#o^j0v(&2&q_c=qnbwmds0=gfk1c@^%y1-fl$vkk(+w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Paquetes de terceros
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'corsheaders',
    
    # Apps propias
    'apps.accounts',
    'apps.academic',
    'apps.institutions',
    'apps.ai_content_generator',
    'apps.portfolios',
    'apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_educativo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_educativo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Configuración de login y logout
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Configuraciones de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Para producción, cambiar a:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configuraciones de seguridad
SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
CSRF_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Permitir iframes del mismo origen

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'accounts.CustomUser'

# Configuraciones para CORS (si se usa API REST)
CORS_ALLOW_ALL_ORIGINS = True  # Cambiar en producción
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Configuraciones ULTRA-OPTIMIZADAS para CONTENIDO EDUCATIVO EXTENSO
AI_CONTENT_CONFIG = {
    'DEFAULT_MAX_TOKENS': 8000,  # AJUSTADO - Máximo permitido por DeepSeek (8192)
    'DEFAULT_TEMPERATURE': 0.8,  # Equilibrio entre creatividad y coherencia
    'CONTENT_STYLE': 'ULTRA_EXTENSIVE',  # NUEVO - Enfoque ULTRA-EXTENSO sin cortes
    'MIN_CONTENT_LENGTH': 8000,  # INCREMENTADO - Mínimo 8000 palabras de contenido
    'TEMPLATE_STYLE': 'modern_educational',  # Plantilla visual moderna
    'FOCUS_ON_TEXT': True,  # PRIORIDAD MÁXIMA en contenido textual
    'REQUIRE_MULTIMEDIA': True,  # Incluir recursos multimedia con descripciones
    'MIN_MULTIMEDIA_RESOURCES': 15,  # INCREMENTADO - Mínimo 15 recursos multimedia
    'EDUCATIONAL_LEVEL': 'SECONDARY_ONLY',  # Solo educación secundaria
    'ENSURE_COMPLETE_SECTIONS': True,  # Completar todas las secciones
    'CONTENT_VERIFICATION': True,  # Verificar completitud del contenido
    'MULTIMEDIA_DESCRIPTIONS': True,  # Descripciones detalladas de multimedia
    'GENERATION_TIMEOUT': 300,  # INCREMENTADO - 5 minutos para contenido EXTENSO
    'ALLOW_EXTENDED_GENERATION': True,  # Permitir tiempo extra si es necesario
    'OPTIMIZE_FOR_SPEED': False,  # NO optimizar velocidad, priorizar completitud
    'TEXT_FIRST_APPROACH': True,  # Enfoque texto primero, diseño después
    'EXTENSIVE_MODE': True,  # NUEVO - Modo contenido extenso activado
    'NO_CONTENT_CUTS': True,  # NUEVO - NO cortar contenido bajo ninguna circunstancia
    'BACKGROUND_EXECUTION': True,  # NUEVO - Ejecución en segundo plano
}

# Configuraciones específicas para el generador de contenido IA con DeepSeek
AI_CONTENT_GENERATOR = {
    'DEFAULT_MODEL': DEEPSEEK_MODEL,
    'API_BASE_URL': 'https://api.deepseek.com/v1',
    'MAX_REQUESTS_PER_DAY': 50,  # Límite de solicitudes diarias por usuario
    'CACHE_RESULTS': True,  # Almacenar resultados en caché para optimizar
    'OPTIMIZE_FOR_SECONDARY': True,  # Optimizado específicamente para secundaria
    'INCLUDE_INTERACTIVE_ELEMENTS': True,  # Incluir elementos interactivos
}

# Configuración para tareas asíncronas (Celery)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE 