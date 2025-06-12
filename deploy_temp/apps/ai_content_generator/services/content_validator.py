"""
Validador de contenido para evitar fallos en generación
"""

class ContentValidator:
    """Valida y ajusta automáticamente el contenido para evitar fallos"""
    
    @staticmethod
    def validate_and_adjust_request(topic, course, grade_level, additional_instructions=""):
        """
        Valida y ajusta automáticamente una solicitud de contenido para evitar fallos
        
        Args:
            topic: Tema original
            course: Curso original
            grade_level: Grado original
            additional_instructions: Instrucciones adicionales
            
        Returns:
            dict: Contenido validado y ajustado
        """
        
        # 1. Normalizar nivel educativo a secundaria
        adjusted_grade = ContentValidator._normalize_grade_to_secondary(grade_level)
        
        # 2. Ajustar tema para que sea específico del curso
        adjusted_topic = ContentValidator._adjust_topic_for_course(topic, course)
        
        # 3. Mejorar instrucciones para evitar fallos
        adjusted_instructions = ContentValidator._enhance_instructions(
            adjusted_topic, course, adjusted_grade, additional_instructions
        )
        
        return {
            'topic': adjusted_topic,
            'course': course,
            'grade_level': adjusted_grade,
            'additional_instructions': adjusted_instructions,
            'validation_notes': ContentValidator._get_validation_notes(topic, adjusted_topic, grade_level, adjusted_grade)
        }
    
    @staticmethod
    def _normalize_grade_to_secondary(grade_level):
        """Normaliza cualquier grado a secundaria"""
        grade_mapping = {
            'PRIMERO': '1° Secundaria',
            'SEGUNDO': '2° Secundaria', 
            'TERCERO': '3° Secundaria',
            'CUARTO': '4° Secundaria',
            'QUINTO': '5° Secundaria',
            '1°': '1° Secundaria',
            '2°': '2° Secundaria',
            '3°': '3° Secundaria',
            '4°': '4° Secundaria',
            '5°': '5° Secundaria',
            'PRIMER': '1° Secundaria',
            'PRIMER GRADO': '1° Secundaria',
            'PRIMERA': '1° Secundaria',
        }
        
        # Buscar coincidencias
        for key, value in grade_mapping.items():
            if key.upper() in grade_level.upper():
                return value
                
        # Si no encuentra coincidencia, asumir 3° Secundaria como default
        return '3° Secundaria'
    
    @staticmethod
    def _adjust_topic_for_course(topic, course):
        """Ajusta el tema para que sea específico del curso"""
        
        course_adjustments = {
            'MATEMATICA': {
                'keywords': ['alimentación', 'saludable', 'nutrición', 'dieta', 'comida'],
                'adjustment': 'Matemáticas aplicadas a la nutrición y alimentación saludable'
            },
            'COMUNICACION': {
                'keywords': ['números', 'cálculos', 'estadísticas', 'gráficos'],
                'adjustment': 'Comunicación efectiva sobre'
            },
            'CIENCIA': {
                'keywords': ['literatura', 'redacción', 'escritura', 'lectura'],
                'adjustment': 'Fundamentos científicos de'
            },
            'HISTORIA': {
                'keywords': ['experimentos', 'laboratorio', 'química', 'física'],
                'adjustment': 'Historia y evolución de'
            }
        }
        
        course_upper = course.upper()
        
        # Si el tema ya incluye matemática, retornarlo tal como está
        if any(word in topic.lower() for word in ['matemática', 'matemáticas', 'math', 'números', 'cálculo']):
            return topic
            
        # Verificar si necesita ajuste
        if course_upper in course_adjustments:
            config = course_adjustments[course_upper]
            topic_lower = topic.lower()
            
            # Si el tema contiene keywords que no coinciden con el curso
            if any(keyword in topic_lower for keyword in config['keywords']):
                return f"{config['adjustment']}: {topic}"
        
        # Si es matemática y el tema no parece matemático, ajustar
        if course_upper == 'MATEMATICA' and not any(word in topic.lower() for word in ['matemática', 'números', 'cálculo', 'estadística', 'geometría', 'álgebra']):
            return f"Aplicaciones matemáticas en: {topic}"
            
        return topic
    
    @staticmethod
    def _enhance_instructions(topic, course, grade_level, original_instructions):
        """Mejora las instrucciones para evitar fallos"""
        
        enhanced = f"""
{original_instructions}

🎯 CONFIGURACIÓN OPTIMIZADA PARA EVITAR FALLOS:

TEMA AJUSTADO: {topic}
CURSO: {course} 
NIVEL: {grade_level} (EDUCACIÓN SECUNDARIA)

INSTRUCCIONES ESPECÍFICAS PARA GENERACIÓN EXITOSA:

1. **NIVEL EDUCATIVO FIJO**: Todo el contenido debe ser para estudiantes de {grade_level}
2. **MATERIA ESPECÍFICA**: Enfocar completamente en {course}
3. **CONTENIDO EXTENSO**: Generar mínimo 5000 palabras de contenido sustantivo
4. **RECURSOS MULTIMEDIA**: Incluir mínimo 15 recursos multimedia detallados
5. **SIN RESTRICCIONES DE TIEMPO**: Tomar el tiempo necesario para contenido completo

ESTRUCTURA OBLIGATORIA - USA EXACTAMENTE ESTOS MARCADORES:
[TÍTULO], [SUBTÍTULO], [PÁRRAFO], [EJEMPLO], [ACTIVIDAD], [MULTIMEDIA], [EVALUACIÓN]

VALIDACIONES AUTOMÁTICAS:
✅ Contenido apropiado para secundaria (12-17 años)
✅ Alineado con currículo de {course}
✅ Mínimo 400 palabras por [PÁRRAFO]
✅ Mínimo 150 palabras por [MULTIMEDIA]
✅ Aplicaciones en tecnología moderna y vida cotidiana
✅ Ejemplos relevantes para adolescentes

IMPORTANTE: Si hay conflicto entre tema y materia, PRIORIZA LA MATERIA ({course}) y encuentra conexiones creativas.
"""
        
        return enhanced
    
    @staticmethod
    def _get_validation_notes(original_topic, adjusted_topic, original_grade, adjusted_grade):
        """Genera notas de validación para debugging"""
        notes = []
        
        if original_topic != adjusted_topic:
            notes.append(f"Tema ajustado: '{original_topic}' → '{adjusted_topic}'")
            
        if original_grade != adjusted_grade:
            notes.append(f"Grado normalizado: '{original_grade}' → '{adjusted_grade}'")
            
        return "; ".join(notes) if notes else "Sin ajustes necesarios"

    @staticmethod
    def validate_content_compatibility(topic, course):
        """Valida si un tema es compatible con un curso específico"""
        
        compatibility_matrix = {
            'MATEMATICA': [
                'números', 'cálculo', 'estadística', 'geometría', 'álgebra', 
                'trigonometría', 'probabilidad', 'gráficos', 'datos', 'medidas',
                'porcentajes', 'fracciones', 'funciones', 'ecuaciones'
            ],
            'COMUNICACION': [
                'lectura', 'escritura', 'literatura', 'redacción', 'gramática',
                'ortografía', 'comprensión', 'texto', 'narración', 'diálogo',
                'comunicación', 'expresión', 'lenguaje'
            ],
            'CIENCIA': [
                'experimento', 'laboratorio', 'química', 'física', 'biología',
                'científico', 'investigación', 'método', 'hipótesis', 'teoría',
                'célula', 'átomo', 'energía', 'materia'
            ],
            'HISTORIA': [
                'histórico', 'pasado', 'época', 'periodo', 'civilización',
                'cultura', 'sociedad', 'país', 'guerra', 'revolución',
                'descubrimiento', 'conquista', 'independencia'
            ]
        }
        
        course_keywords = compatibility_matrix.get(course.upper(), [])
        topic_lower = topic.lower()
        
        # Verificar compatibilidad directa
        direct_match = any(keyword in topic_lower for keyword in course_keywords)
        
        return {
            'is_compatible': direct_match,
            'compatibility_score': sum(1 for keyword in course_keywords if keyword in topic_lower),
            'suggested_connections': ContentValidator._suggest_connections(topic, course)
        }
    
    @staticmethod
    def _suggest_connections(topic, course):
        """Sugiere conexiones entre tema y curso"""
        
        connections = {
            'MATEMATICA': {
                'alimentación': 'cálculo de calorías, porcentajes nutricionales, estadísticas de consumo',
                'salud': 'análisis de datos médicos, gráficos de crecimiento, IMC',
                'medio ambiente': 'estadísticas ambientales, geometría en arquitectura sostenible',
                'tecnología': 'algoritmos, programación, análisis de datos'
            },
            'COMUNICACION': {
                'matemática': 'comunicación de resultados matemáticos, redacción de informes',
                'ciencia': 'comunicación científica, reportes de experimentos',
                'alimentación': 'campañas de comunicación sobre nutrición',
                'historia': 'narrativas históricas, análisis de textos históricos'
            }
        }
        
        course_connections = connections.get(course.upper(), {})
        topic_lower = topic.lower()
        
        for key, connection in course_connections.items():
            if key in topic_lower:
                return connection
                
        return f"Análisis interdisciplinario desde la perspectiva de {course}" 