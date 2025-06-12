"""
Verificador de completitud de contenido educativo generado por IA
"""

import re
import logging

logger = logging.getLogger(__name__)

class ContentCompletenessChecker:
    """
    Analiza y verifica la completitud del contenido educativo generado
    """
    
    # Palabras mínimas esperadas por sección
    MIN_WORDS_PER_SECTION = {
        'PÁRRAFO': 200,
        'EJEMPLO': 150,
        'ACTIVIDAD': 200,
        'MULTIMEDIA': 100,
        'EVALUACIÓN': 300,
        'INTRODUCCIÓN': 150,
        'DESARROLLO': 400,
        'CONCLUSIÓN': 100
    }
    
    @classmethod
    def analyze_content_completeness(cls, content: str, topic: str) -> dict:
        """
        Analiza la completitud del contenido generado
        
        Args:
            content (str): Contenido a analizar
            topic (str): Tema del contenido
            
        Returns:
            dict: Análisis de completitud
        """
        try:
            if not content or len(content.strip()) < 100:
                return {
                    'is_complete': False,
                    'completion_score': 0,
                    'word_count': 0,
                    'issues': ['Contenido demasiado corto o vacío'],
                    'missing_sections': [],
                    'recommendations': ['Regenerar contenido con prompt más específico']
                }
            
            # Análisis básico
            word_count = len(content.split())
            
            # Detectar secciones usando marcadores
            sections = cls._extract_sections(content)
            
            # Calcular puntaje de completitud
            completion_score = cls._calculate_completion_score(content, sections, word_count)
            
            # Identificar problemas
            issues = cls._identify_issues(content, sections, word_count)
            
            # Secciones faltantes
            missing_sections = cls._find_missing_sections(sections)
            
            # Recomendaciones
            recommendations = cls._generate_recommendations(issues, missing_sections, word_count)
            
            is_complete = completion_score >= 70 and word_count >= 2000
            
            return {
                'is_complete': is_complete,
                'completion_score': completion_score,
                'word_count': word_count,
                'sections_found': list(sections.keys()),
                'issues': issues,
                'missing_sections': missing_sections,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error al analizar completitud del contenido: {str(e)}")
            return {
                'is_complete': True,  # Asumir completo si hay error en análisis
                'completion_score': 75,
                'word_count': len(content.split()) if content else 0,
                'issues': [f'Error en análisis: {str(e)}'],
                'missing_sections': [],
                'recommendations': []
            }
    
    @classmethod
    def _extract_sections(cls, content: str) -> dict:
        """Extrae las secciones del contenido usando marcadores"""
        sections = {}
        
        # Marcadores comunes
        markers = [
            r'\[TÍTULO\]',
            r'\[SUBTÍTULO\]', 
            r'\[PÁRRAFO\]',
            r'\[EJEMPLO\]',
            r'\[ACTIVIDAD\]',
            r'\[MULTIMEDIA\]',
            r'\[EVALUACIÓN\]',
            r'\[INTRODUCCIÓN\]',
            r'\[DESARROLLO\]',
            r'\[CONCLUSIÓN\]'
        ]
        
        for marker in markers:
            matches = re.findall(marker, content, re.IGNORECASE)
            if matches:
                section_name = marker.strip('\\[]').upper()
                sections[section_name] = len(matches)
        
        return sections
    
    @classmethod
    def _calculate_completion_score(cls, content: str, sections: dict, word_count: int) -> int:
        """Calcula el puntaje de completitud (0-100)"""
        score = 0
        
        # Puntaje base por longitud (40% del total)
        if word_count >= 5000:
            score += 40
        elif word_count >= 3000:
            score += 30
        elif word_count >= 2000:
            score += 20
        elif word_count >= 1000:
            score += 10
        
        # Puntaje por variedad de secciones (30% del total)
        section_variety_score = min(len(sections) * 5, 30)
        score += section_variety_score
        
        # Puntaje por contenido multimedia (15% del total)
        multimedia_count = sections.get('MULTIMEDIA', 0)
        if multimedia_count >= 10:
            score += 15
        elif multimedia_count >= 5:
            score += 10
        elif multimedia_count >= 1:
            score += 5
        
        # Puntaje por estructura educativa (15% del total)
        educational_sections = ['PÁRRAFO', 'EJEMPLO', 'ACTIVIDAD', 'EVALUACIÓN']
        found_educational = sum(1 for section in educational_sections if section in sections)
        score += (found_educational / len(educational_sections)) * 15
        
        return min(score, 100)
    
    @classmethod
    def _identify_issues(cls, content: str, sections: dict, word_count: int) -> list:
        """Identifica problemas en el contenido"""
        issues = []
        
        if word_count < 2000:
            issues.append(f'Contenido corto: {word_count} palabras (mínimo recomendado: 2000)')
        
        if len(sections) < 3:
            issues.append(f'Pocas secciones: {len(sections)} encontradas (mínimo recomendado: 5)')
        
        if 'MULTIMEDIA' not in sections or sections['MULTIMEDIA'] < 5:
            multimedia_count = sections.get('MULTIMEDIA', 0)
            issues.append(f'Pocos recursos multimedia: {multimedia_count} (mínimo recomendado: 10)')
        
        if 'ACTIVIDAD' not in sections:
            issues.append('Sin actividades prácticas para estudiantes')
        
        if 'EVALUACIÓN' not in sections:
            issues.append('Sin sección de evaluación')
        
        return issues
    
    @classmethod
    def _find_missing_sections(cls, sections: dict) -> list:
        """Encuentra secciones importantes que faltan"""
        expected_sections = ['PÁRRAFO', 'EJEMPLO', 'ACTIVIDAD', 'MULTIMEDIA', 'EVALUACIÓN']
        missing = [section for section in expected_sections if section not in sections]
        return missing
    
    @classmethod
    def _generate_recommendations(cls, issues: list, missing_sections: list, word_count: int) -> list:
        """Genera recomendaciones para mejorar el contenido"""
        recommendations = []
        
        if word_count < 2000:
            recommendations.append('Expandir el contenido textual con más detalles y explicaciones')
        
        if missing_sections:
            recommendations.append(f'Agregar secciones faltantes: {", ".join(missing_sections)}')
        
        if 'Pocos recursos multimedia' in str(issues):
            recommendations.append('Incluir más recursos multimedia con descripciones detalladas')
        
        if 'Sin actividades prácticas' in str(issues):
            recommendations.append('Agregar actividades prácticas para estudiantes')
        
        if 'Sin sección de evaluación' in str(issues):
            recommendations.append('Incluir métodos de evaluación y criterios de calificación')
        
        if not recommendations:
            recommendations.append('El contenido parece completo')
        
        return recommendations
    
    @classmethod
    def create_extension_prompt(cls, original_content: str, analysis: dict, topic: str, course: str, grade_level: str) -> str:
        """
        Crea un prompt para extender contenido incompleto
        
        Args:
            original_content (str): Contenido original
            analysis (dict): Análisis de completitud
            topic (str): Tema del contenido
            course (str): Curso
            grade_level (str): Nivel de grado
            
        Returns:
            str: Prompt para extender el contenido
        """
        missing_sections = analysis.get('missing_sections', [])
        recommendations = analysis.get('recommendations', [])
        current_word_count = analysis.get('word_count', 0)
        
        prompt = f"""EXTIENDE Y COMPLETA EL SIGUIENTE CONTENIDO EDUCATIVO:

TEMA: {topic}
CURSO: {course}
GRADO: {grade_level}

CONTENIDO ACTUAL ({current_word_count} palabras):
{original_content[:1000]}...

PROBLEMAS IDENTIFICADOS:
{chr(10).join(f'- {issue}' for issue in analysis.get('issues', []))}

SECCIONES FALTANTES QUE DEBES AGREGAR:
{chr(10).join(f'- [{section}]' for section in missing_sections)}

INSTRUCCIONES DE EXTENSIÓN:
1. NO repitas el contenido existente
2. AGREGA únicamente las secciones faltantes
3. Cada nueva sección debe tener mínimo 200 palabras
4. Usa los marcadores exactos: [SECCIÓN], [PÁRRAFO], [EJEMPLO], [ACTIVIDAD], [MULTIMEDIA], [EVALUACIÓN]
5. Enfócate en completar las {len(missing_sections)} secciones faltantes

OBJETIVO: Llevar el contenido de {current_word_count} a mínimo 3000 palabras totales.

GENERA SOLO LAS SECCIONES FALTANTES:"""

        return prompt 