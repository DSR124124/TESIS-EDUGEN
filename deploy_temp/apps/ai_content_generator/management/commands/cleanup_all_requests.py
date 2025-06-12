from django.core.management.base import BaseCommand
from django.db import transaction
from apps.ai_content_generator.models import ContentRequest, GeneratedContent
from apps.scorm_packager.models import SCORMPackage
import os
import shutil

class Command(BaseCommand):
    help = 'Elimina TODAS las solicitudes de IA y contenido relacionado - LIMPIEZA COMPLETA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se haría sin ejecutar los cambios',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la eliminación sin confirmación',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('=== LIMPIEZA COMPLETA DE TODAS LAS SOLICITUDES DE IA ==='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY RUN - No se realizarán cambios'))

        # Contar registros actuales
        total_requests = ContentRequest.objects.count()
        total_generated_content = GeneratedContent.objects.count()
        total_scorm_packages = SCORMPackage.objects.count()

        self.stdout.write(f'\n--- ESTADO ACTUAL ---')
        self.stdout.write(f'Total solicitudes: {total_requests}')
        self.stdout.write(f'Total contenido generado: {total_generated_content}')
        self.stdout.write(f'Total paquetes SCORM: {total_scorm_packages}')

        if total_requests == 0:
            self.stdout.write(self.style.SUCCESS('No hay solicitudes para eliminar. La base de datos ya está limpia.'))
            return

        # Mostrar todos los registros a eliminar
        self.stdout.write(f'\n--- TODOS LOS REGISTROS A ELIMINAR ---')
        all_requests = ContentRequest.objects.all().order_by('-created_at')
        
        for i, request in enumerate(all_requests, 1):
            created_date = request.created_at.strftime('%Y-%m-%d %H:%M')
            has_content = request.contents.exists()
            self.stdout.write(
                f'{i:2d}. ID:{request.id} | {request.topic} | {request.status} | {created_date} | Contenido: {"Sí" if has_content else "No"}'
            )

        # Confirmar eliminación total
        if not dry_run and not force:
            self.stdout.write(self.style.WARNING(f'\n⚠️  ADVERTENCIA: Esto eliminará TODAS las {total_requests} solicitudes de IA ⚠️'))
            self.stdout.write(self.style.WARNING('Esta acción NO se puede deshacer.'))
            confirm = input(f'\n¿Estás SEGURO de que quieres eliminar TODO? (escriba "ELIMINAR TODO" para confirmar): ')
            if confirm != 'ELIMINAR TODO':
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        # Proceder con la eliminación completa
        if not dry_run:
            self.stdout.write('\n--- ELIMINANDO TODO EL CONTENIDO ---')
            
            deleted_requests = 0
            deleted_content = 0
            deleted_scorm_packages = 0
            deleted_files = 0
            
            with transaction.atomic():
                # Eliminar todos los paquetes SCORM primero
                for package in SCORMPackage.objects.all():
                    try:
                        # Eliminar archivo físico del paquete SCORM
                        if package.package_file and os.path.exists(package.package_file.path):
                            os.remove(package.package_file.path)
                            deleted_files += 1
                            self.stdout.write(f'✓ Archivo eliminado: {package.package_file.path}')
                        package.delete()
                        deleted_scorm_packages += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error al eliminar paquete SCORM {package.id}: {str(e)}')
                        )

                # Eliminar todo el contenido generado
                for content in GeneratedContent.objects.all():
                    try:
                        content.delete()
                        deleted_content += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error al eliminar contenido {content.id}: {str(e)}')
                        )

                # Eliminar todas las solicitudes
                for request in ContentRequest.objects.all():
                    try:
                        request_info = f'ID:{request.id} "{request.topic}"'
                        request.delete()
                        deleted_requests += 1
                        self.stdout.write(f'✓ Eliminado: {request_info}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error al eliminar request {request.id}: {str(e)}')
                        )

                # Limpiar directorios de archivos subidos si existen
                media_dirs_to_clean = [
                    'media/scorm_packages/',
                    'media/ai_generated_content/',
                ]
                
                for media_dir in media_dirs_to_clean:
                    if os.path.exists(media_dir):
                        try:
                            shutil.rmtree(media_dir)
                            os.makedirs(media_dir, exist_ok=True)
                            self.stdout.write(f'✓ Directorio limpiado: {media_dir}')
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'Error al limpiar directorio {media_dir}: {str(e)}')
                            )

            self.stdout.write(f'\n--- RESUMEN DE ELIMINACIÓN COMPLETA ---')
            self.stdout.write(f'Solicitudes eliminadas: {deleted_requests}')
            self.stdout.write(f'Contenido generado eliminado: {deleted_content}')
            self.stdout.write(f'Paquetes SCORM eliminados: {deleted_scorm_packages}')
            self.stdout.write(f'Archivos físicos eliminados: {deleted_files}')

        # Verificar estado final
        self.stdout.write('\n--- ESTADO FINAL ---')
        
        final_requests = ContentRequest.objects.count()
        final_content = GeneratedContent.objects.count()
        final_scorm = SCORMPackage.objects.count()
        
        self.stdout.write(f'Solicitudes restantes: {final_requests}')
        self.stdout.write(f'Contenido generado restante: {final_content}')
        self.stdout.write(f'Paquetes SCORM restantes: {final_scorm}')
        
        if final_requests == 0 and final_content == 0 and final_scorm == 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 BASE DE DATOS COMPLETAMENTE LIMPIA 🎉'))
            self.stdout.write(self.style.SUCCESS('La página /ai/requests/ ahora aparecerá vacía.'))
        else:
            self.stdout.write(self.style.ERROR(f'\n⚠️  Aún quedan algunos registros. Revisa los errores anteriores.'))
        
        self.stdout.write(self.style.SUCCESS('\n=== LIMPIEZA COMPLETA FINALIZADA ===')) 