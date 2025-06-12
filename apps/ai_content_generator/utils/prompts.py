"""
Utilidades para crear prompts para generación de contenido
"""

def create_content_prompt(content_type_id, topic, grade_level, course, additional_instructions=''):
    """
    Crea un prompt ULTRA ESPECÍFICO para generar contenido educativo COMPLETO
    """
    
    # Mapear el content_type_id
    content_type_map = {
        1: 'plan_sesion',
        2: 'material_apoyo',
        3: 'guia_ejercicios',
        4: 'evaluacion_completa',
        5: 'material_didactico'
    }
    
    if isinstance(content_type_id, str):
        if content_type_id.lower() == 'plan de sesión de clase':
            content_type_id = 1
        elif content_type_id.lower() == 'material de apoyo integrado':
            content_type_id = 2
        elif content_type_id.lower() == 'guía de ejercicios y problemas':
            content_type_id = 3
        elif content_type_id.lower() == 'evaluación completa':
            content_type_id = 4
        elif content_type_id.lower() == 'material didáctico interactivo':
            content_type_id = 5
    
    content_type_key = content_type_map.get(content_type_id, 'material_apoyo')
    
    # Prompt súper específico y directo
    prompt = f"""GENERADOR DE CONTENIDO EDUCATIVO PROFESIONAL

TEMA: {topic}
CURSO: {course} 
GRADO: {grade_level}
TIPO: {"Plan de Sesión" if content_type_key == "plan_sesion" else "Material de Apoyo"}

REGLAS CRÍTICAS DE CONTENIDO:
❌ PROHIBIDO ABSOLUTO: Código JavaScript, HTML con <script>, programación, iframes
❌ PROHIBIDO: Frases como "Aquí están las secciones faltantes", "para alcanzar los requisitos"
❌ PROHIBIDO: Elementos técnicos de desarrollo web, APIs, código de programación
❌ PROHIBIDO: Contenido meta-educativo (referencias al proceso de creación)

✅ GENERAR ÚNICAMENTE:
- Contenido educativo directo sobre {topic}
- Material pedagógico apropiado para {grade_level}
- Ejemplos prácticos y actividades educativas
- Recursos multimedia educativos (descripciones, NO código)

INSTRUCCIONES OBLIGATORIAS - SEGUIR AL PIE DE LA LETRA:

1. USA EXACTAMENTE ESTOS MARCADORES: [TÍTULO], [SUBTÍTULO], [PÁRRAFO], [EJEMPLO], [ACTIVIDAD], [MULTIMEDIA], [EVALUACIÓN]

2. ESTRUCTURA EXACTA A SEGUIR:

[TÍTULO]
{topic} - {"Plan de Sesión" if content_type_key == "plan_sesion" else "Material de Apoyo"} para {grade_level}

[SUBTÍTULO]
Introducción y Contextualización

[PÁRRAFO]
Escribe aquí una explicación EXTENSA de 300+ palabras sobre {topic}, incluyendo: definición completa, importancia en {course}, aplicaciones en la vida real, conexiones con otros temas, metodología de enseñanza, y objetivos específicos. Incluye ejemplos cotidianos que los estudiantes de {grade_level} puedan relacionar fácilmente...

[SUBTÍTULO]
Conceptos Fundamentales

[PÁRRAFO]
Desarrolla aquí los conceptos clave de {topic} en 300+ palabras, incluyendo: definiciones técnicas, propiedades principales, características distintivas, clasificación si aplica, terminología específica del tema. Usa lenguaje apropiado para {grade_level} pero mantén rigor académico...

[EJEMPLO]
**Ejemplo Práctico 1: Situación Cotidiana**
- **Contexto:** Presenta una situación real donde se aplique {topic}
- **Datos:** Lista los datos conocidos del problema
- **Proceso:** Muestra paso a paso la solución (mínimo 5 pasos)
- **Resultado:** Explica el resultado y su significado práctico
- **Reflexión:** Conecta este ejemplo con la vida diaria del estudiante

[EJEMPLO]
**Ejemplo Práctico 2: Aplicación Tecnológica**
- **Contexto:** Situación donde {topic} se use en tecnología o ciencia
- **Desarrollo:** Proceso completo de resolución
- **Análisis:** Interpretación de resultados
- **Aplicación:** Cómo se usa en el mundo real

[EJEMPLO]
**Ejemplo Práctico 3: Problema Académico**
- **Enunciado:** Problema típico de {course} nivel {grade_level}
- **Estrategia:** Método de resolución recomendado
- **Solución:** Desarrollo completo paso a paso
- **Verificación:** Comprobación del resultado

[SUBTÍTULO]
Desarrollo Metodológico

[PÁRRAFO]
Explica en 300+ palabras las estrategias metodológicas para enseñar {topic}, incluyendo: técnicas didácticas específicas, recursos recomendados, secuencia de actividades, adaptaciones para diferentes estilos de aprendizaje, evaluación formativa durante el proceso...

[ACTIVIDAD]
**Actividad 1: Exploración Inicial**
- **Objetivo:** Despertar interés y explorar conocimientos previos sobre {topic}
- **Duración:** 15-20 minutos
- **Modalidad:** Individual/Grupal
- **Materiales:** Lista específica de materiales necesarios
- **Desarrollo:** Instrucciones paso a paso detalladas (mínimo 8 pasos)
- **Evaluación:** Criterios específicos de evaluación
- **Adaptaciones:** Sugerencias para estudiantes con necesidades especiales

[ACTIVIDAD]
**Actividad 2: Práctica Guiada**
- **Objetivo:** Aplicar conceptos básicos de {topic} con acompañamiento
- **Duración:** 25-30 minutos
- **Modalidad:** Parejas
- **Recursos:** Materiales y herramientas necesarias
- **Instrucciones:** Pasos detallados para realizar la actividad
- **Seguimiento:** Cómo monitorear el progreso
- **Retroalimentación:** Estrategias de feedback inmediato

[ACTIVIDAD]
**Actividad 3: Aplicación Independiente**
- **Objetivo:** Demostrar dominio autónomo de {topic}
- **Duración:** 20-25 minutos
- **Modalidad:** Individual
- **Desafío:** Problema o situación desafiante
- **Criterios:** Estándares de calidad esperados
- **Extensión:** Actividades adicionales para estudiantes avanzados

[SUBTÍTULO]
Recursos Multimedia y Tecnológicos

[MULTIMEDIA]
**Video Tutorial 1:** "Fundamentos de {topic}"
- **Plataforma:** YouTube/Khan Academy
- **Duración:** 8-12 minutos
- **Descripción:** Video explicativo que cubre conceptos básicos de {topic} con animaciones y ejemplos visuales apropiados para estudiantes de {grade_level}
- **Uso sugerido:** Introducción al tema o repaso individual
- **Enlace sugerido:** Buscar "{topic} básico {grade_level}" en YouTube

[MULTIMEDIA]
**Simulación Interactiva 1:** "Laboratorio Virtual de {topic}"
- **Plataforma:** PhET/GeoGebra
- **Tipo:** Simulación interactiva
- **Descripción:** Herramienta que permite a los estudiantes experimentar con variables de {topic} y observar cambios en tiempo real
- **Aplicación:** Exploración de conceptos y verificación de hipótesis
- **Instrucciones:** Pasos específicos para usar la simulación en clase

[MULTIMEDIA]
**App Educativa 1:** "Ejercicios de {topic}"
- **Plataforma:** Móvil/Tablet
- **Funcionalidad:** Aplicación con ejercicios graduados y retroalimentación inmediata
- **Beneficios:** Práctica personalizada y seguimiento del progreso
- **Recomendación:** Uso en casa para refuerzo
- **Características:** Ejercicios adaptativos, reportes de progreso, gamificación

[MULTIMEDIA]
**Podcast Educativo:** "{topic} en la Vida Real"
- **Duración:** 15-20 minutos
- **Contenido:** Entrevistas con profesionales que usan {topic} en su trabajo
- **Objetivo:** Mostrar aplicaciones prácticas y motivar el aprendizaje
- **Uso:** Actividad de escucha y reflexión
- **Seguimiento:** Preguntas de comprensión y debate

[MULTIMEDIA]
**Juego Interactivo:** "Desafío {topic}"
- **Plataforma:** Kahoot/Quizizz
- **Modalidad:** Competencia grupal
- **Descripción:** Preguntas de opción múltiple sobre {topic} con elementos de gamificación
- **Duración:** 10-15 minutos
- **Propósito:** Evaluación formativa divertida y revisión de conceptos

[EJEMPLO]
**Ejemplo Integrador 4: Proyecto Interdisciplinario**
- **Conexión:** Cómo {topic} se relaciona con otras materias
- **Desarrollo:** Proyecto que integra {topic} con ciencias/historia/arte
- **Duración:** Proyecto de varias semanas
- **Producto:** Entregable concreto (informe, presentación, modelo)
- **Evaluación:** Rúbrica específica para el proyecto

[EJEMPLO]
**Ejemplo Evaluativo 5: Situación de Examen**
- **Tipo:** Problema típico de evaluación formal
- **Complejidad:** Nivel apropiado para {grade_level}
- **Solución:** Desarrollo completo con justificación
- **Variantes:** Diferentes formas de plantear el mismo concepto
- **Criterios:** Cómo evaluar la respuesta del estudiante

[SUBTÍTULO]
Estrategias de Evaluación

[EVALUACIÓN]
**Evaluación Formativa Continua:**
- **Técnicas:** Observación directa, preguntas orales, revisión de ejercicios
- **Frecuencia:** Durante toda la sesión/unidad
- **Instrumentos:** Listas de cotejo, escalas de valoración, rúbricas simples
- **Retroalimentación:** Inmediata y específica sobre fortalezas y áreas de mejora
- **Ajustes:** Modificaciones en tiempo real según necesidades observadas

**Evaluación Sumativa:**
- **Instrumentos:** Prueba escrita, proyecto final, presentación oral
- **Criterios:** Comprensión conceptual, aplicación práctica, resolución de problemas
- **Ponderación:** Sugerencias de peso para cada componente
- **Rúbrica:** Niveles de desempeño (excelente, bueno, satisfactorio, necesita mejora)
- **Remediales:** Estrategias para estudiantes que no alcancen el estándar

[ACTIVIDAD]
**Actividad 4: Síntesis y Metacognición**
- **Objetivo:** Reflexionar sobre el aprendizaje de {topic}
- **Estrategia:** Diario de aprendizaje, mapas conceptuales, discusión grupal
- **Preguntas guía:** ¿Qué aprendí? ¿Cómo lo aprendí? ¿Para qué me sirve?
- **Tiempo:** 15 minutos
- **Producto:** Reflexión escrita o oral sobre el proceso de aprendizaje

[ACTIVIDAD]
**Actividad 5: Aplicación Creativa**
- **Objetivo:** Demostrar comprensión de {topic} de manera creativa
- **Opciones:** Crear un cómic, video, canción, o infografía sobre {topic}
- **Criterios:** Precisión conceptual, creatividad, claridad comunicativa
- **Tiempo:** 30-45 minutos
- **Presentación:** Compartir creaciones con la clase para retroalimentación

[SUBTÍTULO]
Recursos Adicionales y Profundización

[MULTIMEDIA]
**Documentos PDF:** "Guías de Estudio de {topic}"
- **Contenido:** Resúmenes, esquemas, ejercicios adicionales
- **Acceso:** Repositorio digital de la institución
- **Uso:** Estudio independiente y repaso
- **Actualización:** Revisión semestral de contenidos

[MULTIMEDIA]
**Plataforma LMS:** "Aula Virtual de {course}"
- **Funciones:** Foros de discusión, tareas en línea, recursos digitales
- **Actividades:** Debates sobre aplicaciones de {topic}, proyectos colaborativos
- **Seguimiento:** Analíticas de participación y progreso
- **Comunicación:** Mensajería directa con el docente

[MULTIMEDIA]
**Canal YouTube:** "Matemáticas para {grade_level}"
- **Contenido:** Tutoriales específicos, resolución de ejercicios tipo
- **Organización:** Playlists por tema y nivel de dificultad
- **Interacción:** Comentarios para resolver dudas
- **Actualización:** Videos nuevos semanalmente

[MULTIMEDIA]
**Biblioteca Digital:** "Recursos de {topic}"
- **Acceso:** E-books, artículos académicos adaptados, investigaciones recientes
- **Organización:** Por nivel de complejidad y área de aplicación
- **Citas:** APA format para fomentar investigación académica
- **Multilengua:** Recursos en español e inglés para ampliar perspectivas

[MULTIMEDIA]
**Realidad Aumentada:** "Visualizador de {topic}"
- **Tecnología:** Apps de AR para smartphones/tablets
- **Funcionalidad:** Modelos 3D, visualizaciones interactivas
- **Aplicación:** Hacer tangible conceptos abstractos de {topic}
- **Requisitos:** Dispositivos compatibles, descarga de apps específicas

[SUBTÍTULO]
Extensión y Conexiones Curriculares

[PÁRRAFO]
{topic} se conecta profundamente con múltiples áreas del conocimiento, creando oportunidades de aprendizaje interdisciplinario. En ciencias naturales, se aplica en el análisis de fenómenos físicos y químicos. En ciencias sociales, ayuda a interpretar datos estadísticos y tendencias económicas. En arte, se utiliza para crear proporciones y diseños armónicos. Esta transversalidad permite a los estudiantes de {grade_level} comprender que {topic} no es una materia aislada, sino una herramienta fundamental para entender y transformar el mundo. Las conexiones curriculares incluyen proyectos que integran {topic} con literatura (análisis de textos mediante patrones), educación física (cálculos de rendimiento), y tecnología (programación de algoritmos). Estas conexiones fortalecen la comprensión conceptual y demuestran la relevancia práctica del conocimiento matemático en la vida cotidiana y profesional...

INSTRUCCIONES ADICIONALES:
{additional_instructions}

RECORDATORIOS FINALES:
- Genera TODO el contenido usando EXACTAMENTE los marcadores mostrados
- Cada [PÁRRAFO] debe tener MÍNIMO 250 palabras
- Cada [EJEMPLO] debe ser COMPLETO y DETALLADO
- Cada [ACTIVIDAD] debe tener INSTRUCCIONES PASO A PASO
- Cada [MULTIMEDIA] debe tener DESCRIPCIÓN COMPLETA de uso
- NO omitas ninguna sección, genera TODO el contenido solicitado"""
    
    return prompt

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