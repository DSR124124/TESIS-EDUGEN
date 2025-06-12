from django.db import models
from django.conf import settings
from apps.ai_content_generator.models import GeneratedContent

class SCORMPackage(models.Model):
    STANDARD_CHOICES = (
        ('scorm_1.2', 'SCORM 1.2'),
        ('scorm_2004_3rd', 'SCORM 2004 3rd Edition'),
        ('scorm_2004_4th', 'SCORM 2004 4th Edition'),
    )
    
    generated_content = models.ForeignKey(GeneratedContent, on_delete=models.CASCADE, related_name='scorm_packages')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    standard = models.CharField(max_length=20, choices=STANDARD_CHOICES, default='scorm_2004_4th')
    package_file = models.FileField(upload_to='scorm_packages/')
    manifest_file = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scorm_packages'
    )
    
    def __str__(self):
        return f"{self.title} v{self.version}"
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('scorm_packager:scorm_package_detail', args=[str(self.id)]) 