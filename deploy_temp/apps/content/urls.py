from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Dashboard y listado
    path('', views.dashboard, name='dashboard'),
    
    # Generación y edición de contenido
    path('generar/', views.generar_contenido, name='generar_contenido'),
    path('generar-cuestionario/', views.generar_cuestionario_ia, name='generar_cuestionario_ia'),
    path('editar/<uuid:pk>/', views.editar_contenido, name='editar_contenido'),
    path('detalle/<uuid:pk>/', views.detalle_contenido, name='detalle_contenido'),
    path('eliminar/<uuid:pk>/', views.eliminar_contenido, name='eliminar_contenido'),
    
    # APIs y utilidades
    path('api/buscar_imagenes/', views.buscar_imagenes, name='buscar_imagenes'),
    
    # SCORM
    path('generar_scorm/<uuid:pk>/', views.generar_scorm, name='generar_scorm'),
    path('descargar_scorm/<uuid:pk>/', views.descargar_scorm, name='descargar_scorm'),
] 