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
            
            # Verificar conexión a la API de forma no crítica
            try:
                self._test_api_connection()
            except Exception as e:
                logger.warning(f"⚠️ Error al verificar conexión API, pero continuando: {e}")
                # No marcar como no disponible por un error de conexión
                
        except Exception as e:
            logger.error(f"❌ Error durante inicialización de DeepSeekService: {e}")
            # Mantener disponible incluso con errores, para usar fallback
            logger.info("🔄 Servicio mantenido activo para contenido de fallback")

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

MISIÓN CRÍTICA: Generar contenido educativo HTML5 COMPLETO con TODO EL MATERIAL EDUCATIVO INCLUIDO.

⚠️ OBLIGATORIO: NUNCA generes HTML con contenedores vacíos o placeholders
⚠️ OBLIGATORIO: TODOS los elementos <div>, <section>, <main> deben contener contenido educativo real
⚠️ OBLIGATORIO: Llena COMPLETAMENTE todas las secciones con teoría, ejemplos y ejercicios

REGLAS TÉCNICAS ESTRICTAS:
✅ GENERAR ÚNICAMENTE código HTML5 válido con CSS interno
✅ HTML semántico con DOCTYPE completo
✅ CSS adaptativo para móviles, tablets y desktop
✅ Sin frameworks externos (Bootstrap, etc.)
✅ CSS Grid y/o Flexbox para layouts modernos
✅ Tipografía mínimo 16px en móvil
✅ Sin JavaScript ni código de programación

❌ PROHIBIDO ABSOLUTO: JavaScript, iframes, código de programación, frameworks externos
❌ PROHIBIDO ABSOLUTO: Contenedores vacíos o con placeholder "contenido aquí"
❌ PROHIBIDO: Referencias al proceso de creación del contenido
❌ PROHIBIDO: Explicaciones sobre el código HTML

ESTRUCTURA HTML OBLIGATORIA CON CONTENIDO COMPLETO:
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[TÍTULO DEL TEMA ESPECÍFICO]</title>
    <style>
        /* CSS ADAPTATIVO COMPLETO */
    </style>
</head>
<body>
    <main class="main-container">
        <header>
            <h1>[TÍTULO DEL TEMA]</h1>
        </header>
        <!-- AQUÍ DEBES GENERAR TODO EL CONTENIDO EDUCATIVO REAL -->
        <!-- INCLUYE: teoría completa, ejemplos resueltos, ejercicios, actividades -->
        <!-- NO DEJES SECCIONES VACÍAS -->
    </main>
</body>
</html>

CONTENIDO EDUCATIVO OBLIGATORIO A INCLUIR:
📚 TEORÍA COMPLETA: Explicación detallada del tema con mínimo 8 párrafos
📝 CONCEPTOS FUNDAMENTALES: Definiciones y principios básicos
💡 EJEMPLOS RESUELTOS: Al menos 6 ejemplos paso a paso con soluciones completas
🎯 EJERCICIOS PRÁCTICOS: Mínimo 5 ejercicios para que resuelvan los estudiantes
🔬 ACTIVIDADES EXPERIMENTALES: Experimentos o actividades prácticas detalladas
📊 EVALUACIÓN: Criterios de evaluación y rúbricas
🌍 APLICACIONES REALES: Usos del tema en la vida cotidiana
📖 GLOSARIO: Términos importantes del tema

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

⚠️ CRÍTICO: El HTML resultante debe contener TODO EL MATERIAL EDUCATIVO completo y listo para usar. NO generes estructuras vacías.

IMPORTANTE: Responde ÚNICAMENTE con código HTML completo que incluya TODO EL CONTENIDO EDUCATIVO, sin explicaciones adicionales."""
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
        # Extraer tema principal del prompt
        tema = prompt[:100] if len(prompt) > 100 else prompt
        
        return f"""{{
            "titulo": "Contenido Educativo: {tema}",
            "descripcion": "Contenido educativo base generado automáticamente. Se recomienda editarlo para adaptarlo a las necesidades específicas.",
            "secciones": [
                {{
                    "titulo": "Introducción al Tema",
                    "contenido": "<p>Este tema es fundamental en el curriculum educativo moderno. Requiere un enfoque pedagógico que combine teoría y práctica para lograr un aprendizaje significativo.</p><p>Los estudiantes podrán desarrollar competencias importantes a través del estudio de este contenido.</p>",
                    "imagen_sugerida": "Diagrama introductorio sobre {tema}"
                }},
                {{
                    "titulo": "Conceptos Fundamentales",
                    "contenido": "<p>Los conceptos básicos incluyen:</p><ul><li>Definiciones principales</li><li>Principios fundamentales</li><li>Aplicaciones prácticas</li><li>Relaciones con otros temas</li></ul><p>Es importante que los estudiantes comprendan estos elementos antes de avanzar a temas más complejos.</p>",
                    "imagen_sugerida": "Mapa conceptual de {tema}"
                }},
                {{
                    "titulo": "Aplicaciones Prácticas",
                    "contenido": "<p>Este conocimiento se aplica en diversos contextos:</p><ul><li>En la vida cotidiana</li><li>En el ámbito profesional</li><li>En la resolución de problemas</li><li>En proyectos creativos</li></ul><p>Los estudiantes deben identificar estas aplicaciones para comprender la relevancia del tema.</p>",
                    "imagen_sugerida": "Ejemplos de aplicación de {tema}"
                }}
            ],
            "actividades": [
                "Investigación grupal sobre casos reales relacionados con el tema",
                "Creación de un mapa mental con los conceptos principales",
                "Debate estructurado sobre las implicaciones del tema",
                "Proyecto práctico aplicando los conocimientos adquiridos",
                "Presentación de hallazgos ante la clase"
            ],
            "evaluacion": {{
                "preguntas": [
                    {{
                        "pregunta": "¿Cuáles son los conceptos fundamentales del tema?",
                        "opciones": ["Definiciones básicas", "Principios avanzados", "Aplicaciones específicas", "Todas las anteriores"],
                        "respuesta_correcta": "Todas las anteriores"
                    }},
                    {{
                        "pregunta": "¿Por qué es importante este tema en el curriculum educativo?",
                        "opciones": ["Desarrolla competencias básicas", "Prepara para estudios superiores", "Tiene aplicaciones prácticas", "Todas las anteriores"],
                        "respuesta_correcta": "Todas las anteriores"
                    }},
                    {{
                        "pregunta": "¿Cuál es la mejor manera de aplicar estos conocimientos?",
                        "opciones": ["Solo en teoría", "En proyectos prácticos", "Memorizando conceptos", "Evitando la práctica"],
                        "respuesta_correcta": "En proyectos prácticos"
                    }}
                ]
            }}
        }}"""

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
            logger.info("🤖 Generando HTML con CSS adaptativo y contenido completo...")
            html_content = self.generate_content(
                prompt=html_prompt,
                max_tokens=8000,
                temperature=0.7
            )
            
            if not html_content or html_content.startswith("Error:"):
                logger.error(f"❌ Error en generación: {html_content}")
                return self._create_simple_fallback_html(topic, grade_level, course)
            
            # VALIDACIÓN CRÍTICA: Verificar que el contenido está completo
            logger.info("🔍 Validando completitud del contenido educativo...")
            
            # Verificar longitud mínima del contenido
            if len(html_content.strip()) < 500:
                logger.warning("⚠️ CONTENIDO MUY CORTO - Regenerando con prompt extendido...")
                
                # Prompt más específico para contenido extenso
                extended_prompt = f"""
INSTRUCCIONES ESPECÍFICAS:
- Genera contenido HTML COMPLETO y EXTENSO sobre "{topic}" para {grade_level}
- El contenido debe tener al menos 2000 palabras
- Incluye teoría detallada, múltiples ejemplos y ejercicios variados
- NO uses frases como "aquí va el contenido" o "completar más tarde"

TEMA: {topic}
GRADO: {grade_level}
CURSO: {course}

ESTRUCTURA REQUERIDA:
1. Introducción completa al tema (mínimo 3 párrafos)
2. Teoría fundamental con explicaciones detalladas
3. Al menos 3 ejemplos resueltos paso a paso
4. Ejercicios prácticos con diferentes niveles de dificultad
5. Actividades complementarias
6. Resumen y conclusiones

Genera contenido HTML educativo COMPLETO y EXTENSO:
"""
                
                html_content = self.generate_content(
                    prompt=extended_prompt,
                    max_tokens=8000,
                    temperature=0.7
                )
            
            # Validar si el contenido sigue siendo muy corto
            if len(html_content.strip()) < 800:
                logger.error("⚠️ CONTENIDO SIGUE INCOMPLETO - Usando fallback completo")
                return self._create_comprehensive_fallback_html(topic, grade_level, course)
            
            # Validar que el HTML es completo y limpio
            validated_html = self._validate_and_clean_direct_html(html_content)
            
            logger.info(f"✅ HTML completo validado generado: {len(validated_html)} caracteres")
            return validated_html
                
        except Exception as e:
            logger.exception(f"❌ Error crítico en generate_content_for_grapesjs: {str(e)}")
            return self._create_simple_fallback_html(topic, grade_level, course)

    def _validate_html_content(self, html_content: str) -> bool:
        """Valida que el HTML sea adecuado para GrapesJS y que tenga contenido educativo completo"""
        try:
            # Verificaciones técnicas básicas
            basic_checks = {
                'has_content': len(html_content.strip()) > 500,  # Mínimo 500 caracteres para contenido completo
                'has_body_structure': '<body>' in html_content and '</body>' in html_content,
                'has_css_styles': '<style>' in html_content and '</style>' in html_content,
                'no_script_tags': '<script>' not in html_content,
                'proper_encoding': 'charset=UTF-8' in html_content
            }
            
            # Verificaciones de contenido educativo COMPLETO
            content_checks = {
                'has_main_container': 'main-container' in html_content or '<main' in html_content,
                'has_educational_content': any(word in html_content.lower() for word in ['teoría', 'ejemplo', 'ejercicio', 'actividad', 'definición']),
                'not_empty_containers': '</div>' not in html_content or html_content.count('</div>') < html_content.count('<div'),
                'has_multiple_sections': html_content.count('<h') >= 3,  # Al menos 3 títulos/subtítulos
                'substantial_text': len(html_content) > 2000  # Contenido sustancial
            }
            
            # Verificaciones críticas - detectar contenido incompleto
            completeness_checks = {
                'no_empty_main': 'main-container"></div>' not in html_content and 'main-container"></main>' not in html_content,
                'no_placeholder_text': 'contenido aquí' not in html_content.lower() and 'content here' not in html_content.lower(),
                'no_todo_comments': '<!-- TODO' not in html_content and '<!-- FIXME' not in html_content
            }
            
            all_checks = {**basic_checks, **content_checks, **completeness_checks}
            passed_checks = sum(all_checks.values())
            total_checks = len(all_checks)
            
            logger.info(f"📊 Validación HTML completa: {passed_checks}/{total_checks} checks pasados")
            
            # Log detallado de verificaciones
            for category, checks in [('Básicas', basic_checks), ('Contenido', content_checks), ('Completitud', completeness_checks)]:
                logger.info(f"  📋 {category}:")
                for check, result in checks.items():
                    logger.info(f"     {'✅' if result else '❌'} {check}")
            
            # Detectar contenido específicamente incompleto
            if not content_checks['has_educational_content']:
                logger.error("⚠️ CONTENIDO INCOMPLETO: No se detectó contenido educativo real")
                return False
                
            if not completeness_checks['no_empty_main']:
                logger.error("⚠️ CONTENIDO INCOMPLETO: Contenedor principal vacío detectado")
                return False
            
            # Requiere al menos 85% de checks para considerar válido
            return passed_checks >= (total_checks * 0.85)
            
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

⚠️ OBLIGATORIO: Debes generar TODO EL CONTENIDO EDUCATIVO COMPLETO sobre "{topic}"
⚠️ NO dejes contenedores vacíos - llena TODAS las secciones con contenido real
⚠️ Incluye mínimo 8 párrafos de explicación teórica sobre el tema
⚠️ Incluye mínimo 5 ejemplos prácticos con desarrollo completo
⚠️ Incluye mínimo 4 actividades detalladas para estudiantes

ESTRUCTURA HTML OBLIGATORIA:
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {content_type_name}</title>
    <style>
        /* CSS ADAPTATIVO COMPLETO AQUÍ */
    </style>
</head>
<body>
    <!-- CONTENIDO EDUCATIVO COMPLETO Y ESTRUCTURADO -->
    <main class="main-container">
        <header class="content-header">
            <h1>{topic}</h1>
            <p class="course-info">{course} - {grade_level}</p>
        </header>
        
        <!-- AQUÍ DEBES GENERAR TODO EL CONTENIDO EDUCATIVO REAL -->
        <!-- NO DEJES ESTA SECCIÓN VACÍA -->
        <!-- INCLUYE: teoría, ejemplos, ejercicios, actividades -->
        
    </main>
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

CONTENIDO EDUCATIVO OBLIGATORIO:
📚 TEORÍA: Explicación completa del tema "{topic}" con mínimo 8 párrafos
💡 EJEMPLOS: Mínimo 5 ejemplos resueltos paso a paso
🎯 EJERCICIOS: Mínimo 6 ejercicios para que resuelvan los estudiantes
🔬 EXPERIMENTOS/ACTIVIDADES: Mínimo 4 actividades prácticas detalladas
📊 EVALUACIÓN: Criterios de evaluación y rúbrica
🌍 APLICACIONES: Usos en la vida real del tema
📖 GLOSARIO: Términos importantes con definiciones
🔗 RECURSOS: Referencias y enlaces para profundizar

⚠️ CRÍTICO: La sección <main class="main-container"> DEBE estar LLENA de contenido educativo real.
⚠️ NO generes HTML con contenedores vacíos o placeholder de "contenido aquí"
⚠️ TODO el contenido debe ser específico sobre "{topic}" en {course}

{f"INSTRUCCIONES ADICIONALES DEL PROFESOR: {additional_instructions}" if additional_instructions else ""}

IMPORTANTE: Responde ÚNICAMENTE con el código HTML completo y válido que incluya TODO EL CONTENIDO EDUCATIVO, sin explicaciones adicionales ni texto fuera del HTML.
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
        <div class="content-section">
            <h2>📚 Teoría Fundamental</h2>
            <p><strong>{topic}</strong> es un tema esencial en {course} para estudiantes de {grade_level}. Este concepto forma parte del currículo básico y requiere comprensión profunda para el éxito académico.</p>
            <p>Los aspectos más importantes incluyen la comprensión de definiciones básicas, el dominio de conceptos fundamentales, y la capacidad de aplicar estos conocimientos en situaciones prácticas.</p>
            <p>Es fundamental establecer una base sólida en este tema para poder avanzar a conceptos más complejos en futuros niveles educativos.</p>
        </div>
        
        <div class="content-section">
            <h2>💡 Ejemplos Prácticos</h2>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50;">
                <h3>Ejemplo 1: Aplicación Básica</h3>
                <p>Para entender mejor {topic}, consideremos este ejemplo práctico:</p>
                <p><strong>Planteamiento:</strong> Identificar los elementos principales del tema.</p>
                <p><strong>Desarrollo:</strong> Aplicar los conceptos paso a paso.</p>
                <p><strong>Solución:</strong> Verificar el resultado obtenido.</p>
            </div>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50;">
                <h3>Ejemplo 2: Caso Avanzado</h3>
                <p>Un ejemplo más complejo nos permite profundizar en la aplicación de {topic}:</p>
                <p>Este caso requiere análisis más detallado y aplicación de múltiples conceptos relacionados.</p>
            </div>
        </div>
        
        <div class="content-section">
            <h2>✏️ Ejercicios para Practicar</h2>
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
                <h3>Ejercicio 1</h3>
                <p><strong>Problema:</strong> Resuelve la siguiente situación aplicando los conceptos de {topic}.</p>
                <p><strong>Instrucciones:</strong> Sigue los pasos metodológicos aprendidos y muestra tu procedimiento.</p>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
                <h3>Ejercicio 2</h3>
                <p><strong>Desafío:</strong> Analiza el siguiente caso y propón una solución creativa.</p>
                <p><strong>Objetivo:</strong> Demostrar comprensión profunda del tema.</p>
            </div>
        </div>
        
        <div class="content-section">
            <h2>🎯 Actividades de Aprendizaje</h2>
            <div style="background: #ffe6e6; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #FF6B6B;">
                <h3>Actividad 1: Investigación</h3>
                <p>Investiga aplicaciones de {topic} en la vida cotidiana y presenta tus hallazgos.</p>
                <p><strong>Tiempo estimado:</strong> 20 minutos</p>
            </div>
            
            <div style="background: #ffe6e6; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #FF6B6B;">
                <h3>Actividad 2: Análisis Colaborativo</h3>
                <p>Trabaja en equipo para resolver problemas complejos relacionados con {topic}.</p>
                <p><strong>Metodología:</strong> Aprendizaje colaborativo y discusión dirigida.</p>
            </div>
        </div>
        
        <div class="content-section">
            <h2>📊 Evaluación del Aprendizaje</h2>
            <p><strong>Criterios de Evaluación:</strong></p>
            <ul>
                <li>Comprensión conceptual de {topic} (30%)</li>
                <li>Aplicación práctica en ejercicios (40%)</li>
                <li>Análisis y reflexión crítica (20%)</li>
                <li>Participación en actividades (10%)</li>
            </ul>
            
            <p><strong>Instrumentos de Evaluación:</strong></p>
            <ul>
                <li>Prueba escrita sobre conceptos fundamentales</li>
                <li>Resolución de ejercicios prácticos</li>
                <li>Presentación oral de investigación</li>
                <li>Autoevaluación y coevaluación</li>
            </ul>
        </div>
        
        <div class="content-section">
            <h2>🌍 Aplicaciones en la Vida Real</h2>
            <p>El conocimiento de {topic} tiene múltiples aplicaciones prácticas:</p>
            <ul>
                <li>En el ámbito profesional y laboral</li>
                <li>En la resolución de problemas cotidianos</li>
                <li>Como base para estudios superiores</li>
                <li>En el desarrollo del pensamiento crítico</li>
            </ul>
        </div>
        
        <div class="content-section">
            <h2>📚 Recursos Adicionales</h2>
            <p>Para profundizar en el estudio de {topic}, se recomienda:</p>
            <ul>
                <li>Consultar libros de texto especializados</li>
                <li>Revisar recursos educativos en línea</li>
                <li>Practicar con ejercicios adicionales</li>
                <li>Participar en grupos de estudio</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

    def _create_comprehensive_fallback_html(self, topic: str, grade_level: str, course: str) -> str:
        """
        Crea HTML de fallback extenso y completo cuando todas las generaciones fallan
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - Material Educativo Completo</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.7;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        .main-container {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        h1 {{ margin: 0; font-size: 2.5em; }}
        .subtitle {{ margin: 10px 0 0 0; opacity: 0.9; }}
        h2 {{ 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        h3 {{ color: #34495e; margin-top: 25px; }}
        .section {{ margin: 35px 0; }}
        .intro-box {{
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .theory-section {{
            background: #f8f9fa;
            padding: 25px;
            border-left: 5px solid #3498db;
            margin: 20px 0;
        }}
        .example {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #16a085;
        }}
        .exercise {{
            background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #e74c3c;
        }}
        .activity {{
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #f39c12;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #81ecec 0%, #74b9ff 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        ul, ol {{ padding-left: 30px; }}
        li {{ margin: 10px 0; }}
        .highlight {{ 
            background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
            color: white;
            padding: 3px 8px; 
            border-radius: 5px;
            font-weight: bold;
        }}
        .step {{
            background: #e8f4f8;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #0984e3;
        }}
        .tips {{
            background: #fff5cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #f39c12;
            margin: 20px 0;
        }}
        @media (max-width: 768px) {{
            .main-container {{ padding: 20px; }}
            body {{ padding: 10px; }}
            h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header">
            <h1>{topic}</h1>
            <p class="subtitle">Material Educativo para {grade_level} - {course}</p>
        </div>
        
        <div class="intro-box">
            <h2 style="color: white; border: none; margin-top: 0;">🎯 Introducción al Tema</h2>
            <p>Bienvenido al estudio de <strong>{topic}</strong>. Este tema es fundamental en el desarrollo de tus competencias académicas y te proporcionará las bases necesarias para comprender conceptos más avanzados.</p>
            <p>A lo largo de este material, exploraremos los aspectos teóricos y prácticos, con ejemplos detallados y ejercicios que te ayudarán a consolidar tu aprendizaje.</p>
            <p>Es importante que dediques tiempo suficiente a cada sección y practiques con los ejercicios propuestos para obtener el máximo beneficio de este contenido educativo.</p>
        </div>

        <div class="section">
            <h2>📚 Fundamentos Teóricos</h2>
            <div class="theory-section">
                <h3>Conceptos Fundamentales</h3>
                <p>Para comprender completamente <span class="highlight">{topic}</span>, es esencial dominar los siguientes conceptos básicos:</p>
                <ul>
                    <li><strong>Definición principal:</strong> {topic} se refiere a los principios y métodos fundamentales que rigen esta área de conocimiento.</li>
                    <li><strong>Características clave:</strong> Los elementos distintivos que definen y caracterizan este tema.</li>
                    <li><strong>Principios básicos:</strong> Las reglas fundamentales que guían la aplicación práctica.</li>
                    <li><strong>Aplicaciones:</strong> Los contextos donde estos conocimientos resultan útiles y necesarios.</li>
                </ul>
                
                <h3>Importancia en el Contexto Académico</h3>
                <p>Este tema ocupa un lugar central en el curriculum de {course} porque:</p>
                <ol>
                    <li>Proporciona las bases teóricas necesarias para temas más avanzados</li>
                    <li>Desarrolla habilidades de pensamiento crítico y análisis</li>
                    <li>Conecta conocimientos previos con nuevos aprendizajes</li>
                    <li>Prepara para aplicaciones prácticas en situaciones reales</li>
                </ol>
            </div>
        </div>

        <div class="section">
            <h2>💡 Ejemplos Detallados</h2>
            
            <div class="example">
                <h3>Ejemplo 1: Aplicación Básica</h3>
                <p>Consideremos una situación práctica donde aplicamos los conceptos de {topic}:</p>
                <div class="step">
                    <strong>Paso 1:</strong> Identificación del problema
                    <p>Primero, debemos reconocer cuándo estamos ante una situación que requiere aplicar {topic}.</p>
                </div>
                <div class="step">
                    <strong>Paso 2:</strong> Análisis de componentes
                    <p>Descomponemos el problema en sus elementos fundamentales para una mejor comprensión.</p>
                </div>
                <div class="step">
                    <strong>Paso 3:</strong> Aplicación de principios
                    <p>Utilizamos los conceptos teóricos aprendidos para resolver la situación planteada.</p>
                </div>
                <div class="step">
                    <strong>Paso 4:</strong> Verificación de resultados
                    <p>Comprobamos que nuestra solución es correcta y coherente con los principios estudiados.</p>
                </div>
            </div>

            <div class="example">
                <h3>Ejemplo 2: Aplicación Intermedia</h3>
                <p>En este ejemplo más complejo, veremos cómo {topic} se integra con otros conocimientos:</p>
                <p>La comprensión profunda de este tema nos permite abordar problemas multidisciplinarios donde se combinan diferentes áreas del conocimiento.</p>
                <div class="tips">
                    <strong>💡 Consejo importante:</strong> Siempre relaciona los conceptos nuevos con conocimientos previos para crear conexiones significativas en tu aprendizaje.
                </div>
            </div>

            <div class="example">
                <h3>Ejemplo 3: Aplicación Avanzada</h3>
                <p>Para estudiantes que deseen profundizar, este ejemplo muestra aplicaciones más sofisticadas:</p>
                <p>Las aplicaciones avanzadas de {topic} requieren integrar múltiples conceptos y desarrollar soluciones creativas e innovadoras.</p>
            </div>
        </div>

        <div class="section">
            <h2>🏋️‍♂️ Ejercicios Prácticos</h2>
            
            <div class="exercise">
                <h3>Ejercicio 1: Comprensión Básica</h3>
                <p><strong>Objetivo:</strong> Verificar la comprensión de conceptos fundamentales</p>
                <ol>
                    <li>Define con tus propias palabras qué es {topic}</li>
                    <li>Menciona al menos tres características principales</li>
                    <li>Explica por qué es importante este tema en {course}</li>
                    <li>Identifica dos aplicaciones prácticas en la vida cotidiana</li>
                </ol>
                <div class="tips">
                    <strong>Sugerencia:</strong> Utiliza ejemplos concretos para ilustrar tus respuestas.
                </div>
            </div>

            <div class="exercise">
                <h3>Ejercicio 2: Análisis y Aplicación</h3>
                <p><strong>Objetivo:</strong> Desarrollar habilidades de análisis crítico</p>
                <ol>
                    <li>Analiza una situación real donde se aplique {topic}</li>
                    <li>Identifica los elementos clave presentes en esa situación</li>
                    <li>Propone una solución basada en los conceptos estudiados</li>
                    <li>Justifica tu propuesta con argumentos sólidos</li>
                </ol>
            </div>

            <div class="exercise">
                <h3>Ejercicio 3: Síntesis y Creatividad</h3>
                <p><strong>Objetivo:</strong> Integrar conocimientos y desarrollar pensamiento creativo</p>
                <ol>
                    <li>Crea un mapa conceptual que relacione {topic} con otros temas del curso</li>
                    <li>Diseña un mini-proyecto que demuestre la aplicación práctica</li>
                    <li>Elabora una presentación de 5 minutos sobre los aspectos más importantes</li>
                    <li>Propón tres preguntas de investigación relacionadas con el tema</li>
                </ol>
            </div>
        </div>

        <div class="summary-box">
            <h2 style="color: white; border: none; margin-top: 0;">📋 Resumen y Conclusiones</h2>
            <p>En este material hemos explorado los aspectos fundamentales de <strong>{topic}</strong>, un tema central en {course} para estudiantes de {grade_level}.</p>
            <p><strong>Puntos clave para recordar:</strong></p>
            <ul>
                <li>Los conceptos fundamentales y su importancia en el contexto académico</li>
                <li>Las aplicaciones prácticas y su relevancia en situaciones reales</li>
                <li>Las conexiones con otros temas y áreas del conocimiento</li>
                <li>Las habilidades desarrolladas a través del estudio de este tema</li>
            </ul>
            <p><strong>Próximos pasos:</strong> Continúa practicando con los ejercicios propuestos y no dudes en consultar fuentes adicionales para profundizar tu comprensión. El dominio de {topic} te proporcionará una base sólida para avanzar en tus estudios.</p>
        </div>

        <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <p><em>Material educativo generado para apoyar tu proceso de aprendizaje</em></p>
            <p><strong>{course} - {grade_level}</strong></p>
        </div>
    </div>
</body>
</html>"""

# Alias para mantener compatibilidad con código existente
OpenAIService = DeepSeekService
