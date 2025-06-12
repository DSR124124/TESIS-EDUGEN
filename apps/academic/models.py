from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.institutions.models import Institution
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    """Modelo para los cursos."""
    name = models.CharField(max_length=200, verbose_name="Nombre del curso")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    description = models.TextField(verbose_name="Descripción", default="Sin descripción")
    credits = models.IntegerField(verbose_name="Créditos", default=3)
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Teacher(models.Model):
    """Modelo para los profesores."""
    SPECIALITY_CHOICES = [
        ('MAT', 'Matemática'),
        ('COM', 'Comunicación'),
        ('CTA', 'Ciencia y Tecnología'),
        ('SOC', 'Ciencias Sociales'),
        ('ING', 'Inglés'),
        ('ART', 'Arte y Cultura'),
        ('EFI', 'Educación Física'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    dni = models.CharField(_('DNI'), max_length=8, unique=True)
    speciality = models.CharField(
        _('especialidad'),
        max_length=3,
        choices=SPECIALITY_CHOICES
    )
    teacher_code = models.CharField(max_length=10, unique=True, editable=False, default='DOC-00000')
    phone = models.CharField(_('teléfono'), max_length=9, default='000000000')
    address = models.CharField(_('dirección'), max_length=200, blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'academic'
        verbose_name = _('profesor')
        verbose_name_plural = _('profesores')

    def __str__(self):
        if hasattr(self.user, 'get_full_name') and self.user.get_full_name():
            return f"{self.user.get_full_name()} ({self.teacher_code})"
        return f"{self.user.username} ({self.teacher_code})"
    
    def get_speciality_display(self):
        return dict(self.SPECIALITY_CHOICES).get(self.speciality, self.speciality)
        
    def save(self, *args, **kwargs):
        if not self.teacher_code or self.teacher_code == 'DOC-00000':
            # Generar código: DOC-XXXXX (donde X son números aleatorios)
            import random
            import string
            while True:
                code = 'DOC-' + ''.join(random.choices(string.digits, k=5))
                if not Teacher.objects.filter(teacher_code=code).exists():
                    self.teacher_code = code
                    break
        super().save(*args, **kwargs)

class Student(models.Model):
    """Modelo para los estudiantes."""
    class Meta:
        app_label = 'academic'
        verbose_name = _('estudiante')
        verbose_name_plural = _('estudiantes')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    dni = models.CharField(_('DNI'), max_length=8, unique=True)
    birth_date = models.DateField(_('fecha de nacimiento'))
    address = models.TextField(_('dirección'), blank=True)
    guardian_name = models.CharField(_('nombre del apoderado'), max_length=200)
    guardian_phone = models.CharField(_('teléfono del apoderado'), max_length=15)
    is_active = models.BooleanField(_('activo'), default=True)
    google_account = models.EmailField(_('cuenta de Google'), blank=True, null=True)
    google_account_linked = models.BooleanField(_('cuenta Google vinculada'), default=False)
    google_linked_at = models.DateTimeField(_('fecha de vinculación'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if hasattr(self, 'user') and self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return f"Estudiante {self.id}"

    def link_google_account(self, email):
        """Vincula una cuenta de Google al estudiante"""
        self.google_account = email
        self.google_account_linked = True
        self.google_linked_at = timezone.now()
        self.save(update_fields=['google_account', 'google_account_linked', 'google_linked_at'])
        
    def unlink_google_account(self):
        """Desvincula la cuenta de Google del estudiante"""
        self.google_account = None
        self.google_account_linked = False
        self.google_linked_at = None
        self.save(update_fields=['google_account', 'google_account_linked', 'google_linked_at'])

class Grade(models.Model):
    LEVEL_CHOICES = [
        ('SECUNDARIA', 'Secundaria'),
    ]
    
    name = models.CharField('Nombre', max_length=50)
    level = models.CharField('Nivel', max_length=50, choices=LEVEL_CHOICES, default='SECUNDARIA')
    description = models.TextField('Descripción', default='')
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de creación', default=timezone.now)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
        ordering = ['level', 'name']

    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"

    @classmethod
    def create_secondary_grades(cls):
        grades = [
            ('PRIMERO', 'Primer grado de secundaria'),
            ('SEGUNDO', 'Segundo grado de secundaria'),
            ('TERCERO', 'Tercer grado de secundaria'),
            ('CUARTO', 'Cuarto grado de secundaria'),
            ('QUINTO', 'Quinto grado de secundaria'),
        ]
        created_grades = []
        for name, description in grades:
            grade, created = cls.objects.get_or_create(
                name=name,
                level='SECUNDARIA',
                defaults={
                    'description': description,
                    'is_active': True
                }
            )
            if created:
                created_grades.append(grade)
                # Crear secciones automáticamente
                Section.create_sections_for_grade(grade)
        return created_grades

class Section(models.Model):
    name = models.CharField('Nombre', max_length=1)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    capacity = models.PositiveIntegerField('Capacidad', default=30)
    current_students = models.PositiveIntegerField('Estudiantes Actuales', default=0)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de creación', default=timezone.now)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering = ['grade', 'name']
        unique_together = ['grade', 'name']

    def __str__(self):
        return f"{self.grade.name} - Sección {self.name}"

    @classmethod
    def create_sections_for_grade(cls, grade):
        sections = ['A', 'B', 'C']
        created_sections = []
        for name in sections:
            section, created = cls.objects.get_or_create(
                name=name,
                grade=grade,
                defaults={
                    'capacity': 30,
                    'is_active': True
                }
            )
            if created:
                created_sections.append(section)
        return created_sections

    def get_available_seats(self):
        """Retorna el número de vacantes disponibles"""
        return self.capacity - self.current_students

    def is_full(self):
        """Retorna True si la sección está llena"""
        return self.current_students >= self.capacity

class Enrollment(models.Model):
    """Modelo para la matrícula de estudiantes en secciones."""
    ENROLLMENT_STATUS = [
        ('ACTIVE', 'Activo'),
        ('WITHDRAWN', 'Retirado'),
        ('SUSPENDED', 'Suspendido'),
        ('GRADUATED', 'Graduado'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Estudiante')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Sección')
    academic_year = models.CharField(max_length=9, verbose_name='Año Académico', default=str(timezone.now().year))
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='ACTIVE', verbose_name='Estado')
    enrollment_date = models.DateField(verbose_name='Fecha de Matrícula', default=timezone.now)
    withdrawal_date = models.DateField(verbose_name='Fecha de Retiro', null=True, blank=True)
    notes = models.TextField(verbose_name='Observaciones', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        ordering = ['-enrollment_date']
        unique_together = ['student', 'section', 'academic_year']

    def __str__(self):
        return f"{self.student} - {self.section} - {self.academic_year}"
    
    def save(self, *args, **kwargs):
        # Si es una nueva matrícula y está activa, incrementar el contador de estudiantes
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            # Obtener el estado anterior si es una actualización
            old_status = Enrollment.objects.get(pk=self.pk).status
        
        # Guardar el objeto primero
        super().save(*args, **kwargs)
        
        # Actualizar el contador de estudiantes en la sección
        section = self.section
        
        if is_new and self.status == 'ACTIVE':
            # Nueva matrícula activa
            section.current_students += 1
        elif not is_new and old_status != 'ACTIVE' and self.status == 'ACTIVE':
            # Cambio de estado de inactivo a activo
            section.current_students += 1
        elif not is_new and old_status == 'ACTIVE' and self.status != 'ACTIVE':
            # Cambio de estado de activo a inactivo
            section.current_students -= 1
        
        section.save()

class CourseAssignment(models.Model):
    """Modelo para la asignación de cursos a secciones con su respectivo docente."""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='course_assignments', verbose_name='Sección')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_assignments', verbose_name='Curso')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='course_assignments', verbose_name='Docente')
    hours_per_week = models.PositiveIntegerField(verbose_name='Horas semanales', default=4)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignación de Curso'
        verbose_name_plural = 'Asignaciones de Cursos'
        ordering = ['section', 'course']
        unique_together = ['section', 'course']  # Una sección solo puede tener una asignación por curso

    def __str__(self):
        return f"{self.course.name} - {self.section} - {self.teacher}"

class CourseMaterial(models.Model):
    """Modelo para los materiales de curso."""
    MATERIAL_TYPE_CHOICES = [
        ('PRESENTACION', 'Presentación'),
        ('GUIA', 'Guía de estudio'),
        ('TAREA', 'Tarea'),
        ('EXAMEN', 'Examen'),
        ('LECTURA', 'Lectura'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('OTRO', 'Otro'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials', verbose_name='Curso')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción', blank=True)
    file = models.FileField(upload_to='course_materials/%Y/%m/', verbose_name='Archivo', blank=True, null=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='OTRO', verbose_name='Tipo de Material')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_materials', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Material de Curso'
        verbose_name_plural = 'Materiales de Curso'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.course.name}"

class CourseTopic(models.Model):
    """Modelo para los temas del curso a nivel general (no por estudiante individual)."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics', verbose_name='Curso')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='course_topics', verbose_name='Sección')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='course_topics', verbose_name='Profesor')
    title = models.CharField(max_length=200, verbose_name='Título del Tema')
    description = models.TextField(verbose_name='Descripción del Tema', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_course_topics',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tema de Curso'
        verbose_name_plural = 'Temas de Curso'
        ordering = ['course', 'section', 'created_at']
        unique_together = ['course', 'section', 'title']  # Un tema único por curso/sección

    def __str__(self):
        return f"{self.title} - {self.course.name} - {self.section}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='assignments')
    section = models.ForeignKey('Section', on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.course.name} ({self.section.name})"
