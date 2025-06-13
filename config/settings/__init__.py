# Este archivo solo importa la configuración base
from .base import *
import os

# Configuración de desarrollo
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'd1e0-2800-200-e731-1d0e-00-6e1b.ngrok-free.app', '504d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', '0d0b-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'de60-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'b60d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', '004d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', '599d-2800-200-e731-1d0e-00-641d.ngrok-free.app', '*.ngrok-free.app', '*.ngrok.io']

# Configuración para manejar proxy HTTPS (ngrok)
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Orígenes confiables para CSRF
CSRF_TRUSTED_ORIGINS = ['https://d1e0-2800-200-e731-1d0e-00-6e1b.ngrok-free.app', 'https://504d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'https://0d0b-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'https://de60-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'https://b60d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'https://004d-2800-200-e731-1d0e-00-9a11.ngrok-free.app', 'https://599d-2800-200-e731-1d0e-00-641d.ngrok-free.app', 'https://*.ngrok-free.app', 'https://*.ngrok.io']

# Configuración de OAuth para forzar una URI de redirección específica
# Usar localhost para evitar problemas con ngrok cambiante
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://localhost:8000/auth/complete/google-oauth2/'
# SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'https://599d-2800-200-e731-1d0e-00-641d.ngrok-free.app/auth/complete/google-oauth2/'
# Permitir redireccionamientos a localhost incluso en producción para desarrollo
SOCIAL_AUTH_ALLOW_INSECURE_REDIRECTS = True

# Configurar valores directamente sin depender del archivo .env - Cambiado a DeepSeek
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-f1bfb13127b14daf97788bb0232a5584")  # API Key configurada
DEEPSEEK_MODEL = "deepseek-chat"

# Mantener compatibilidad con código existente
OPENAI_API_KEY = DEEPSEEK_API_KEY  # Para compatibilidad
OPENAI_MODEL = DEEPSEEK_MODEL     # Para compatibilidad

# Base de datos - Cambiado para usar el directorio db en el proyecto
DB_PATH = os.path.join(BASE_DIR, "db", "sistema_educativo_db.sqlite3")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

print(f"Base de datos ubicada en: {DB_PATH}")

# Configuraciones adicionales para contenido grande (override de base.py)
# Aumentar límites para manejar contenido AI generado extenso
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Más campos permitidos
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB para archivos

# Configuración de logging para ver errores en consola
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}