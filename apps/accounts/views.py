from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
import logging
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)

# Create your views here.

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'  # Restaurar al template original
    redirect_authenticated_user = False  # Cambiado a False para evitar conflictos

    def dispatch(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir inmediatamente
        if request.user.is_authenticated:
            logger.info(f"Usuario {request.user.username} ya autenticado, redirigiendo...")
            return self.redirect_authenticated_user_to_dashboard()
        return super().dispatch(request, *args, **kwargs)

    def redirect_authenticated_user_to_dashboard(self):
        """Redirige a un usuario ya autenticado al dashboard apropiado"""
        user = self.request.user
        
        logger.info(f"=== REDIRECCIÓN DE USUARIO AUTENTICADO ===")
        logger.info(f"Usuario: {user.username}")
        logger.info(f"Rol: {user.role}")
        
        # Verificar perfiles específicos usando related_name
        if hasattr(user, 'director_profile'):
            logger.info("Redirigiendo usuario autenticado a director:dashboard")
            return redirect('director:dashboard')
        elif hasattr(user, 'teacher_profile'):
            logger.info("Redirigiendo usuario autenticado a dashboard:teacher")
            return redirect('dashboard:teacher')
        elif hasattr(user, 'student_profile'):
            logger.info("Redirigiendo usuario autenticado a dashboard:student")
            return redirect('dashboard:student')
        
        # Fallback para superuser/staff
        if user.is_staff or user.is_superuser:
            logger.info("Redirigiendo usuario autenticado a admin")
            return redirect('admin:index')
        
        # Fallback final
        logger.warning(f"Usuario autenticado {user.username} sin perfil definido")
        return redirect('admin:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_login_url'] = reverse_lazy('social:begin', kwargs={'backend': 'google-oauth2'})
        return context

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        # Log para debugging
        logger.info(f"=== INTENTO DE LOGIN ===")
        logger.info(f"Email ingresado: {email}")
        
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            logger.info(f"Usuario encontrado: {user.username}")
            logger.info(f"Usuario activo: {user.is_active}")
            logger.info(f"Usuario rol: {user.role}")
            logger.info(f"Usuario staff: {user.is_staff}")
            logger.info(f"Usuario superuser: {user.is_superuser}")
            
            # Intentar autenticar
            auth_user = authenticate(
                self.request,
                username=user.username,
                password=password
            )
            
            if auth_user is not None:
                logger.info("=== AUTENTICACIÓN EXITOSA ===")
                logger.info(f"Usuario autenticado: {auth_user.username}")
                
                # Llamar al método padre para completar el login PERO sin usar get_success_url
                response = super().form_valid(form)
                
                # Log adicional después del login
                logger.info(f"Usuario en request después del login: {self.request.user}")
                logger.info(f"Usuario autenticado en request: {self.request.user.is_authenticated}")
                
                # Calcular y redirigir a la URL correcta directamente
                success_url = self.calculate_success_url()
                logger.info(f"URL de redirección calculada: {success_url}")
                
                # Devolver redirección directa en lugar de usar el response del padre
                return redirect(success_url)
            else:
                logger.warning("Autenticación fallida - contraseña incorrecta")
        except User.DoesNotExist:
            logger.warning(f"Usuario no encontrado con email: {email}")
        
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return self.form_invalid(form)

    def calculate_success_url(self):
        """Calcula la URL de redirección después del login exitoso"""
        user = self.request.user
        
        logger.info(f"=== CALCULANDO URL DE REDIRECCIÓN ===")
        logger.info(f"Usuario: {user.username}, roles: {user.role}")
        logger.info(f"Es autenticado: {user.is_authenticated}")
        
        # Redirigir usuarios superuser/staff al admin
        if user.is_staff or user.is_superuser:
            logger.info("Redirigiendo a admin:index")
            return 'admin:index'
        
        # Verificar perfiles específicos usando related_name
        if hasattr(user, 'director_profile'):
            logger.info("Redirigiendo a director:dashboard")
            return 'director:dashboard'
        elif hasattr(user, 'teacher_profile'):
            logger.info("Redirigiendo a dashboard:teacher")
            return 'dashboard:teacher'
        elif hasattr(user, 'student_profile'):
            logger.info("Redirigiendo a dashboard:student")
            return 'dashboard:student'
        
        # Si no tiene perfiles pero tiene rol definido, redirigir según el rol con mensaje de advertencia
        if user.role == 'director':
            logger.warning(f"Usuario {user.username} tiene rol director pero no perfil - redirigiendo a admin")
            messages.warning(self.request, 'Tu cuenta de director no está completamente configurada. Contacta al administrador.')
            return 'admin:index'
        elif user.role == 'teacher':
            logger.warning(f"Usuario {user.username} tiene rol teacher pero no perfil - redirigiendo a admin")
            messages.warning(self.request, 'Tu cuenta de profesor no está completamente configurada. Contacta al administrador.')
            return 'admin:index'
        elif user.role == 'student':
            logger.warning(f"Usuario {user.username} tiene rol student pero no perfil - redirigiendo a admin")
            messages.warning(self.request, 'Tu cuenta de estudiante no está completamente configurada. Contacta al administrador.')
            return 'admin:index'
        
        # Si no tiene rol definido, redirigir a admin con mensaje de error
        logger.error(f"Usuario {user.username} no tiene rol definido, redirigiendo a admin")
        messages.error(self.request, 'Tu cuenta no tiene un rol asignado. Contacta al administrador del sistema.')
        return 'admin:index'

    def get_success_url(self):
        """Método sobreescrito para evitar que se use - usamos calculate_success_url en su lugar"""
        return self.calculate_success_url()

    def form_invalid(self, form):
        logger.error(f"=== FORMULARIO INVÁLIDO ===")
        logger.error(f"Errores del formulario: {form.errors}")
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = 'login'  # Esto redirigirá al usuario a la página de login
    http_method_names = ['get', 'post']  # Asegurar que acepta tanto GET como POST

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, '¡Has cerrado sesión exitosamente!')
            # Usar el método logout de Django para cerrar la sesión
            logout(request)
        
        # Redirigir explícitamente a la página de login
        return redirect('login')

class AccessDeniedView(TemplateView):
    template_name = 'accounts/access_denied.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = "No tienes permiso para acceder a esta página. Por favor, inicia sesión con una cuenta autorizada."
        return context

class SocialAuthErrorView(TemplateView):
    template_name = 'accounts/social_auth_error.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_type = self.request.GET.get('error_type', 'unknown')
        error_msg = self.request.GET.get('error_msg', '')
        
        # Check if this is an AuthAlreadyAssociated error by checking the session or URL parameters
        if 'AuthAlreadyAssociated' in error_msg or self.request.session.get('auth_already_associated'):
            context['error_title'] = 'Cuenta ya Vinculada'
            context['error_message'] = 'Esta cuenta de Google ya está asociada a otro usuario en el sistema.'
            context['error_type'] = 'auth_already_associated'
            context['suggestions'] = [
                'Si esta es tu cuenta, intenta iniciar sesión con las credenciales del usuario ya registrado',
                'Si olvidaste tu contraseña, puedes restablecerla usando el enlace "¿Olvidaste tu contraseña?"',
                'Si crees que esto es un error, contacta al administrador del sistema'
            ]
            # Clear the session flag
            if 'auth_already_associated' in self.request.session:
                del self.request.session['auth_already_associated']
        elif error_type == 'auth_canceled':
            context['error_title'] = 'Autenticación Cancelada'
            context['error_message'] = 'El correo electrónico que intentaste usar no está verificado o no tiene permisos para acceder. Por favor, contacta al administrador.'
            context['error_type'] = 'auth_canceled'
        elif error_type == 'auth_error':
            context['error_title'] = 'Error de Autenticación'
            context['error_message'] = 'Hubo un problema al intentar autenticarte. Por favor, intenta de nuevo.'
            context['error_type'] = 'auth_error'
        else:
            context['error_title'] = 'Error Desconocido'
            context['error_message'] = 'Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde.'
            context['error_type'] = 'unknown'
            
        if error_msg:
            context['error_details'] = error_msg
            
        return context
