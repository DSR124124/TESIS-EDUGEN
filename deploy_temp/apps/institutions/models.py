from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from apps.accounts.models import Director

class Institution(models.Model):
    """Modelo para instituciones educativas."""
    
    name = models.CharField('Nombre', max_length=200)
    code = models.CharField(
        _('código modular'), 
        max_length=20, 
        unique=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{7}$',
                message='El código modular debe tener 7 dígitos'
            )
        ]
    )
    domain = models.CharField(
        _('dominio'), 
        max_length=100, 
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-z0-9]+$',
                message='El dominio solo puede contener letras minúsculas y números'
            )
        ],
        help_text='Este será el subdominio para la institución (ejemplo: miescuela)'
    )
    logo = models.ImageField(
        _('logo'), 
        upload_to='institutions/logos/', 
        blank=True, 
        null=True
    )
    address = models.CharField('Dirección', max_length=200, blank=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Correo electrónico', blank=True)
    website = models.URLField('Sitio web', blank=True)
    
    # Nuevos campos para información institucional
    mission = models.TextField('Misión', blank=True, null=True)
    vision = models.TextField('Visión', blank=True, null=True)
    description = models.TextField('Descripción', blank=True, null=True)
    type = models.CharField('Tipo de Educación', max_length=100, blank=True)
    established_year = models.PositiveIntegerField('Año de Fundación', blank=True, null=True)
    
    school_director = models.OneToOneField(
        Director,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_institution'
    )
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de creación', default=timezone.now)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Institución'
        verbose_name_plural = 'Instituciones'
        
    def __str__(self):
        return self.name


class InstitutionSettings(models.Model):
    """Configuraciones específicas por institución."""
    
    institution = models.OneToOneField(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='settings'
    )
    academic_year_start = models.DateField(_('inicio del año académico'), blank=True, null=True)
    academic_year_end = models.DateField(_('fin del año académico'), blank=True, null=True)
    enable_portfolio = models.BooleanField(_('habilitar portafolios'), default=True)
    enable_ai_content = models.BooleanField(_('habilitar contenido IA'), default=True)
    logo_enabled = models.BooleanField(_('mostrar logo en plataforma'), default=True)
    custom_theme = models.JSONField(_('tema personalizado'), default=dict, blank=True)
    
    # Colores personalizados del colegio
    primary_color = models.CharField(
        'Color Primario', 
        max_length=7, 
        default='#005CFF',
        help_text='Color principal de la institución (formato: #RRGGBB)'
    )
    secondary_color = models.CharField(
        'Color Secundario', 
        max_length=7, 
        default='#A142F5',
        help_text='Color secundario de la institución (formato: #RRGGBB)'
    )
    accent_color = models.CharField(
        'Color de Acento', 
        max_length=7, 
        default='#00CFFF',
        help_text='Color de acento de la institución (formato: #RRGGBB)'
    )
    
    class Meta:
        verbose_name = _('configuración de institución')
        verbose_name_plural = _('configuraciones de instituciones')
        
    def __str__(self):
        return f"Configuración: {self.institution.name}"


class Director(models.Model):
    """Modelo para directores de instituciones."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='director_profile'
    )
    institution = models.OneToOneField(
        Institution, 
        on_delete=models.CASCADE,
        related_name='director'
    )
    dni = models.CharField(_('DNI'), max_length=8, unique=True)
    phone = models.CharField(_('teléfono'), max_length=15)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('director')
        verbose_name_plural = _('directores')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.institution.name}"