from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, GrapesJSTemplateViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'grapesjs-templates', GrapesJSTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 