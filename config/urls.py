"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import CustomLoginView, CustomLogoutView
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, JsonResponse
import django.utils.timezone
import logging

logger = logging.getLogger(__name__)

# Define simple error handlers directly in urls.py
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)

def handler400(request, exception):
    return render(request, 'errors/400.html', status=400)

# Vista de prueba simple
def test_view(request):
    try:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prueba Django</title>
            <style>
                body { 
                    font-family: Arial; 
                    background: #005CFF;
                    color: white;
                    text-align: center;
                    padding: 50px;
                    margin: 0;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    display: inline-block;
                }
                a {
                    color: #00CFFF;
                    font-weight: bold;
                    text-decoration: none;
                    background: rgba(255,255,255,0.1);
                    padding: 10px 20px;
                    border-radius: 5px;
                    margin: 10px;
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Django Funciona!</h1>
                <p>El servidor esta funcionando correctamente</p>
                <p>Version: Simple Test</p>
                <div>
                    <a href="/login/">Ir a Login</a>
                    <a href="/admin/">Admin</a>
                    <a href="/health/">Health Check</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"<h1>Error Simple</h1><p>{str(e)}</p>", status=500)

# Vista para probar base.html
def test_base_view(request):
    return render(request, 'test_base.html')

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    # Vista de prueba para diagnosticar problemas
    path('test/', test_view, name='test'),
    
    # Vista para probar base.html
    path('test-base/', test_base_view, name='test_base'),
    
    # Página principal redirige al login
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico')), name='favicon'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include('api.urls')),
    
    # Autenticación social (solo un path para social-auth)
    path('auth/', include('social_django.urls', namespace='social')),
    
    # Login y logout personalizados
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard del director
    path('director/', include('apps.director.urls', namespace='director')),
    # Dashboard para otros roles (profesores, estudiantes, etc.)
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('institutions/', include('apps.institutions.urls')),
    path('academic/', include('apps.academic.urls', namespace='academic')),
    # Comentamos las URLs que aún no están implementadas
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('content/', include('apps.content.urls')),
    path('portfolios/', include('apps.portfolios.urls', namespace='portfolios')),
    
    # Nuevas aplicaciones
    path('ai/', include('apps.ai_content_generator.urls', namespace='ai')),
    path('scorm/', include('apps.scorm_packager.urls', namespace='scorm_packager')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    
    # URLs para restablecer contraseña
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('health/', health_check, name='health_check'),
]

# Serve media files in all environments
# In production, this is a temporary solution - Azure Blob Storage is preferred
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Agregar las URLs de debug_toolbar cuando estamos en modo DEBUG
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        # debug_toolbar no está instalado, continuar sin él
        pass
