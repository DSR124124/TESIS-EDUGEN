"""
WSGI config for EduGen project in Azure App Service.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

application = get_wsgi_application() 