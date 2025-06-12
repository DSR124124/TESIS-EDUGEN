# Configuración de Gunicorn para Azure App Service
import multiprocessing
import os

# Configuración del servidor
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "edugen"

# Django WSGI application
wsgi_module = "config.wsgi:application"

# Preload app
preload_app = True

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE=config.settings.azure_production",
    f"PYTHONUNBUFFERED=1"
] 