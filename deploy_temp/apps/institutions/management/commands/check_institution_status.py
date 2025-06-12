from django.core.management.base import BaseCommand
from apps.institutions.models import Institution
from apps.accounts.models import Director
from apps.academic.models import Student


class Command(BaseCommand):
    help = 'Check institution and user status'

    def handle(self, *args, **options):
        # Check institutions
        institutions = Institution.objects.all()
        self.stdout.write(f'Total instituciones: {institutions.count()}')
        
        for inst in institutions:
            self.stdout.write(f'- {inst.name}: Logo={bool(inst.logo)}')
            if inst.logo:
                self.stdout.write(f'  Logo path: {inst.logo.url}')
        
        # Check directors
        directors = Director.objects.all()
        self.stdout.write(f'\nTotal directores: {directors.count()}')
        
        for director in directors:
            inst_name = director.institution.name if director.institution else 'Sin institución'
            self.stdout.write(f'- {director.user.get_full_name()}: {inst_name}')
        
        # Check students
        students = Student.objects.all()
        self.stdout.write(f'\nTotal estudiantes: {students.count()}')
        
        if students.exists():
            for student in students[:3]:
                self.stdout.write(f'- {student.user.get_full_name()}: {student.dni}')
        
        self.stdout.write(self.style.SUCCESS('Status check completed!')) 