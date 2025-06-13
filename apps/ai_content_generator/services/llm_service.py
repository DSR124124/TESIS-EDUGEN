import os
import time
import json
import logging
import requests
import traceback
from django.conf import settings
# Importar el prompt mejorado  
from apps.ai_content_generator.utils.prompts import create_content_prompt, get_enhanced_content_prompts
# Procesador optimizado removido - ahora generamos HTML directo

logger = logging.getLogger(__name__)

class DeepSeekService:
    def __init__(self):
        # Inicialización segura que no falla
        self.api_key = None
        self.api_available = False
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
        try:
            # Configuración para DeepSeek API con manejo de errores
            self.api_key = os.environ.get("DEEPSEEK_API_KEY") or getattr(settings, "DEEPSEEK_API_KEY", None)
            self.api_available = bool(self.api_key)
            
            if not self.api_key:
                logger.warning("⚠️ API key de DeepSeek no encontrada. Servicio de IA no disponible.")
                self.api_available = False
                return

            logger.info(f"Tipo de clave API DeepSeek: {type(self.api_key)}")
            logger.info(f"Longitud de clave API: {len(self.api_key) if self.api_key else 0}")
            logger.info(f"Primeros 8 caracteres: {self.api_key[:8] if self.api_key and len(self.api_key) > 8 else 'N/A'}")
            logger.info(f"Últimos 4 caracteres: {self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else 'N/A'}")

            # Configuración específica de DeepSeek OPTIMIZADA para contenido extenso
            self.model = os.environ.get("DEEPSEEK_MODEL") or getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat")
            
            logger.info(f"URL base DeepSeek: {self.base_url}")
            logger.info(f"Modelo configurado: {self.model}")
            logger.info("✅ Servicio HTML directo configurado")
            
            # Verificar conexión a la API
            self._test_api_connection()
            
        except Exception as e:
            logger.error(f"❌ Error durante inicialización de DeepSeekService: {e}")
            self.api_available = False

    def _test_api_connection(self):
        """Prueba la conexión a la API de DeepSeek"""
        if not self.api_available:
            logger.info("⚠️ API de DeepSeek no disponible - saltando prueba de conexión")
            return
            
        try:
            logger.info("Probando conexión a la API de DeepSeek...")
            url = f"{self.base_url}/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Conexión a la API de DeepSeek exitosa")
                # Log de modelos disponibles (opcional)
                try:
                    models_data = response.json()
                    model_names = [model.get('id', 'unknown') for model in models_data.get('data', [])]
                    logger.info(f"Modelos disponibles: {model_names}")
                except:
                    logger.info("Modelos disponibles: No se pudo obtener la lista")
            else:
                logger.error(f"❌ Error al conectar con la API de DeepSeek: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                self.api_available = False
                # Verificar si es error de autenticación
                if response.status_code == 401:
                    logger.error("ERROR CRÍTICO: Clave API de DeepSeek inválida o expirada")
                elif response.status_code == 403:
                    logger.error("ERROR CRÍTICO: Sin permisos para acceder a la API de DeepSeek")
        except Exception as e:
            logger.exception(f"❌ Error al probar conexión a API de DeepSeek: {str(e)}")
            self.api_available = False

    def generate_content(self, prompt: str, max_tokens: int = 8000, temperature: float = 0.8) -> str:
        """
        Genera contenido EXTENSO usando DeepSeek con manejo mejorado de errores
        
        Args:
            prompt: El prompt para generar contenido
            max_tokens: Tokens para contenido EXTENSO (8000 máximo por DeepSeek)
            temperature: Creatividad del modelo (0.8)
        
        Returns:
            str: Contenido generado completo y extenso
        """
        if not self.api_available:
            logger.warning("⚠️ API de DeepSeek no disponible - retornando contenido de fallback")
            return self._create_fallback_content(prompt)
            
        try:
            # Validar que el prompt no esté vacío
            if not prompt or not prompt.strip():
                logger.error("El prompt está vacío")
                return "Error: El prompt proporcionado está vacío."
            
            # Validar longitud del prompt
            if len(prompt) > 50000:  # Límite razonable para evitar prompts extremadamente largos
                logger.warning(f"Prompt muy largo ({len(prompt)} caracteres), truncando...")
                prompt = prompt[:50000] + "... [PROMPT TRUNCADO AUTOMÁTICAMENTE]"
            
            # Asegurar que max_tokens esté en el rango válido de DeepSeek
            max_tokens = min(max_tokens, 8192)  # Límite máximo de DeepSeek
            max_tokens = max(max_tokens, 1)     # Límite mínimo
            
            logger.info(f"Generando contenido EXTENSO con DeepSeek - Tokens: {max_tokens}, Temp: {temperature}")
            logger.info(f"Longitud del prompt: {len(prompt)} caracteres")
            
            # Configurar mensajes para la API - ULTRA-OPTIMIZADO PARA CONTENIDO EXTENSO
            messages = [
                {
                    "role": "system",
                    "content": """Eres un experto desarrollador de contenido educativo que genera HTML completo y adaptativo para educación secundaria.

MISIÓN: Generar contenido educativo HTML5 completo, limpio y totalmente adaptativo.

REGLAS TÉCNICAS ESTRICTAS:
✅ GENERAR ÚNICAMENTE código HTML5 válido con CSS interno
✅ HTML semántico con DOCTYPE completo
✅ CSS adaptativo para móviles, tablets y desktop
✅ Sin frameworks externos (Bootstrap, etc.)
✅ CSS Grid y/o Flexbox para layouts modernos
✅ Tipografía mínimo 16px en móvil
✅ Sin JavaScript ni código de programación

❌ PROHIBIDO ABSOLUTO: JavaScript, iframes, código de programación, frameworks externos
❌ PROHIBIDO: Referencias al proceso de creación del contenido
❌ PROHIBIDO: Explicaciones sobre el código HTML

ESTRUCTURA HTML OBLIGATORIA:
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[TÍTULO]</title>
    <style>
        /* CSS ADAPTATIVO COMPLETO */
    </style>
</head>
<body>
    <!-- CONTENIDO EDUCATIVO ESTRUCTURADO -->
</body>
</html>

CONTENIDO EDUCATIVO REQUERIDO:
📚 Título principal y subtítulos organizados semánticamente
📝 Mínimo 8 secciones de contenido educativo
💡 Al menos 6 ejemplos prácticos con casos reales
🎯 Mínimo 5 actividades interactivas bien detalladas
📊 Recursos multimedia descriptivos
✅ Evaluación con criterios y rúbricas completas

DISEÑO ADAPTATIVO OBLIGATORIO:
📱 Mobile-first: 320px-768px
📟 Tablet: 768px-1024px
🖥️ Desktop: 1024px+
🎨 Colores educativos profesionales y accesibles
📖 Tipografía legible y jerarquía clara
🎯 Navegación intuitiva

CALIDAD EDUCATIVA:
✨ Apropiado para estudiantes de 12-17 años
🎓 Metodologías activas de aprendizaje
🌍 Ejemplos de la vida real
📱 Integración conceptual con tecnología educativa

IMPORTANTE: Responde ÚNICAMENTE con código HTML completo, sin explicaciones adicionales."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Datos para la petición SIN PRISA
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # Headers para la petición
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Realizar la llamada a la API SIN LÍMITES DE TIEMPO para contenido EXTENSO
            logger.info(f"Enviando petición a DeepSeek - GENERANDO CONTENIDO EXTENSO SIN PRISA")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=300  # 5 minutos para contenido EXTENSO completo sin prisa
            )
            
            # Verificar respuesta con logging detallado
            logger.info(f"Respuesta de DeepSeek API - Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    content = response_data["choices"][0]["message"]["content"].strip()
                    
                    # Log de estadísticas de la respuesta
                    token_usage = response_data.get("usage", {})
                    logger.info(f"✅ Contenido generado exitosamente")
                    logger.info(f"📊 Tokens utilizados: {token_usage}")
                    logger.info(f"📝 Longitud del contenido: {len(content)} caracteres")
                    
                    return content
                    
                except KeyError as e:
                    logger.error(f"❌ Error en estructura de respuesta de DeepSeek: {e}")
                    logger.error(f"Respuesta completa: {response.text}")
                    return self._create_fallback_content(prompt)
                    
            else:
                logger.error(f"❌ Error HTTP de DeepSeek API: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                
                # Manejo específico de errores HTTP
                if response.status_code == 401:
                    logger.error("🔐 Error de autenticación - verificar clave API")
                elif response.status_code == 429:
                    logger.error("⏰ Límite de velocidad excedido - intentar más tarde")
                elif response.status_code == 500:
                    logger.error("🔧 Error del servidor de DeepSeek")
                
                return self._create_fallback_content(prompt)
                
        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout en la petición a DeepSeek API")
            return self._create_fallback_content(prompt)
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"❌ Error de conexión con DeepSeek API: {str(e)}")
            return self._create_fallback_content(prompt)
            
        except Exception as e:
            logger.exception(f"❌ Error inesperado en generate_content: {str(e)}")
            return self._create_fallback_content(prompt)

    def _create_fallback_content(self, prompt: str) -> str:
        """Crea contenido de fallback cuando la API no está disponible"""
        return f"""
        <h2>Contenido Educativo: {prompt[:100]}...</h2>
        <p><strong>Nota:</strong> El servicio de IA no está disponible en este momento. Este es contenido de ejemplo.</p>
        <div class="content-section">
            <h3>Introducción</h3>
            <p>Este es un tema importante en el curriculum educativo que merece atención especial.</p>
        </div>
        <div class="content-section">
            <h3>Desarrollo del Tema</h3>
            <p>Para desarrollar este contenido educativo, se recomienda seguir una metodología estructurada.</p>
        </div>
        <div class="content-section">
            <h3>Actividades Sugeridas</h3>
            <ul>
                <li>Investigación individual sobre el tema</li>
                <li>Discusión grupal en clase</li>
                <li>Presentación de resultados</li>
            </ul>
        </div>
        """

    def generate_content_with_openai(self, prompt, max_tokens, temperature):
        """Método de compatibilidad - redirige a generate_content"""
        logger.warning("Método generate_content_with_openai está obsoleto, usando DeepSeek")
        return self.generate_content(prompt, max_tokens, temperature)

    def generate_content_direct_api(self, prompt, max_tokens=3000, temperature=0.8):
        """Método de compatibilidad - redirige a generate_content con parámetros optimizados"""
        logger.warning("Método generate_content_direct_api está obsoleto, usando DeepSeek")
        return self.generate_content(prompt, max_tokens, temperature)

    def _generate_with_simplified_prompt(self, original_prompt: str, max_tokens: int, temperature: float) -> str:
        """
        Genera contenido con un prompt simplificado cuando el original es muy largo
        """
        try:
            # Extraer información clave del prompt original
            topic = "Tema Educativo"
            grade = "Secundaria"
            
            # Buscar tema en el prompt original
            if "TEMA:" in original_prompt:
                topic_line = original_prompt.split("TEMA:")[1].split("|")[0].strip()
                if topic_line:
                    topic = topic_line
            
            # Crear prompt simplificado pero completo
            simplified_prompt = f"""
Genera material educativo COMPLETO Y LIMPIO para secundaria sobre: {topic}

REGLAS CRÍTICAS:
❌ NO incluir: Código JavaScript, HTML con scripts, programación, iframes
❌ NO incluir: Frases como "Aquí están las secciones faltantes" o "para alcanzar los requisitos"
❌ NO incluir: Referencias al proceso de creación del material

✅ GENERAR ÚNICAMENTE contenido educativo directo sobre {topic}

ESTRUCTURA REQUERIDA:
[TÍTULO] {topic}: Guía Completa para Estudiantes

[PÁRRAFO] Introducción motivadora de 300+ palabras conectando el tema con la vida real de los adolescentes, aplicaciones tecnológicas educativas actuales, importancia para su futuro académico y profesional...

[SUBTÍTULO] Conceptos Fundamentales
[PÁRRAFO] Definiciones claras y completas con ejemplos cotidianos...
[PÁRRAFO] Explicaciones paso a paso con analogías apropiadas...

[SUBTÍTULO] Ejemplos Prácticos
[EJEMPLO] Ejemplo 1: Aplicación en la vida cotidiana...
[EJEMPLO] Ejemplo 2: Situación educativa práctica...
[EJEMPLO] Ejemplo 3: Aplicación en el futuro profesional...

[SUBTÍTULO] Actividades Prácticas
[ACTIVIDAD] Actividad 1: Descripción completa con materiales, pasos, tiempo estimado...
[ACTIVIDAD] Actividad 2: Proyecto grupal con instrucciones detalladas...

[SUBTÍTULO] Recursos Multimedia
[MULTIMEDIA] Video 1: "Título exacto" - Plataforma educativa - Descripción completa del contenido...
[MULTIMEDIA] App 1: "Nombre exacto" - Funcionalidades educativas y uso en clase...
[MULTIMEDIA] Simulación 1: "Nombre" - Descripción de la experiencia educativa...
[MULTIMEDIA] Podcast 1: "Título" - Contenido educativo y aplicación...
[MULTIMEDIA] Juego educativo: "Nombre" - Descripción de mecánicas de aprendizaje...
[MULTIMEDIA] Canal YouTube: "Nombre" - Contenidos educativos recomendados...
[MULTIMEDIA] Laboratorio virtual: "Nombre" - Experimentos educativos disponibles...
[MULTIMEDIA] Sitio web: "Nombre" - Recursos educativos interactivos...

[SUBTÍTULO] Evaluación
[EVALUACIÓN] Criterios de evaluación detallados con descriptores...
[EVALUACIÓN] Rúbrica con niveles de desempeño específicos...

REQUISITOS:
- Mínimo 2500 palabras de contenido educativo puro
- Mínimo 8 recursos multimedia con descripciones educativas detalladas
- Todas las secciones completamente desarrolladas
- Enfoque en educación secundaria (12-17 años)
- Incluir aplicaciones tecnológicas educativas actuales
- SIN código, SIN scripts, SIN elementos técnicos de programación
"""
            
            logger.info("Generando contenido con prompt simplificado...")
            
            # Datos para la petición simplificada
            simplified_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": """Eres un experto en educación secundaria especializado en generar contenido educativo COMPLETO, EXTENSO y LIMPIO.

REGLAS CRÍTICAS:
❌ PROHIBIDO ABSOLUTO: Código JavaScript, HTML con scripts, programación, iframes
❌ PROHIBIDO: Frases meta-educativas como "Aquí están las secciones faltantes"
❌ PROHIBIDO: Referencias al proceso de creación del material
❌ PROHIBIDO: Elementos técnicos de desarrollo web o programación

✅ GENERAR ÚNICAMENTE:
- Material educativo directo y práctico
- Contenido apropiado para adolescentes de 12-17 años
- Ejemplos de aplicaciones educativas reales
- Actividades pedagógicamente estructuradas
- Recursos multimedia educativos (descripciones, NO código)

ENFOQUE: Crear material práctico, interactivo y relevante para educación secundaria SIN elementos problemáticos."""
                    },
                    {
                        "role": "user",
                        "content": simplified_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=simplified_data,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"].strip()
                
                if content:
                    word_count = len(content.split())
                    logger.info(f"Contenido simplificado generado exitosamente - {word_count} palabras")
                    return content
                else:
                    return "Error: No se pudo generar contenido con prompt simplificado."
            else:
                logger.error(f"Error en prompt simplificado: {response.status_code}")
                return f"Error: No se pudo generar contenido (código {response.status_code})"
                
        except Exception as e:
            logger.error(f"Error en prompt simplificado: {str(e)}")
            return f"Error en generación simplificada: {str(e)}"

# Método optimizado removido - ahora usamos generate_content_for_grapesjs

    def generate_content_for_grapesjs(self, content_type_id: int, topic: str, grade_level: str, course: str, additional_instructions: str = '') -> str:
        """
        Genera contenido COMPLETO en formato HTML adaptativo directamente
        
        Args:
            content_type_id: ID del tipo de contenido (1=plan_sesion, 2=material_apoyo, etc.)
            topic: Tema del contenido educativo
            grade_level: Nivel educativo (PRIMERO, SEGUNDO, etc.)
            course: Curso (MATEMATICA, CIENCIAS, etc.)
            additional_instructions: Instrucciones adicionales del profesor
            
        Returns:
            str: HTML completo con CSS adaptativo listo para usar
        """
        try:
            logger.info(f"🎯 Generando contenido HTML directo:")
            logger.info(f"   📚 Tema: {topic}")
            logger.info(f"   🎓 Grado: {grade_level}")
            logger.info(f"   📖 Curso: {course}")
            logger.info(f"   🔧 Tipo: {content_type_id}")
            
            # Crear prompt optimizado para generar HTML directo
            logger.info("📝 Creando prompt para HTML directo...")
            html_prompt = self._create_direct_html_prompt(
                content_type_id, topic, grade_level, course, additional_instructions
            )
            
            # Generar HTML directamente usando DeepSeek
            logger.info("🤖 Generando HTML con CSS adaptativo...")
            html_content = self.generate_content(
                prompt=html_prompt,
                max_tokens=8000,
                temperature=0.7
            )
            
            if not html_content or html_content.startswith("Error:"):
                logger.error(f"❌ Error en generación: {html_content}")
                return self._create_simple_fallback_html(topic, grade_level, course)
            
            # Validar que el HTML es completo y limpio
            validated_html = self._validate_and_clean_direct_html(html_content)
            
            logger.info(f"✅ HTML directo generado: {len(validated_html)} caracteres")
            return validated_html
                
        except Exception as e:
            logger.exception(f"❌ Error crítico en generate_content_for_grapesjs: {str(e)}")
            return self._create_simple_fallback_html(topic, grade_level, course)

    def _validate_html_content(self, html_content: str) -> bool:
        """Valida que el HTML sea adecuado para GrapesJS"""
        try:
            # Verificaciones básicas
            checks = {
                'has_content': len(html_content.strip()) > 100,
                'has_body_structure': '<body>' in html_content and '</body>' in html_content,
                'has_grapesjs_attributes': 'data-gjs-type=' in html_content,
                'has_css_styles': '<style>' in html_content and '</style>' in html_content,
                'no_script_tags': '<script>' not in html_content,  # GrapesJS prefiere sin scripts
                'proper_encoding': 'charset=UTF-8' in html_content
            }
            
            passed_checks = sum(checks.values())
            total_checks = len(checks)
            
            logger.info(f"📊 Validación HTML: {passed_checks}/{total_checks} checks pasados")
            for check, result in checks.items():
                logger.info(f"   {'✅' if result else '❌'} {check}")
            
            return passed_checks >= (total_checks * 0.8)  # 80% de checks deben pasar
            
        except Exception as e:
            logger.error(f"Error en validación HTML: {str(e)}")
            return False

    def _fix_html_content(self, html_content: str) -> str:
        """Aplica correcciones básicas al HTML para mejorar compatibilidad"""
        try:
            logger.info("🔧 Aplicando correcciones al HTML...")
            
            # Asegurar estructura básica
            if '<body>' not in html_content:
                html_content = f"<body>{html_content}</body>"
            
            if '<html>' not in html_content:
                html_content = f"<html><head><meta charset='UTF-8'></head>{html_content}</html>"
            
            # Añadir atributos básicos de GrapesJS si faltan
            if 'data-gjs-type=' not in html_content:
                html_content = html_content.replace('<body>', '<body data-gjs-type="wrapper">')
            
            logger.info("✅ Correcciones aplicadas")
            return html_content
            
        except Exception as e:
            logger.error(f"Error aplicando correcciones: {str(e)}")
            return html_content

    def _create_fallback_html(self, raw_content: str, topic: str, grade_level: str, course: str) -> str:
        """Crea HTML de respaldo cuando el template manager falla"""
        logger.info("🆘 Creando HTML de respaldo...")
        
        # HTML básico pero funcional para GrapesJS
        fallback_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {course}</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .content-section {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #3E82FC;
            border-bottom: 2px solid #3E82FC;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #FF6B6B;
            margin-top: 25px;
        }}
        .example-box {{
            background-color: #e8f5e8;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 15px 0;
        }}
        .activity-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
        }}
    </style>
</head>
<body data-gjs-type="wrapper">
    <div class="content-section" data-gjs-type="section">
        <h1 data-gjs-type="text">{topic} - {course} ({grade_level})</h1>
        <div data-gjs-type="text">
            {self._process_content_to_html(raw_content)}
        </div>
    </div>
</body>
</html>"""
        
        logger.info("✅ HTML de respaldo creado")
        return fallback_html

    def _process_content_to_html(self, content: str) -> str:
        """Procesa contenido con marcadores a HTML básico"""
        try:
            # Reemplazos básicos de marcadores
            content = content.replace('[TÍTULO]', '<h1>')
            content = content.replace('[SUBTÍTULO]', '</div><h2>')
            content = content.replace('[PÁRRAFO]', '<p>')
            content = content.replace('[EJEMPLO]', '<div class="example-box"><strong>Ejemplo:</strong><br>')
            content = content.replace('[ACTIVIDAD]', '<div class="activity-box"><strong>Actividad:</strong><br>')
            content = content.replace('[MULTIMEDIA]', '<div class="multimedia-box"><strong>Recurso Multimedia:</strong><br>')
            content = content.replace('[EVALUACIÓN]', '<div class="evaluation-box"><strong>Evaluación:</strong><br>')
            
            # Cerrar divs abiertos
            content += '</div>'
            
            return content
        except Exception as e:
            logger.error(f"Error procesando contenido: {str(e)}")
            return f"<p>Contenido generado disponible</p><div>{content}</div>"

    def _create_error_content(self, error_message: str) -> str:
        """Crea contenido de error en formato HTML para mostrar al usuario"""
        error_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Error en Generación de Contenido</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .error-container {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .error-title {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .error-message {{
            margin-bottom: 15px;
        }}
        .error-actions {{
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }}
    </style>
</head>
<body data-gjs-type="wrapper">
    <div class="error-container" data-gjs-type="section">
        <div class="error-title">⚠️ Error en la Generación de Contenido</div>
        <div class="error-message">
            <p>Se produjo un error al generar el contenido educativo:</p>
            <p><strong>{error_message}</strong></p>
        </div>
        <div class="error-actions">
            <p><strong>💡 Sugerencias:</strong></p>
            <ul>
                <li>Intenta generar el contenido nuevamente</li>
                <li>Verifica que el tema esté bien especificado</li>
                <li>Contacta al administrador si el problema persiste</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        return error_html

    def _create_direct_html_prompt(self, content_type_id: int, topic: str, grade_level: str, course: str, additional_instructions: str) -> str:
        """
        Crea un prompt optimizado para generar HTML directo con CSS adaptativo según el tipo de material
        """
        content_types = {
            1: {
                "name": "Plan de Sesión de Clase",
                "structure": """
ESTRUCTURA OBLIGATORIA:
• Datos generales (área, grado, fecha, duración)
• Título de la sesión
• Competencias y capacidades
• Desempeños esperados
• Materiales y recursos
• INICIO: motivación, pregunta detonante
• DESARROLLO: explicación, actividades en clase
• CIERRE: reflexión y consolidación
• EVALUACIÓN: criterios y evidencias
• Tarea o continuación (opcional)""",
                "focus": "Guiar al docente en la ejecución completa de una clase estructurada con momentos pedagógicos claros"
            },
            2: {
                "name": "Material de Apoyo Integrado",
                "structure": """
ESTRUCTURA OBLIGATORIA:
• Título del tema
• Resumen teórico (breve y con lenguaje sencillo)
• Ejemplos explicativos
• Diagramas / imágenes / esquemas
• Actividades prácticas o preguntas guía
• Glosario (opcional)
• Referencias o enlaces útiles""",
                "focus": "Reforzar aprendizajes previos o acompañar las sesiones con material de estudio completo"
            },
            3: {
                "name": "Guía de Ejercicios y Problemas",
                "structure": """
ESTRUCTURA OBLIGATORIA:
• Instrucciones iniciales
• Ejercicios graduados (fácil → complejo)
• Espacios para resolver
• Indicaciones para docentes (opcional)
• Clave de respuestas (si aplica)""",
                "focus": "Promover la práctica autónoma o guiada con ejercicios progresivos y bien estructurados"
            },
            4: {
                "name": "Evaluación Completa",
                "structure": """
ESTRUCTURA OBLIGATORIA:
• Datos generales (curso, grado, tema, duración)
• Instrucciones claras
• Sección A: Preguntas de selección múltiple / verdadero-falso
• Sección B: Preguntas de desarrollo / casos
• Criterios de evaluación
• Rúbrica (si aplica)""",
                "focus": "Medir conocimientos o habilidades adquiridas de forma integral y estructurada"
            },
            5: {
                "name": "Material Didáctico Interactivo",
                "structure": """
ESTRUCTURA OBLIGATORIA:
• Presentación breve del contenido
• Instrucciones de uso
• Actividades interactivas (juegos, simulaciones, quiz)
• Retroalimentación inmediata
• Conclusión/reflexión
• Pistas de ayuda o reforzamiento""",
                "focus": "Facilitar el aprendizaje con herramientas dinámicas e interactivas que motiven la participación"
            }
        }
        
        content_info = content_types.get(content_type_id, content_types[2])  # Default a Material de Apoyo
        content_type_name = content_info["name"]
        content_structure = content_info["structure"]
        content_focus = content_info["focus"]
        
        return f"""
Crea un {content_type_name} completo sobre "{topic}" para {grade_level} de {course}.

OBJETIVO: {content_focus}

{content_structure}

REQUISITOS TÉCNICOS ESTRICTOS:
✅ Genera ÚNICAMENTE código HTML5 completo con CSS interno
✅ DOCTYPE html y estructura semántica válida
✅ CSS adaptativo/responsive para móviles, tablets y desktop
✅ Sin frameworks externos (Bootstrap, Tailwind, etc.)
✅ CSS Grid y/o Flexbox para layouts modernos
✅ Colores accesibles y tipografía clara
✅ Sin JavaScript ni código de programación
✅ Incluir header institucional sencillo y elegante
✅ NO usar logos externos o imágenes complejas

ESTRUCTURA HTML OBLIGATORIA:
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {content_type_name}</title>
    <style>
        /* CSS ADAPTATIVO COMPLETO AQUÍ */
        /* INCLUIR ESTILOS PARA HEADER INSTITUCIONAL SENCILLO */
    </style>
</head>
<body>
    <!-- HEADER INSTITUCIONAL SENCILLO (OPCIONAL) -->
    <header class="header-institucional">
        <div class="header-content">
            <div class="logo-placeholder">🎓</div>
            <div class="info-institucional">
                <h1>Material Educativo</h1>
                <p>Generado con IA - {content_type_name}</p>
            </div>
        </div>
    </header>
    
    <!-- CONTENIDO EDUCATIVO ESTRUCTURADO -->
</body>
</html>

DISEÑO ADAPTATIVO OBLIGATORIO:
📱 Mobile-first: 320px-768px (navegación táctil, texto min 16px)
📟 Tablet: 768px-1024px (layout híbrido, interactividad media)
🖥️ Desktop: 1024px+ (aprovechamiento completo del espacio)
🎨 Paleta de colores educativos profesionales y accesibles
📖 Tipografía legible con jerarquía clara
🎯 Navegación intuitiva y accesible

CALIDAD EDUCATIVA REQUERIDA:
✨ Apropiado para estudiantes de 12-17 años
🎓 Metodologías activas de aprendizaje
🌍 Ejemplos de la vida real y contextualización actual
📱 Integración conceptual con tecnología educativa (apps, plataformas, herramientas digitales)
🔬 Enfoque científico y basado en evidencia
🎯 Conexiones interdisciplinarias cuando sea relevante

HEADER INSTITUCIONAL REQUERIDO:
🏫 Incluir header simple con título "Material Educativo"
📚 Subtítulo: "Generado con IA - {content_type_name}"
🎨 Usar emoji 🎓 como ícono institucional
💫 Diseño limpio y profesional sin imágenes externas
📱 Header responsive y adaptativo

{f"INSTRUCCIONES ADICIONALES DEL PROFESOR: {additional_instructions}" if additional_instructions else ""}

IMPORTANTE: Responde ÚNICAMENTE con el código HTML completo y válido, sin explicaciones adicionales ni texto fuera del HTML.
"""
    
    def _validate_and_clean_direct_html(self, html_content: str) -> str:
        """
        Valida y limpia el HTML generado directamente
        """
        try:
            # Verificar que es HTML válido
            if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
                logger.warning("HTML no tiene estructura completa, añadiendo...")
                html_content = self._wrap_incomplete_html(html_content)
            
            # Limpiar caracteres problemáticos
            html_content = html_content.replace('```html', '').replace('```', '')
            html_content = html_content.strip()
            
            # Verificar elementos básicos
            required_elements = ['<html', '<head', '<body', '<style']
            missing_elements = [elem for elem in required_elements if elem not in html_content]
            
            if missing_elements:
                logger.warning(f"Elementos HTML faltantes: {missing_elements}")
                html_content = self._add_missing_html_elements(html_content)
            
            # Asegurar viewport para responsividad
            if 'viewport' not in html_content:
                html_content = html_content.replace(
                    '<head>',
                    '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                )
            
            logger.info("✅ HTML validado y limpiado")
            return html_content
            
        except Exception as e:
            logger.error(f"Error validando HTML: {str(e)}")
            return html_content
    
    def _wrap_incomplete_html(self, content: str) -> str:
        """
        Envuelve contenido incompleto en estructura HTML básica
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contenido Educativo</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            body {{ padding: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""

    def _add_missing_html_elements(self, html_content: str) -> str:
        """
        Añade elementos HTML faltantes básicos
        """
        if '<head>' not in html_content and '<html>' in html_content:
            html_content = html_content.replace(
                '<html>',
                '<html lang="es">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Contenido Educativo</title>\n</head>'
            )
        
        return html_content
    
    def _create_simple_fallback_html(self, topic: str, grade_level: str, course: str) -> str:
        """
        Crea HTML básico de respaldo cuando falla la generación
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {course}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        .content-section {{
            background: #f8f9fa;
            padding: 25px;
            margin: 25px 0;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        .loading-message {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 40px;
            background: #ecf0f1;
            border-radius: 10px;
            margin: 20px 0;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            h1 {{
                font-size: 2rem;
            }}
            body {{
                padding: 10px;
            }}
        }}
        @media (max-width: 480px) {{
            h1 {{
                font-size: 1.5rem;
            }}
            .container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{topic}</h1>
        <div class="content-section">
            <h2>Información del Curso</h2>
            <p><strong>Materia:</strong> {course}</p>
            <p><strong>Nivel:</strong> {grade_level}</p>
            <p><strong>Tema:</strong> {topic}</p>
        </div>
        <div class="loading-message">
            <h3>🔄 Contenido en Preparación</h3>
            <p>El contenido educativo está siendo generado. Por favor, edita este material para añadir el contenido específico que necesitas.</p>
        </div>
        <div class="content-section">
            <h2>📚 Objetivos de Aprendizaje</h2>
            <p>Los estudiantes serán capaces de comprender y aplicar los conceptos fundamentales de {topic}.</p>
        </div>
        <div class="content-section">
            <h2>📝 Contenido Principal</h2>
            <p>Aquí puedes agregar el contenido educativo específico sobre {topic}.</p>
        </div>
        <div class="content-section">
            <h2>🎯 Actividades Prácticas</h2>
            <p>Desarrolla actividades interactivas para reforzar el aprendizaje.</p>
        </div>
        <div class="content-section">
            <h2>📊 Evaluación</h2>
            <p>Define los criterios y métodos de evaluación para este tema.</p>
        </div>
    </div>
</body>
</html>"""

# Alias para mantener compatibilidad con código existente
OpenAIService = DeepSeekService
