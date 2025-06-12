"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application

# Establecer configuración de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

# Opcional: log simple al iniciar el servidor
try:
    application = get_wsgi_application()
    logging.info("✅ WSGI application cargada correctamente.")
except Exception as e:
    logging.error(f"❌ Error al iniciar WSGI: {e}")
    raise
