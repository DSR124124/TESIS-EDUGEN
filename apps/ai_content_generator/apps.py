from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AiContentGeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_content_generator'
    verbose_name = 'Generador de Contenido IA'

    def ready(self):
        """
        Se ejecuta cuando la aplicación está lista
        """
        # Conectar la señal post_migrate para configurar tipos de contenido
        post_migrate.connect(self.setup_default_content_types, sender=self)

    def setup_default_content_types(self, sender, **kwargs):
        """
        Configura los tipos de contenido por defecto después de las migraciones
        """
        # Solo ejecutar si es la primera vez o si la tabla está vacía
        try:
            from .models import ContentType
            
            # Si ya existen tipos de contenido, no hacer nada
            if ContentType.objects.exists():
                return
            
            # Crear los tipos de contenido por defecto
            content_types = [
                {
                    'id': 1,
                    'name': 'Explicación de tema',
                    'description': 'Explicación detallada de conceptos con ejemplos y ejercicios de comprensión.',
                    'template_prompt': 'Se genera automáticamente con prompts específicos para explicaciones'
                },
                {
                    'id': 2,
                    'name': 'Ejercicios prácticos',
                    'description': 'Conjunto de ejercicios graduados con soluciones paso a paso.',
                    'template_prompt': 'Se genera automáticamente con prompts específicos para ejercicios'
                },
                {
                    'id': 3,
                    'name': 'Evaluación',
                    'description': 'Evaluación completa con diferentes tipos de preguntas y rúbrica.',
                    'template_prompt': 'Se genera automáticamente con prompts específicos para evaluaciones'
                },
                {
                    'id': 4,
                    'name': 'Material didáctico',
                    'description': 'Material educativo interactivo con actividades y recursos multimedia.',
                    'template_prompt': 'Se genera automáticamente con prompts específicos para material didáctico'
                },
                {
                    'id': 5,
                    'name': 'Resumen',
                    'description': 'Síntesis concisa de los conceptos principales con puntos clave.',
                    'template_prompt': 'Se genera automáticamente con prompts específicos para resúmenes'
                }
            ]
            
            # Crear los tipos de contenido
            for ct_data in content_types:
                ContentType.objects.get_or_create(
                    id=ct_data['id'],
                    defaults={
                        'name': ct_data['name'],
                        'description': ct_data['description'],
                        'template_prompt': ct_data['template_prompt']
                    }
                )
            
            print("✅ Tipos de contenido por defecto configurados automáticamente")
            
        except Exception as e:
            # Si hay algún error (como que la tabla no exista aún), ignorar silenciosamente
            pass 