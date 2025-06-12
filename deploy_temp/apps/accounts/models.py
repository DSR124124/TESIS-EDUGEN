# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import random
import string

class CustomUser(AbstractUser):
    ROLES = (
        ('director', 'Director'),
        ('teacher', 'Docente'),
        ('student', 'Estudiante'),
    )
    
    role = models.CharField(max_length=10, choices=ROLES, default='student')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.get_full_name() or self.username
        
    @property
    def is_student(self):
        """Verifica si el usuario es estudiante por su rol"""
        return self.role == 'student'
        
    @property
    def is_teacher(self):
        """Verifica si el usuario es docente por su rol"""
        return self.role == 'teacher'
        
    @property
    def is_director(self):
        """Verifica si el usuario es director por su rol"""
        return self.role == 'director'

class Director(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    dni = models.CharField(max_length=8, unique=True)
    phone = models.CharField(max_length=9)
    address = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Director'
        verbose_name_plural = 'Directores'

    def __str__(self):
        return self.user.get_full_name()

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    teacher_code = models.CharField(max_length=10, unique=True, editable=False)
    dni = models.CharField(max_length=8, unique=True)
    phone = models.CharField(max_length=9)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.teacher_code:
            # Generar código: DOC-XXXXX (donde X son números aleatorios)
            while True:
                code = 'DOC-' + ''.join(random.choices(string.digits, k=5))
                if not Teacher.objects.filter(teacher_code=code).exists():
                    self.teacher_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.teacher_code})"

    class Meta:
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'

class UserSettings(models.Model):
    """Modelo para almacenar las configuraciones de usuario"""
    THEME_CHOICES = [
        ('light', 'Claro'),
        ('dark', 'Oscuro'),
        ('blue', 'Azul'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    email_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    reminders = models.BooleanField(default=True)
    animations_enabled = models.BooleanField(default=True)
    compact_mode = models.BooleanField(default=False)
    show_contact_info = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de Usuario'
        verbose_name_plural = 'Configuraciones de Usuario'
        
    def __str__(self):
        return f"Configuración de {self.user.username}"
    
    @classmethod
    def get_or_create_settings(cls, user):
        """Obtiene las configuraciones de un usuario o crea unas por defecto"""
        settings, created = cls.objects.get_or_create(user=user)
        return settings