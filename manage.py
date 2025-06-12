#!/usr/bin/env python"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

# Configuración básica de logging para reducir mensajes
logging.basicConfig(level=logging.ERROR)

# Silenciar solo los loggers específicos relacionados con SQL
logging.getLogger('django.db.backends').setLevel(logging.ERROR)
logging.getLogger('django.db.backends.schema').setLevel(logging.ERROR)

# Variables de entorno para reducir los mensajes
os.environ['DJANGO_LOG_LEVEL'] = 'ERROR'
os.environ['PYTHONWARNINGS'] = 'ignore'


def main():
    """Run administrative tasks."""
    # Configurar entorno
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        # Importar Django
        from django.core.management import execute_from_command_line
        
        # Ajustar verbosity para ciertos comandos
        if len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'migrate', 'makemigrations']:
            if '--verbosity' not in ' '.join(sys.argv) and '-v' not in ' '.join(sys.argv):
                sys.argv.append('--verbosity=0')
        
        # Intentar importar el módulo para silenciar SQL
        try:
            from django.db.backends.base.base import BaseDatabaseWrapper
            
            # Si DEBUG está activado y no hay contexto, silenciar la salida SQL
            if os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.local':
                BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: cursor
        except Exception:
            pass
        
        # Ejecutar el comando
        execute_from_command_line(sys.argv)
    
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


if __name__ == '__main__':
    main()