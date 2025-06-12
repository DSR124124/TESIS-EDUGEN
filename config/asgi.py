"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import logging

# Desactivar todos los logs SQL
logging.getLogger('django.db.backends').disabled = True
logging.getLogger('django.server').disabled = True

# Desactivar salida SQL en consola
os.environ['DJANGO_DEBUG_SQL'] = "False"
os.environ['PYTHONWARNINGS'] = "ignore"
os.environ['DJANGO_COLORS'] = "nocolor"
os.environ['DJANGO_LOG_LEVEL'] = "CRITICAL"

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
