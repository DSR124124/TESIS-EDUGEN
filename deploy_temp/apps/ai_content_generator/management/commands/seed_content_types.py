from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import ContentType

class Command(BaseCommand):
    help = 'Inicializa los tipos de contenido predefinidos para la generación de contenido con IA'

    def handle(self, *args, **options):
        content_types = [
            {
                'name': 'Material de Apoyo Integrado',
                'description': 'Material educativo completo que integra teoría, ejercicios, evaluación y seguimiento académico.',
                'template_prompt': '''Crea un material educativo completo e integrado sobre {topic} para estudiantes de {grade_level} de secundaria en el curso de {course}. 

Este material debe contener TODAS las siguientes secciones:

SECCIÓN 1 - CONTENIDO TEÓRICO:
1. Introducción al tema (150 palabras)
2. Objetivos de aprendizaje (5 objetivos específicos)
3. Desarrollo teórico con 3-4 subtemas principales
4. Conceptos clave y definiciones destacadas
5. Ejemplos prácticos contextualizados

SECCIÓN 2 - EJERCICIOS PRÁCTICOS:
1. 5 ejercicios básicos con soluciones paso a paso
2. 5 ejercicios de nivel intermedio
3. 2 ejercicios de nivel avanzado
4. 1 actividad grupal colaborativa

SECCIÓN 3 - EVALUACIÓN Y SEGUIMIENTO:
1. 10 preguntas de opción múltiple (con respuestas correctas)
2. 5 preguntas de desarrollo corto
3. 2 problemas de aplicación
4. Rúbrica de evaluación con criterios específicos
5. Indicadores de logro para seguimiento académico

SECCIÓN 4 - MATERIAL DE REFUERZO:
1. Resumen de los conceptos clave (250 palabras)
2. Mapa conceptual del tema
3. Glosario de términos importantes (10 términos)
4. Recursos adicionales recomendados

CONSIDERACIONES IMPORTANTES:
- Adapta el contenido al nivel educativo de {grade_level}
- Incluye referencias a la realidad peruana
- Proporciona indicadores específicos para evaluar el progreso del estudiante
- Incluye secciones para registro de avance que permitan el seguimiento académico
- Asegúrate que el contenido esté alineado con el currículo nacional de educación básica
- Proporciona estrategias para identificar áreas de mejora en el alumno
- Incluye al menos 3 métricas concretas para evaluar el progreso

{additional_instructions}'''
            },
            {
                'name': 'Plan de Sesión de Clase',
                'description': 'Estructura completa de una sesión de clase con actividades, materiales y evaluación.',
                'template_prompt': '''Crea un plan detallado de sesión de clase sobre {topic} para estudiantes de {grade_level} en el curso de {course}.

El plan de sesión debe incluir TODAS las siguientes secciones:

DATOS INFORMATIVOS:
- Grado y nivel: {grade_level}
- Área curricular: {course}
- Tiempo: 90 minutos
- Fecha: [Por completar por el docente]

PROPÓSITOS DE APRENDIZAJE:
- Competencia(s): [Especificar según el Currículo Nacional]
- Capacidad(es): [Derivadas de las competencias]
- Desempeño(s): [Específicos para esta sesión]
- Enfoque transversal: [Según corresponda al tema]
- Producto de la sesión: [Especificar]

PREPARACIÓN DE LA SESIÓN:
- Recursos y materiales necesarios (detallados)
- Recursos TIC a utilizar

SECUENCIA DIDÁCTICA:
1. INICIO (15-20 minutos):
   - Actividades de motivación
   - Recojo de saberes previos
   - Conflicto cognitivo
   - Comunicación del propósito de la sesión

2. DESARROLLO (50-60 minutos):
   - Actividades detalladas paso a paso
   - Estrategias didácticas específicas
   - Trabajo individual/grupal
   - Acompañamiento docente
   - Productos parciales

3. CIERRE (10-15 minutos):
   - Estrategia de metacognición
   - Evaluación formativa
   - Conclusiones
   - Retroalimentación

EVALUACIÓN:
- Criterios de evaluación específicos
- Evidencias de aprendizaje
- Instrumentos a utilizar
- Indicadores de logro observables

ANEXOS:
- Fichas de trabajo para estudiantes
- Recursos complementarios
- Listado de referencias utilizadas
- Material de apoyo para el docente

ADAPTACIONES:
- Propuestas para estudiantes con necesidades educativas especiales
- Actividades alternativas según ritmos de aprendizaje

{additional_instructions}'''
            },
            {
                'name': 'Guía de Ejercicios y Problemas',
                'description': 'Colección estructurada de ejercicios y problemas con soluciones.',
                'template_prompt': '''Genera una guía completa de ejercicios y problemas sobre {topic} para estudiantes de {grade_level} en el curso de {course}.

La guía debe incluir TODAS las siguientes secciones:

SECCIÓN 1 - INTRODUCCIÓN:
- Objetivos de aprendizaje (5 objetivos específicos)
- Conceptos clave a reforzar (lista con breve explicación)
- Instrucciones de uso de la guía
- Recomendaciones para el estudio

SECCIÓN 2 - EJERCICIOS BÁSICOS (10 ejercicios):
- Ejercicios de reconocimiento y aplicación directa
- Cada ejercicio con su resolución detallada paso a paso
- Clasificados por subtemas o conceptos

SECCIÓN 3 - EJERCICIOS INTERMEDIOS (10 ejercicios):
- Ejercicios que combinen conceptos
- Problemas de aplicación contextualizada
- Resolución detallada de la mitad de los ejercicios
- Respuestas finales de todos

SECCIÓN 4 - PROBLEMAS AVANZADOS (5 problemas):
- Problemas complejos que integren múltiples conceptos
- Situaciones contextualizadas en la realidad peruana
- Pistas o sugerencias para la resolución
- Solución completa de 2 problemas como ejemplo

SECCIÓN 5 - AUTOEVALUACIÓN:
- 15 preguntas de opción múltiple con respuestas explicadas
- 5 problemas integradores
- Rúbrica de autoevaluación
- Recomendaciones según nivel de logro

CARACTERÍSTICAS ESPECÍFICAS:
- Variedad de formatos (cálculos, análisis, aplicación, etc.)
- Problemas contextualizados a la realidad peruana
- Progresión clara de dificultad
- Indicaciones para identificar errores comunes
- Tips y estrategias de resolución

{additional_instructions}'''
            },
            {
                'name': 'Evaluación Completa',
                'description': 'Evaluación integral con diferentes tipos de preguntas y rúbrica de evaluación.',
                'template_prompt': '''Crea una evaluación completa sobre {topic} para estudiantes de {grade_level} en el curso de {course}.

La evaluación debe incluir TODAS las siguientes secciones:

INFORMACIÓN GENERAL:
- Curso: {course}
- Grado: {grade_level}
- Tiempo de duración: 60 minutos
- Puntaje total: 20 puntos
- Instrucciones generales claras y precisas

PARTE I - CONOCIMIENTOS (6 puntos):
- 6 preguntas de opción múltiple (cada una con 4 alternativas)
- Temas específicos relacionados con {topic}
- Clave de respuestas correctas al final

PARTE II - COMPRENSIÓN (5 puntos):
- 3 preguntas de verdadero/falso con justificación
- 1 pregunta de desarrollo corto (5-6 líneas)
- 1 pregunta de completar un esquema/tabla
- Criterios claros de calificación

PARTE III - APLICACIÓN (5 puntos):
- 2 ejercicios o problemas para resolver paso a paso
- Espacio adecuado para las resoluciones
- Puntaje asignado a procedimiento y resultado

PARTE IV - ANÁLISIS Y EVALUACIÓN (4 puntos):
- 1 caso práctico contextualizado en la realidad peruana
- 2-3 preguntas de análisis sobre el caso
- 1 pregunta de reflexión o postura crítica
- Criterios de evaluación detallados

RECURSOS ADICIONALES:
- Tablas de datos (si son necesarias)
- Fórmulas permitidas (si aplica)
- Figuras o imágenes relevantes

DOCUMENTACIÓN PARA EL DOCENTE:
- Tabla de especificaciones (relación con competencias)
- Rúbrica de evaluación detallada
- Solucionario completo
- Escala de calificación sugerida

CONSIDERACIONES IMPORTANTES:
- Preguntas claras y sin ambigüedades
- Diferentes niveles de demanda cognitiva
- Evaluación alineada con el currículo nacional
- Lenguaje apropiado para el nivel educativo

{additional_instructions}'''
            },
            {
                'name': 'Material Didáctico Interactivo',
                'description': 'Recurso educativo con actividades interactivas para el aprendizaje activo.',
                'template_prompt': '''Diseña un material didáctico interactivo completo sobre {topic} para estudiantes de {grade_level} en el curso de {course}.

El material debe incluir TODAS las siguientes secciones:

INFORMACIÓN BÁSICA:
- Título creativo y llamativo
- Objetivos de aprendizaje (5 específicos)
- Público objetivo: {grade_level}
- Área curricular: {course}
- Tiempo estimado de uso: 2-3 horas (en sesiones)

SECCIÓN 1 - EXPLORACIÓN INTERACTIVA:
- Introducción multimedia al tema (texto + propuesta visual)
- 3 actividades de exploración inicial
- Preguntas de activación de conocimientos previos
- Reto introductorio motivador

SECCIÓN 2 - CONTENIDO PRINCIPAL:
- Desarrollo teórico dividido en 4-5 subtemas
- Cada subtema con:
  * Explicación concisa (200-250 palabras)
  * 1 elemento visual (infografía, diagrama, etc.)
  * 1 actividad interactiva (quiz, ordenar, relacionar, etc.)
  * 1 desafío práctico
- Retroalimentación inmediata para cada actividad

SECCIÓN 3 - APLICACIÓN PRÁCTICA:
- 5 ejercicios interactivos de complejidad progresiva
- 2 simulaciones o estudios de caso contextualizados
- 1 proyecto creativo aplicando lo aprendido
- Sistema de puntaje o recompensas

SECCIÓN 4 - EVALUACIÓN INTERACTIVA:
- Evaluación gamificada (15 preguntas variadas)
- Diferentes formatos: opción múltiple, completar, ordenar, etc.
- Retos de tiempo para resolver problemas
- Insignias o reconocimientos por logros

SECCIÓN 5 - RECURSOS COMPLEMENTARIOS:
- Glosario interactivo (mínimo 15 términos)
- Biblioteca de recursos adicionales
- Desafíos extra para ampliación
- Guía para padres/tutores

CARACTERÍSTICAS ESPECIALES:
- Instrucciones claras para cada actividad
- Propuestas de trabajo individual y colaborativo
- Referencias culturales peruanas
- Adaptable a diferentes ritmos de aprendizaje
- Sugerencias para implementación digital e impresa

{additional_instructions}'''
            }
        ]

        self.stdout.write(self.style.WARNING("Iniciando la creación de tipos de contenido..."))

        # Verificar si ya existen tipos de contenido
        existing_count = ContentType.objects.count()
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f"Ya existen {existing_count} tipos de contenido en la base de datos."))
            confirmation = input("¿Desea eliminar los tipos existentes y crear nuevos? (s/n): ")
            if confirmation.lower() != 's':
                self.stdout.write(self.style.WARNING("Operación cancelada."))
                return
            
            # Eliminar los tipos anteriores para una implementación limpia
            ContentType.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Tipos de contenido anteriores eliminados."))

        created_count = 0
        for ct_data in content_types:
            ContentType.objects.create(**ct_data)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Creado tipo de contenido: {ct_data['name']}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso completado. Tipos de contenido creados: {created_count}"
            )
        ) 