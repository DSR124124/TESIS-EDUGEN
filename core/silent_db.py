"""
Backend de base de datos personalizado que elimina todos los mensajes de depuración.
"""
import logging

# Configurar el logging general
logging.basicConfig(level=logging.CRITICAL)
for name in logging.Logger.manager.loggerDict:
    if 'django' in name:
        logging.getLogger(name).setLevel(logging.CRITICAL)
        logging.getLogger(name).propagate = False

# Un enfoque más seguro: solo modificar la función make_debug_cursor
from django.db.backends.base.base import BaseDatabaseWrapper

# Guardar la función original por si acaso
original_make_debug_cursor = BaseDatabaseWrapper.make_debug_cursor

# Redefinir la función para que simplemente devuelva el cursor sin registrar
def silent_cursor(self, cursor):
    return cursor

# Aplicar el monkey patch
BaseDatabaseWrapper.make_debug_cursor = silent_cursor

print("Configuración de silenciamiento SQL aplicada correctamente") 