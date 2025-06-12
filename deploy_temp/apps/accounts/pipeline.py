from django.contrib.auth import get_user_model
from apps.institutions.models import Director
from apps.academic.models import Teacher, Student
from django.shortcuts import redirect
from social_core.exceptions import AuthForbidden, AuthAlreadyAssociated
from django.urls import reverse
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def create_user(backend, user, response, *args, **kwargs):
    """
    Crea o actualiza el usuario basado en la respuesta de Google
    """
    if backend.name == 'google-oauth2':
        email = response.get('email')
        if not email:
            return None
            
        # Buscar si existe un director con este email
        try:
            director = Director.objects.get(user__email=email)
            if director.is_active:
                return {'user': director.user}
        except Director.DoesNotExist:
            pass
            
        # Buscar si existe un docente con este email
        try:
            teacher = Teacher.objects.get(user__email=email)
            if teacher.is_active:
                return {'user': teacher.user}
        except Teacher.DoesNotExist:
            pass
            
        # Buscar si existe un estudiante con este email vinculado a Google
        try:
            student = Student.objects.get(google_account=email, google_account_linked=True)
            if student.is_active:
                return {'user': student.user}
        except Student.DoesNotExist:
            pass
            
        return None

def check_if_institutional_user(backend, details, response, user=None, *args, **kwargs):
    """
    Verifica si el usuario que intenta iniciar sesión es un director, docente o estudiante
    Si no lo es, redirige a una página de acceso denegado
    """
    if not backend.name == 'google-oauth2':
        return

    email = details.get('email')
    logger.debug(f"Verificando email: {email}")

    if not email:
        logger.error("No se encontró email en la respuesta de Google")
        raise AuthForbidden(backend)

    # Si el usuario ya existe, verificar su rol
    if user:
        # Comprobar si es director
        try:
            director = Director.objects.get(user=user)
            if director.is_active:
                logger.debug(f"Director existente y activo: {director}")
                backend.strategy.session_set('role_redirect', 'director')
                return {'is_new': False, 'user': user, 'is_director': True}
            else:
                logger.warning(f"Director inactivo: {director}")
                backend.strategy.session_set('access_denied', True)
                return redirect('/accounts/access-denied/')
        except Director.DoesNotExist:
            # No es director, comprobar si es docente
            try:
                teacher = Teacher.objects.get(user=user)
                if teacher.is_active:
                    logger.debug(f"Docente existente y activo: {teacher}")
                    backend.strategy.session_set('role_redirect', 'teacher')
                    return {'is_new': False, 'user': user, 'is_teacher': True}
                else:
                    logger.warning(f"Docente inactivo: {teacher}")
                    backend.strategy.session_set('access_denied', True)
                    return redirect('/accounts/access-denied/')
            except Teacher.DoesNotExist:
                # No es docente, comprobar si es estudiante
                try:
                    student = Student.objects.get(user=user, google_account_linked=True)
                    if student.is_active:
                        logger.debug(f"Estudiante existente y activo: {student}")
                        backend.strategy.session_set('role_redirect', 'student')
                        return {'is_new': False, 'user': user, 'is_student': True}
                    else:
                        logger.warning(f"Estudiante inactivo: {student}")
                        backend.strategy.session_set('access_denied', True)
                        return redirect('/accounts/access-denied/')
                except Student.DoesNotExist:
                    logger.warning(f"Usuario existe pero no es director, docente ni estudiante: {user}")
                    backend.strategy.session_set('access_denied', True)
                    return redirect('/accounts/access-denied/')

    # Si el usuario no existe, verificar por email
    # Comprobar si hay un director con ese email
    try:
        director = Director.objects.get(user__email=email)
        if director.is_active:
            logger.debug(f"Director encontrado por email: {director}")
            backend.strategy.session_set('role_redirect', 'director')
            return {'is_new': False, 'user': director.user, 'is_director': True}
        else:
            logger.warning(f"Director inactivo encontrado por email: {director}")
            backend.strategy.session_set('access_denied', True)
            return redirect('/accounts/access-denied/')
    except Director.DoesNotExist:
        # No es director, comprobar si es docente
        try:
            teacher = Teacher.objects.get(user__email=email)
            if teacher.is_active:
                logger.debug(f"Docente encontrado por email: {teacher}")
                backend.strategy.session_set('role_redirect', 'teacher')
                return {'is_new': False, 'user': teacher.user, 'is_teacher': True}
            else:
                logger.warning(f"Docente inactivo encontrado por email: {teacher}")
                backend.strategy.session_set('access_denied', True)
                return redirect('/accounts/access-denied/')
        except Teacher.DoesNotExist:
            # No es docente, comprobar si es estudiante
            try:
                student = Student.objects.get(google_account=email, google_account_linked=True)
                if student.is_active:
                    logger.debug(f"Estudiante encontrado por email: {student}")
                    backend.strategy.session_set('role_redirect', 'student')
                    return {'is_new': False, 'user': student.user, 'is_student': True}
                else:
                    logger.warning(f"Estudiante inactivo encontrado por email: {student}")
                    backend.strategy.session_set('access_denied', True)
                    return redirect('/accounts/access-denied/')
            except Student.DoesNotExist:
                logger.warning(f"No se encontró director, docente ni estudiante con email: {email}")
                backend.strategy.session_set('access_denied', True)
                return redirect('/accounts/access-denied/')

# Mantener este método para compatibilidad
def check_if_director(backend, details, response, user=None, *args, **kwargs):
    """
    Alias para check_if_institutional_user para mantener compatibilidad
    """
    return check_if_institutional_user(backend, details, response, user, *args, **kwargs)

def handle_auth_already_associated(backend, details, response, uid, user, social, *args, **kwargs):
    """
    Handle AuthAlreadyAssociated exceptions by redirecting to a custom error page
    """
    if social and social.user != user:
        # This social account is already associated with another user
        backend.strategy.session_set('auth_already_associated', True)
        return redirect(reverse('accounts:social_auth_error') + '?error_type=auth_already_associated')
    return None 