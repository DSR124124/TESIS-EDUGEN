"""
Local settings for Sistema Educativo project.
"""
from .base import *  # noqa

# Monkey patch para eliminar los logs SQL de Django
from django.db.backends.base.base import BaseDatabaseWrapper
BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: cursor

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Permitir cargar contenido en iframes para SCORM (solo en desarrollo)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'sistema_educativo_db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Timeout en segundos
        },
        # Esta configuración silencia los logs de SQL
        'ATOMIC_REQUESTS': False,
        'CONN_MAX_AGE': 0,
    }
}

# Desactivar logs SQL de forma más agresiva
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django.db': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django.server': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
    },
}

# Desactivar panel SQL de debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': False,
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    # 'debug_toolbar.panels.sql.SQLPanel',  # Comentar este panel para desactivar los SQL logs
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']  # noqa F405
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa F405
INTERNAL_IPS = ['127.0.0.1']

# Django Extensions
INSTALLED_APPS += ['django_extensions']  # noqa F405