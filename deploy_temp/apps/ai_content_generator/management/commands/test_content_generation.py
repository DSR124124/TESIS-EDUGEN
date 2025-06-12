from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.ai_content_generator.models import ContentRequest, ContentType
from apps.academic.models import Course
from apps.ai_content_generator.tasks import generate_content_sync
import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba la generación de contenido para diagnosticar errores'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, default=1, help='ID del usuario teacher')
        parser.add_argument('--course-id', type=int, default=1, help='ID del curso')
        parser.add_argument('--content-type-id', type=int, default=1, help='ID del tipo de contenido')

    def handle(self, *args, **options):
        self.stdout.write("🧪 INICIANDO PRUEBA DE GENERACIÓN DE CONTENIDO")
        self.stdout.write("=" * 60)
        
        try:
            # Obtener usuario
            user_id = options['user_id']
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"✅ Usuario encontrado: {user.username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Usuario con ID {user_id} no encontrado"))
                return

            # Obtener curso
            course_id = options['course_id']
            try:
                course = Course.objects.get(id=course_id)
                self.stdout.write(f"✅ Curso encontrado: {course.name}")
            except Course.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Curso con ID {course_id} no encontrado"))
                return

            # Obtener tipo de contenido
            content_type_id = options['content_type_id']
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                self.stdout.write(f"✅ Tipo de contenido encontrado: {content_type.name}")
            except ContentType.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Tipo de contenido con ID {content_type_id} no encontrado"))
                return

            # Crear solicitud de prueba
            content_request = ContentRequest.objects.create(
                teacher=user,
                course=course,
                content_type=content_type,
                topic="Alimentación Saludable - PRUEBA",
                grade_level="PRIMERO",
                additional_instructions="Esta es una prueba de generación de contenido para diagnosticar errores.",
                status='pending'
            )
            
            self.stdout.write(f"✅ Solicitud creada con ID: {content_request.id}")
            
            # Ejecutar generación
            self.stdout.write("\n🤖 INICIANDO GENERACIÓN...")
            start_time = time.time()
            
            try:
                result = generate_content_sync(content_request.id)
                end_time = time.time()
                duration = end_time - start_time
                
                # Actualizar estado de la solicitud
                content_request.refresh_from_db()
                
                self.stdout.write(f"\n⏱️  Duración: {duration:.2f} segundos")
                self.stdout.write(f"📊 Estado final: {content_request.status}")
                
                if result:
                    self.stdout.write(self.style.SUCCESS("🎉 ¡GENERACIÓN EXITOSA!"))
                    
                    # Mostrar información del contenido generado
                    if content_request.contents.exists():
                        content = content_request.contents.first()
                        word_count = len(content.raw_content.split()) if content.raw_content else 0
                        self.stdout.write(f"📝 Palabras generadas: {word_count}")
                        self.stdout.write(f"🎯 Título: {content.title}")
                        self.stdout.write(f"🤖 Modelo usado: {content.model_used}")
                        self.stdout.write(f"🔢 Tokens usados: {content.tokens_used}")
                        
                        # Mostrar primeras líneas del contenido
                        preview = content.raw_content[:200] if content.raw_content else "Sin contenido"
                        self.stdout.write(f"👀 Vista previa: {preview}...")
                    
                else:
                    self.stdout.write(self.style.ERROR("❌ GENERACIÓN FALLÓ"))
                    
                    # Mostrar detalles del error
                    if hasattr(content_request, 'error_message'):
                        self.stdout.write(f"🚨 Error: {content_request.error_message}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"💥 ERROR DURANTE GENERACIÓN: {str(e)}"))
                import traceback
                self.stdout.write(traceback.format_exc())
            
            # Limpiar (opcional)
            self.stdout.write(f"\n🗑️  Eliminando solicitud de prueba...")
            content_request.delete()
            self.stdout.write("✅ Limpieza completada")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"💥 ERROR GENERAL: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🏁 PRUEBA COMPLETADA") 