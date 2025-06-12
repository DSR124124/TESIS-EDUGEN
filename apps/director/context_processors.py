from apps.institutions.models import InstitutionSettings

def institution_context(request):
    """
    Context processor para agregar información institucional y colores a todas las plantillas
    """
    context = {
        'institution': None,
        'institution_colors': {
            'primary': '#005CFF',
            'secondary': '#A142F5',
            'accent': '#00CFFF'
        }
    }
    
    if request.user.is_authenticated:
        institution = None
        
        # Para directores
        if hasattr(request.user, 'director_profile'):
            try:
                if hasattr(request.user.director_profile, 'institution') and request.user.director_profile.institution:
                    institution = request.user.director_profile.institution
            except Exception:
                pass
                
        # Para estudiantes
        elif hasattr(request.user, 'student_profile'):
            try:
                from apps.academic.models import Teacher
                student = request.user.student_profile
                active_enrollment = student.enrollments.filter(status='ACTIVE').select_related('section').first()
                if active_enrollment:
                    teachers = Teacher.objects.filter(
                        course_assignments__section=active_enrollment.section
                    ).first()
                    
                    if teachers and hasattr(teachers.user, 'director_profile'):
                        institution = teachers.user.director_profile.institution
            except Exception:
                pass
                
        # Para profesores
        elif hasattr(request.user, 'teacher_profile'):
            try:
                # Los profesores también pueden tener acceso a través del director
                if hasattr(request.user, 'director_profile'):
                    institution = request.user.director_profile.institution
            except Exception:
                pass
        
        # Si encontramos una institución, agregarla al contexto
        if institution:
            context['institution'] = institution
            
            # Obtener colores personalizados
            try:
                if hasattr(institution, 'settings'):
                    settings = institution.settings
                    context['institution_colors'] = {
                        'primary': settings.primary_color,
                        'secondary': settings.secondary_color,
                        'accent': settings.accent_color
                    }
            except Exception:
                pass
    
    return context 