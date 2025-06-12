"""
Comando para regenerar paquetes SCORM existentes con mejoras implementadas
"""
import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.scorm_packager.models import SCORMPackage
from apps.scorm_packager.services.packager import SCORMPackager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Regenera paquetes SCORM existentes aplicando las mejoras de duplicación y estilos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--package_id',
            type=int,
            help='ID específico del paquete SCORM a regenerar',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerar todos los paquetes SCORM existentes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar regeneración aunque el archivo ya exista',
        )
    
    def handle(self, *args, **options):
        if not options['package_id'] and not options['all']:
            raise CommandError('Debes especificar --package_id o --all')
        
        if options['all']:
            packages = SCORMPackage.objects.all()
            self.stdout.write(
                self.style.SUCCESS(f'Regenerando {packages.count()} paquetes SCORM...')
            )
        else:
            try:
                packages = [SCORMPackage.objects.get(pk=options['package_id'])]
                self.stdout.write(
                    self.style.SUCCESS(f'Regenerando paquete SCORM ID {options["package_id"]}...')
                )
            except SCORMPackage.DoesNotExist:
                raise CommandError(f'Paquete SCORM con ID {options["package_id"]} no existe')
        
        success_count = 0
        error_count = 0
        
        for package in packages:
            try:
                self.stdout.write(f'Procesando: {package.title} (ID: {package.id})')
                
                # Verificar si el archivo existe y si se debe forzar la regeneración
                if package.package_file and os.path.exists(package.package_file.path) and not options['force']:
                    self.stdout.write(
                        self.style.WARNING(f'  - Archivo ya existe, usa --force para sobrescribir')
                    )
                    continue
                
                # Verificar que existe el contenido generado asociado
                if not hasattr(package, 'generated_content') or not package.generated_content:
                    self.stdout.write(
                        self.style.ERROR(f'  - No hay contenido generado asociado')
                    )
                    error_count += 1
                    continue
                
                # Regenerar el paquete SCORM con las mejoras
                packager = SCORMPackager()
                
                # Obtener el contenido HTML del GeneratedContent
                html_content = package.generated_content.generated_content
                
                if not html_content:
                    self.stdout.write(
                        self.style.ERROR(f'  - El contenido generado está vacío')
                    )
                    error_count += 1
                    continue
                
                # Generar nuevo paquete SCORM
                self.stdout.write('  - Aplicando mejoras de duplicación y estilos...')
                new_file_path = packager.create_scorm_package(
                    title=package.title,
                    content_html=html_content,
                    author=package.generated_content.request.teacher.get_full_name() or package.generated_content.request.teacher.username,
                    description=package.description or f"Contenido educativo: {package.title}"
                )
                
                # Actualizar el archivo del paquete
                if os.path.exists(new_file_path):
                    # Eliminar archivo anterior si existe
                    if package.package_file and os.path.exists(package.package_file.path):
                        try:
                            os.remove(package.package_file.path)
                        except Exception as e:
                            logger.warning(f"No se pudo eliminar archivo anterior: {e}")
                    
                    # Actualizar con el nuevo archivo
                    with open(new_file_path, 'rb') as f:
                        package.package_file.save(
                            f"{package.title}_mejorado.zip",
                            f,
                            save=True
                        )
                    
                    # Limpiar archivo temporal
                    try:
                        os.remove(new_file_path)
                    except Exception as e:
                        logger.warning(f"No se pudo limpiar archivo temporal: {e}")
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Regenerado exitosamente')
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  - Error: No se generó el archivo SCORM')
                    )
                    error_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  - Error procesando: {str(e)}')
                )
                logger.exception(f"Error regenerando paquete SCORM {package.id}: {e}")
                error_count += 1
        
        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Regeneración completada:')
        )
        self.stdout.write(f'  • Exitosos: {success_count}')
        self.stdout.write(f'  • Errores: {error_count}')
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n¡{success_count} paquetes regenerados con mejoras!')
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f'\n{error_count} paquetes tuvieron errores. Revisa los logs.')
            ) 