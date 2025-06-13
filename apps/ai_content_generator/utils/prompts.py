"""
Utilidades para crear prompts para generación de contenido
"""

def create_content_prompt(content_type_id, topic, grade_level, course, additional_instructions=''):
    """
    Crea prompts específicos y estructurados para cada tipo de contenido educativo
    """
    
    # Mapear content_type_id a nombres específicos
    content_types = {
        1: 'Explicación de tema',
        2: 'Ejercicios prácticos', 
        3: 'Evaluación',
        4: 'Material didáctico',
        5: 'Resumen'
    }
    
    # Obtener el nombre del tipo de contenido
    content_type_name = content_types.get(content_type_id, 'Material didáctico')
    
    # Prompts específicos según el tipo de contenido
    if content_type_id == 1:  # Explicación de tema
        return create_explanation_prompt(topic, grade_level, course, additional_instructions)
    elif content_type_id == 2:  # Ejercicios prácticos
        return create_exercises_prompt(topic, grade_level, course, additional_instructions)
    elif content_type_id == 3:  # Evaluación
        return create_evaluation_prompt(topic, grade_level, course, additional_instructions)
    elif content_type_id == 4:  # Material didáctico
        return create_didactic_material_prompt(topic, grade_level, course, additional_instructions)
    elif content_type_id == 5:  # Resumen
        return create_summary_prompt(topic, grade_level, course, additional_instructions)
    else:
        return create_didactic_material_prompt(topic, grade_level, course, additional_instructions)

def create_explanation_prompt(topic, grade_level, course, additional_instructions=''):
    """Prompt específico para generar explicaciones de tema"""
    return f"""
GENERA UNA EXPLICACIÓN COMPLETA SOBRE: {topic}
CURSO: {course} | GRADO: {grade_level}

ESTRUCTURA OBLIGATORIA:

[SECCIÓN]
Introducción al tema
Explica qué es {topic}, por qué es importante en {course} y cómo se conecta con la vida cotidiana de estudiantes de {grade_level}. Incluye objetivos de aprendizaje claros y motivación inicial. (200-250 palabras)

[SECCIÓN]
Conceptos fundamentales
Desarrolla los conceptos clave de {topic} de forma clara y ordenada. Define términos importantes, explica propiedades principales y establece relaciones entre conceptos. Usa lenguaje apropiado para {grade_level}. (300-400 palabras)

[EJEMPLO]
Situación cotidiana
Presenta un ejemplo real y cercano donde los estudiantes puedan ver {topic} en acción. Incluye:
- Contexto familiar para el estudiante
- Explicación paso a paso
- Conexión clara con los conceptos teóricos
- Reflexión sobre la aplicación práctica

[EJEMPLO]
Aplicación académica
Muestra cómo {topic} se aplica en problemas típicos de {course}:
- Problema claramente planteado
- Método de resolución explicado
- Solución desarrollada paso a paso
- Verificación del resultado

[SECCIÓN]
Aspectos importantes a recordar
Destaca los puntos clave que los estudiantes deben recordar sobre {topic}. Incluye consejos para evitar errores comunes y estrategias de estudio. (150-200 palabras)

[ACTIVIDAD]
Verificación de comprensión
Diseña una actividad simple donde los estudiantes puedan comprobar si entendieron los conceptos:
- Instrucciones claras
- 3-4 preguntas o ejercicios breves
- Respuestas esperadas
- Criterios de autoevaluación

INSTRUCCIONES ADICIONALES: {additional_instructions}

GENERAR CONTENIDO EDUCATIVO DIRECTO - NO META-COMENTARIOS
"""

def create_exercises_prompt(topic, grade_level, course, additional_instructions=''):
    """Prompt específico para generar ejercicios prácticos"""
    return f"""
GENERA EJERCICIOS PRÁCTICOS SOBRE: {topic}
CURSO: {course} | GRADO: {grade_level}

ESTRUCTURA OBLIGATORIA:

[SECCIÓN]
Introducción a los ejercicios
Explica el propósito de estos ejercicios y cómo ayudan a dominar {topic}. Incluye consejos generales para resolverlos exitosamente. (100-150 palabras)

[EJEMPLO]
Ejercicio modelo resuelto
Presenta un ejercicio completo con solución detallada:
- Enunciado claro del problema
- Análisis de los datos
- Método de resolución elegido
- Desarrollo paso a paso
- Resultado final con interpretación
- Verificación de la respuesta

[ACTIVIDAD]
Ejercicios de práctica básica
**Nivel inicial** (3 ejercicios)
Diseña ejercicios que apliquen directamente los conceptos fundamentales de {topic}:
- Ejercicio 1: [Enunciado y tipo de problema]
- Ejercicio 2: [Enunciado y tipo de problema]  
- Ejercicio 3: [Enunciado y tipo de problema]
*Incluye las respuestas al final*

[ACTIVIDAD]
Ejercicios de aplicación intermedia
**Nivel intermedio** (3 ejercicios)
Crea ejercicios que requieran análisis y aplicación de múltiples conceptos:
- Ejercicio 4: [Problema contextualizado]
- Ejercicio 5: [Problema con análisis]
- Ejercicio 6: [Problema de síntesis]
*Incluye las respuestas al final*

[ACTIVIDAD]
Desafíos avanzados
**Nivel avanzado** (2 ejercicios)
Propone problemas que requieran pensamiento crítico y creatividad:
- Desafío 1: [Problema complejo o abierto]
- Desafío 2: [Problema de investigación]
*Incluye orientaciones para la solución*

[SECCIÓN]
Solucionario y explicaciones
Proporciona todas las respuestas con explicaciones breves del proceso de solución para cada ejercicio.

[SECCIÓN]
Consejos para el estudio
Ofrece estrategias específicas para practicar {topic} de manera efectiva y evitar errores comunes.

INSTRUCCIONES ADICIONALES: {additional_instructions}
"""

def create_evaluation_prompt(topic, grade_level, course, additional_instructions=''):
    """Prompt específico para generar evaluaciones"""
    return f"""
GENERA UNA EVALUACIÓN COMPLETA SOBRE: {topic}
CURSO: {course} | GRADO: {grade_level}

ESTRUCTURA OBLIGATORIA:

[SECCIÓN]
Información de la evaluación
**Datos generales:**
- Asignatura: {course}
- Tema: {topic}
- Grado: {grade_level}
- Duración: 60 minutos
- Puntaje total: 100 puntos
- Competencias evaluadas: [Listar 3-4 competencias específicas]

[SECCIÓN]
Instrucciones para el estudiante
Explica claramente cómo desarrollar la evaluación, criterios de calificación, recomendaciones importantes y distribución del tiempo.

[ACTIVIDAD]
Parte I: Preguntas de selección múltiple
**Valor: 30 puntos (10 preguntas x 3 puntos)**

Desarrolla 10 preguntas de opción múltiple que evalúen:
- Conceptos fundamentales (4 preguntas)
- Aplicación de procedimientos (3 preguntas)
- Análisis de situaciones (3 preguntas)

Cada pregunta debe tener 4 alternativas (a, b, c, d) con una sola respuesta correcta.

[ACTIVIDAD]
Parte II: Preguntas de desarrollo corto
**Valor: 35 puntos**

Crea 5 preguntas que requieran respuestas de 3-5 líneas:
1. [Pregunta sobre definición o concepto] (5 puntos)
2. [Pregunta sobre procedimiento] (7 puntos)
3. [Pregunta sobre aplicación] (8 puntos)
4. [Pregunta sobre análisis] (8 puntos)
5. [Pregunta sobre evaluación/síntesis] (7 puntos)

[ACTIVIDAD]
Parte III: Resolución de problemas
**Valor: 35 puntos**

Diseña 2 problemas complejos que integren múltiples aspectos de {topic}:
- Problema 1: [Situación contextualizada] (15 puntos)
- Problema 2: [Aplicación práctica] (20 puntos)

Cada problema debe incluir criterios específicos de evaluación.

[SECCIÓN]
Solucionario completo
Proporciona las respuestas correctas para todas las preguntas:
- Respuestas de selección múltiple con justificación
- Respuestas modelo para preguntas de desarrollo
- Soluciones paso a paso para los problemas
- Criterios de evaluación específicos

[SECCIÓN]
Rúbrica de calificación
Establece niveles de desempeño:
- Excelente (90-100 puntos)
- Bueno (80-89 puntos)
- Regular (70-79 puntos)
- Insuficiente (0-69 puntos)

Con descriptores específicos para cada nivel.

INSTRUCCIONES ADICIONALES: {additional_instructions}
"""

def create_didactic_material_prompt(topic, grade_level, course, additional_instructions=''):
    """Prompt específico para generar material didáctico"""
    return f"""
GENERA MATERIAL DIDÁCTICO INTERACTIVO SOBRE: {topic}
CURSO: {course} | GRADO: {grade_level}

ESTRUCTURA OBLIGATORIA:

[SECCIÓN]
Presentación del material
**Título:** Material Didáctico - {topic}
**Dirigido a:** Estudiantes de {grade_level}
**Asignatura:** {course}
**Objetivos:** 
- [3-4 objetivos específicos de aprendizaje]
**Duración estimada:** 90 minutos
**Modalidad:** Individual y grupal

[SECCIÓN]
Conocimientos previos
Identifica qué deben saber los estudiantes antes de usar este material y cómo conectar con sus experiencias previas sobre {topic}.

[ACTIVIDAD]
Actividad de inicio: "Descubriendo el tema"
**Duración:** 15 minutos
Diseña una actividad motivadora que despierte curiosidad sobre {topic}:
- Pregunta detonante interesante
- Situación problemática o enigma
- Predicciones sobre el tema
- Lluvia de ideas grupal

[SECCIÓN]
Desarrollo del contenido principal
Explica {topic} de manera clara y estructurada:
- Conceptos fundamentales explicados paso a paso
- Definiciones importantes destacadas
- Propiedades y características principales
- Relaciones con otros conceptos de {course}
(400-500 palabras)

[EJEMPLO]
Ejemplo interactivo 1: Situación real
Presenta un caso práctico donde {topic} sea relevante:
- Contexto familiar para estudiantes de {grade_level}
- Desarrollo paso a paso del ejemplo
- Participación activa del estudiante
- Conexión clara con la teoría

[EJEMPLO]
Ejemplo interactivo 2: Experimento o demostración
Diseña una actividad práctica o experimento simple:
- Materiales necesarios (accesibles)
- Procedimiento claro
- Observaciones esperadas
- Conclusiones guiadas

[ACTIVIDAD]
Taller práctico: "Aplicamos lo aprendido"
**Duración:** 25 minutos
**Modalidad:** Trabajo en parejas
Crea una actividad donde los estudiantes apliquen {topic}:
- Instrucciones paso a paso
- Materiales o recursos necesarios
- Guía de trabajo estructurada
- Criterios de evaluación

[MULTIMEDIA]
Recursos digitales sugeridos
**Video explicativo:**
- Descripción: Video de 8-10 minutos sobre {topic}
- Plataforma sugerida: YouTube Educativo
- Uso: Refuerzo visual del contenido
- Momento de uso: Después de la explicación inicial

**Simulación interactiva:**
- Herramienta digital que permita explorar {topic}
- Función: Experimentar con variables
- Beneficio: Visualización de conceptos abstractos

**Juego educativo:**
- Actividad lúdica relacionada con {topic}
- Objetivo: Reforzar aprendizaje de manera divertida
- Modalidad: Individual o grupal

[ACTIVIDAD]
Proyecto creativo: "Mi propia creación"
**Duración:** 30 minutos
Propone un proyecto donde los estudiantes creen algo original aplicando {topic}:
- Opciones de proyecto (3 alternativas diferentes)
- Recursos y materiales necesarios
- Criterios de evaluación creativos
- Tiempo para presentación grupal

[SECCIÓN]
Consolidación y reflexión
Actividades para cerrar el aprendizaje:
- Síntesis de lo aprendido
- Reflexión personal sobre la utilidad de {topic}
- Conexión con la vida cotidiana
- Preguntas para seguir investigando

[ACTIVIDAD]
Autoevaluación interactiva
Diseña un sistema para que los estudiantes evalúen su propio aprendizaje:
- 5 preguntas de comprensión
- 3 preguntas de aplicación
- 2 preguntas de reflexión personal
- Guía de respuestas para autoverificación

[SECCIÓN]
Recursos adicionales para profundizar
- 3 sitios web educativos recomendados
- 2 videos complementarios
- 1 libro o artículo de consulta
- Apps educativas relacionadas con {topic}
- Sugerencias para proyectos de investigación

INSTRUCCIONES ADICIONALES: {additional_instructions}
"""

def create_summary_prompt(topic, grade_level, course, additional_instructions=''):
    """Prompt específico para generar resúmenes"""
    return f"""
GENERA UN RESUMEN COMPLETO SOBRE: {topic}
CURSO: {course} | GRADO: {grade_level}

ESTRUCTURA OBLIGATORIA:

[SECCIÓN]
Introducción al resumen
Explica brevemente qué es {topic}, su importancia en {course} y qué aprenderán los estudiantes con este resumen. (100-120 palabras)

[SECCIÓN]
Conceptos clave
**Definiciones fundamentales:**
Presenta los 5-7 conceptos más importantes de {topic} de forma clara y concisa:
- Concepto 1: [Definición y explicación breve]
- Concepto 2: [Definición y explicación breve]
- Concepto 3: [Definición y explicación breve]
[...continuar según corresponda]

[SECCIÓN]
Ideas principales
Organiza las ideas más importantes sobre {topic} en puntos claros:
- Punto principal 1: [Idea central con explicación breve]
- Punto principal 2: [Idea central con explicación breve]
- Punto principal 3: [Idea central con explicación breve]
- Punto principal 4: [Idea central con explicación breve]

[EJEMPLO]
Ejemplo representativo
Presenta un ejemplo que ilustre claramente los conceptos principales de {topic}:
- Situación o problema típico
- Aplicación de los conceptos
- Resultado o solución
- Por qué este ejemplo es representativo

[SECCIÓN]
Puntos importantes a recordar
Lista los aspectos críticos que los estudiantes deben memorizar sobre {topic}:
- 5-7 puntos clave ordenados por importancia
- Consejos para recordar mejor la información
- Errores comunes a evitar

[SECCIÓN]
Aplicaciones prácticas
Menciona 3-4 situaciones donde {topic} se aplica en la vida real o en otras materias:
- Aplicación 1: [Descripción breve]
- Aplicación 2: [Descripción breve]
- Aplicación 3: [Descripción breve]

[ACTIVIDAD]
Repaso rápido
Crea 5 preguntas cortas para que los estudiantes verifiquen si comprendieron el resumen:
1. [Pregunta sobre concepto básico]
2. [Pregunta sobre aplicación]
3. [Pregunta sobre relación entre conceptos]
4. [Pregunta sobre ejemplo práctico]
5. [Pregunta de síntesis]

*Incluye las respuestas al final*

[SECCIÓN]
Para seguir aprendiendo
Sugiere recursos adicionales para profundizar en {topic}:
- 2 sitios web educativos
- 1 video explicativo recomendado
- 1 libro de consulta
- Temas relacionados para investigar

INSTRUCCIONES ADICIONALES: {additional_instructions}
"""

def get_enhanced_content_prompts():
    """
    Devuelve plantillas mejoradas para diferentes tipos de contenido con estructura específica.
    """
    return {
        'plan_sesion': {
            'name': 'Plan de Sesión de Clase',
            'template': """
[TÍTULO]
Plan de Sesión: {topic} para {grade_level}

[SUBTÍTULO]
Información General de la Sesión

[PÁRRAFO]
Descripción detallada de la sesión, objetivos generales, duración, y metodología a utilizar...

[SUBTÍTULO]
Objetivos de Aprendizaje

[PÁRRAFO]
Listado de 3-5 objetivos específicos que los estudiantes lograrán al finalizar la sesión...

[SUBTÍTULO]
Materiales y Recursos Necesarios

[PÁRRAFO]
Lista detallada de todos los materiales, recursos tecnológicos, y espacios requeridos...

[SUBTÍTULO]
Actividad de Inicio (10-15 minutos)

[ACTIVIDAD]
**Actividad de Motivación:**
[Descripción completa de la actividad inicial]

[SUBTÍTULO]
Desarrollo del Tema (25-30 minutos)

[PÁRRAFO]
Explicación detallada de los conceptos principales...

[EJEMPLO]
**Ejemplo Demostrativo:**
[Ejemplo paso a paso que el profesor desarrollará]

[SUBTÍTULO]  
Actividad Práctica (15-20 minutos)

[ACTIVIDAD]
**Actividad de Aplicación:**
[Actividad para que los estudiantes practiquen]

[SUBTÍTULO]
Recursos Multimedia de Apoyo

[MULTIMEDIA]
[Mínimo 3 recursos multimedia para esta sesión]

[SUBTÍTULO]
Evaluación y Cierre (5-10 minutos)

[EVALUACIÓN]
Criterios de evaluación para esta sesión...

[SUBTÍTULO]
Tarea para Casa

[ACTIVIDAD]
**Tarea de Refuerzo:**
[Actividad para realizar en casa]
"""
        },
        
        'material_apoyo': {
            'name': 'Material de Apoyo Integrado',
            'template': """
[TÍTULO]
Guía de Estudio: {topic}

[SUBTÍTULO]
Introducción al Tema

[PÁRRAFO]
Introducción motivadora que conecte el tema con la vida real de los estudiantes...

[SUBTÍTULO]
Conceptos Fundamentales

[PÁRRAFO]
Definiciones y explicaciones de los conceptos clave...

[SUBTÍTULO]
Desarrollo Teórico

[PÁRRAFO]
Explicación detallada de la teoría y principios...

[EJEMPLO]
**Ejemplo 1:**
[Primer ejemplo resuelto paso a paso]

[EJEMPLO]
**Ejemplo 2:**  
[Segundo ejemplo con variación]

[SUBTÍTULO]
Aplicaciones Prácticas

[PÁRRAFO]
Cómo se aplica este conocimiento en situaciones reales...

[EJEMPLO]
**Ejemplo de Aplicación:**
[Ejemplo contextualizado en la vida real]

[SUBTÍTULO]
Recursos Multimedia Complementarios

[MULTIMEDIA]
[Mínimo 8 recursos multimedia variados]

[SUBTÍTULO]
Actividades de Refuerzo

[ACTIVIDAD]
**Actividad 1:**
[Primera actividad de práctica]

[ACTIVIDAD]
**Actividad 2:**
[Segunda actividad más compleja]

[SUBTÍTULO]
Autoevaluación

[EVALUACIÓN]
Preguntas y criterios para que el estudiante evalúe su comprensión...
"""
        },
        
        'guia_ejercicios': {
            'name': 'Guía de Ejercicios y Problemas',
            'template': """
[TÍTULO]
Guía de Ejercicios: {topic}

[SUBTÍTULO]
Instrucciones Generales

[PÁRRAFO]
Indicaciones sobre cómo abordar los ejercicios y estrategias de resolución...

[SUBTÍTULO]
Repaso de Conceptos Clave

[PÁRRAFO]
Breve repaso de los conceptos necesarios para resolver los ejercicios...

[SUBTÍTULO]
Ejercicios Nivel Básico

[EJEMPLO]
**Ejercicio Modelo 1:**
[Ejercicio resuelto completamente]

[ACTIVIDAD]
**Ejercicios para Resolver:**
[2-3 ejercicios básicos para practicar]

[SUBTÍTULO]
Ejercicios Nivel Intermedio

[EJEMPLO]  
**Ejercicio Modelo 2:**
[Ejercicio más complejo resuelto]

[ACTIVIDAD]
**Ejercicios Intermedios:**
[2-3 ejercicios de nivel medio]

[SUBTÍTULO]
Problemas Nivel Avanzado

[EJEMPLO]
**Problema Modelo:**
[Problema complejo con solución detallada]

[ACTIVIDAD]
**Problemas Desafiantes:**
[1-2 problemas complejos]

[SUBTÍTULO]
Problema de Aplicación Real

[EJEMPLO]
**Situación Real:**
[Problema contextualizado en la vida real]

[ACTIVIDAD]
**Análisis del Problema:**
[Actividad de análisis y reflexión]

[SUBTÍTULO]
Recursos de Apoyo

[MULTIMEDIA]
[Recursos para profundizar y practicar más]

[SUBTÍTULO]
Criterios de Evaluación

[EVALUACIÓN]
Rúbrica para evaluar la resolución de problemas...
"""
        },
        
        'evaluacion_completa': {
            'name': 'Evaluación Completa',
            'template': """
[TÍTULO]
Evaluación: {topic}

[SUBTÍTULO]
Información de la Evaluación

[PÁRRAFO]
Instrucciones generales, tiempo, puntaje total, y criterios de evaluación...

[SUBTÍTULO]
Sección I: Preguntas de Selección Múltiple

[ACTIVIDAD]
**Preguntas de Alternativas:**
[3-5 preguntas con alternativas múltiples]

[SUBTÍTULO]
Sección II: Preguntas de Respuesta Corta

[ACTIVIDAD]
**Preguntas Breves:**
[3-4 preguntas que requieren respuestas cortas]

[SUBTÍTULO]
Sección III: Preguntas de Desarrollo

[ACTIVIDAD]
**Problemas de Desarrollo:**
[2-3 problemas que requieren desarrollo completo]

[SUBTÍTULO]
Sección IV: Problema de Aplicación

[EJEMPLO]
**Situación Contextualizada:**
[Problema aplicado a una situación real]

[ACTIVIDAD]
**Análisis y Resolución:**
[Preguntas sobre el problema planteado]

[SUBTÍTULO]
Pauta de Evaluación

[EVALUACIÓN]
Rúbrica detallada con criterios de corrección...

[SUBTÍTULO]
Recursos Permitidos

[PÁRRAFO]
Lista de materiales y recursos que el estudiante puede usar durante la evaluación...

[SUBTÍTULO]
Actividades de Refuerzo Post-Evaluación

[MULTIMEDIA]
[Recursos para estudiantes que necesiten refuerzo]
"""
        },
        
        'material_didactico': {
            'name': 'Material Didáctico Interactivo',
            'template': """
[TÍTULO]
Material Interactivo: {topic}

[SUBTÍTULO]
¡Bienvenido a la Aventura del Aprendizaje!

[PÁRRAFO]
Introducción motivadora y objetivos de aprendizaje presentados de forma atractiva...

[SUBTÍTULO]
Actividad de Exploración Inicial

[ACTIVIDAD]
**¡Descubramos Juntos!**
[Actividad exploratoria para despertar la curiosidad]

[SUBTÍTULO]
Fundamentos del Tema

[PÁRRAFO]
Explicación de conceptos básicos con analogías y ejemplos cotidianos...

[SUBTÍTULO]
Laboratorio Virtual

[MULTIMEDIA]
[Simulaciones y laboratorios virtuales]

[SUBTÍTULO]
Ejemplos Interactivos

[EJEMPLO]
**Ejemplo Paso a Paso:**
[Ejemplo con elementos interactivos]

[EJEMPLO]
**Tu Turno de Intentar:**
[Ejemplo guiado para que el estudiante participe]

[SUBTÍTULO]
Actividades Prácticas

[ACTIVIDAD]
**Actividad Colaborativa:**
[Actividad para realizar en grupos]

[ACTIVIDAD]
**Proyecto Personal:**
[Actividad individual creativa]

[SUBTÍTULO]
Galería Multimedia

[MULTIMEDIA]
[Colección variada de recursos multimedia]

[SUBTÍTULO]
Verifica Tu Aprendizaje

[EVALUACIÓN]
Autoevaluación interactiva con retroalimentación inmediata...

[SUBTÍTULO]
¡Lleva Tu Aprendizaje Más Allá!

[ACTIVIDAD]
**Proyecto de Extensión:**
[Actividad opcional para profundizar]

[MULTIMEDIA]
[Recursos adicionales para explorar]
"""
        }
    } 