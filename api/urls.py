from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Endpoint raíz de la API para verificar su funcionamiento
    """
    return Response({
        "status": "ok",
        "message": "API del Sistema Educativo funcionando correctamente"
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('v1/', include('api.v1.urls')),
] 