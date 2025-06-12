from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import ContentType

class Command(BaseCommand):
    help = 'Configura tipos de contenido con prompts específicos y estructurados'

    def handle(self, *args, **options):
        """
        Configura los tipos de contenido con prompts optimizados y estructurados
        """
        content_types = [
            {
                'id': 1,
                'name': 'Material de Apoyo Integrado',
                'description': 'Material educativo completo que integra teoría, ejercicios y evaluación.',
                'template_prompt': '''
Genera un Material de Apoyo Integrado completo sobre: "{topic}" para estudiantes de {grade_level} del curso {course}.

El material debe estar estructurado con las siguientes secciones usando MARCADORES específicos:

[TÍTULO] {topic}

[INTRODUCCIÓN] 
Escribe una introducción clara y motivadora (100-150 palabras) que explique:
- La importancia del tema en el contexto del curso
- Cómo se relaciona con la vida cotidiana del estudiante
- Los beneficios de dominar este conocimiento

[OBJETIVOS]
Presenta 4-5 objetivos de aprendizaje específicos y medibles usando verbos de acción como "identificar", "analizar", "aplicar", "resolver", etc.

[DESARROLLO TEÓRICO]
Desarrolla el contenido teórico principal dividido en 3-4 subtemas. Para cada subtema:
- Explicación clara y concisa (200-300 palabras por subtema)
- Conceptos clave destacados
- Ejemplos contextualizados al nivel del estudiante

[EJEMPLOS PRÁCTICOS]
Incluye 3 ejemplos resueltos paso a paso que demuestren la aplicación de los conceptos teóricos. Cada ejemplo debe:
- Presentar un problema real y relevante
- Mostrar el proceso de solución completo
- Explicar el razonamiento detrás de cada paso

[ACTIVIDADES]
Diseña 5 actividades prácticas de diferentes niveles:
- 2 actividades básicas (aplicación directa)
- 2 actividades intermedias (análisis y síntesis)
- 1 actividad avanzada (evaluación y creatividad)

[EVALUACIÓN]
Crea una evaluación completa con:
- 8 preguntas de opción múltiple
- 3 preguntas de desarrollo corto
- 2 problemas de aplicación práctica
- Incluye las respuestas correctas y criterios de evaluación

[RECURSOS ADICIONALES]
Sugiere recursos complementarios:
- 3 sitios web educativos relevantes
- 2 videos explicativos recomendados
- 1 libro o manual de consulta
- Glosario con 10 términos clave

INSTRUCCIONES ESPECÍFICAS:
- Adapta el lenguaje al nivel de {grade_level}
- Incluye referencias al contexto peruano cuando sea pertinente
- Asegúrate de que el contenido sea coherente y progresivo
- Usa un tono didáctico pero accesible

{additional_instructions}
'''
            },
            {
                'id': 2,
                'name': 'Plan de Sesión de Clase',
                'description': 'Plan detallado para una sesión de clase con actividades, recursos y evaluación.',
                'template_prompt': '''
Genera un Plan de Sesión de Clase completo sobre: "{topic}" para estudiantes de {grade_level} del curso {course}.

Estructura el plan usando los siguientes MARCADORES:

[TÍTULO] {topic} - Plan de Sesión

[INFORMACIÓN GENERAL]
- Grado: {grade_level}
- Asignatura: {course}
- Duración: 90 minutos
- Modalidad: Presencial/Virtual adaptable

[OBJETIVOS DE SESIÓN]
Define 3-4 objetivos específicos que los estudiantes lograrán al final de la sesión, usando verbos medibles como: identificar, explicar, aplicar, resolver.

[COMPETENCIAS Y CAPACIDADES]
Indica las competencias del Currículo Nacional de Educación Básica que se desarrollarán:
- Competencia principal
- Capacidades específicas
- Desempeños esperados

[SECUENCIA DIDÁCTICA]

**INICIO (15 minutos)**
- Actividad de motivación y enganche
- Recuperación de saberes previos (3 preguntas clave)
- Presentación del propósito de la sesión
- Establecimiento de acuerdos de convivencia

**DESARROLLO (60 minutos)**
Divide en 3 momentos:

1. **Construcción del Aprendizaje (25 min)**
   - Presentación del contenido principal
   - Explicación con ejemplos
   - Demostración práctica

2. **Aplicación Guiada (20 min)**
   - Actividad dirigida en grupos pequeños
   - Resolución de ejercicios con acompañamiento

3. **Aplicación Autónoma (15 min)**
   - Trabajo individual o en parejas
   - Ejercicios de consolidación

**CIERRE (15 minutos)**
- Síntesis de aprendizajes (¿Qué aprendimos hoy?)
- Metacognición (¿Cómo aprendimos?)
- Evaluación formativa rápida
- Asignación de tarea o proyecto

[MATERIALES Y RECURSOS]
Lista detallada de:
- Materiales físicos necesarios
- Recursos digitales (apps, plataformas, videos)
- Espacios requeridos
- Preparación previa del docente

[ESTRATEGIAS DIDÁCTICAS]
Especifica las metodologías a usar:
- Aprendizaje colaborativo
- Gamificación educativa
- Resolución de problemas
- Aprendizaje basado en proyectos

[EVALUACIÓN]
**Evaluación Formativa:**
- Técnicas de observación durante la clase
- Preguntas orales de verificación
- Lista de cotejo para actividades grupales

**Evaluación Sumativa:**
- 5 preguntas de salida (ticket de salida)
- Rúbrica para evaluar la participación
- Criterios de evaluación del trabajo realizado

[ATENCIÓN A LA DIVERSIDAD]
Estrategias para estudiantes con:
- Diferentes ritmos de aprendizaje
- Necesidades educativas especiales
- Distintos estilos de aprendizaje

[TAREA O EXTENSIÓN]
Actividad para realizar en casa que refuerce lo aprendido en la sesión.

CONSIDERACIONES:
- Adapta las actividades al nivel cognitivo de {grade_level}
- Incluye momentos de reflexión y autoevaluación
- Asegura la participación activa de todos los estudiantes
- Considera el uso de tecnología apropiada

{additional_instructions}
'''
            },
            {
                'id': 3,
                'name': 'Guía de Ejercicios y Problemas',
                'description': 'Conjunto estructurado de ejercicios y problemas con diferentes niveles de dificultad.',
                'template_prompt': '''
Genera una Guía de Ejercicios y Problemas sobre: "{topic}" para estudiantes de {grade_level} del curso {course}.

Estructura la guía usando los siguientes MARCADORES:

[TÍTULO] Guía de Ejercicios: {topic}

[INSTRUCCIONES GENERALES]
Proporciona instrucciones claras sobre:
- Cómo usar esta guía
- Tiempo estimado para completarla
- Materiales necesarios
- Criterios de autoevaluación

[RECORDATORIO TEÓRICO]
Presenta un resumen conciso (150-200 palabras) de los conceptos fundamentales necesarios para resolver los ejercicios, incluyendo:
- Definiciones clave
- Fórmulas o procedimientos importantes
- Tips para recordar conceptos

[EJEMPLOS RESUELTOS]
Presenta 3 ejemplos completamente resueltos de complejidad creciente:

**Ejemplo 1 (Nivel Básico):**
- Problema planteado
- Proceso de solución paso a paso
- Explicación del razonamiento
- Respuesta final

**Ejemplo 2 (Nivel Intermedio):**
- Problema más complejo
- Análisis de la situación
- Estrategia de solución
- Desarrollo detallado
- Verificación de resultados

**Ejemplo 3 (Nivel Avanzado):**
- Problema que requiere análisis crítico
- Múltiples enfoques de solución
- Proceso de selección de estrategia
- Solución completa
- Reflexión sobre el resultado

[EJERCICIOS NIVEL BÁSICO]
10 ejercicios de aplicación directa que refuercen:
- Comprensión de conceptos fundamentales
- Aplicación de fórmulas básicas
- Procedimientos estándar

[EJERCICIOS NIVEL INTERMEDIO]
8 ejercicios que requieran:
- Análisis de situaciones
- Combinación de conceptos
- Resolución de problemas multi-paso
- Interpretación de resultados

[EJERCICIOS NIVEL AVANZADO]
5 ejercicios desafiantes que involucren:
- Pensamiento crítico
- Resolución creativa de problemas
- Aplicación en contextos nuevos
- Análisis de casos complejos

[PROBLEMAS DE APLICACIÓN]
3 problemas contextualizados que conecten el tema con situaciones reales de la vida del estudiante o el entorno peruano.

[EJERCICIOS DE AUTOEVALUACIÓN]
5 ejercicios con respuestas para que el estudiante verifique su progreso:
- Incluye las soluciones completas
- Criterios para evaluar si la respuesta es correcta
- Sugerencias para mejorar si hay errores

[DESAFÍOS EXTRA]
2 problemas opcionales para estudiantes que deseen profundizar:
- Problemas que integren múltiples conceptos
- Situaciones que requieran investigación adicional
- Proyectos de aplicación creativa

[CLAVES DE RESPUESTAS]
Proporciona:
- Respuestas numéricas o conceptuales para todos los ejercicios
- Explicaciones breves para ejercicios complejos
- Referencias a los ejemplos resueltos cuando sea útil

CONSIDERACIONES PEDAGÓGICAS:
- Progresión gradual de dificultad
- Variedad en los tipos de problemas
- Conexión con situaciones reales
- Fomento del razonamiento lógico
- Adaptación al nivel de {grade_level}

{additional_instructions}
'''
            },
            {
                'id': 4,
                'name': 'Evaluación Completa',
                'description': 'Evaluación integral con diferentes tipos de preguntas y criterios de calificación.',
                'template_prompt': '''
Genera una Evaluación Completa sobre: "{topic}" para estudiantes de {grade_level} del curso {course}.

Estructura la evaluación usando los siguientes MARCADORES:

[TÍTULO] Evaluación: {topic}

[INFORMACIÓN DE LA EVALUACIÓN]
- Asignatura: {course}
- Grado: {grade_level}
- Duración: 90 minutos
- Puntaje total: 20 puntos
- Modalidad: Escrita/Digital adaptable

[INSTRUCCIONES GENERALES]
Proporciona instrucciones claras para el estudiante:
- Cómo completar cada sección
- Distribución del tiempo sugerida
- Materiales permitidos
- Criterios de presentación
- Advertencias importantes

[COMPETENCIAS EVALUADAS]
Lista las competencias y capacidades del Currículo Nacional que se evalúan:
- Competencia principal
- Capacidades específicas
- Criterios de desempeño

[SECCIÓN I: CONOCIMIENTOS BÁSICOS]
**Preguntas de Opción Múltiple (8 preguntas - 2 puntos c/u)**

Crea 8 preguntas de opción múltiple que evalúen:
- Comprensión de conceptos fundamentales
- Identificación de elementos clave
- Aplicación de definiciones
- Cada pregunta con 4 alternativas (solo una correcta)
- Marca claramente la respuesta correcta

[SECCIÓN II: COMPRENSIÓN Y ANÁLISIS]
**Preguntas de Desarrollo Corto (4 preguntas - 1 punto c/u)**

Diseña 4 preguntas que requieran respuestas de 2-3 líneas:
- Explicación de conceptos
- Comparación entre elementos
- Justificación de afirmaciones
- Análisis de situaciones simples

[SECCIÓN III: APLICACIÓN PRÁCTICA]
**Ejercicios de Resolución (2 ejercicios - Ejercicio 1: 3 puntos, Ejercicio 2: 4 puntos)**

**Ejercicio 1 (Nivel Intermedio):**
- Problema contextualizado
- Requiere aplicación directa de conceptos
- Incluye el proceso de solución paso a paso

**Ejercicio 2 (Nivel Avanzado):**
- Problema complejo que integra varios conceptos
- Requiere análisis y síntesis
- Múltiples pasos de solución
- Interpretación de resultados

[SECCIÓN IV: PENSAMIENTO CRÍTICO]
**Pregunta de Análisis Profundo (1 pregunta - 3 puntos)**

Una pregunta que evalúe:
- Capacidad de análisis crítico
- Argumentación fundamentada
- Aplicación creativa del conocimiento
- Reflexión sobre implicaciones o consecuencias

[CLAVE DE RESPUESTAS Y CRITERIOS]

**Sección I - Respuestas Múltiple Opción:**
1. [Respuesta correcta con breve justificación]
2. [Respuesta correcta con breve justificación]
[...continúa para las 8 preguntas]

**Sección II - Criterios para Desarrollo Corto:**
- Criterios específicos para cada pregunta
- Elementos clave que debe incluir la respuesta
- Puntaje parcial por elementos correctos

**Sección III - Procedimientos de Solución:**
- Solución completa paso a paso para cada ejercicio
- Distribución de puntajes por pasos
- Errores comunes y cómo descontarlos

**Sección IV - Rúbrica para Pensamiento Crítico:**
- Excelente (3 pts): Criterios específicos
- Bueno (2 pts): Criterios específicos  
- Regular (1 pt): Criterios específicos
- Deficiente (0 pts): Criterios específicos

[TABLA DE ESPECIFICACIONES]
Presenta una tabla que muestre:
- Contenidos evaluados
- Tipo de pregunta
- Nivel cognitivo (recuerdo, comprensión, aplicación, análisis)
- Puntaje asignado
- Tiempo estimado

[CRITERIOS DE CALIFICACIÓN]
- Escala vigesimal (0-20)
- Nivel de logro esperado: 14-20 (Logro destacado)
- Nivel de logro: 11-13 (Logro esperado)
- En proceso: 08-10 (En proceso)
- En inicio: 00-07 (En inicio)

CONSIDERACIONES:
- Evalúa diferentes niveles cognitivos según la Taxonomía de Bloom
- Incluye preguntas contextualizadas al entorno del estudiante
- Asegura claridad en el lenguaje apropiado para {grade_level}
- Distribuye equilibradamente los puntajes
- Considera diferentes estilos de aprendizaje

{additional_instructions}
'''
            },
            {
                'id': 5,
                'name': 'Material Didáctico Interactivo',
                'description': 'Recurso educativo con actividades interactivas y elementos multimedia.',
                'template_prompt': '''
Genera un Material Didáctico Interactivo sobre: "{topic}" para estudiantes de {grade_level} del curso {course}.

Estructura el material usando los siguientes MARCADORES:

[TÍTULO] Material Interactivo: {topic}

[PRESENTACIÓN DEL MATERIAL]
Introduce el material con:
- Objetivo principal del recurso
- Público objetivo: {grade_level}
- Tiempo estimado de uso: 45-60 minutos
- Modalidad: Individual y grupal
- Competencias que desarrolla

[GUÍA DE NAVEGACIÓN]
Explica cómo usar el material:
- Estructura general del contenido
- Tipos de actividades incluidas
- Símbolos y códigos utilizados
- Recomendaciones de uso

[ACTIVACIÓN DE CONOCIMIENTOS]
**Actividad de Inicio: "¿Qué sabes sobre...?"**
- 3 preguntas abiertas para reflexionar
- Actividad de lluvia de ideas
- Conexión con experiencias previas
- Predicciones sobre el tema

[EXPLORACIÓN INTERACTIVA]
**Módulo 1: Descubrimiento del Tema**
- Presentación multimedia del contenido principal
- Infografía descriptiva sugerida
- 3 preguntas de comprensión intercaladas
- Enlaces a recursos externos (videos, simulaciones)

**Módulo 2: Profundización**
- Desarrollo detallado de conceptos clave
- Ejemplos interactivos paso a paso
- Actividad de arrastrar y soltar (conceptual)
- Quiz de verificación (5 preguntas)

[ACTIVIDADES INTERACTIVAS]

**Actividad 1: "Clasifica y Ordena"**
- Ejercicio de categorización
- 10 elementos para clasificar en 3 categorías
- Retroalimentación inmediata
- Explicación de respuestas correctas

**Actividad 2: "Completa el Mapa"**
- Mapa conceptual con espacios en blanco
- Banco de palabras para completar
- Conexiones entre conceptos
- Autoevaluación del resultado

**Actividad 3: "Simulador Práctico"**
- Descripción de una simulación interactiva
- Pasos para realizar la actividad
- Variables que el estudiante puede modificar
- Análisis de resultados obtenidos

[LABORATORIO VIRTUAL]
**Experimento/Ejercicio Práctico:**
- Situación problema contextualizada
- Materiales virtuales necesarios
- Procedimiento paso a paso
- Registro de observaciones
- Conclusiones guiadas

[JUEGOS EDUCATIVOS]
**Juego 1: "Desafío Rápido"**
- 10 preguntas de respuesta rápida
- Sistema de puntuación
- Niveles de dificultad progresiva
- Retroalimentación motivadora

**Juego 2: "Resuelve el Misterio"**
- Caso o problema para resolver
- Pistas que se van revelando
- Aplicación del conocimiento adquirido
- Solución final explicada

[PROYECTO CREATIVO]
**Tarea de Aplicación:**
- Proyecto individual o grupal
- Uso creativo del conocimiento adquirido
- Recursos digitales sugeridos
- Criterios de evaluación
- Tiempo estimado: 1 semana

[EVALUACIÓN GAMIFICADA]
**Sistema de Insignias:**
- "Explorador": Completar todos los módulos
- "Investigador": Resolver el laboratorio virtual
- "Maestro": Obtener 80% en todas las actividades
- "Creativo": Completar el proyecto final

**Evaluación Final Interactiva:**
- 15 preguntas de diferentes formatos
- Retroalimentación inmediata por pregunta
- Puntaje final con recomendaciones
- Certificado digital de completion

[RECURSOS COMPLEMENTARIOS]
**Biblioteca Digital:**
- 3 videos explicativos (con enlaces sugeridos)
- 2 lecturas complementarias
- 1 podcast o audio relacionado
- Galería de imágenes temáticas

**Para Profundizar:**
- Proyectos de investigación sugeridos
- Enlaces a museos virtuales o sitios especializados
- Apps educativas recomendadas
- Libros digitales de consulta

[GUÍA PARA EL DOCENTE]
**Implementación en Clase:**
- Estrategias para uso presencial y virtual
- Sugerencias de trabajo colaborativo
- Adaptaciones para diferentes ritmos de aprendizaje
- Criterios de evaluación y seguimiento

**Extensiones Curriculares:**
- Conexión con otras asignaturas
- Actividades de refuerzo
- Desafíos para estudiantes avanzados
- Apoyo para estudiantes con dificultades

CARACTERÍSTICAS TÉCNICAS:
- Compatible con dispositivos móviles y computadoras
- Accesible para estudiantes con necesidades especiales
- Navegación intuitiva apropiada para {grade_level}
- Elementos visuales atractivos y educativos
- Interactividad que promueve el aprendizaje activo

{additional_instructions}
'''
            }
        ]

        self.stdout.write(self.style.SUCCESS("🚀 Configurando tipos de contenido estructurados..."))

        created_count = 0
        updated_count = 0

        for content_type_data in content_types:
            content_type, created = ContentType.objects.update_or_create(
                id=content_type_data['id'],
                defaults={
                    'name': content_type_data['name'],
                    'description': content_type_data['description'],
                    'template_prompt': content_type_data['template_prompt']
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Creado: {content_type.name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"🔄 Actualizado: {content_type.name}"))

        self.stdout.write(self.style.SUCCESS(f"""
🎉 CONFIGURACIÓN COMPLETADA:
📊 Tipos de contenido creados: {created_count}
🔄 Tipos de contenido actualizados: {updated_count}

📋 TIPOS DE CONTENIDO DISPONIBLES:
1. Material de Apoyo Integrado - Material completo con teoría, ejercicios y evaluación
2. Plan de Sesión de Clase - Plan detallado para clase de 90 minutos con secuencia didáctica
3. Guía de Ejercicios y Problemas - Ejercicios estructurados por niveles de dificultad
4. Evaluación Completa - Evaluación integral con diferentes tipos de preguntas
5. Material Didáctico Interactivo - Recurso con actividades interactivas y multimedia

✨ Todos los tipos incluyen marcadores específicos para estructuración automática
🎯 Cada tipo está optimizado para el contexto educativo peruano
"""))