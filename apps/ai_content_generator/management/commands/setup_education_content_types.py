from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import ContentType

class Command(BaseCommand):
    help = 'Crear los tipos de contenido educativo estructurados'

    def handle(self, *args, **options):
        """
        Función principal para crear/actualizar los tipos de contenido educativo
        """
        content_types = [
            {
                'code': 'material_apoyo',
                'name': 'Material de Apoyo Integrado',
                'description': 'Material educativo integral que combina teoría, ejemplos y actividades.',
                'template': '''
                    Genera un Material de Apoyo Integrado sobre el tema: {{topic}} para {{grade_level}} de {{course}}.
                    
                    El contenido debe incluir:
                    
                    1. Introducción clara que explique el tema y su importancia (50-80 palabras)
                    2. Objetivos de aprendizaje (2-3 objetivos concretos)
                    3. Desarrollo teórico conciso del tema (150-250 palabras)
                    4. Ejemplos resueltos para ilustrar los conceptos (1-2 ejemplos relevantes)
                    5. Actividades prácticas sugeridas (1-2 actividades)
                    6. Referencias y recursos adicionales (1-2 recursos)
                    
                    El contenido debe ser adecuado para el nivel educativo {{grade_level}} y específico para la asignatura {{course}}.
                    
                    Instrucciones adicionales:
                    {{additional_instructions}}
                    
                    Genera un contenido estructurado en HTML que incluya encabezados, párrafos, listas y secciones bien definidas.
                ''',
            },
            {
                'code': 'plan_sesion',
                'name': 'Plan de Sesión de Clase',
                'description': 'Planificación detallada para una sesión de clase con objetivos, actividades y evaluación.',
                'template': '''
                    Genera un Plan de Sesión de Clase completo para enseñar sobre: {{topic}} a estudiantes de {{grade_level}} en la asignatura {{course}}.
                    
                    El plan debe incluir:
                    
                    1. Datos generales (título, duración: 45-90 minutos, materiales necesarios)
                    2. Objetivos específicos de aprendizaje (2-3 objetivos claros y medibles)
                    3. Secuencia completa de la sesión:
                       - Actividad de inicio/motivación (5-10 minutos)
                       - Desarrollo principal (20-40 minutos)
                       - Cierre y evaluación (10-15 minutos)
                    4. Estrategias didácticas específicas para cada momento
                    5. Criterios e instrumentos de evaluación
                    
                    Adapta el contenido al nivel educativo {{grade_level}} y a la asignatura {{course}}.
                    
                    Instrucciones adicionales:
                    {{additional_instructions}}
                    
                    Genera un plan estructurado en HTML con secciones claramente definidas.
                ''',
            },
            {
                'code': 'guia_ejercicios',
                'name': 'Guía de Ejercicios y Problemas',
                'description': 'Conjunto de ejercicios y problemas para practicar conceptos con soluciones.',
                'template': '''
                    Genera una Guía de Ejercicios y Problemas completa sobre: {{topic}} para estudiantes de {{grade_level}} de {{course}}.
                    
                    La guía debe incluir:
                    
                    1. Breve repaso teórico de los conceptos clave (100-200 palabras)
                    2. Ejercicios resueltos paso a paso (2-3 ejercicios con solución detallada)
                    3. Ejercicios propuestos para práctica independiente (4-6 ejercicios variados)
                       - Ejercicios básicos
                       - Ejercicios de nivel intermedio
                       - Desafíos (opcional)
                    4. Orientaciones para la resolución
                    
                    Adapta el nivel de dificultad al grado {{grade_level}} y al curso {{course}}.
                    
                    Instrucciones adicionales:
                    {{additional_instructions}}
                    
                    Genera un contenido estructurado en HTML con secciones claramente diferenciadas.
                ''',
            },
            {
                'code': 'evaluacion',
                'name': 'Evaluación Completa',
                'description': 'Instrumento de evaluación con diferentes tipos de preguntas y criterios de calificación.',
                'template': '''
                    Genera una Evaluación Completa sobre: {{topic}} para estudiantes de {{grade_level}} de {{course}}.
                    
                    La evaluación debe incluir:
                    
                    1. Instrucciones claras para el estudiante
                    2. Información general (tiempo recomendado: 30-60 minutos, puntaje total)
                    3. Preguntas variadas:
                       - Preguntas de desarrollo conceptual (2-3 preguntas)
                       - Ejercicios o problemas para resolver (2-3 problemas)
                       - Preguntas de aplicación o análisis (1-2 preguntas)
                    4. Criterios de evaluación o rúbrica
                    5. Soluciones o respuestas esperadas (opcional)
                    
                    Adapta la dificultad al nivel educativo {{grade_level}} y a la asignatura {{course}}.
                    
                    Instrucciones adicionales:
                    {{additional_instructions}}
                    
                    Genera un contenido estructurado en HTML bien organizado y fácil de seguir.
                ''',
            },
            {
                'code': 'material_interactivo',
                'name': 'Material Didáctico Interactivo',
                'description': 'Recursos didácticos con componentes interactivos para fomentar la participación.',
                'template': '''
                    Genera un Material Didáctico Interactivo sobre: {{topic}} para estudiantes de {{grade_level}} de {{course}}.
                    
                    El material debe incluir:
                    
                    1. Introducción al tema (50-100 palabras)
                    2. Guía de uso del material interactivo
                    3. Secuencia de actividades interactivas:
                       - Actividad de exploración inicial
                       - Actividad de aplicación práctica
                       - Actividad de evaluación formativa
                    4. Sugerencias para implementación (presencial o virtual)
                    5. Recursos complementarios
                    
                    Adapta el contenido al nivel educativo {{grade_level}} y a la asignatura {{course}}.
                    
                    Instrucciones adicionales:
                    {{additional_instructions}}
                    
                    Genera un contenido estructurado en HTML que sugiera elementos interactivos (aunque no sean funcionales en el HTML).
                ''',
            },
        ]

        # Crear o actualizar los tipos de contenido
        created_count = 0
        updated_count = 0

        # Añadir instrucciones para archivos indexados y additional_instructions a todos los prompts
        for content_type_data in content_types:
            # Encontrar la posición de {additional_instructions}
            prompt = content_type_data['template']
            additional_instr_pos = prompt.find('{{additional_instructions}}')
            
            if additional_instr_pos != -1:
                # Insertar antes de {additional_instructions}
                archivo_indexado_instr = """
INSTRUCCIONES PARA CONTENIDO EXTERNO:

1. Si se ha proporcionado un ANÁLISIS DE PDF:
   - Incorpora la información extraída del PDF proporcionado
   - Prioriza los conceptos, ejemplos y terminología encontrados en el PDF
   - Adapta el contenido para mantener coherencia con el material del PDF

2. Si se ha proporcionado INFORMACIÓN DEL ESTUDIANTE:
   - Personaliza el contenido específicamente para el estudiante mencionado
   - Ajusta el nivel de complejidad según el grado indicado
   - Haz referencias a los intereses o al tema del portafolio del estudiante cuando sea apropiado

3. Para cualquier otra INSTRUCCIÓN ADICIONAL:
   - Sigue exactamente las instrucciones especiales proporcionadas
   - Da prioridad a estas instrucciones sobre las pautas generales cuando haya conflicto
   - Mantén la estructura solicitada pero adapta el contenido según las instrucciones adicionales

"""
                
                # Insertar las nuevas instrucciones antes de {additional_instructions}
                content_type_data['template'] = (
                    prompt[:additional_instr_pos] + 
                    archivo_indexado_instr + 
                    prompt[additional_instr_pos:]
                )

        for content_type_data in content_types:
            content_type, created = ContentType.objects.update_or_create(
                name=content_type_data['name'],
                defaults={
                    'description': content_type_data['description'],
                    'template_prompt': content_type_data['template']
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Creado: {content_type.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Actualizado: {content_type.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'Proceso completado: {created_count} tipos de contenido creados, {updated_count} actualizados.'
        )) 