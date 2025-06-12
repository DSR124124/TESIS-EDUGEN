from django.db import models
from django.conf import settings
from django.utils import timezone

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
