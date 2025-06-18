"""
Utilidades para crear prompts para generación de contenido
"""

PROMPT_TEMPLATES = {
    "explanation": """ ... """,  # Aquí tu plantilla completa
    "exercises": """ ... """,
    "evaluation": """ ... """,
    "didactic_material": """ ... """,
    "summary": """ ... """
}

def create_content_prompt(content_type_id, topic, grade_level, course, additional_instructions=''):
    template_keys = {
        1: "explanation",
        2: "exercises",
        3: "evaluation",
        4: "didactic_material",
        5: "summary"
    }
    template_key = template_keys.get(content_type_id, "didactic_material")
    return PROMPT_TEMPLATES[template_key].format(
        topic=topic,
        grade_level=grade_level,
        course=course,
        additional_instructions=additional_instructions
    )

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
