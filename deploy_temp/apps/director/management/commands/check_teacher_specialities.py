from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Teacher as DirectorTeacher
from apps.academic.models import Teacher as AcademicTeacher

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica las especialidades de los docentes entre apps/accounts y apps/academic'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFICACIÓN DE ESPECIALIDADES ==='))
        
        # Obtener todos los docentes académicos
        academic_teachers = AcademicTeacher.objects.all().select_related('user')
        
        self.stdout.write(f'Total de docentes académicos: {academic_teachers.count()}')
        
        for teacher in academic_teachers:
            self.stdout.write(f'\n--- DOCENTE: {teacher.user.get_full_name()} ---')
            self.stdout.write(f'Usuario: {teacher.user.username}')
            self.stdout.write(f'Código: {teacher.teacher_code}')
            self.stdout.write(f'DNI: {teacher.dni}')
            self.stdout.write(f'Especialidad: {teacher.speciality} ({teacher.get_speciality_display()})')
            self.stdout.write(f'Activo: {teacher.is_active}')
            
            # Verificar si existe en apps/accounts
            try:
                director_teacher = DirectorTeacher.objects.get(user=teacher.user)
                self.stdout.write(f'Existe en accounts: ✓ (Código: {director_teacher.teacher_code})')
            except DirectorTeacher.DoesNotExist:
                self.stdout.write(self.style.WARNING('Existe en accounts: ✗'))
        
        # Verificar docentes sin especialidad definida
        teachers_without_speciality = academic_teachers.filter(speciality__isnull=True)
        if teachers_without_speciality.exists():
            self.stdout.write(f'\n{self.style.WARNING("DOCENTES SIN ESPECIALIDAD:")}')
            for teacher in teachers_without_speciality:
                self.stdout.write(f'- {teacher.user.get_full_name()} (ID: {teacher.id})')
        
        # Mostrar resumen de especialidades
        self.stdout.write(f'\n=== RESUMEN POR ESPECIALIDAD ===')
        for code, name in AcademicTeacher.SPECIALITY_CHOICES:
            count = academic_teachers.filter(speciality=code).count()
            self.stdout.write(f'{name}: {count} docentes')
        
        self.stdout.write(f'\n=== VERIFICACIÓN COMPLETADA ===') 