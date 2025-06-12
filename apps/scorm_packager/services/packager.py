import os
import uuid
import zipfile
import tempfile
import shutil
import logging
import re
from django.conf import settings
from django.template.loader import render_to_string
from bs4 import BeautifulSoup

# Configurar logger
logger = logging.getLogger(__name__)

class SCORMPackager:
    def __init__(self, content, metadata):
        self.original_content = content
        self.metadata = metadata
        self.temp_dir = None
        
        # Procesar contenido para evitar duplicaciones y preservar estilos
        self.processed_content = self._process_content_for_scorm(content)
        
        # Asegurar que tengamos valores predeterminados para todos los campos necesarios
        if 'title' not in self.metadata or not self.metadata['title']:
            self.metadata['title'] = 'Contenido Educativo'
        if 'description' not in self.metadata or not self.metadata['description']:
            self.metadata['description'] = 'Contenido generado automáticamente'
        if 'version' not in self.metadata:
            self.metadata['version'] = '1.0'
        if 'standard' not in self.metadata:
            self.metadata['standard'] = 'scorm_2004_4th'
            
        logger.info(f"SCORMPackager inicializado con metadata: {self.metadata}")
        
        # Comprobar que el directorio de medios existe
        scorm_dir = os.path.join(settings.MEDIA_ROOT, 'scorm_packages')
        if not os.path.exists(scorm_dir):
            try:
                os.makedirs(scorm_dir, exist_ok=True)
                logger.info(f"Directorio para paquetes SCORM creado: {scorm_dir}")
            except Exception as e:
                logger.error(f"Error al crear directorio SCORM: {str(e)}")
    
    def create_package(self):
        # Crear directorio temporal
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Directorio temporal creado: {self.temp_dir}")
        
        try:
            # Crear estructura de archivos SCORM
            self._create_content_files()
            self._create_manifest()
            
            # Empaquetar como ZIP
            package_path = self._create_zip()
            logger.info(f"Paquete SCORM creado exitosamente en: {package_path}")
            
            return package_path
        except Exception as e:
            logger.exception(f"Error al crear paquete SCORM: {str(e)}")
            # Crear un paquete de respaldo mínimo en caso de error
            try:
                fallback_path = self._create_fallback_package()
                logger.warning(f"Se creó un paquete de respaldo debido a errores: {fallback_path}")
                return fallback_path
            except Exception as e2:
                logger.exception(f"Error al crear paquete de respaldo: {str(e2)}")
                raise
        finally:
            # Limpiar archivos temporales
            try:
                if self.temp_dir and os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                    logger.info(f"Directorio temporal limpiado: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Error al limpiar directorio temporal: {str(e)}")
    
    def _create_fallback_package(self):
        """Crear un paquete SCORM mínimo en caso de error"""
        # Crear un nuevo directorio temporal
        backup_temp_dir = tempfile.mkdtemp()
        logger.info(f"Creando paquete de respaldo en: {backup_temp_dir}")
        
        try:
            # Crear un archivo HTML simple
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{self.metadata['title']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                </style>
            </head>
            <body>
                <h1>{self.metadata['title']}</h1>
                <div>{self.content}</div>
                <p style="margin-top: 20px; color: #999;">Este es un paquete SCORM mínimo generado automáticamente.</p>
            </body>
            </html>"""
            
            with open(os.path.join(backup_temp_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Crear un archivo manifest simple
            manifest_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <manifest identifier="{uuid.uuid4()}" version="1.0" 
                    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1">
            <metadata>
                <schema>ADL SCORM</schema>
                <schemaversion>2004 4th Edition</schemaversion>
            </metadata>
            <organizations default="default_org">
                <organization identifier="default_org">
                <title>{self.metadata['title']}</title>
                <item identifier="item_1" identifierref="resource_1">
                    <title>{self.metadata['title']}</title>
                </item>
                </organization>
            </organizations>
            <resources>
                <resource identifier="resource_1" type="webcontent" href="index.html">
                <file href="index.html"/>
                </resource>
            </resources>
            </manifest>"""
            
            with open(os.path.join(backup_temp_dir, 'imsmanifest.xml'), 'w', encoding='utf-8') as f:
                f.write(manifest_content)
            
            # Crear el archivo ZIP
            output_filename = f"fallback_{uuid.uuid4()}.zip"
            output_path = os.path.join(settings.MEDIA_ROOT, 'scorm_packages', output_filename)
            
            with zipfile.ZipFile(output_path, 'w') as zipf:
                for root, dirs, files in os.walk(backup_temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_temp_dir)
                        zipf.write(file_path, arcname)
            
            return output_path
        finally:
            # Limpiar
            if backup_temp_dir and os.path.exists(backup_temp_dir):
                shutil.rmtree(backup_temp_dir)
    
    def _create_content_files(self):
        # Crear index.html y otros archivos necesarios
        try:
            logger.info("Generando archivo index.html para el paquete SCORM")
            # Intentar primero con la ruta absoluta
            index_html = render_to_string('apps/scorm_packager/templates/scorm/index.html', {
                'title': self.metadata['title'],
                'content': self.processed_content['html'],
                'content_styles': self.processed_content['styles']
            })
            logger.debug("Template index.html renderizado correctamente con ruta absoluta")
        except Exception as e:
            logger.warning(f"Error al renderizar plantilla con ruta absoluta: {str(e)}")
            # Si falla, intentar con la ruta relativa
            try:
                index_html = render_to_string('scorm/index.html', {
                    'title': self.metadata['title'],
                    'content': self.processed_content['html'],
                    'content_styles': self.processed_content['styles']
                })
                logger.debug("Template index.html renderizado correctamente con ruta relativa")
            except Exception as e2:
                logger.warning(f"Error al renderizar plantilla con ruta relativa: {str(e2)}")
                # Si todavía falla, usar una versión simple predeterminada
                logger.info("Utilizando plantilla HTML predeterminada")
                index_html = f"""<!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{self.metadata['title']}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                        h1 {{ color: #333; margin-bottom: 1em; }}
                        .content {{ max-width: 100%; overflow-x: auto; }}
                        img {{ max-width: 100%; height: auto; }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        {self.processed_content['styles']}
                    </style>
                    <script type="text/javascript" src="scorm_api.js"></script>
                </head>
                <body>
                    <h1>{self.metadata['title']}</h1>
                    <div class="content">{self.processed_content['html']}</div>
                </body>
                </html>"""
        
        with open(os.path.join(self.temp_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
            logger.debug(f"Archivo index.html guardado en: {os.path.join(self.temp_dir, 'index.html')}")
        
        # Verificar que existen los archivos estáticos y copiarlos
        try:
            logger.info("Copiando archivos estáticos para el paquete SCORM")
            # Intentar primero con la ruta absoluta
            static_path = os.path.join(settings.BASE_DIR, 'apps/scorm_packager/static/scorm')
            logger.debug(f"Buscando archivos estáticos en: {static_path}")
            
            if not os.path.exists(static_path):
                logger.warning(f"Ruta de archivos estáticos no encontrada: {static_path}")
                # Si no existe, intentar con la ruta relativa
                static_path = os.path.join(settings.STATIC_ROOT, 'scorm')
                logger.debug(f"Buscando archivos estáticos en ruta alternativa: {static_path}")
                
                if not os.path.exists(static_path):
                    logger.warning(f"Ruta alternativa de archivos estáticos no encontrada: {static_path}")
                    # Si ninguna ruta existe, crear archivos mínimos
                    logger.info("Creando archivos estáticos predeterminados")
                    self._create_fallback_static_files()
                    return
            
            for filename in ['scorm_api.js', 'styles.css']:
                src = os.path.join(static_path, filename)
                if os.path.exists(src):
                    dst = os.path.join(self.temp_dir, filename)
                    shutil.copy(src, dst)
                    logger.debug(f"Archivo estático copiado: {src} -> {dst}")
                else:
                    logger.warning(f"Archivo estático no encontrado: {src}")
                    self._create_fallback_static_file(filename)
        except Exception as e:
            logger.exception(f"Error al copiar archivos estáticos: {str(e)}")
            # En caso de error, crear archivos mínimos
            self._create_fallback_static_files()
            
    def _create_manifest(self):
        # Crear el archivo imsmanifest.xml
        try:
            logger.info("Generando archivo imsmanifest.xml para el paquete SCORM")
            # Generar identificador único 
            identifier = str(uuid.uuid4())
            
            # Intentar primero con la ruta absoluta
            manifest_xml = render_to_string('apps/scorm_packager/templates/scorm/imsmanifest.xml', {
                'identifier': identifier,
                'title': self.metadata['title'],
                'description': self.metadata.get('description', ''),
                'version': self.metadata.get('version', '1.0'),
                'standard': self.metadata.get('standard', 'scorm_2004_4th')
            })
            logger.debug("Template imsmanifest.xml renderizado correctamente con ruta absoluta")
        except Exception as e:
            logger.warning(f"Error al renderizar plantilla de manifiesto con ruta absoluta: {str(e)}")
            # Si falla, intentar con la ruta relativa
            try:
                manifest_xml = render_to_string('scorm/imsmanifest.xml', {
                    'identifier': identifier,
                    'title': self.metadata['title'],
                    'description': self.metadata.get('description', ''),
                    'version': self.metadata.get('version', '1.0'),
                    'standard': self.metadata.get('standard', 'scorm_2004_4th')
                })
                logger.debug("Template imsmanifest.xml renderizado correctamente con ruta relativa")
            except Exception as e2:
                logger.warning(f"Error al renderizar plantilla de manifiesto con ruta relativa: {str(e2)}")
                # Si todavía falla, usar una versión simple predeterminada
                logger.info("Utilizando plantilla de manifiesto predeterminada")
                manifest_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{identifier}" version="1.0" 
          xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
          xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"
          xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p3"
          xmlns:imsss="http://www.imsglobal.org/xsd/imsss"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd
                              http://www.adlnet.org/xsd/adlcp_v1p3 adlcp_v1p3.xsd
                              http://www.adlnet.org/xsd/adlseq_v1p3 adlseq_v1p3.xsd
                              http://www.adlnet.org/xsd/adlnav_v1p3 adlnav_v1p3.xsd
                              http://www.imsglobal.org/xsd/imsss imsss_v1p0.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>2004 4th Edition</schemaversion>
  </metadata>
  <organizations default="default_org">
    <organization identifier="default_org">
      <title>{self.metadata['title']}</title>
      <item identifier="item_1" identifierref="resource_1">
        <title>{self.metadata['title']}</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="resource_1" type="webcontent" adlcp:scormType="sco" href="index.html">
      <file href="index.html"/>
      <file href="scorm_api.js"/>
      <file href="styles.css"/>
    </resource>
  </resources>
</manifest>"""
        
        with open(os.path.join(self.temp_dir, 'imsmanifest.xml'), 'w', encoding='utf-8') as f:
            f.write(manifest_xml)
            logger.debug(f"Archivo imsmanifest.xml guardado en: {os.path.join(self.temp_dir, 'imsmanifest.xml')}")
    
    def _create_zip(self):
        # Crear archivo ZIP con todos los archivos
        output_filename = f"{uuid.uuid4()}.zip"
        output_path = os.path.join(settings.MEDIA_ROOT, 'scorm_packages', output_filename)
        
        logger.info(f"Creando archivo ZIP en: {output_path}")
        
        # Asegurar que el directorio existe
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logger.debug(f"Directorio para el ZIP creado: {os.path.dirname(output_path)}")
        except Exception as e:
            logger.error(f"Error al crear directorio para el ZIP: {str(e)}")
            raise
        
        try:
            with zipfile.ZipFile(output_path, 'w') as zipf:
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.temp_dir)
                        zipf.write(file_path, arcname)
                        logger.debug(f"Archivo añadido al ZIP: {arcname}")
            
            # Verificar que el archivo ZIP existe y tiene un tamaño razonable
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Archivo ZIP creado exitosamente: {output_path} ({os.path.getsize(output_path)} bytes)")
            else:
                logger.error(f"Error: El archivo ZIP no existe o está vacío: {output_path}")
                raise Exception("El archivo ZIP generado está vacío o no se creó correctamente")
                
            return output_path
        except Exception as e:
            logger.exception(f"Error al crear archivo ZIP: {str(e)}")
            raise 
    
    def _create_fallback_static_files(self):
        """Crear versiones mínimas de los archivos estáticos en caso de error"""
        logger.info("Creando archivos estáticos de respaldo")
        self._create_fallback_static_file('scorm_api.js')
        self._create_fallback_static_file('styles.css')
    
    def _create_fallback_static_file(self, filename):
        """Crear un archivo estático específico con contenido mínimo"""
        logger.info(f"Creando archivo estático de respaldo: {filename}")
        content = ""
        if filename == 'scorm_api.js':
            content = """// SCORM API Adapter (minimal version)
var API = null;
var API_1484_11 = null;

function findAPI(win) {
    if (win.API) return win.API;
    if (win.API_1484_11) return win.API_1484_11;
    if (win.parent && win.parent != win) return findAPI(win.parent);
    return null;
}

function initializeSCORM() {
    API = findAPI(window);
    if (API) {
        API.LMSInitialize("");
    }
}

function terminateSCORM() {
    if (API) {
        API.LMSFinish("");
    }
}

window.onload = initializeSCORM;
window.onunload = terminateSCORM;
"""
        elif filename == 'styles.css':
            content = """/* Minimal CSS */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    color: #333;
}
h1, h2, h3 {
    margin-top: 20px;
}
"""
        
        with open(os.path.join(self.temp_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
            logger.debug(f"Archivo estático de respaldo creado: {os.path.join(self.temp_dir, filename)}") 

    def _process_content_for_scorm(self, content):
        """
        Procesa el contenido para evitar duplicaciones de encabezados y preservar estilos
        """
        try:
            # Parsear el contenido HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extraer estilos inline del contenido original
            extracted_styles = self._extract_inline_styles(soup)
            
            # Detectar y remover encabezados institucionales duplicados
            self._remove_institutional_headers(soup)
            
            # Detectar si el contenido ya está en un HTML completo
            has_full_html = bool(soup.find('html') or soup.find('head') or soup.find('body'))
            
            if has_full_html:
                # Si ya es HTML completo, extraer solo el contenido del body
                body = soup.find('body')
                if body:
                    # Obtener todo el contenido del body excluyendo headers institucionales
                    content_html = str(body)
                    # Remover las etiquetas <body> pero mantener el contenido
                    content_html = re.sub(r'^<body[^>]*>', '', content_html)
                    content_html = re.sub(r'</body>$', '', content_html)
                else:
                    content_html = str(soup)
            else:
                # Si no es HTML completo, usar todo el contenido
                content_html = str(soup)
            
            # Crear diccionario con contenido procesado y estilos extraídos
            return {
                'html': content_html,
                'styles': extracted_styles,
                'has_native_styles': bool(extracted_styles)
            }
            
        except Exception as e:
            logger.warning(f"Error al procesar contenido para SCORM: {str(e)}")
            # Si hay error, retornar contenido original como fallback
            return {
                'html': content,
                'styles': '',
                'has_native_styles': False
            }

    def _extract_inline_styles(self, soup):
        """
        Extrae estilos inline y de etiquetas <style> del contenido original
        """
        extracted_styles = []
        
        # Extraer estilos de etiquetas <style>
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                extracted_styles.append(style_tag.string)
            # Remover la etiqueta style del contenido para evitar conflictos
            style_tag.decompose()
        
        # Extraer estilos CSS custom properties (variables CSS)
        for tag in soup.find_all(True):
            style_attr = tag.get('style', '')
            if style_attr and ('--' in style_attr or 'var(' in style_attr):
                # Preservar estilos con variables CSS
                extracted_styles.append(f".scorm-content {tag.name} {{ {style_attr} }}")
        
        return '\n'.join(extracted_styles)

    def _remove_institutional_headers(self, soup):
        """
        Detecta y remueve encabezados institucionales duplicados
        """
        # Patrones para detectar encabezados institucionales
        institutional_patterns = [
            r'INSTITUCIÓN EDUCATIVA',
            r'🎓.*INSTITUCIÓN.*EDUCATIVA',
            r'COLEGIO.*NACIONAL',
            r'I\.E\..*\d+',
            r'header-institucional',
            r'encabezado-institucional'
        ]
        
        # Buscar elementos que contengan patrones institucionales
        elements_to_remove = []
        
        for element in soup.find_all(True):
            # Verificar contenido de texto
            text_content = element.get_text().strip().upper()
            
            # Verificar clases CSS
            css_classes = ' '.join(element.get('class', []))
            
            # Verificar si coincide con algún patrón
            is_institutional = False
            
            for pattern in institutional_patterns:
                if re.search(pattern, text_content, re.IGNORECASE) or \
                   re.search(pattern, css_classes, re.IGNORECASE):
                    is_institutional = True
                    break
            
            # Si es un header/encabezado y contiene emoji de graduación
            if (element.name in ['header', 'h1', 'h2', 'div'] and 
                ('🎓' in text_content or 'graduation' in css_classes.lower())):
                is_institutional = True
            
            if is_institutional:
                elements_to_remove.append(element)
        
        # Remover elementos institucionales detectados
        for element in elements_to_remove:
            logger.info(f"Removiendo encabezado institucional detectado: {element.name} - {element.get_text()[:50]}...")
            element.decompose() 