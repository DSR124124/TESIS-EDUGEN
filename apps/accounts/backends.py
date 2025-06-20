from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Backend de autenticación personalizado que permite login con email o username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
            
        try:
            # Buscar usuario por email o username
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
        except User.DoesNotExist:
            # Ejecutar el hasher de contraseñas por defecto para evitar timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios, buscar primero por email exacto
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        
        # Verificar la contraseña y si el usuario está activo
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None 