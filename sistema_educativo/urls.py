from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de la aplicación
    path('accounts/', include('apps.accounts.urls')),
    path('academic/', include('apps.academic.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('ai/', include('apps.ai_content_generator.urls')),
    path('portfolios/', include('apps.portfolios.urls')),
    path('scorm/', include('apps.scorm_packager.urls')),
    
    # API endpoints
    path('api/', include('api.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 