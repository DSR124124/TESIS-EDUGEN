# Configuración de Gunicorn para Azure App Service
import os

# Configuración de Gunicorn para Azure App Service
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 2
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
worker_class = "sync"

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "edugen"

# Django WSGI application
wsgi_module = "config.wsgi:application"

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE=config.settings.azure_production",
    f"PYTHONUNBUFFERED=1"
] 