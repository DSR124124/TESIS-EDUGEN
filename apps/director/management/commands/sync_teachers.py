import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Teacher as DirectorTeacher
from apps.academic.models import Teacher as AcademicTeacher

User = get_user_model()

class Command(BaseCommand):
    help = 'Sincroniza los docentes entre apps/accounts y apps/academic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Crear registros faltantes en apps/academic',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SINCRONIZACIÓN DE DOCENTES ==='))
        
        # Contar registros existentes
        director_teachers = DirectorTeacher.objects.all()
        academic_teachers = AcademicTeacher.objects.all()
        
        self.stdout.write(f'Docentes en apps/accounts: {director_teachers.count()}')
        self.stdout.write(f'Docentes en apps/academic: {academic_teachers.count()}')
        
        # Mostrar docentes en apps/accounts
        self.stdout.write('\n--- DOCENTES EN APPS/ACCOUNTS ---')
        for teacher in director_teachers:
            self.stdout.write(f'- {teacher.user.get_full_name()} (DNI: {teacher.dni}, Código: {teacher.teacher_code})')
        
        # Mostrar docentes en apps/academic
        self.stdout.write('\n--- DOCENTES EN APPS/ACADEMIC ---')
        for teacher in academic_teachers:
            self.stdout.write(f'- {teacher.user.get_full_name()} (DNI: {teacher.dni}, Código: {teacher.teacher_code})')
        
        # Verificar docentes que están en apps/accounts pero no en apps/academic
        missing_in_academic = []
        for director_teacher in director_teachers:
            if not AcademicTeacher.objects.filter(user=director_teacher.user).exists():
                missing_in_academic.append(director_teacher)
        
        if missing_in_academic:
            self.stdout.write(f'\n--- DOCENTES FALTANTES EN APPS/ACADEMIC ({len(missing_in_academic)}) ---')
            for teacher in missing_in_academic:
                self.stdout.write(f'- {teacher.user.get_full_name()} (DNI: {teacher.dni})')
                
                if options['create_missing']:
                    # Crear el registro en apps/academic con especialidad por defecto
                    academic_teacher = AcademicTeacher.objects.create(
                        user=teacher.user,
                        dni=teacher.dni,
                        speciality='MAT',  # Especialidad por defecto
                        phone=teacher.phone,
                        address=teacher.address,
                        is_active=teacher.is_active
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Creado en academic: {academic_teacher.teacher_code}'))
        else:
            self.stdout.write('\n✓ Todos los docentes están sincronizados')
        
        # Verificar docentes que están en apps/academic pero no en apps/accounts
        missing_in_accounts = []
        for academic_teacher in academic_teachers:
            if not DirectorTeacher.objects.filter(user=academic_teacher.user).exists():
                missing_in_accounts.append(academic_teacher)
        
        if missing_in_accounts:
            self.stdout.write(f'\n--- DOCENTES FALTANTES EN APPS/ACCOUNTS ({len(missing_in_accounts)}) ---')
            for teacher in missing_in_accounts:
                self.stdout.write(f'- {teacher.user.get_full_name()} (Código: {teacher.teacher_code})')
        
        self.stdout.write('\n=== RESUMEN ===')
        self.stdout.write(f'Total apps/accounts: {director_teachers.count()}')
        self.stdout.write(f'Total apps/academic: {academic_teachers.count()}')
        self.stdout.write(f'Faltantes en academic: {len(missing_in_academic)}')
        self.stdout.write(f'Faltantes en accounts: {len(missing_in_accounts)}')
        
        if options['create_missing'] and missing_in_academic:
            self.stdout.write(self.style.SUCCESS(f'✓ Se crearon {len(missing_in_academic)} registros en apps/academic'))
        elif missing_in_academic:
            self.stdout.write(self.style.WARNING('⚠ Ejecuta con --create-missing para crear los registros faltantes')) 