# core/permissions.py
from rest_framework import permissions
from apps.accounts.models import User

class IsAdministrator(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es un administrador del sistema.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.ADMIN


class IsDirector(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es un director.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.DIRECTOR


class IsTeacher(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es un profesor.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.TEACHER


class IsStudent(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es un estudiante.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.STUDENT


class IsAdminOrDirector(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario es un administrador o director.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.ADMIN, User.DIRECTOR]


class IsSameInstitution(permissions.BasePermission):
    """
    Permiso personalizado para verificar si el usuario pertenece a la misma institución.
    """
    
    def has_object_permission(self, request, view, obj):
        # Administradores pueden acceder a todos
        if request.user.role == User.ADMIN:
            return True
        
        # Verificar si el objeto tiene una institución asignada
        if hasattr(obj, 'institution'):
            return obj.institution == request.user.institution
        
        # Verificar si el objeto es un usuario
        if hasattr(obj, 'institution_id'):
            return obj.institution_id == request.user.institution_id
        
        # Para objetos con otros tipos de relaciones institucionales
        if hasattr(obj, 'get_institution'):
            return obj.get_institution() == request.user.institution
        
        return False


class IsOwnerOrInstitutionStaff(permissions.BasePermission):
    """
    Permiso para verificar si el usuario es propietario o parte del personal de la institución.
    """
    
    def has_object_permission(self, request, view, obj):
        # Administradores pueden acceder a todos
        if request.user.role == User.ADMIN:
            return True
        
        # Verificar si el objeto tiene un propietario
        if hasattr(obj, 'user_id'):
            if obj.user_id == request.user.id:
                return True
        
        # Verificar si el objeto tiene alguna relación con un creador
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Directores pueden acceder a todo en su institución
        if request.user.role == User.DIRECTOR and request.user.institution:
            if hasattr(obj, 'institution') and obj.institution == request.user.institution:
                return True
            
            # Para estudiantes o profesores
            if hasattr(obj, 'user') and hasattr(obj.user, 'institution'):
                return obj.user.institution == request.user.institution
        
        return False