from django.core.management.base import BaseCommand
from apps.academic.models import Teacher

class Command(BaseCommand):
    help = 'Lists all teachers in the academic app'

    def handle(self, *args, **options):
        teachers = Teacher.objects.all()
        self.stdout.write(f"Found {teachers.count()} teachers in academic app:")
        for teacher in teachers:
            self.stdout.write(f"- {teacher} (Code: {teacher.teacher_code})") 