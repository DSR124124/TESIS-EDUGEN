"""
Utilidad para silenciar los mensajes SQL de Django

Este módulo debe importarse al inicio de la aplicación para silenciar
todos los mensajes SQL de depuración.
"""
import logging

# Silenciar todos los loggers relacionados con SQL
loggers = [
    'django.db.backends',
    'django.db.backends.schema',
    'django.db.backends.sqlite3',
    'django.db',
    'django',
    'django.server',
    'django.request',
]

# Desactivar completamente cada logger
for logger_name in loggers:
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.disabled = True
    logger.setLevel(logging.CRITICAL)
    
    # Eliminar cualquier handler existente
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    # Añadir un handler nulo
    null_handler = logging.NullHandler()
    logger.addHandler(null_handler)

# Monkey patch para eliminar los mensajes SQL
try:
    from django.db.backends.base.base import BaseDatabaseWrapper
    
    # Reemplazar la función que muestra los mensajes de depuración
    original_make_debug_cursor = BaseDatabaseWrapper.make_debug_cursor
    
    def silent_cursor(self, cursor):
        return cursor
    
    # Aplicar el monkey patch
    BaseDatabaseWrapper.make_debug_cursor = silent_cursor
    
    print("Mensajes SQL desactivados correctamente")
except ImportError:
    print("No se pudo desactivar los mensajes SQL, Django no está disponible")
except Exception as e:
    print(f"Error al desactivar mensajes SQL: {e}") 