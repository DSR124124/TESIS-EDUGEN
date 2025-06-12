import requests
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def analizar_con_deepseek(texto_pdf):
    """
    Analiza el texto extraído de un PDF utilizando DeepSeek.
    
    Args:
        texto_pdf (str): Texto extraído del PDF
        
    Returns:
        str: Análisis generado por DeepSeek
    """
    # Conseguir la API key desde entorno o settings
    api_key = os.environ.get("DEEPSEEK_API_KEY") or getattr(settings, "DEEPSEEK_API_KEY", None)
    if not api_key:
        raise ValueError("No se encontró la clave API de DeepSeek")
    
    # Configuración de DeepSeek
    base_url = "https://api.deepseek.com/v1"
    model = getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat")
    
    # Prompt educativo especializado para el análisis
    system_prompt = """Eres un experto en pedagogía y diseño curricular con experiencia en analizar material educativo para EDUCACIÓN SECUNDARIA. 
Tu tarea es analizar el contenido educativo proporcionado (exámenes, materiales didácticos, resultados de evaluaciones, etc.) 
y extraer información relevante para ayudar a un docente de secundaria a generar contenido personalizado para adolescentes de 12-17 años.

Estructura tu análisis de manera concisa y útil con estos elementos específicos para EDUCACIÓN SECUNDARIA:

1. RESUMEN GENERAL: Síntesis breve del tipo de contenido y su propósito principal para secundaria.
2. TEMAS IDENTIFICADOS: Lista de temas principales apropiados para nivel secundario.
3. NIVEL DE DIFICULTAD: Evalúa si el material es apropiado para secundaria (básico, intermedio o avanzado dentro del nivel secundario).
4. COMPETENCIAS SECUNDARIAS: Identifica competencias específicas de educación secundaria que se desarrollan.
5. ÁREAS DE OPORTUNIDAD: Identifica áreas donde se necesita refuerzo en nivel secundario.
6. RECOMENDACIONES: Sugiere enfoques educativos específicos para adolescentes de secundaria.

Tu análisis debe ser directo, enfocado en la aplicación práctica para la creación de materiales educativos de NIVEL SECUNDARIO.
NO incluyas evaluaciones generales como "es un buen material" o frases sin valor concreto.
SÍ incluye EXACTAMENTE los elementos que encuentres en el material original que puedan ser relevantes para generar contenido de EDUCACIÓN SECUNDARIA.
IMPORTANTE: Todo el análisis debe estar enfocado en educación secundaria para adolescentes de 12-17 años.
"""
    
    user_prompt = f"""Analiza el siguiente contenido educativo extraído de un PDF y proporciona información estructurada 
que un docente de EDUCACIÓN SECUNDARIA pueda utilizar para generar materiales educativos personalizados y efectivos para adolescentes de 12-17 años:

====== CONTENIDO DEL PDF ======
{texto_pdf}
==============================

Proporciona SOLAMENTE información objetiva y útil sobre el contenido para NIVEL SECUNDARIO. No inventes información que no esté presente en el texto.
Mantén tu respuesta estructurada, concisa y directamente aplicable a la creación de contenido educativo para EDUCACIÓN SECUNDARIA.
Si el contenido no es apropiado para secundaria, adáptalo o sugiere cómo enfocarlo para este nivel educativo."""
    
    # Configurar datos para la petición a DeepSeek
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.5,  # Temperatura más baja para respuestas más precisas y menos creativas
        "max_tokens": 2000
    }
    
    try:
        logger.info(f"Analizando PDF con DeepSeek modelo: {model}")
        
        # Llamada a la API de DeepSeek
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            logger.info("Análisis con DeepSeek completado exitosamente")
            return content
        else:
            error_msg = f"Error de API DeepSeek: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                error_msg = f"{error_msg} - {response.text}"
            
            logger.error(f"Error en DeepSeek API: {error_msg}")
            return f"Error al analizar el contenido con DeepSeek: {error_msg}"
            
    except requests.exceptions.Timeout:
        logger.error("Timeout al conectar con DeepSeek API")
        return "Error: Tiempo de espera agotado al conectar con DeepSeek"
    except requests.exceptions.ConnectionError:
        logger.error("Error de conexión con DeepSeek API")
        return "Error: No se pudo conectar con DeepSeek"
    except Exception as e:
        logger.exception(f"Error inesperado al analizar con DeepSeek: {str(e)}")
        return f"Error inesperado al analizar el contenido: {str(e)}"


# Alias para mantener compatibilidad con código existente
analizar_con_openai = analizar_con_deepseek 