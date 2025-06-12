# core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from apps.accounts.models import User

class InstitutionMiddleware(MiddlewareMixin):
    """
    Middleware para filtrar el acceso a datos por institución.
    
    Este middleware verifica que un usuario solo pueda acceder a datos de su propia institución,
    excepto los administradores del sistema que pueden acceder a todas las instituciones.
    """
    
    def process_request(self, request):
        """
        Procesa la solicitud y agrega la institución actual al request.
        """
        if request.user.is_authenticated:
            # Agregar la institución del usuario al request
            request.institution = request.user.institution
            
            # Para administradores, no hay restricción de institución
            request.is_admin = request.user.role == User.ADMIN
        else:
            # Usuario no autenticado
            request.institution = None
            request.is_admin = False
        
        return None