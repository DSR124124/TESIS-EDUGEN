from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import os
import logging
from django.db import models
from django.conf import settings
import zipfile
import tempfile
import shutil
import uuid
import re
from io import BytesIO
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

from .models import SCORMPackage
from .services.validator import SCORMValidator
from .services.packager import SCORMPackager
from apps.ai_content_generator.models import GeneratedContent
from apps.academic.models import Student
from apps.portfolios.models import PortfolioMaterial

class SCORMPackageListView(LoginRequiredMixin, ListView):
    model = SCORMPackage
    template_name = 'scorm_packager/package_list.html'
    context_object_name = 'packages'
    
    def get_queryset(self):
        # Mostrar todos los paquetes SCORM disponibles para el usuario
        return SCORMPackage.objects.filter(
            generated_content__request__teacher=self.request.user
        ).select_related(
            'generated_content',
            'generated_content__request',
            'generated_content__request__teacher'
        ).order_by('-created_at')

class SCORMPackageDetailView(LoginRequiredMixin, DetailView):
    model = SCORMPackage
    template_name = 'scorm_packager/package_detail.html'
    context_object_name = 'package'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Validar el paquete SCORM
            validator = SCORMValidator(self.object.package_file.path)
            validation_result = validator.validate()
            
            context['validation'] = {
                'is_valid': True,
                'errors': [],
                'checks': [
                    {
                        'name': 'Archivo ZIP válido',
                        'result': True,
                        'description': 'El archivo es un ZIP válido que puede ser extraído.'
                    },
                    {
                        'name': 'Manifiesto SCORM',
                        'result': True,
                        'description': 'Contiene un archivo imsmanifest.xml válido.'
                    },
                    {
                        'name': 'Archivo index.html',
                        'result': True,
                        'description': 'Contiene un archivo index.html para la presentación del contenido.'
                    }
                ]
            }
            
            # Verificar si el archivo existe
            if not os.path.exists(self.object.package_file.path):
                context['validation']['is_valid'] = False
                context['validation']['errors'].append('El archivo del paquete no se encuentra en el servidor.')
                context['validation']['checks'][0]['result'] = False
            
            # Verificar el contenido del ZIP
            if validation_result.get('errors'):
                context['validation']['is_valid'] = False
                context['validation']['errors'].extend(validation_result.get('errors'))
                # Actualizar los checks basados en los errores
                if 'No se encontró el archivo imsmanifest.xml' in validation_result.get('errors'):
                    context['validation']['checks'][1]['result'] = False
                if 'No se encontró el archivo index.html' in validation_result.get('errors'):
                    context['validation']['checks'][2]['result'] = False
            
        except Exception as e:
            logger.error(f"Error al validar paquete SCORM {self.object.id}: {str(e)}")
            context['validation'] = {
                'is_valid': False,
                'errors': [f"Error al validar el paquete: {str(e)}"],
                'checks': []
            }
        
        return context
    
    def get_queryset(self):
        # Filtrar para mostrar solo los paquetes a los que el usuario tiene acceso
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(created_by=self.request.user) |
                models.Q(generated_content__request__teacher=self.request.user)
            )
        return queryset

@login_required
def download_scorm_package(request, pk):
    """Vista para descargar un paquete SCORM"""
    package = get_object_or_404(SCORMPackage, pk=pk)
    
    # Verificar que el usuario tenga permisos para descargar este paquete
    if request.user != package.generated_content.request.teacher and not request.user.is_staff:
        messages.error(request, "No tiene permisos para descargar este paquete SCORM.")
        return redirect('ai:content_request_list')
    
    try:
        package_path = package.package_file.path
        filename = os.path.basename(package_path)
        
        # Verificar que el archivo existe
        if not os.path.exists(package_path):
            logger.error(f"Archivo no encontrado: {package_path}")
            messages.error(request, "El archivo del paquete SCORM no fue encontrado en el servidor.")
            return redirect('scorm_packager:scorm_package_detail', pk=package.id)
        
        # Generar respuesta de descarga
        response = FileResponse(open(package_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{package.title.replace(" ", "_")}_SCORM.zip"'
        response['Content-Type'] = 'application/zip'
        
        logger.info(f"Usuario {request.user.username} descargó paquete SCORM {package.id}: {package.title}")
        return response
    
    except Exception as e:
        logger.exception(f"Error al descargar paquete SCORM {package.id}: {str(e)}")
        messages.error(request, f"Error al descargar el paquete SCORM: {str(e)}")
        return redirect('scorm_packager:scorm_package_detail', pk=package.id)

@login_required
def delete_scorm_package(request, pk):
    """Vista para eliminar un paquete SCORM"""
    package = get_object_or_404(SCORMPackage, pk=pk)
    
    # Verificar que el usuario tenga permisos para eliminar este paquete
    if request.user != package.generated_content.request.teacher and not request.user.is_staff:
        messages.error(request, "No tiene permisos para eliminar este paquete SCORM.")
        return redirect('scorm_packager:scorm_package_list')
    
    if request.method == 'POST':
        try:
            # Obtener información del paquete antes de eliminarlo
            package_title = package.title
            package_file_path = package.package_file.path if package.package_file else None
            
            # Verificar si hay materiales de portafolio que usan este paquete SCORM
            portfolio_materials = PortfolioMaterial.objects.filter(scorm_package=package)
            if portfolio_materials.exists():
                # Mostrar advertencia pero permitir eliminación
                material_count = portfolio_materials.count()
                messages.warning(
                    request, 
                    f"Este paquete SCORM está siendo usado en {material_count} material(es) de portafolio. "
                    f"Al eliminarlo, esos materiales perderán la referencia al paquete SCORM."
                )
                # Limpiar las referencias
                portfolio_materials.update(scorm_package=None)
            
            # Eliminar el archivo físico del paquete SCORM si existe
            if package_file_path and os.path.exists(package_file_path):
                try:
                    os.remove(package_file_path)
                    logger.info(f"Archivo físico eliminado: {package_file_path}")
                except OSError as e:
                    logger.warning(f"No se pudo eliminar el archivo físico {package_file_path}: {str(e)}")
            
            # Eliminar el registro de la base de datos
            package.delete()
            
            logger.info(f"Usuario {request.user.username} eliminó paquete SCORM: {package_title}")
            messages.success(request, f"El paquete SCORM '{package_title}' ha sido eliminado correctamente.")
            
        except Exception as e:
            logger.exception(f"Error al eliminar paquete SCORM {package.id}: {str(e)}")
            messages.error(request, f"Error al eliminar el paquete SCORM: {str(e)}")
            return redirect('scorm_packager:scorm_package_detail', pk=package.id)
    
    return redirect('scorm_packager:scorm_package_list')

@login_required
def generate_from_ai_content(request, content_id):
    """Generate a SCORM package from AI generated content"""
    try:
        # Get the AI content
        content = get_object_or_404(GeneratedContent, pk=content_id)
        
        # Check if user has permission to access this content
        if request.user != content.request.teacher and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para acceder a este contenido'})
        
        # Check if SCORM package already exists for this content
        existing_package = SCORMPackage.objects.filter(generated_content=content).first()
        if existing_package:
            return JsonResponse({
                'success': True, 
                'message': 'El paquete SCORM ya existe',
                'download_url': reverse('scorm_packager:download_scorm_package', kwargs={'pk': existing_package.id})
            })
        
        # Prepare metadata for the SCORM package
        metadata = {
            'title': content.title,
            'description': f'Contenido generado por IA para el curso {content.request.course.name}',
            'version': '1.0',
            'standard': 'scorm_2004_4th'
        }
        
        # Create the SCORM package
        packager = SCORMPackager(content.formatted_content, metadata)
        package_path = packager.create_package()
        
        # Save the package information to the database
        scorm_package = SCORMPackage.objects.create(
            title=content.title,
            description=metadata['description'],
            package_file=os.path.relpath(package_path, settings.MEDIA_ROOT),
            generated_content=content,
            created_by=request.user
        )
        
        logger.info(f"SCORM package created successfully: {scorm_package.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Paquete SCORM generado correctamente',
            'download_url': reverse('scorm_packager:download_scorm_package', kwargs={'pk': scorm_package.id})
        })
        
    except GeneratedContent.DoesNotExist:
        logger.error(f"AI content with ID {content_id} not found")
        return JsonResponse({'success': False, 'error': 'El contenido no existe'})
    except Exception as e:
        logger.exception(f"Error generating SCORM package: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def student_scorm_execute(request, pk):
    """Vista para que los estudiantes ejecuten paquetes SCORM a través de material de portafolio"""
    package = get_object_or_404(SCORMPackage, pk=pk)
    
    # Verificar que el estudiante tenga acceso a este paquete a través de su material de portafolio
    
    try:
        # Verificar si el usuario es estudiante
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            messages.error(request, "Solo los estudiantes pueden ejecutar contenido SCORM.")
            return redirect('dashboard:home')
        
        # Buscar si este estudiante tiene acceso al material SCORM
        accessible_material = PortfolioMaterial.objects.filter(
            scorm_package=package,
            topic__portfolio__student=student
        ).first()
        
        if not accessible_material:
            messages.error(request, "No tienes acceso a este material SCORM.")
            return redirect('dashboard:student_portfolio')
        
        # Verificar que el archivo del paquete existe
        if not os.path.exists(package.package_file.path):
            messages.error(request, "El archivo SCORM no está disponible.")
            return redirect('portfolios:student_topic_detail', pk=accessible_material.topic.id)
        
        # Preparar el contexto para ejecutar el SCORM
        context = {
            'package': package,
            'material': accessible_material,
            'topic': accessible_material.topic,
            'student': student,
        }
        
        logger.info(f"Estudiante {student.user.username} ejecutando SCORM {package.id}: {package.title}")
        return render(request, 'scorm_packager/student_execute.html', context)
        
    except Exception as e:
        logger.exception(f"Error al ejecutar SCORM {package.id} para estudiante: {str(e)}")
        messages.error(request, f"Error al cargar el contenido SCORM: {str(e)}")
        return redirect('dashboard:student_portfolio')

def _process_content_for_scorm_viewer(content):
    """
    Procesa el contenido HTML para la vista de SCORM eliminando duplicados y preservando estilos
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # 1. Eliminar encabezados institucionales duplicados
        content = _remove_institutional_headers(content)
        
        # 2. Extraer estilos inline nativos
        extracted_styles = _extract_inline_styles(content)
        
        # 3. Actualizar el contenido con los estilos preservados
        soup = BeautifulSoup(content, 'html.parser')
        
        # Agregar los estilos extraídos al head o crear uno si no existe
        if extracted_styles:
            head = soup.find('head')
            if not head:
                head = soup.new_tag('head')
                if soup.html:
                    soup.html.insert(0, head)
                else:
                    soup.insert(0, head)
            
            style_tag = soup.new_tag('style')
            style_tag.string = f"\n/* Estilos nativos preservados */\n{extracted_styles}\n"
            head.append(style_tag)
        
        return str(soup)
    
    except Exception as e:
        logger.warning(f"Error procesando contenido SCORM para vista: {e}")
        return content

def _remove_institutional_headers(content):
    """
    Elimina encabezados institucionales duplicados del contenido HTML
    """
    # Patrones para detectar encabezados institucionales
    institutional_patterns = [
        r'<[^>]*class="[^"]*(?:header-institucional|institucional-header)[^"]*"[^>]*>.*?</[^>]*>',
        r'<h[1-6][^>]*>.*?🎓.*?INSTITUCIÓN.*?EDUCATIVA.*?</h[1-6]>',
        r'<h[1-6][^>]*>.*?INSTITUCIÓN\s+EDUCATIVA.*?</h[1-6]>',
        r'<h[1-6][^>]*>.*?COLEGIO.*?NACIONAL.*?</h[1-6]>',
        r'<div[^>]*>.*?🎓.*?INSTITUCIÓN.*?EDUCATIVA.*?</div>',
        r'<header[^>]*>.*?(?:INSTITUCIÓN|COLEGIO).*?(?:EDUCATIVA|NACIONAL).*?</header>',
    ]
    
    processed_content = content
    
    for pattern in institutional_patterns:
        matches = re.findall(pattern, processed_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # Solo eliminar si no es el único encabezado
            if processed_content.count(match) > 1 or len(matches) > 1:
                processed_content = processed_content.replace(match, '', 1)
    
    return processed_content

def _extract_inline_styles(content):
    """
    Extrae y preserva estilos CSS importantes del contenido HTML
    """
    important_styles = []
    
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extraer estilos de etiquetas <style>
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                css_content = style_tag.string.strip()
                if css_content:
                    important_styles.append(css_content)
        
        # Extraer estilos inline importantes de elementos
        elements_with_style = soup.find_all(attrs={'style': True})
        inline_rules = []
        
        for element in elements_with_style:
            style_value = element.get('style', '').strip()
            if style_value:
                # Generar un selector único para este elemento
                tag_name = element.name
                classes = element.get('class', [])
                element_id = element.get('id')
                
                if element_id:
                    selector = f"#{element_id}"
                elif classes:
                    selector = f"{tag_name}.{'.'.join(classes)}"
                else:
                    selector = tag_name
                
                # Preservar propiedades CSS importantes
                if any(prop in style_value.lower() for prop in [
                    'gradient', 'var(', '--', 'animation', 'transform', 
                    'grid', 'flex', 'background-image', 'filter'
                ]):
                    inline_rules.append(f"{selector} {{ {style_value} }}")
        
        if inline_rules:
            important_styles.append('\n'.join(inline_rules))
    
    except Exception as e:
        logger.warning(f"Error extrayendo estilos inline: {e}")
    
    return '\n'.join(important_styles) if important_styles else ''

@login_required
def scorm_content_viewer(request, pk):
    """Vista para servir el contenido SCORM descomprimido"""
    package = get_object_or_404(SCORMPackage, pk=pk)
    
    # Verificar acceso
    
    # Verificar acceso según el tipo de usuario
    is_student = False
    try:
        student = request.user.student_profile
        is_student = True
        accessible_material = PortfolioMaterial.objects.filter(
            scorm_package=package,
            topic__portfolio__student=student
        ).first()
        
        if not accessible_material:
            return HttpResponse("No tienes acceso a este contenido.", status=403)
    except Student.DoesNotExist:
        # No es estudiante, verificar si es profesor o staff
        if not request.user.is_staff and package.generated_content.request.teacher != request.user:
            return HttpResponse("No tienes acceso a este contenido.", status=403)
    
    import zipfile
    import tempfile
    import shutil
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(package.package_file.path):
            return HttpResponse("Archivo SCORM no encontrado.", status=404)
        
        # Crear directorio temporal para extraer el contenido
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extraer el archivo ZIP
            with zipfile.ZipFile(package.package_file.path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Buscar el archivo index.html
            index_path = None
            for root, dirs, files in os.walk(temp_dir):
                if 'index.html' in files:
                    index_path = os.path.join(root, 'index.html')
                    break
            
            if not index_path:
                return HttpResponse("No se encontró index.html en el paquete SCORM.", status=404)
            
            # Leer el contenido del index.html
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # *** APLICAR PROCESAMIENTO DE CONTENIDO MEJORADO ***
            content = _process_content_for_scorm_viewer(content)
            
            # Reemplazar SOLO rutas relativas para que apunten a nuestro servidor de recursos
            import re
            
            # Construir la URL base para recursos SCORM
            resource_base_url = request.build_absolute_uri(f'/scorm/packages/{package.id}/resource/')
            
            # Patrones más amplios para capturar todos los recursos
            # Reemplazar src relativos (archivos de imagen, video, audio, etc.)
            content = re.sub(r'src="(?!https?://|data:|#)([^"]*)"', f'src="{resource_base_url}\\1"', content)
            
            # Reemplazar href relativos (CSS, archivos descargables, etc.) 
            content = re.sub(r'href="(?!https?://|mailto:|tel:|#)([^"]*\.(?:css|js|pdf|doc|docx|xls|xlsx|ppt|pptx))"', 
                           f'href="{resource_base_url}\\1"', content)
            
            # Reemplazar urls en CSS inline
            content = re.sub(r'url\((?![\'"]*(?:https?://|data:))([\'"]?)([^\'"()]+)\1\)', 
                           f'url("{resource_base_url}\\2")', content)
            
            # Agregar meta tag para hacer el contenido responsive
            if '<head>' in content:
                viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                content = content.replace('<head>', f'<head>\n{viewport_meta}')
            
            # Leer el CSS de mejora desde el archivo estático
            enhancement_css_path = os.path.join(settings.BASE_DIR, 'apps', 'scorm_packager', 'static', 'scorm', 'scorm-enhancement.css')
            enhancement_css = ""
            
            try:
                if os.path.exists(enhancement_css_path):
                    with open(enhancement_css_path, 'r', encoding='utf-8') as css_file:
                        enhancement_css = css_file.read()
                else:
                    # CSS básico como fallback
                    enhancement_css = """
                    /* Fallback CSS básico para SCORM */
                    * { box-sizing: border-box !important; }
                    body { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100vh !important; overflow-x: hidden !important; }
                    img { max-width: 100% !important; height: auto !important; }
                    .container, .content, .main { max-width: 100% !important; padding: 10px !important; }
                    table { width: 100% !important; table-layout: fixed !important; }
                    p, div, span { line-height: 1.6 !important; word-wrap: break-word !important; }
                    """
            except Exception as e:
                logger.warning(f"No se pudo cargar el CSS de mejora: {e}")
                enhancement_css = "/* CSS de mejora no disponible */"
            
            # Agregar estilos para mejorar la visualización en iframe
            iframe_styles = f"""
            <style>
                /* CSS de mejora SCORM */
                {enhancement_css}
                
                /* Estilos adicionales específicos para este contexto */
                body {{
                    font-size: 14px !important;
                }}
                
                /* Mejorar interactividad */
                button, .btn, input[type="button"] {{
                    touch-action: manipulation !important;
                    -webkit-tap-highlight-color: transparent !important;
                }}
                
                /* Prevenir duplicación de encabezados institucionales */
                .header-institucional + .header-institucional,
                .institucional-header + .institucional-header {{
                    display: none !important;
                }}
                
                /* Mejorar legibilidad del contenido nativo */
                .content-wrapper, .scorm-content {{
                    max-width: 100% !important;
                    margin: 0 auto !important;
                    padding: 20px !important;
                }}
                
                /* Preservar animaciones y transiciones nativas */
                .animated, [class*="animate"], [style*="animation"] {{
                    animation-fill-mode: both !important;
                }}
            </style>
            """
            
            # Cargar el script avanzado de correcciones SCORM
            fixer_js_path = os.path.join(settings.BASE_DIR, 'apps', 'scorm_packager', 'static', 'scorm', 'scorm-content-fixer.js')
            duplicate_removal_js = ""
            
            try:
                if os.path.exists(fixer_js_path):
                    with open(fixer_js_path, 'r', encoding='utf-8') as js_file:
                        fixer_js_content = js_file.read()
                        duplicate_removal_js = f"<script>{fixer_js_content}</script>"
                else:
                    # Fallback con JavaScript básico
                    duplicate_removal_js = """
                    <script>
                        console.log('🔧 Fallback SCORM fixer iniciado');
                        document.addEventListener('DOMContentLoaded', function() {
                            // Función básica para remover encabezados duplicados
                            const patterns = [
                                /🎓.*INSTITUCIÓN.*EDUCATIVA/gi,
                                /INSTITUCIÓN\\s+EDUCATIVA/gi,
                                /COLEGIO.*NACIONAL/gi
                            ];
                            
                            patterns.forEach(pattern => {
                                const elements = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, div, header'));
                                const matches = elements.filter(el => pattern.test(el.textContent));
                                
                                if (matches.length > 1) {
                                    matches.slice(1).forEach(el => {
                                        el.style.display = 'none';
                                        el.setAttribute('data-scorm-hidden', 'duplicate-header');
                                        console.log('Encabezado duplicado ocultado:', el.textContent.trim().substr(0, 50));
                                    });
                                }
                            });
                            
                            // Mejorar accesibilidad básica
                            document.querySelectorAll('img:not([alt])').forEach((img, i) => {
                                img.alt = `Imagen del contenido educativo ${i + 1}`;
                            });
                            
                            console.log('✅ Correcciones SCORM básicas aplicadas');
                        });
                    </script>
                    """
            except Exception as e:
                logger.warning(f"No se pudo cargar el script de correcciones SCORM: {e}")
                duplicate_removal_js = "<script>console.log('SCORM fixer no disponible');</script>"
            
            # Leer el script de bridge desde el archivo estático
            bridge_js_path = os.path.join(settings.BASE_DIR, 'apps', 'scorm_packager', 'static', 'scorm', 'scorm-iframe-bridge.js')
            bridge_js = ""
            
            try:
                if os.path.exists(bridge_js_path):
                    with open(bridge_js_path, 'r', encoding='utf-8') as js_file:
                        bridge_js = js_file.read()
            except Exception as e:
                logger.warning(f"No se pudo cargar el script de bridge: {e}")
            
            # Agregar el script de bridge
            bridge_script = f"""
            <script>
                {bridge_js}
            </script>
            """
            
            if '</head>' in content:
                content = content.replace('</head>', f'{iframe_styles}{duplicate_removal_js}{bridge_script}</head>')
            elif '<body>' in content:
                content = content.replace('<body>', f'<head>{iframe_styles}{duplicate_removal_js}{bridge_script}</head><body>')
            else:
                # Si no hay head ni body, agregar al principio
                content = f'<head>{iframe_styles}{duplicate_removal_js}{bridge_script}</head>{content}'
            
            response = HttpResponse(content, content_type='text/html')
            
            # Cabeceras para el contenido principal SCORM
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Frame-Options'] = 'SAMEORIGIN'  # Permitir en iframe del mismo origen
            
            logger.info(f"Contenido SCORM servido exitosamente para paquete {package.id} con mejoras aplicadas")
            return response
            
        finally:
            # Limpiar directorio temporal
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"No se pudo limpiar directorio temporal: {e}")
    
    except Exception as e:
        logger.exception(f"Error sirviendo contenido SCORM {package.id}: {str(e)}")
        return HttpResponse(f"Error cargando contenido SCORM: {str(e)}", status=500)

@login_required 
def scorm_resource_viewer(request, pk, resource_path):
    """Vista para servir recursos estáticos del SCORM (CSS, JS, imágenes, etc.)"""
    package = get_object_or_404(SCORMPackage, pk=pk)
    
    # Verificar acceso (similar a scorm_content_viewer)
    
    try:
        student = request.user.student_profile
        accessible_material = PortfolioMaterial.objects.filter(
            scorm_package=package,
            topic__portfolio__student=student
        ).first()
        
        if not accessible_material:
            return HttpResponse("No tienes acceso a este contenido.", status=403)
    except Student.DoesNotExist:
        if not request.user.is_staff and package.generated_content.request.teacher != request.user:
            return HttpResponse("No tienes acceso a este contenido.", status=403)
    
    import zipfile
    import tempfile
    import shutil
    import mimetypes
    
    try:
        if not os.path.exists(package.package_file.path):
            return HttpResponse("Archivo SCORM no encontrado.", status=404)
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extraer el archivo ZIP
            with zipfile.ZipFile(package.package_file.path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Buscar el archivo solicitado con mejor lógica de búsqueda
            resource_full_path = None
            
            # Intentar encontrar el archivo directamente por la ruta
            direct_path = os.path.join(temp_dir, resource_path)
            if os.path.exists(direct_path):
                resource_full_path = direct_path
            else:
                # Buscar recursivamente
                for root, dirs, files in os.walk(temp_dir):
                    # Intentar coincidencia exacta de ruta relativa
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, temp_dir).replace('\\', '/')
                        
                        if relative_path == resource_path or relative_path.endswith(resource_path):
                            resource_full_path = file_path
                            break
                    
                    if resource_full_path:
                        break
                
                # Si no se encuentra, buscar solo por nombre de archivo
                if not resource_full_path:
                    filename = os.path.basename(resource_path)
                    for root, dirs, files in os.walk(temp_dir):
                        if filename in files:
                            resource_full_path = os.path.join(root, filename)
                            break
            
            if not resource_full_path or not os.path.exists(resource_full_path):
                return HttpResponse("Recurso no encontrado.", status=404)
            
            # Determinar el tipo MIME
            content_type, _ = mimetypes.guess_type(resource_full_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Servir el archivo con cabeceras apropiadas
            with open(resource_full_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                
                # Agregar cabeceras para cacheo
                response['Cache-Control'] = 'public, max-age=3600'  # Cache por 1 hora
                
                # Cabeceras específicas para tipos de archivo
                if content_type.startswith('image/'):
                    response['Cache-Control'] = 'public, max-age=86400'  # Imágenes cache 24h
                elif content_type.startswith('text/css') or content_type.startswith('application/javascript'):
                    response['Cache-Control'] = 'public, max-age=3600'  # CSS/JS cache 1h
                
                return response
                
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        logger.exception(f"Error al servir recurso SCORM {resource_path}: {str(e)}")
        return HttpResponse("Error al cargar el recurso.", status=500) 