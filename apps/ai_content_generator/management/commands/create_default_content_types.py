from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import ContentType

class Command(BaseCommand):
    help = 'Crear tipos de contenido predeterminados para el generador de contenido AI'

    def handle(self, *args, **kwargs):
        content_types = [
            {
                'name': 'Explicación de tema',
                'description': 'Una explicación detallada sobre un tema específico.',
                'template_prompt': 'Genera una explicación detallada sobre el tema {topic} para estudiantes de {grade_level}. {additional_instructions}'
            },
            {
                'name': 'Ejercicios prácticos',
                'description': 'Conjunto de ejercicios para practicar un tema.',
                'template_prompt': 'Genera 5-8 ejercicios prácticos sobre {topic} para estudiantes de {grade_level}. Incluye sus respuestas. {additional_instructions}'
            },
            {
                'name': 'Evaluación',
                'description': 'Evaluación con preguntas sobre un tema específico.',
                'template_prompt': 'Genera una evaluación con 10 preguntas sobre {topic} para estudiantes de {grade_level}. Incluye una rúbrica de evaluación. {additional_instructions}'
            },
            {
                'name': 'Material didáctico',
                'description': 'Material didáctico para ayudar a enseñar un tema.',
                'template_prompt': 'Genera material didáctico sobre {topic} para estudiantes de {grade_level}. Incluye actividades interactivas y recursos visuales. {additional_instructions}'
            },
            {
                'name': 'Resumen',
                'description': 'Un resumen conciso de un tema.',
                'template_prompt': 'Genera un resumen conciso y claro sobre {topic} para estudiantes de {grade_level}. {additional_instructions}'
            },
        ]

        count = 0
        for content_type in content_types:
            obj, created = ContentType.objects.get_or_create(
                name=content_type['name'],
                defaults={
                    'description': content_type['description'],
                    'template_prompt': content_type['template_prompt']
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Creado tipo de contenido: {obj.name}'))
            else:
                self.stdout.write(f'El tipo de contenido "{obj.name}" ya existe.')

        self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se crearon {count} nuevos tipos de contenido.')) 