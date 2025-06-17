from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from apps.academic.models import Grade, Section, Course, CourseAssignment, Teacher as AcademicTeacher
from apps.accounts.models import Teacher, CustomUser, UserSettings
from .forms import TeacherRegistrationForm, SectionForm, TeacherUpdateForm, CourseAssignmentForm, UserProfileForm, CourseForm, InstitutionEditForm, InstitutionSettingsForm
from django.db.models import Q, Count
from django.utils import timezone
from apps.academic.models import Student, Enrollment
from .forms import StudentForm, StudentUserForm, EnrollmentForm
from apps.institutions.models import Institution, InstitutionSettings

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'director/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = Grade.objects.all()
        context['sections'] = Section.objects.all()
        context['teachers'] = Teacher.objects.all()
        
        # Agregar contadores de estudiantes y matrículas
        context['students_count'] = Student.objects.filter(is_active=True).count()
        context['active_enrollments'] = Enrollment.objects.filter(status='ACTIVE').count()
        
        # Últimas matrículas realizadas
        context['recent_enrollments'] = Enrollment.objects.filter(
            status='ACTIVE'
        ).select_related('student', 'section').order_by('-created_at')[:5]
        
        # Información de la institución
        try:
            from apps.institutions.models import Institution
            # Intentar obtener la institución desde el perfil de director
            if hasattr(self.request.user, 'director_profile') and hasattr(self.request.user.director_profile, 'institution'):
                context['institution'] = self.request.user.director_profile.institution
            else:
                # Valor por defecto si no hay institución asociada
                context['institution_name'] = "Colegio Nacional EduGen"
                context['institution_address'] = "Av. Universidad 1234, Lima"
                context['institution_type'] = "Educación Secundaria"
        except (AttributeError, ImportError):
            # Valores por defecto si no existe el módulo
            context['institution_name'] = "Colegio Nacional EduGen"
            context['institution_address'] = "Av. Universidad 1234, Lima"
            context['institution_type'] = "Educación Secundaria"
            
        return context

class RedirectUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('director:dashboard')

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'director/courses/course_list.html'
    context_object_name = 'courses'

class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    template_name = 'director/courses/course_form.html'
    form_class = CourseForm
    success_url = reverse_lazy('director:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Curso creado exitosamente.')
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    template_name = 'director/courses/course_form.html'
    form_class = CourseForm
    success_url = reverse_lazy('director:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Curso actualizado exitosamente.')
        return super().form_valid(form)

class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = 'director/courses/course_confirm_delete.html'
    success_url = reverse_lazy('director:course_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Curso eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class AcademicStructureView(LoginRequiredMixin, TemplateView):
    template_name = 'director/academic_structure.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los grados
        grades = Grade.objects.all()
        if not grades.exists():
            Grade.create_secondary_grades()
            grades = Grade.objects.all()
        
        # Ordenar los grados jerárquicamente (Primero a Quinto)
        grade_order = {'PRIMERO': 1, 'SEGUNDO': 2, 'TERCERO': 3, 'CUARTO': 4, 'QUINTO': 5}
        ordered_grades = sorted(grades, key=lambda g: grade_order.get(g.name, 999))
        
        # Agrupar secciones por grado
        sections_by_grade = {}
        for grade in grades:
            sections_by_grade[grade] = grade.sections.all()
            
        context['grades'] = grades
        context['ordered_grades'] = ordered_grades
        context['sections_by_grade'] = sections_by_grade
        
        # Estadísticas
        context['total_grades'] = grades.count()
        context['total_sections'] = Section.objects.count()
        context['active_sections'] = Section.objects.filter(is_active=True).count()
        
        return context

class SectionCreateView(LoginRequiredMixin, CreateView):
    model = Section
    form_class = SectionForm
    template_name = 'director/sections/section_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        # Si se proporciona grade_id en los parámetros GET, pre-seleccionar el grado
        grade_id = self.request.GET.get('grade')
        if grade_id:
            try:
                grade = Grade.objects.get(pk=grade_id)
                initial['grade'] = grade
            except Grade.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        messages.success(self.request, 'Sección creada exitosamente.')
        return reverse_lazy('director:academic_structure')
    
    def form_valid(self, form):
        # Asignar el director actual como creador de la sección
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class SectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'director/sections/section_form.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Sección actualizada exitosamente.')
        return reverse_lazy('director:academic_structure')
    
    def form_valid(self, form):
        # Asignar el director actual como último actualizador
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

class SectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Section
    template_name = 'director/sections/section_confirm_delete.html'
    success_url = reverse_lazy('director:academic_structure')
    
    def delete(self, request, *args, **kwargs):
        section = self.get_object()
        # Cambiar estado a inactivo en lugar de eliminar
        section.is_active = False
        section.save()
        messages.success(request, f'Sección {section.name} desactivada exitosamente.')
        return redirect(self.success_url)

class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'director/teachers/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 12  # Paginar resultados

    def get_queryset(self):
        queryset = Teacher.objects.filter(user__is_active=True).select_related('user')
        
        # Aplicar filtros de búsqueda si existen
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(teacher_code__icontains=search) |
                Q(dni__icontains=search)
            )
        
        # Aplicar filtro de estado
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(user__is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(user__is_active=False)
        
        return queryset.order_by('user__first_name', 'user__last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas para el dashboard
        total_teachers = Teacher.objects.count()
        active_teachers = Teacher.objects.filter(user__is_active=True).count()
        inactive_teachers = total_teachers - active_teachers
        
        context.update({
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            'inactive_teachers': inactive_teachers,
            'search_query': self.request.GET.get('search', ''),
            'status_filter': self.request.GET.get('status', 'all'),
        })
        
        return context

class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherRegistrationForm
    template_name = 'director/teachers/teacher_form.html'
    success_url = reverse_lazy('director:teacher_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Arreglo para cuando no hay institución asociada al director
        # Usar un valor por defecto para que el formulario no falle
        try:
            from apps.institutions.models import Institution
            # Intentar obtener la institución desde el perfil de director en institutions
            director_institution = self.request.user.director_profile.institution
            kwargs['institution'] = director_institution
            self.institution = director_institution
        except (AttributeError, ImportError):
            # Si no existe la relación o hay otro error, usar una institución por defecto
            # O simplemente establecer un dominio predeterminado
            class DefaultInstitution:
                domain = "escuela"
            kwargs['institution'] = DefaultInstitution()
            self.institution = DefaultInstitution()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['institution'] = getattr(self, 'institution', None)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Docente registrado exitosamente')
        return response

class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    template_name = 'director/teachers/teacher_form.html'
    form_class = TeacherUpdateForm
    success_url = reverse_lazy('director:teacher_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def form_valid(self, form):
        # Verificar si la especialidad cambió para mostrar mensaje específico
        old_speciality = None
        new_speciality = form.cleaned_data.get('speciality')
        
        try:
            from apps.academic.models import Teacher as AcademicTeacher
            academic_teacher = AcademicTeacher.objects.get(user=self.object.user)
            old_speciality = academic_teacher.speciality
        except AcademicTeacher.DoesNotExist:
            pass
        
        response = super().form_valid(form)
        
        # Mensaje específico si cambió la especialidad
        if old_speciality and new_speciality and old_speciality != new_speciality:
            speciality_choices = dict(AcademicTeacher.SPECIALITY_CHOICES)
            old_name = speciality_choices.get(old_speciality, old_speciality)
            new_name = speciality_choices.get(new_speciality, new_speciality)
            messages.success(
                self.request, 
                f'Docente actualizado exitosamente. Especialidad cambiada de {old_name} a {new_name}.'
            )
        else:
            messages.success(self.request, 'Docente actualizado exitosamente')
        
        return response

class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'director/teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('director:teacher_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Docente eliminado exitosamente')
        return super().delete(request, *args, **kwargs)

# Vistas para la asignación de cursos a secciones
class SectionDetailView(LoginRequiredMixin, DetailView):
    model = Section
    template_name = 'director/sections/section_detail.html'
    context_object_name = 'section'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todas las asignaciones de cursos para esta sección
        context['course_assignments'] = CourseAssignment.objects.filter(
            section=self.object
        ).select_related('course', 'teacher')
        
        # Obtener las matrículas activas para esta sección y los estudiantes relacionados
        enrollments = Enrollment.objects.filter(
            section=self.object,
            status='ACTIVE'
        ).select_related('student', 'student__user')
        
        context['enrollments'] = enrollments
        context['enrolled_students'] = [enrollment.student for enrollment in enrollments]
        
        return context

# Agregamos la vista para la asignación de cursos
class CourseAssignmentView(LoginRequiredMixin, TemplateView):
    template_name = 'director/sections/course_assignments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id = self.kwargs.get('section_id')
        section = get_object_or_404(Section, pk=section_id)
        context['section'] = section
        context['course_assignments'] = CourseAssignment.objects.filter(
            section=section
        ).select_related('course', 'teacher')
        context['available_courses'] = Course.objects.filter(is_active=True)
        context['available_teachers'] = AcademicTeacher.objects.filter(is_active=True)
        return context

class CourseAssignmentCreateView(LoginRequiredMixin, CreateView):
    model = CourseAssignment
    form_class = CourseAssignmentForm
    template_name = 'director/sections/course_assignment_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar el ID de la sección al formulario si está en los parámetros de la URL
        if 'section_id' in self.kwargs:
            kwargs['section_id'] = self.kwargs['section_id']
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Si hay un section_id en los parámetros, agregar la sección al contexto
        if 'section_id' in self.kwargs:
            context['section'] = get_object_or_404(Section, pk=self.kwargs['section_id'])
        
        # Agregar información adicional para debugging
        from apps.academic.models import Teacher as AcademicTeacher
        context['total_teachers'] = AcademicTeacher.objects.count()
        context['active_teachers'] = AcademicTeacher.objects.filter(is_active=True).count()
        
        return context
    
    def get_success_url(self):
        # Redirigir de vuelta a la página de detalle de la sección
        if 'section_id' in self.kwargs:
            return reverse('director:section_detail', kwargs={'pk': self.kwargs['section_id']})
        return reverse_lazy('director:section_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Curso asignado exitosamente')
        return response

class CourseAssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = CourseAssignment
    form_class = CourseAssignmentForm
    template_name = 'director/sections/course_assignment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.object.section
        context['is_update'] = True
        return context
    
    def get_success_url(self):
        return reverse('director:section_detail', kwargs={'pk': self.object.section.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Asignación de curso actualizada exitosamente')
        return response

class CourseAssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseAssignment
    template_name = 'director/sections/course_assignment_confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.object.section
        return context
    
    def get_success_url(self):
        return reverse('director:section_detail', kwargs={'pk': self.object.section.pk})
    
    def delete(self, request, *args, **kwargs):
        course_assignment = self.get_object()
        section = course_assignment.section
        messages.success(request, f'El curso {course_assignment.course.name} ha sido desasignado de la sección {section}')
        return super().delete(request, *args, **kwargs)

# View for testing dropdown
class TestDropdownView(TemplateView):
    template_name = 'test_dropdown.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all teachers from academic app
        context['teachers'] = AcademicTeacher.objects.all()
        return context

# Vista para mostrar y editar el perfil de usuario
class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = 'director/profile/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Comprobar qué tipo de usuario es y obtener su perfil específico
        context['is_director'] = hasattr(user, 'director') if user.role == 'director' else False
        context['is_teacher'] = hasattr(user, 'teacher') if user.role == 'teacher' else False
        
        if context['is_director'] and hasattr(user, 'director'):
            context['profile'] = user.director
        elif context['is_teacher'] and hasattr(user, 'teacher'):
            context['profile'] = user.teacher
            # Si es un profesor, también podemos obtener su perfil académico
            try:
                from apps.academic.models import Teacher as AcademicTeacher
                context['academic_profile'] = AcademicTeacher.objects.filter(user=user).first()
            except:
                context['academic_profile'] = None
        
        return context
        
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'director/profile/profile_edit.html'
    success_url = reverse_lazy('director:user_profile')
    
    def get_object(self):
        return self.request.user
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        if user.role == 'director' and hasattr(user, 'director'):
            kwargs['profile_type'] = 'director'
        elif user.role == 'teacher' and hasattr(user, 'teacher'):
            kwargs['profile_type'] = 'teacher'
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)

# Vista para la configuración de la cuenta de usuario
class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'director/settings/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener o crear configuraciones del usuario
        settings = UserSettings.get_or_create_settings(user)
        
        # Información del usuario para la página de configuración
        context['user'] = user
        context['is_director'] = hasattr(user, 'director') if user.role == 'director' else False
        context['is_teacher'] = hasattr(user, 'teacher') if user.role == 'teacher' else False
        context['settings'] = settings
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        settings = UserSettings.get_or_create_settings(user)
        
        # Actualizar configuraciones desde el formulario
        settings.theme = request.POST.get('theme', 'light')
        settings.email_notifications = 'email_notifications' in request.POST
        settings.system_notifications = 'system_notifications' in request.POST
        settings.reminders = 'reminders' in request.POST
        settings.animations_enabled = 'animations' in request.POST
        settings.compact_mode = 'compact_mode' in request.POST
        settings.show_contact_info = 'show_contact_info' in request.POST
        settings.two_factor_enabled = 'two_factor' in request.POST
        
        # Guardar cambios
        settings.save()
        
        messages.success(request, 'Configuración guardada correctamente')
        return redirect('director:user_settings')

# Vista para la información institucional
class InstitutionInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'director/institution/institution_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Intentar obtener información de la institución
        try:
            from apps.institutions.models import Institution
            # Intentar obtener la institución desde el perfil de director
            if hasattr(self.request.user, 'director_profile') and hasattr(self.request.user.director_profile, 'institution'):
                institution = self.request.user.director_profile.institution
                context['institution'] = institution
                context['has_institution'] = True
                
                # Obtener configuraciones de colores
                try:
                    settings = institution.settings
                    context['institution_colors'] = {
                        'primary': settings.primary_color,
                        'secondary': settings.secondary_color,
                        'accent': settings.accent_color,
                        'logo_enabled': settings.logo_enabled
                    }
                except InstitutionSettings.DoesNotExist:
                    context['institution_colors'] = {
                        'primary': '#005CFF',
                        'secondary': '#A142F5',
                        'accent': '#00CFFF',
                        'logo_enabled': True
                    }
            else:
                context['has_institution'] = False
        except (AttributeError, ImportError):
            context['has_institution'] = False
            
        # Estadísticas reales del sistema
        context['system_stats'] = {
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_teachers': Teacher.objects.filter(user__is_active=True).count(),
            'total_sections': Section.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.count(),
            'active_enrollments': Enrollment.objects.filter(status='ACTIVE').count()
        }
        
        # Información básica del director actual
        context['director_name'] = self.request.user.get_full_name()
        
        return context

# Vista para editar información institucional
class InstitutionEditView(LoginRequiredMixin, TemplateView):
    template_name = 'director/institution/institution_edit.html'
    
    def get_institution(self):
        # Obtener o crear la institución del director
        try:
            if hasattr(self.request.user, 'director_profile') and hasattr(self.request.user.director_profile, 'institution'):
                return self.request.user.director_profile.institution
            else:
                # Si no hay institución asociada, crear una nueva
                institution = Institution.objects.create(
                    name=f"Institución de {self.request.user.get_full_name()}",
                    code="0000000",  # Código temporal
                    domain=f"inst{self.request.user.id}",  # Dominio temporal
                    address=""
                )
                # Asociar al director si existe el perfil
                if hasattr(self.request.user, 'director_profile'):
                    self.request.user.director_profile.institution = institution
                    self.request.user.director_profile.save()
                return institution
        except Exception:
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        institution = self.get_institution()
        
        if institution:
            context['form'] = InstitutionEditForm(instance=institution)
            
            # Obtener o crear configuraciones de la institución
            settings, created = InstitutionSettings.objects.get_or_create(
                institution=institution,
                defaults={
                    'primary_color': '#005CFF',
                    'secondary_color': '#A142F5',
                    'accent_color': '#00CFFF',
                    'logo_enabled': True
                }
            )
            context['settings_form'] = InstitutionSettingsForm(instance=settings)
        
        return context
    
    def post(self, request, *args, **kwargs):
        institution = self.get_institution()
        if not institution:
            messages.error(request, 'No se pudo encontrar la institución.')
            return redirect('director:institution_info')
        
        # Guardar logo anterior para debug
        old_logo = institution.logo
        
        form = InstitutionEditForm(request.POST, request.FILES, instance=institution)
        
        # Obtener configuraciones de la institución
        settings, created = InstitutionSettings.objects.get_or_create(
            institution=institution,
            defaults={
                'primary_color': '#005CFF',
                'secondary_color': '#A142F5',
                'accent_color': '#00CFFF',
                'logo_enabled': True
            }
        )
        settings_form = InstitutionSettingsForm(request.POST, instance=settings)
        
        if form.is_valid() and settings_form.is_valid():
            # El formulario de Django maneja automáticamente la eliminación del logo
            # a través del campo ClearableFileInput y el checkbox logo-clear_id
            form.save()
            settings_form.save()
            
            # Verificar si se eliminó el logo
            if old_logo and not institution.logo:
                messages.success(request, f'Logo eliminado correctamente para {institution.name}.')
            elif 'logo' in request.FILES:
                messages.success(request, f'Logo actualizado correctamente para {institution.name}.')
            else:
                messages.success(request, f'Información de {institution.name} actualizada correctamente.')
            
            return redirect('director:institution_info')
        else:
            # Mostrar errores específicos del formulario
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            if settings_form.errors:
                for field, errors in settings_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Configuración - {field}: {error}')
            
            return self.render_to_response(
                self.get_context_data(form=form, settings_form=settings_form)
            )

# Vista para actualizar configuración de colores
class InstitutionSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = InstitutionSettings
    form_class = InstitutionSettingsForm
    success_url = reverse_lazy('director:institution_info')
    
    def get_object(self):
        # Obtener configuraciones de la institución del director
        try:
            if hasattr(self.request.user, 'director_profile') and hasattr(self.request.user.director_profile, 'institution'):
                institution = self.request.user.director_profile.institution
                settings, created = InstitutionSettings.objects.get_or_create(
                    institution=institution,
                    defaults={
                        'primary_color': '#005CFF',
                        'secondary_color': '#A142F5',
                        'accent_color': '#00CFFF',
                        'logo_enabled': True
                    }
                )
                return settings
        except Exception:
            pass
        return None
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            messages.error(request, 'No se pudo encontrar la configuración de la institución.')
            return redirect('director:institution_info')
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, 'Error al actualizar la configuración.')
            return redirect('director:institution_info')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Configuración de colores actualizada correctamente.')
        return redirect(self.success_url)

# Vistas para la gestión de estudiantes
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'director/students/student_list.html'
    context_object_name = 'students'
    paginate_by = 15  # Mostrar 15 estudiantes por página
    ordering = ['user__first_name', 'user__last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user').prefetch_related('enrollments__section__grade')
        
        # Filtrar por búsqueda si se proporciona
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(dni__icontains=search_query) |
                Q(guardian_name__icontains=search_query) |
                Q(guardian_phone__icontains=search_query)
            )
        
        # Filtrar por grado si se proporciona
        grade_filter = self.request.GET.get('grade', '')
        if grade_filter:
            queryset = queryset.filter(enrollments__section__grade__id=grade_filter, enrollments__status='ACTIVE')
        
        # Filtrar por estado si se proporciona
        status_filter = self.request.GET.get('status', '')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['grade_filter'] = self.request.GET.get('grade', '')
        context['status_filter'] = self.request.GET.get('status', '')
        
        # Obtener todos los grados para el filtro
        context['available_grades'] = Grade.objects.all()
        
        # Contar estudiantes por grado y sección (optimizado)
        enrollments = Enrollment.objects.filter(status='ACTIVE').select_related('student', 'section__grade')
        context['total_students'] = enrollments.values('student').distinct().count()
        
        # Calcular estadísticas por grado de manera más eficiente
        context['students_by_grade'] = {}
        grade_counts = enrollments.values('section__grade').annotate(
            student_count=Count('student', distinct=True)
        )
        
        for grade_count in grade_counts:
            try:
                grade = Grade.objects.get(id=grade_count['section__grade'])
                context['students_by_grade'][grade] = grade_count['student_count']
            except Grade.DoesNotExist:
                continue
                
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'director/students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        # Obtener matrículas del estudiante
        context['enrollments'] = student.enrollments.all().order_by('-academic_year')
        # Obtener matrícula activa actual
        context['current_enrollment'] = student.enrollments.filter(status='ACTIVE').first()
        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'director/students/student_form.html'
    success_url = reverse_lazy('director:student_list')
    
    def get_context_data(self, **kwargs):
        # Reemplazar super().get_context_data() porque causa el error de 'object'
        context = {}
        context.update(kwargs)
        context['view'] = self
        
        # Agregar el formulario si no está en kwargs
        if 'form' not in context:
            context['form'] = self.get_form()
            
        # Agregar el user_form si no está en contexto
        if 'user_form' not in context:
            context['user_form'] = StudentUserForm()
            
        # Agregar información adicional para la plantilla
        context['is_create'] = True
        context['title'] = 'Crear Estudiante'
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        user_form = StudentUserForm(request.POST)
        
        if form.is_valid() and user_form.is_valid():
            return self.form_valid(form, user_form)
        else:
            return self.form_invalid(form, user_form)
    
    def form_valid(self, form, user_form):
        # Obtener valores de los campos
        link_with_google = form.cleaned_data.get('link_with_google', False)
        generate_username = form.cleaned_data.get('generate_username', True)
        default_password = form.cleaned_data.get('default_password', 'estudiante123')
        
        # Generar username automáticamente si está marcado
        if generate_username and not user_form.cleaned_data.get('username'):
            first_name = user_form.cleaned_data.get('first_name', '')
            dni = form.cleaned_data.get('dni', '')
            # Generar username: primera letra del nombre + dni
            username = f"{first_name[0].lower() if first_name else 'e'}{dni}"
            user_form.cleaned_data['username'] = username
            user_form.instance.username = username
        
        # Crear usuario con la contraseña apropiada
        user = user_form.save(
            link_with_google=link_with_google,
            default_password=default_password if not link_with_google else None
        )
        
        # Crear estudiante
        student = form.save(commit=False)
        student.user = user
        
        # Configurar vinculación con Google si está marcado
        if link_with_google and user_form.cleaned_data.get('email'):
            student.google_account = user_form.cleaned_data.get('email')
            student.google_account_linked = True
            student.google_linked_at = timezone.now()
        else:
            student.google_account_linked = False
        
        student.save()
        
        # Mensaje personalizado según el tipo de autenticación
        if link_with_google:
            messages.success(self.request, f'Estudiante creado correctamente. Podrá iniciar sesión con Google usando: {user.email}')
        else:
            messages.success(self.request, f'Estudiante creado correctamente. Credenciales de acceso: Usuario: {user.username} | Contraseña: {default_password}')
        
        return redirect(self.success_url)
    
    def form_invalid(self, form, user_form):
        # No usar el método get_context_data que causa el error
        context = {
            'form': form,
            'user_form': user_form,
            'view': self,
            'is_create': True,
            'title': 'Crear Estudiante'
        }
        return render(self.request, self.template_name, context)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'director/students/student_form.html'
    
    def get_success_url(self):
        return reverse_lazy('director:student_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = StudentUserForm(instance=self.object.user)
            # No mostrar el campo de contraseña en edición
            context['user_form'].fields.pop('password')
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        # Para el user_form, no incluimos el campo password en la edición
        user_form_data = request.POST.copy()
        if 'password' in user_form_data and not user_form_data['password']:
            user_form_data.pop('password')
        
        user_form = StudentUserForm(user_form_data, instance=self.object.user)
        if 'password' in user_form.fields:
            user_form.fields.pop('password')
        
        if form.is_valid() and user_form.is_valid():
            return self.form_valid(form, user_form)
        else:
            return self.form_invalid(form, user_form)
    
    def form_valid(self, form, user_form):
        # Actualizar usuario
        user = user_form.save()
        # Actualizar estudiante
        student = form.save()
        
        messages.success(self.request, 'Estudiante actualizado correctamente.')
        return redirect(self.get_success_url())
    
    def form_invalid(self, form, user_form):
        return self.render_to_response(
            self.get_context_data(form=form, user_form=user_form)
        )

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'director/students/student_confirm_delete.html'
    success_url = reverse_lazy('director:student_list')
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        # Primero inactivar el usuario asociado
        user = student.user
        user.is_active = False
        user.save()
        
        # Inactivar al estudiante
        student.is_active = False
        student.save()
        
        messages.success(request, 'Estudiante eliminado correctamente.')
        return redirect(self.success_url)

# Vistas para la gestión de matrículas
class EnrollmentCreateView(LoginRequiredMixin, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'director/enrollment/enrollment_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        # Si se proporciona student_id en la URL, pre-seleccionar el estudiante
        student_id = self.kwargs.get('student_id')
        if student_id:
            initial['student'] = student_id
            
        # Si se proporciona section_id en los parámetros GET, pre-seleccionar la sección
        section_id = self.request.GET.get('section')
        if section_id:
            try:
                section = Section.objects.get(pk=section_id)
                initial['section'] = section.id
            except Section.DoesNotExist:
                pass
                
        return initial
    
    def get_success_url(self):
        student_id = self.object.student.id
        return reverse_lazy('director:student_detail', kwargs={'pk': student_id})
    
    def form_valid(self, form):
        enrollment = form.save()
        messages.success(self.request, 'Matrícula creada correctamente.')
        return super().form_valid(form)

class EnrollmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'director/enrollment/enrollment_form.html'
    
    def get_success_url(self):
        student_id = self.object.student.id
        return reverse_lazy('director:student_detail', kwargs={'pk': student_id})
    
    def form_valid(self, form):
        enrollment = form.save()
        messages.success(self.request, 'Matrícula actualizada correctamente.')
        return super().form_valid(form)

class EnrollmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Enrollment
    template_name = 'director/enrollment/enrollment_confirm_delete.html'
    
    def get_success_url(self):
        student_id = self.object.student.id
        return reverse_lazy('director:student_detail', kwargs={'pk': student_id})
    
    def delete(self, request, *args, **kwargs):
        enrollment = self.get_object()
        # Cambiar estado a retirado en lugar de eliminar
        enrollment.status = 'WITHDRAWN'
        enrollment.withdrawal_date = timezone.now().date()
        enrollment.save()
        
        messages.success(request, 'Matrícula cancelada correctamente.')
        return redirect(self.get_success_url()) 