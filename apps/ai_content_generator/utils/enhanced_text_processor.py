"""
Procesador mejorado de texto que convierte contenido con marcadores
en HTML perfectamente estructurado y visualmente atractivo
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class EnhancedTextProcessor:
    """
    Procesa texto con marcadores y lo convierte en HTML súper estructurado
    """
    
    def __init__(self):
        self.icon_map = {
            'TÍTULO': '📚',
            'SUBTÍTULO': '📖',
            'PÁRRAFO': '📝',
            'EJEMPLO': '💡',
            'ACTIVIDAD': '🎯',
            'MULTIMEDIA': '🎥',
            'EVALUACIÓN': '📊',
            'INTRODUCCIÓN': '🌟',
            'DESARROLLO': '🔬',
            'CONCLUSIÓN': '🎉',
            'MATERIALES': '🧰',
            'PASOS': '👣',
            'RESULTADOS': '🏆',
            'OBJETIVOS': '🎯',
            'CRONOGRAMA': '⏰',
            'FASES': '📋',
            'ENTREGABLES': '📦'
        }
    
    def process_to_structured_html(self, raw_text: str, topic: str, course: str, grade: str) -> str:
        """
        Convierte texto con marcadores en HTML súper estructurado
        """
        try:
            # Limpiar el texto de contenido problemático antes de procesar
            cleaned_text = self._clean_problematic_content(raw_text)
            
            # Extraer todos los elementos del texto limpio
            elements = self._extract_all_elements(cleaned_text)
            
            # Crear estructura HTML moderna
            html = self._create_modern_html_structure(elements, topic, course, grade)
            
            return html
            
        except Exception as e:
            logger.error(f"Error procesando texto a HTML estructurado: {str(e)}")
            return self._create_fallback_html(raw_text, topic, course, grade)
    
    def _clean_problematic_content(self, text: str) -> str:
        """
        Limpia el texto de contenido problemático o no deseado
        """
        # Lista de frases problemáticas a eliminar
        problematic_phrases = [
            "Aquí están las secciones faltantes completamente desarrolladas para alcanzar los requisitos:",
            "Aquí están las secciones faltantes completamente desarrolladas para alcanzar los requisitos solicitados:",
            "**Nota**: Este es solo un extracto inicial. El contenido completo incluirá:",
            "Continúa con más secciones para alcanzar los 5000+ palabras...",
            "Continúa con más contenido hasta superar las 5000 palabras...",
            "Total: 5000+ palabras desarrolladas completamente.",
            "TOTAL MÍNIMO:",
            "AL MÍNIMO:",
            "MÍNIMO:",
            "contentData && iframe",
            "const blob = new Blob",
            "URL.createObjectURL",
            "iframe.src = url",
            "// Animaciones de entrada mejoradas",
            "const observerOptions",
            "const observer = new IntersectionObserver",
            "document.querySelectorAll('.workflow-step, .content-display').forEach",
            "el.style.opacity = '0'",
            "el.style.transform = 'translateY(30px)'",
            "observer.observe(el)",
            "btn.addEventListener('mouseenter'",
            "btn.addEventListener('mouseleave'",
            "const iframeContainer = document.querySelector",
            "const loadingIndicator = document.createElement",
            "loadingIndicator.innerHTML =",
            "Cargando contenido...",
            "loadingIndicator.style.cssText",
            "iframeContainer.appendChild(loadingIndicator)",
            "iframe.addEventListener('load'",
            "setTimeout(() => {",
            "loadingIndicator.style.opacity = '0'",
            "loadingIndicator.remove()",
            "});",
            "`; if (contentData && iframe)",
            "javascript",
            "document.addEventListener",
            "DOMContentLoaded"
        ]
        
        cleaned_text = text
        
        # Eliminar frases problemáticas
        for phrase in problematic_phrases:
            cleaned_text = cleaned_text.replace(phrase, "")
        
        # Eliminar líneas que contengan solo guiones o asteriscos
        lines = cleaned_text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Saltar líneas problemáticas
            if (line.startswith('---') or 
                line.startswith('***') or
                line.startswith('```') or
                line.startswith('`') or
                'palabras' in line.lower() and ('mínimo' in line.lower() or 'total' in line.lower()) or
                line.startswith('8 [EJEMPLO]') or
                line.startswith('5 [ACTIVIDAD]') or
                line.startswith('12 [MULTIMEDIA]') or
                line.startswith('[EVALUACIÓN] expandida') or
                'extracto inicial' in line.lower() or
                'contenido completo' in line.lower() or
                'javascript' in line.lower() or
                'contentdata' in line.lower() or
                'iframe' in line.lower() or
                'const ' in line or
                'document.' in line or
                'addEventListener' in line or
                'querySelector' in line or
                'createElement' in line or
                'appendChild' in line or
                'setTimeout' in line or
                '.style.' in line or
                'function(' in line or
                '=>' in line or
                'loadingIndicator' in line):
                continue
            
            filtered_lines.append(line)
        
        # Limpiar líneas vacías excesivas
        cleaned_text = '\n'.join(filtered_lines)
        cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def _extract_all_elements(self, text: str) -> Dict:
        """
        Extrae todos los elementos del texto usando marcadores
        """
        elements = {
            'title': '',
            'sections': [],
            'examples': [],
            'activities': [],
            'multimedia': [],
            'evaluation': []
        }
        
        # Dividir el texto en líneas
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar marcadores
            if self._is_marker(line):
                # Guardar contenido anterior si existe
                if current_section and current_content:
                    self._add_to_elements(elements, current_section, '\n'.join(current_content))
                
                # Iniciar nueva sección
                current_section = self._extract_marker_type(line)
                current_content = []
                
                # Si es título, extraer directamente
                if current_section == 'TÍTULO':
                    title_text = line.replace('[TÍTULO]', '').strip()
                    if title_text:
                        elements['title'] = title_text
                    current_section = None
                else:
                    # Extraer contenido que está en la misma línea que el marcador
                    marker_pattern = f'[{current_section}]'
                    content_in_line = line.replace(marker_pattern, '').strip()
                    if content_in_line:
                        current_content.append(content_in_line)
            else:
                # Agregar contenido a la sección actual
                if current_section:
                    current_content.append(line)
        
        # Agregar último contenido
        if current_section and current_content:
            self._add_to_elements(elements, current_section, '\n'.join(current_content))
        
        return elements
    
    def _is_marker(self, line: str) -> bool:
        """Verifica si una línea contiene un marcador"""
        return re.match(r'\[([A-ZÁÉÍÓÚÜ\s]+)\]', line) is not None
    
    def _extract_marker_type(self, line: str) -> str:
        """Extrae el tipo de marcador de una línea"""
        match = re.match(r'\[([A-ZÁÉÍÓÚÜ\s]+)\]', line)
        return match.group(1).strip() if match else ''
    
    def _add_to_elements(self, elements: Dict, section_type: str, content: str):
        """Agrega contenido a la estructura de elementos con manejo mejorado de tipos"""
        content = content.strip()
        if not content:
            return
        
        # Mapear marcadores específicos según los tipos de contenido estructurados
        if section_type in ['EJEMPLO', 'EJEMPLOS RESUELTOS', 'EJEMPLOS PRÁCTICOS']:
            elements['examples'].append(content)
        elif section_type in ['ACTIVIDAD', 'ACTIVIDADES', 'ACTIVIDADES INTERACTIVAS', 'LABORATORIO VIRTUAL', 'JUEGOS EDUCATIVOS']:
            elements['activities'].append(content)
        elif section_type in ['MULTIMEDIA', 'RECURSOS COMPLEMENTARIOS', 'BIBLIOTECA DIGITAL']:
            elements['multimedia'].append(content)
        elif section_type in ['EVALUACIÓN', 'EVALUACIÓN COMPLETA', 'EVALUACIÓN GAMIFICADA', 'AUTOEVALUACIÓN']:
            elements['evaluation'].append(content)
        else:
            # Cualquier otra sección (INTRODUCCIÓN, OBJETIVOS, DESARROLLO TEÓRICO, etc.)
            elements['sections'].append({
                'type': section_type,
                'content': content
            })
    
    def _create_modern_html_structure(self, elements: Dict, topic: str, course: str, grade: str) -> str:
        """
        Crea estructura HTML moderna y súper organizada
        """
        html_parts = []
        
        # Header institucional primero
        html_parts.append(self._get_institutional_header())
        
        # Header principal del contenido
        title = elements.get('title', topic)
        html_parts.append(self._create_header(title, course, grade))
        
        # Contenedor principal
        html_parts.append('<div class="main-container">')
        
        # Procesar secciones principales
        for section in elements.get('sections', []):
            html_parts.append(self._create_section_html(section))
        
        # Ejemplos si existen
        if elements.get('examples'):
            html_parts.append(self._create_examples_section(elements['examples']))
        
        # Actividades si existen
        if elements.get('activities'):
            html_parts.append(self._create_activities_section(elements['activities']))
        
        # Multimedia si existe
        if elements.get('multimedia'):
            html_parts.append(self._create_multimedia_section(elements['multimedia']))
        
        # Evaluación si existe
        if elements.get('evaluation'):
            html_parts.append(self._create_evaluation_section(elements['evaluation']))
        
        html_parts.append('</div>')  # Cerrar contenedor principal
        
        # Crear documento completo
        full_html = self._wrap_in_document(html_parts)
        
        return full_html
    
    def _get_institutional_header(self) -> str:
        """Genera el encabezado institucional con logo y nombre del colegio"""
        try:
            # Intentar obtener información de la institución
            from apps.institutions.models import Institution
            institution = Institution.objects.filter(is_active=True).first()
            
            if institution:
                # Generar HTML con la información institucional
                logo_html = ""
                if institution.logo:
                    logo_html = f'''
                    <div class="institution-logo">
                        <img src="{institution.logo.url}" alt="Logo de {institution.name}" />
                    </div>
                    '''
                else:
                    logo_html = '''
                    <div class="institution-logo placeholder">
                        <i class="fas fa-university"></i>
                    </div>
                    '''
                
                return f'''
                <div class="institutional-header" data-gjs-type="institutional-header">
                    <div class="institutional-content">
                        <div class="institution-brand">
                            {logo_html}
                            <div class="institution-info">
                                <h1 class="institution-name">{institution.name}</h1>
                                <div class="institution-details">
                                    <div class="institution-type">Institución Educativa</div>
                                    {f'<div class="institution-address">{institution.address}</div>' if institution.address else ''}
                                </div>
                            </div>
                        </div>
                        <div class="header-badges">
                            <div class="ai-badge">
                                <i class="fas fa-robot"></i>
                                <span>Generado con IA</span>
                            </div>
                            <div class="date-badge">
                                <i class="fas fa-calendar-alt"></i>
                                <span id="current-date"></span>
                            </div>
                        </div>
                    </div>
                    <div class="header-decoration"></div>
                </div>
                '''
            else:
                # Fallback sin institución específica
                return '''
                <div class="institutional-header default" data-gjs-type="institutional-header">
                    <div class="institutional-content">
                        <div class="institution-brand">
                            <div class="institution-logo placeholder">
                                <i class="fas fa-graduation-cap"></i>
                            </div>
                            <div class="institution-info">
                                <h1 class="institution-name">Material Educativo</h1>
                                <div class="institution-details">
                                    <div class="institution-type">Contenido Pedagógico Digital</div>
                                </div>
                            </div>
                        </div>
                        <div class="header-badges">
                            <div class="ai-badge">
                                <i class="fas fa-robot"></i>
                                <span>Generado con IA</span>
                            </div>
                            <div class="date-badge">
                                <i class="fas fa-calendar-alt"></i>
                                <span id="current-date"></span>
                            </div>
                        </div>
                    </div>
                    <div class="header-decoration"></div>
                </div>
                '''
        except Exception as e:
            logger.error(f"Error obteniendo información institucional: {str(e)}")
            # Fallback en caso de error
            return '''
            <div class="institutional-header default" data-gjs-type="institutional-header">
                <div class="institutional-content">
                    <div class="institution-brand">
                        <div class="institution-logo placeholder">
                            <i class="fas fa-graduation-cap"></i>
                        </div>
                        <div class="institution-info">
                            <h1 class="institution-name">Material Educativo</h1>
                            <div class="institution-details">
                                <div class="institution-type">Contenido Pedagógico Digital</div>
                            </div>
                        </div>
                    </div>
                    <div class="header-badges">
                        <div class="ai-badge">
                            <i class="fas fa-robot"></i>
                            <span>Generado con IA</span>
                        </div>
                        <div class="date-badge">
                            <i class="fas fa-calendar-alt"></i>
                            <span id="current-date"></span>
                        </div>
                    </div>
                </div>
                <div class="header-decoration"></div>
            </div>
            '''

    def _create_header(self, title: str, course: str, grade: str) -> str:
        """Crea el header principal del contenido (sin el header institucional que ya se agregó)"""
        return f'''
        <header class="content-header" data-gjs-type="header">
            <div class="header-content">
                <h1 class="main-title" data-gjs-type="text">{title}</h1>
                <div class="course-info" data-gjs-type="text">
                    <span class="course-badge">📚 {course}</span>
                    <span class="grade-badge">🎓 {grade}</span>
                </div>
            </div>
        </header>
        '''
    
    def _create_section_html(self, section: Dict) -> str:
        """Crea HTML para una sección específica con estilos mejorados según tipo"""
        section_type = section['type']
        content = section['content']
        
        # Mapa de iconos expandido para todos los tipos de contenido
        icon_map = {
            'INTRODUCCIÓN': '🚀',
            'OBJETIVOS': '🎯', 
            'DESARROLLO TEÓRICO': '📚',
            'DESARROLLO': '📚',
            'EJEMPLOS PRÁCTICOS': '💡',
            'EVALUACIÓN': '📊',
            'RECURSOS ADICIONALES': '🔗',
            'INSTRUCCIONES GENERALES': '📋',
            'RECORDATORIO TEÓRICO': '🧠',
            'INFORMACIÓN GENERAL': 'ℹ️',
            'COMPETENCIAS Y CAPACIDADES': '⭐',
            'SECUENCIA DIDÁCTICA': '🛤️',
            'MATERIALES Y RECURSOS': '🧰',
            'ESTRATEGIAS DIDÁCTICAS': '👨‍🏫',
            'ATENCIÓN A LA DIVERSIDAD': '👥',
            'TAREA O EXTENSIÓN': '🏠',
            'PRESENTACIÓN DEL MATERIAL': '🎪',
            'GUÍA DE NAVEGACIÓN': '🧭',
            'ACTIVACIÓN DE CONOCIMIENTOS': '💡',
            'EXPLORACIÓN INTERACTIVA': '🔍',
            'PROYECTO CREATIVO': '🎨',
            'GUÍA PARA EL DOCENTE': '👔',
            'EJERCICIOS NIVEL BÁSICO': '🔰',
            'EJERCICIOS NIVEL INTERMEDIO': '⚡',
            'EJERCICIOS NIVEL AVANZADO': '🔥',
            'PROBLEMAS DE APLICACIÓN': '🌟',
            'DESAFÍOS EXTRA': '🏆',
            'CLAVES DE RESPUESTAS': '🔑'
        }
        
        icon = icon_map.get(section_type, '📄')
        
        # Procesar el contenido en párrafos
        paragraphs = self._process_paragraphs(content)
        
        # Determinar clase especial según el tipo
        css_class = section_type.lower().replace(' ', '-').replace('ó', 'o').replace('é', 'e').replace('í', 'i')
        
        return f'''
        <section class="content-section {css_class}-section" data-gjs-type="section">
            <div class="section-header">
                <h2 class="section-title" data-gjs-type="text">
                    <span class="section-icon">{icon}</span>
                    {section_type.title()}
                </h2>
            </div>
            <div class="section-content" data-gjs-type="text">
                {paragraphs}
            </div>
        </section>
        '''
    
    def _create_examples_section(self, examples: List[str]) -> str:
        """Crea sección de ejemplos"""
        examples_html = []
        for i, example in enumerate(examples, 1):
            examples_html.append(f'''
            <div class="example-card" data-gjs-type="example">
                <div class="example-header">
                    <h4>💡 Ejemplo {i}</h4>
                </div>
                <div class="example-content" data-gjs-type="text">
                    {self._process_paragraphs(example)}
                </div>
            </div>
            ''')
        
        return f'''
        <section class="examples-section" data-gjs-type="examples-container">
            <div class="section-header">
                <h2 class="section-title" data-gjs-type="text">
                    <span class="section-icon">💡</span>
                    Ejemplos Prácticos
                </h2>
            </div>
            <div class="examples-grid">
                {''.join(examples_html)}
            </div>
        </section>
        '''
    
    def _create_activities_section(self, activities: List[str]) -> str:
        """Crea sección de actividades"""
        activities_html = []
        for i, activity in enumerate(activities, 1):
            activities_html.append(f'''
            <div class="activity-card" data-gjs-type="activity">
                <div class="activity-header">
                    <h4>🎯 Actividad {i}</h4>
                </div>
                <div class="activity-content" data-gjs-type="text">
                    {self._process_paragraphs(activity)}
                </div>
            </div>
            ''')
        
        return f'''
        <section class="activities-section" data-gjs-type="activities-container">
            <div class="section-header">
                <h2 class="section-title" data-gjs-type="text">
                    <span class="section-icon">🎯</span>
                    Actividades Prácticas
                </h2>
            </div>
            <div class="activities-grid">
                {''.join(activities_html)}
            </div>
        </section>
        '''
    
    def _create_multimedia_section(self, multimedia: List[str]) -> str:
        """Crea sección de recursos multimedia"""
        multimedia_html = []
        for i, resource in enumerate(multimedia, 1):
            multimedia_html.append(f'''
            <div class="multimedia-card" data-gjs-type="multimedia">
                <div class="multimedia-header">
                    <h4>🎥 Recurso {i}</h4>
                </div>
                <div class="multimedia-content" data-gjs-type="text">
                    {self._process_paragraphs(resource)}
                </div>
            </div>
            ''')
        
        return f'''
        <section class="multimedia-section" data-gjs-type="multimedia-container">
            <div class="section-header">
                <h2 class="section-title" data-gjs-type="text">
                    <span class="section-icon">🎥</span>
                    Recursos Multimedia
                </h2>
            </div>
            <div class="multimedia-grid">
                {''.join(multimedia_html)}
            </div>
        </section>
        '''
    
    def _create_evaluation_section(self, evaluation: List[str]) -> str:
        """Crea sección de evaluación"""
        return f'''
        <section class="evaluation-section" data-gjs-type="evaluation-container">
            <div class="section-header">
                <h2 class="section-title" data-gjs-type="text">
                    <span class="section-icon">📊</span>
                    Evaluación
                </h2>
            </div>
            <div class="evaluation-content" data-gjs-type="text">
                {self._process_paragraphs(''.join(evaluation))}
            </div>
        </section>
        '''
    
    def _process_paragraphs(self, content: str) -> str:
        """Procesa contenido en párrafos HTML bien formateados"""
        if not content:
            return ''
        
        paragraphs = content.split('\n')
        processed = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Detectar listas
            if paragraph.startswith('- ') or paragraph.startswith('• '):
                if not processed or not processed[-1].startswith('<ul>'):
                    processed.append('<ul class="content-list">')
                processed.append(f'<li>{paragraph[2:].strip()}</li>')
            else:
                # Cerrar lista si estaba abierta
                if processed and processed[-1].startswith('<li>'):
                    processed.append('</ul>')
                
                # Agregar párrafo normal
                processed.append(f'<p class="content-paragraph">{paragraph}</p>')
        
        # Cerrar lista final si quedó abierta
        if processed and processed[-1].startswith('<li>'):
            processed.append('</ul>')
        
        return '\n'.join(processed)
    
    def _wrap_in_document(self, html_parts: List[str]) -> str:
        """Envuelve el contenido en un documento HTML completo"""
        return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contenido Educativo Estructurado</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    {self._get_modern_styles()}
</head>
<body data-gjs-type="wrapper">
    {''.join(html_parts)}
    <script>
        // Establecer fecha actual
        document.addEventListener('DOMContentLoaded', function() {{
            const dateElement = document.getElementById('current-date');
            if (dateElement) {{
                const now = new Date();
                const options = {{ 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                }};
                dateElement.textContent = now.toLocaleDateString('es-ES', options);
            }}
        }});
    </script>
</body>
</html>'''
    
    def _get_modern_styles(self) -> str:
        """Retorna estilos CSS modernos y atractivos"""
        return '''<style>
        :root {
            --primary-color: #3e82fc;
            --secondary-color: #ff6b6b;
            --accent-color: #ffc107;
            --success-color: #28a745;
            --bg-color: #f8f9fa;
            --text-color: #2c3e50;
            --border-radius: 12px;
            --shadow: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-hover: 0 8px 24px rgba(0,0,0,0.15);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background: var(--bg-color);
            padding: 0;
            margin: 0;
        }

        /* Encabezado Institucional */
        .institutional-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298, #005CFF);
            color: white;
            padding: 25px 30px;
            position: relative;
            overflow: hidden;
            border-bottom: 4px solid #FFD700;
            box-shadow: 0 4px 20px rgba(0, 92, 255, 0.3);
        }

        .institutional-header.default {
            background: linear-gradient(135deg, #4a5568, #2d3748, #1a202c);
        }

        .institutional-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 2;
            max-width: 1200px;
            margin: 0 auto;
        }

        .institution-brand {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .institution-logo {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
        }

        .institution-logo img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 13px;
        }

        .institution-logo.placeholder {
            font-size: 2rem;
            color: rgba(255, 255, 255, 0.8);
        }

        .institution-info {
            flex: 1;
        }

        .institution-name {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0 0 5px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            line-height: 1.2;
        }

        .institution-details {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        .institution-type {
            font-size: 0.9rem;
            opacity: 0.9;
            font-weight: 500;
            color: #FFD700;
        }

        .institution-address {
            font-size: 0.8rem;
            opacity: 0.8;
            font-weight: 400;
        }

        .header-badges {
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: flex-end;
        }

        .ai-badge, .date-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.15);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .ai-badge {
            background: rgba(255, 215, 0, 0.2);
            color: #FFD700;
            border-color: rgba(255, 215, 0, 0.3);
        }

        .date-badge {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.9);
        }

        .header-decoration {
            position: absolute;
            top: 0;
            right: 0;
            width: 200px;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="dots" patternUnits="userSpaceOnUse" width="20" height="20"><circle cx="10" cy="10" r="2" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23dots)"/></svg>') repeat;
            opacity: 0.3;
        }

        .content-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 40px;
            border-radius: 0;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: var(--shadow);
        }

        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .course-info {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }

        .course-badge, .grade-badge {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }

        .main-container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .content-section {
            background: white;
            margin: 25px 0;
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .content-section:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
        }

        .section-header {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }

        .section-title {
            font-size: 1.8rem;
            color: var(--primary-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-icon {
            font-size: 1.5rem;
        }

        .content-paragraph {
            margin-bottom: 15px;
            text-align: justify;
            font-size: 1.1rem;
        }

        .content-list {
            margin: 15px 0;
            padding-left: 25px;
        }

        .content-list li {
            margin-bottom: 8px;
            font-size: 1.05rem;
        }

        .examples-section, .activities-section, .multimedia-section {
            background: white;
            margin: 30px 0;
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        .examples-grid, .activities-grid, .multimedia-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .example-card, .activity-card, .multimedia-card {
            background: linear-gradient(135deg, #fff8e1, #ffecb3);
            border: 1px solid #ffc107;
            border-radius: var(--border-radius);
            padding: 20px;
            transition: transform 0.3s ease;
        }

        .activity-card {
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
            border-color: var(--success-color);
        }

        .multimedia-card {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            border-color: var(--primary-color);
        }

        .example-card:hover, .activity-card:hover, .multimedia-card:hover {
            transform: translateY(-3px);
        }

        .example-header, .activity-header, .multimedia-header {
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }

        .example-header h4, .activity-header h4, .multimedia-header h4 {
            color: var(--text-color);
            font-size: 1.2rem;
        }

        .evaluation-section {
            background: linear-gradient(135deg, #fff0f0, #ffe0e0);
            border: 2px solid var(--secondary-color);
            margin: 30px 0;
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }

        @media (max-width: 768px) {
            .institutional-content {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            .institution-brand {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            .institution-logo {
                width: 60px;
                height: 60px;
            }
            
            .institution-name {
                font-size: 1.4rem;
            }
            
            .header-badges {
                flex-direction: row;
                justify-content: center;
                gap: 10px;
            }
            
            .institutional-header {
                padding: 20px 15px;
            }
            
            .examples-grid, .activities-grid, .multimedia-grid {
                grid-template-columns: 1fr;
            }
            
            .course-info {
                flex-direction: column;
                gap: 10px;
            }
            
            .main-title {
                font-size: 2rem;
            }
            
            body {
                padding: 0;
            }
            
            .main-container {
                padding: 10px;
            }
            
            .content-section {
                margin: 15px 0;
                padding: 20px;
            }
        }
        </style>'''
    
    def _create_fallback_html(self, raw_text: str, topic: str, course: str, grade: str) -> str:
        """Crea HTML de respaldo si falla el procesamiento principal"""
        return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            line-height: 1.6; 
            background: #f8f9fa; 
        }}
        .fallback-container {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }}
        h1 {{ color: #3e82fc; }}
        p {{ margin-bottom: 15px; }}
    </style>
</head>
<body data-gjs-type="wrapper">
    <div class="fallback-container" data-gjs-type="container">
        <h1 data-gjs-type="text">{topic}</h1>
        <p data-gjs-type="text"><strong>Curso:</strong> {course} | <strong>Grado:</strong> {grade}</p>
        <div data-gjs-type="text">{self._process_paragraphs(raw_text)}</div>
    </div>
</body>
</html>''' 