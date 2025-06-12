"""
Entry point for Azure App Service
This file helps Azure detect and run the Django application
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.azure_production')

# Import Django WSGI application
from config.wsgi import application

# This is what Azure will use
app = application 