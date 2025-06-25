from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class StudentPortfolio(models.Model):
    """Modelo para el portafolio mensual de estudiantes."""
    MONTH_CHOICES = [
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    ]

    student = models.ForeignKey('academic.Student', on_delete=models.CASCADE, related_name='portfolios', verbose_name='Estudiante')
    academic_year = models.CharField(max_length=9, verbose_name='Año Académico', default=str(timezone.now().year))
    month = models.IntegerField(choices=MONTH_CHOICES, verbose_name='Mes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portafolio de Estudiante'
        verbose_name_plural = 'Portafolios de Estudiantes'
        ordering = ['academic_year', 'month', 'student']
        unique_together = ['student', 'academic_year', 'month']

    def __str__(self):
        return f"Portafolio de {self.student} - {self.get_month_display()} {self.academic_year}"

    def get_status(self):
        """Calcula el estado de completitud del portafolio basado en los temas."""
        from apps.academic.models import Course  # Import diferido para evitar import circular

        total_courses = Course.objects.filter(
            course_assignments__section__enrollments__student=self.student,
            course_assignments__is_active=True
        ).distinct().count()

        courses_with_topics = self.portfolio_topics.values('course').distinct().count()

        if total_courses == 0:
            return 0

        return (courses_with_topics / total_courses) * 100

class PortfolioTopic(models.Model):
    """Modelo para los temas dentro del portafolio mensual del estudiante."""
    portfolio = models.ForeignKey(StudentPortfolio, on_delete=models.CASCADE, related_name='portfolio_topics', verbose_name='Portafolio')
    course = models.ForeignKey('academic.Course', on_delete=models.CASCADE, related_name='portfolio_topics', verbose_name='Curso')
    teacher = models.ForeignKey('academic.Teacher', on_delete=models.CASCADE, related_name='portfolio_topics', verbose_name='Profesor')
    title = models.CharField(max_length=200, verbose_name='Título del Tema')
    description = models.TextField(verbose_name='Descripción del Tema', blank=True)
    is_complete = models.BooleanField(default=False, verbose_name='Completado')
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_portfolio_topics',
        verbose_name='Última actualización por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tema de Portafolio'
        verbose_name_plural = 'Temas de Portafolio'
        ordering = ['portfolio', 'course', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.course.name} - {self.portfolio}"

class PortfolioMaterial(models.Model):
    """Modelo para los materiales adjuntos a un tema de portafolio."""
    MATERIAL_TYPE_CHOICES = [
        ('EJERCICIO', 'Ejercicio'),
        ('TAREA', 'Tarea'),
        ('EXAMEN', 'Examen'),
        ('PROYECTO', 'Proyecto'),
        ('LECTURA', 'Lectura'),
        ('OTRO', 'Otro'),
        ('SCORM', 'Paquete SCORM'),
    ]
    
    topic = models.ForeignKey(PortfolioTopic, on_delete=models.CASCADE, related_name='materials', verbose_name='Tema de Portafolio', null=True, blank=True)
    course_topic = models.ForeignKey('academic.CourseTopic', on_delete=models.CASCADE, related_name='materials', verbose_name='Tema de Curso', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción', blank=True)
    file = models.FileField(upload_to='portfolio_materials/%Y/%m/', verbose_name='Archivo', blank=True, null=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='EJERCICIO', verbose_name='Tipo de Material')
    scorm_package = models.ForeignKey('scorm_packager.SCORMPackage', on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_materials', verbose_name='Paquete SCORM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_generated = models.BooleanField(default=False, verbose_name='Generado por IA')
    is_class_material = models.BooleanField(default=True, verbose_name='Material de Clase')
    
    class Meta:
        verbose_name = 'Material de Portafolio'
        verbose_name_plural = 'Materiales de Portafolio'
        ordering = ['-created_at']

    def __str__(self):
        if self.course_topic:
            return f"{self.title} - {self.course_topic.title} - {self.course_topic.course.name}"
        return f"{self.title} - {self.topic.title} - {self.topic.course.name}"

@receiver(post_save, sender=PortfolioMaterial)
def auto_process_scorm_material(sender, instance, created, **kwargs):
    """
    Signal para procesar automáticamente materiales SCORM cuando se crean
    """
    if created and instance.material_type == 'SCORM' and instance.file:
        # Verificar si es un archivo ZIP
        if instance.file.name.lower().endswith('.zip'):
            # Verificar si ya tiene un SCORM package asociado
            if not hasattr(instance, 'scorm_package') or not instance.scorm_package:
                try:
                    from apps.scorm_packager.models import SCORMPackage
                    from apps.ai_content_generator.models import GeneratedContent, ContentRequest, ContentType
                    
                    # Obtener el profesor
                    teacher = instance.topic.teacher if instance.topic else instance.course_topic.teacher
                    
                    # Crear o obtener ContentType para SCORM
                    content_type, created_type = ContentType.objects.get_or_create(
                        name='SCORM Package',
                        defaults={
                            'description': 'Paquete SCORM interactivo',
                            'template_prompt': 'Contenido SCORM interactivo'
                        }
                    )
                    
                    # Obtener el curso
                    course = instance.topic.course if instance.topic else instance.course_topic.course
                    
                    # Crear ContentRequest
                    content_request = ContentRequest.objects.create(
                        teacher=teacher.user,
                        course=course,
                        content_type=content_type,
                        topic=instance.title,
                        grade_level='General',
                        additional_instructions=instance.description or 'Material SCORM procesado automáticamente',
                        status='completed',
                        related_topic=instance.topic,
                        for_class=instance.is_class_material
                    )
                    
                    # Crear GeneratedContent
                    generated_content = GeneratedContent.objects.create(
                        request=content_request,
                        title=instance.title,
                        raw_content=f"Contenido SCORM: {instance.title}",
                        formatted_content=f"<p>Material SCORM interactivo: {instance.title}</p>",
                        model_used='auto_processed',
                        tokens_used=0
                    )
                    
                    # Crear el paquete SCORM
                    scorm_package = SCORMPackage.objects.create(
                        generated_content=generated_content,
                        title=instance.title,
                        description=instance.description or f"Paquete SCORM: {instance.title}",
                        standard='scorm_2004_4th',
                        package_file=instance.file,
                        is_published=True,
                        created_by=teacher.user
                    )
                    
                    # Asociar el paquete SCORM al material
                    instance.scorm_package = scorm_package
                    instance.save(update_fields=['scorm_package'])
                    
                    logger.info(f"🤖 SCORM procesado automáticamente por signal: {scorm_package.id} para material: {instance.title}")
                    
                except Exception as e:
                    logger.error(f"❌ Error en signal auto_process_scorm_material: {str(e)}")
            else:
                logger.info(f"📦 Material SCORM ya tiene paquete asociado: {instance.title}")
        else:
            logger.warning(f"⚠️ Material marcado como SCORM pero no es ZIP: {instance.title}")
    elif not created and instance.material_type == 'SCORM':
        logger.info(f"🔄 Material SCORM actualizado: {instance.title}")
