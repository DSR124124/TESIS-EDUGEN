from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from apps.academic.models import Enrollment, CourseAssignment, Section
from apps.portfolios.models import StudentPortfolio, PortfolioTopic

class Command(BaseCommand):
    help = 'Crea portafolios y temas iniciales para todas las matrículas existentes'

    def handle(self, *args, **kwargs):
        current_month = timezone.now().month
        current_year = timezone.now().year
        academic_year = str(current_year)
        
        # Obtener todas las matrículas activas
        enrollments = Enrollment.objects.filter(status='ACTIVE')
        self.stdout.write(f"Procesando {enrollments.count()} matrículas...")
        
        portfolios_created = 0
        topics_created = 0
        
        # Crear portafolios y temas iniciales
        for enrollment in enrollments:
            student = enrollment.student
            section = enrollment.section
            
            # Crear o obtener el portafolio para este estudiante
            portfolio, portfolio_created = StudentPortfolio.objects.get_or_create(
                student=student,
                month=current_month,
                academic_year=academic_year
            )
            
            if portfolio_created:
                portfolios_created += 1
            
            # Obtener asignaciones de cursos para esta sección
            course_assignments = CourseAssignment.objects.filter(
                section=section,
                is_active=True
            )
            
            # Crear temas para cada curso asignado
            for assignment in course_assignments:
                # Verificar si ya existe un tema para este curso
                topic_exists = PortfolioTopic.objects.filter(
                    portfolio=portfolio,
                    course=assignment.course,
                    teacher=assignment.teacher
                ).exists()
                
                if not topic_exists:
                    PortfolioTopic.objects.create(
                        portfolio=portfolio,
                        course=assignment.course,
                        teacher=assignment.teacher,
                        title=f"Tema inicial - {assignment.course.name}",
                        description="Tema creado automáticamente. Puede agregar materiales didácticos dentro de este tema.",
                        is_complete=False
                    )
                    topics_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Proceso completado: {portfolios_created} portafolios creados, "
            f"{topics_created} temas iniciales creados."
        )) 