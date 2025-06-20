# config/settings/base.py
from pathlib import Path
import socket
# import dns.resolver  # Comentado temporalmente
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Forzar el uso de DNS de Google
# dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)  # Comentado temporalmente
# dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Comentado temporalmente

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'd1e0-2800-200-e731-1d0e-00-6e1b.ngrok-free.app', '504d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'b60d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', '004d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', '599d-2800-200-e731-1d0e-00-641d.ngrok-free.app', '*.ngrok-free.app', '*.ngrok.io']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'corsheaders',
    'tinymce',
    'social_django',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.academic',
    'apps.dashboard',
    'apps.ai_content_generator',
    'apps.portfolios',
    'apps.institutions',
    'apps.director',
    'apps.scorm_packager',
    'apps.analytics',
    'apps.content',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Middleware requerido por allauth
    # Middleware para manejar errores de autenticación social
    'apps.accounts.middleware.SocialAuthExceptionMiddleware',
    # Middleware automático para prevención de errores de temas
    'apps.portfolios.middleware.TopicRelationshipErrorMiddleware',
    'apps.portfolios.middleware.PortfolioErrorRecoveryMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.director.context_processors.institution_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(str(BASE_DIR), 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
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
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Configuración de DeepSeek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-f1bfb13127b14daf97788bb0232a5584")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# Mantener compatibilidad con código existente (OpenAI variables apuntan a DeepSeek)
OPENAI_API_KEY = DEEPSEEK_API_KEY  # Para compatibilidad con código existente
OPENAI_MODEL = DEEPSEEK_MODEL     # Para compatibilidad con código existente

# Sitio (necesario para la base de Django)
SITE_ID = 1

# Auth settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

# Configuración de autenticación
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'apps.accounts.backends.EmailBackend',  # Backend personalizado para login con email
    'django.contrib.auth.backends.ModelBackend',
)

# Configuración de Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '50661052209-7g0jf8e59ea1tme1sqaa80mgouibuj01.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

# Pipeline personalizado
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'apps.accounts.pipeline.check_if_institutional_user',  # Pipeline personalizado
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Configuración adicional de social auth
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/social-auth-error/'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/accounts/social-auth-error/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/dashboard/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/dashboard/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/accounts/login/'
SOCIAL_AUTH_INACTIVE_USER_URL = '/accounts/login/'

# Configuración adicional de errores de social auth
SOCIAL_AUTH_PIPELINE_ERROR_URL = '/accounts/social-auth-error/'

# Configuración de tiempo de expiración de tokens
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_TIME = 600  # Aumentar a 10 minutos
SOCIAL_AUTH_SESSION_EXPIRATION = True

# Configuración adicional para tolerancia a errores de red
SOCIAL_AUTH_GOOGLE_OAUTH2_TIMEOUT = 30
SOCIAL_AUTH_REQUESTS_TIMEOUT = 30

# Configuraciones de Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'prompt': 'select_account'
}
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/dashboard/'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

# Configuraciones adicionales para requests y conectividad
session = requests.Session()
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Configurar timeout por defecto
requests.adapters.DEFAULT_TIMEOUT = 30

# Logging mejorado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'ai_content_file': {
            'class': 'logging.FileHandler',
            'filename': 'ai_content.log',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'social_core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.ai_content_generator': {
            'handlers': ['console', 'ai_content_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuración de mensajes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo
EMAIL_HOST = 'smtp.gmail.com'  # Para producción
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_correo@gmail.com'  # Reemplaza con tu correo
EMAIL_HOST_PASSWORD = 'tu_contraseña'  # Reemplaza con tu contraseña de aplicación
DEFAULT_FROM_EMAIL = 'Sistema Educativo <noreply@sistemaeducativo.com>'

# TinyMCE Configuration
TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': '''
        textcolor save link image media preview codesample contextmenu
        table code lists fullscreen insertdatetime nonbreaking
        contextmenu directionality searchreplace wordcount visualblocks
        visualchars code fullscreen autolink lists charmap print hr
        anchor pagebreak
    ''',
    'toolbar1': '''
        fullscreen preview bold italic underline | fontselect,
        fontsizeselect | forecolor backcolor | alignleft alignright |
        aligncenter alignjustify | indent outdent | bullist numlist table |
        | link image media | codesample |
    ''',
    'toolbar2': '''
        visualblocks visualchars |
        charmap hr pagebreak nonbreaking anchor | code |
    ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}

# Configuraciones para manejar contenido grande (especialmente contenido AI generado)
# Aumentar límites de carga de datos para formularios grandes
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB en bytes
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Aumentar número máximo de campos
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB para archivos en memoria

# Configuraciones adicionales para contenido AI
# Aumentar límites de request body para contenido generado por IA
import sys
if hasattr(sys, '_getframe'):
    # Solo aplicar en desarrollo/testing
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
# Configuración de cache para contenido grande
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}