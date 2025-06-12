import os
import shutil
import zipfile
import tempfile
import logging
import uuid
import re
import urllib.parse
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

class ScormGenerator:
    """
    Servicio para generar paquetes SCORM a partir de contenido HTML editado
    Soporta SCORM 1.2
    """
    
    def __init__(self):
        self.temp_dir = None
        self.resource_files = []
        self.title = "Contenido Educativo"
        self.identifier = str(uuid.uuid4())
        
    def generate_scorm_package(self, contenido, output_path=None):
        """
        Genera un paquete SCORM a partir de un objeto ContenidoInteractivo
        """
        try:
            # Crear un directorio temporal para trabajar
            self.temp_dir = tempfile.mkdtemp(prefix='scorm_')
            
            # Preparar datos
            self.title = contenido.titulo
            self.identifier = f"content_{contenido.id}".replace('-', '_')
            
            # Extraer y guardar recursos del HTML
            html_content = self._process_html(contenido.contenido_html)
            
            # Crear archivos necesarios para SCORM
            self._create_scorm_files(html_content)
            
            # Crear el archivo ZIP (paquete SCORM)
            if output_path is None:
                output_file = ContentFile(b'')
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self._add_directory_to_zip(self.temp_dir, zipf)
                return output_file
            else:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    self._add_directory_to_zip(self.temp_dir, zipf)
                return output_path
                
        except Exception as e:
            logger.exception(f"Error al generar paquete SCORM: {str(e)}")
            return None
            
        finally:
            # Limpiar el directorio temporal
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def _process_html(self, html_content):
        """
        Procesa el HTML para identificar y guardar recursos (imágenes, etc.)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Procesar imágenes
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and (src.startswith('http://') or src.startswith('https://') or src.startswith('data:')):
                new_src = self._save_external_resource(src)
                if new_src:
                    img['src'] = new_src
        
        # Procesar archivos CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href and (href.startswith('http://') or href.startswith('https://')):
                new_href = self._save_external_resource(href)
                if new_href:
                    link['href'] = new_href
        
        # Procesar archivos JavaScript
        for script in soup.find_all('script', src=True):
            src = script.get('src', '')
            if src and (src.startswith('http://') or src.startswith('https://')):
                new_src = self._save_external_resource(src)
                if new_src:
                    script['src'] = new_src
        
        # Agregar los estilos y scripts necesarios para SCORM
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
            else:
                html = soup.new_tag('html')
                html.append(head)
                soup.append(html)
        
        # Agregar scripts de SCORM
        script_tag = soup.new_tag('script')
        script_tag['src'] = 'scorm_api.js'
        head.append(script_tag)
        
        # Agregar CSS básico
        style_tag = soup.new_tag('style')
        style_tag.string = """
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        img { max-width: 100%; height: auto; }
        h1, h2, h3 { color: #333; }
        a { color: #0066cc; }
        .container { max-width: 960px; margin: 0 auto; }
        """
        head.append(style_tag)
        
        # Asegurar estructura HTML correcta
        if not soup.find('body'):
            body = soup.new_tag('body')
            content_div = soup.new_tag('div')
            content_div['class'] = 'container'
            
            # Mover todo el contenido al div
            for child in list(soup.children):
                if child.name not in ['html', 'head']:
                    content_div.append(child.extract())
            
            body.append(content_div)
            
            if soup.html:
                soup.html.append(body)
            else:
                html = soup.new_tag('html')
                html.append(body)
                soup.append(html)
        
        return str(soup)
    
    def _save_external_resource(self, url):
        """
        Descarga y guarda un recurso externo (imagen, CSS, JS)
        """
        if url.startswith('data:'):
            # Procesar URLs de datos (base64)
            match = re.match(r'data:([^;]+);base64,(.+)', url)
            if match:
                mime_type, data = match.groups()
                import base64
                try:
                    ext = mime_type.split('/')[-1]
                    filename = f"resource_{len(self.resource_files)}.{ext}"
                    file_path = os.path.join(self.temp_dir, filename)
                    
                    # Decodificar y guardar
                    with open(file_path, 'wb') as f:
                        f.write(base64.b64decode(data))
                    
                    self.resource_files.append(filename)
                    return filename
                except Exception as e:
                    logger.error(f"Error al procesar URL data: {str(e)}")
                    return url
        
        else:
            # Procesar URLs externas
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Obtener nombre de archivo de la URL
                    parsed_url = urllib.parse.urlparse(url)
                    path = parsed_url.path
                    filename = os.path.basename(path)
                    
                    # Si no tiene extensión o es muy largo, usar uno genérico
                    if not filename or len(filename) > 50:
                        ext = self._get_extension_from_content_type(response.headers.get('Content-Type', ''))
                        filename = f"resource_{len(self.resource_files)}.{ext}"
                    
                    file_path = os.path.join(self.temp_dir, filename)
                    
                    # Guardar archivo
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.resource_files.append(filename)
                    return filename
                else:
                    logger.error(f"Error al descargar recurso {url}: HTTP {response.status_code}")
                    return url
            except Exception as e:
                logger.error(f"Error al descargar recurso {url}: {str(e)}")
                return url
    
    def _get_extension_from_content_type(self, content_type):
        """
        Determina la extensión de archivo basada en el Content-Type
        """
        extensions = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/svg+xml': 'svg',
            'text/css': 'css',
            'application/javascript': 'js',
            'text/javascript': 'js',
            'application/pdf': 'pdf',
            'text/plain': 'txt',
            'application/zip': 'zip',
        }
        
        # Extraer el tipo MIME principal
        mime_type = content_type.split(';')[0].strip().lower()
        return extensions.get(mime_type, 'bin')
    
    def _create_scorm_files(self, html_content):
        """
        Crea los archivos necesarios para el paquete SCORM
        """
        # Crear archivo index.html
        with open(os.path.join(self.temp_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Crear archivo imsmanifest.xml
        manifest_content = render_to_string('content/scorm/imsmanifest.xml', {
            'identifier': self.identifier,
            'title': self.title,
            'resources': self.resource_files
        })
        
        with open(os.path.join(self.temp_dir, 'imsmanifest.xml'), 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        # Crear archivo scorm_api.js (API básica de SCORM)
        api_js_content = render_to_string('content/scorm/scorm_api.js')
        with open(os.path.join(self.temp_dir, 'scorm_api.js'), 'w', encoding='utf-8') as f:
            f.write(api_js_content)
        
        # Copiar archivos adicionales necesarios para SCORM
        # (logos, esquemas XSD, etc.)
        static_scorm_dir = os.path.join(settings.STATIC_ROOT, 'content', 'scorm')
        if os.path.exists(static_scorm_dir):
            for item in os.listdir(static_scorm_dir):
                item_path = os.path.join(static_scorm_dir, item)
                if os.path.isfile(item_path):
                    shutil.copy(item_path, self.temp_dir)
    
    def _add_directory_to_zip(self, path, zipf, arcpath=''):
        """
        Agrega recursivamente un directorio a un archivo ZIP
        """
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join(arcpath, os.path.relpath(file_path, path))
                zipf.write(file_path, arcname=arcname)

# Instancia singleton para usar en toda la aplicación
scorm_generator = ScormGenerator() 