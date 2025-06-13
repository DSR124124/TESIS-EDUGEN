from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import Director, Teacher, CustomUser
from apps.academic.models import Section, Grade, Course, CourseAssignment, Teacher as AcademicTeacher, Student, Enrollment
from apps.institutions.models import Institution, InstitutionSettings
import unicodedata
from django.contrib.auth import get_user_model

class TeacherRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(
        label='Correo Institucional', 
        required=True
    )
    dni = forms.CharField(label='DNI', max_length=8)
    phone = forms.CharField(label='Teléfono', max_length=9)
    address = forms.CharField(label='Dirección', max_length=200)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput, required=False)
    link_with_google = forms.BooleanField(
        label='Vincular con Google', 
        required=False, 
        initial=True,
        help_text='El docente podrá iniciar sesión con su cuenta de Google institucional'
    )
    speciality = forms.ChoiceField(
        label='Especialidad',
        choices=[
            ('MAT', 'Matemática'),
            ('COM', 'Comunicación'),
            ('CTA', 'Ciencia y Tecnología'),
            ('SOC', 'Ciencias Sociales'),
            ('ING', 'Inglés'),
            ('ART', 'Arte y Cultura'),
            ('EFI', 'Educación Física'),
        ]
    )

    class Meta:
        model = Teacher
        fields = ['dni', 'phone', 'address', 'speciality']

    def __init__(self, *args, **kwargs):
        self.institution = kwargs.pop('institution', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit() or len(dni) != 8:
            raise ValidationError('El DNI debe contener 8 dígitos')
        if Teacher.objects.filter(dni=dni).exists():
            raise ValidationError('Este DNI ya está registrado')
        return dni

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 9:
            raise ValidationError('El teléfono debe contener 9 dígitos')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        link_with_google = cleaned_data.get('link_with_google')
        
        # Si no se vincula con Google, la contraseña es obligatoria
        if not link_with_google:
            if not password1:
                self.add_error('password1', 'Este campo es obligatorio si no se vincula con Google')
            if not password2:
                self.add_error('password2', 'Este campo es obligatorio si no se vincula con Google')
        
        # Verificar que las contraseñas coincidan si se proporcionaron
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden')
            
        return cleaned_data

    def save(self, commit=True):
        link_with_google = self.cleaned_data.get('link_with_google')
        
        # Crear usuario con o sin contraseña dependiendo de si se vincula con Google
        if link_with_google:
            user = CustomUser.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                password=None,  # Sin contraseña para usuarios vinculados a Google
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                role='teacher'
            )
            # Marcar que el usuario debe autenticarse con Google
            user.set_unusable_password()
        else:
            user = CustomUser.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                role='teacher'
            )
            
        teacher = super().save(commit=False)
        teacher.user = user
        if commit:
            teacher.save()
        return teacher

class TeacherUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombres', max_length=150, required=False)
    last_name = forms.CharField(label='Apellidos', max_length=150, required=False)
    email = forms.EmailField(label='Correo Institucional', required=False, disabled=False)
    dni = forms.CharField(label='DNI', max_length=8)
    phone = forms.CharField(label='Teléfono', max_length=9)
    address = forms.CharField(label='Dirección', max_length=200)
    is_active = forms.BooleanField(label='Activo', required=False)
    speciality = forms.ChoiceField(
        label='Especialidad',
        choices=[
            ('MAT', 'Matemática'),
            ('COM', 'Comunicación'),
            ('CTA', 'Ciencia y Tecnología'),
            ('SOC', 'Ciencias Sociales'),
            ('ING', 'Inglés'),
            ('ART', 'Arte y Cultura'),
            ('EFI', 'Educación Física'),
        ],
        required=False
    )

    class Meta:
        model = Teacher
        fields = ['dni', 'phone', 'address', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar clases CSS para los widgets
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Si tenemos una instancia (estamos editando un docente existente)
        if self.instance and self.instance.pk:
            # Pre-llenar los campos del usuario asociado
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            
            # Pre-llenar especialidad desde el perfil académico si existe
            try:
                academic_teacher = AcademicTeacher.objects.get(user=self.instance.user)
                self.fields['speciality'].initial = academic_teacher.speciality
            except AcademicTeacher.DoesNotExist:
                # Si no existe el perfil académico, usar especialidad por defecto
                self.fields['speciality'].initial = 'MAT'
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit() or len(dni) != 8:
            raise ValidationError('El DNI debe contener 8 dígitos')
        
        # Verificar si el DNI ya está en uso, excluyendo al docente actual
        if Teacher.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este DNI ya está registrado')
        
        return dni
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 9:
            raise ValidationError('El teléfono debe contener 9 dígitos')
        return phone
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        # Actualizar datos del usuario asociado
        if self.cleaned_data.get('first_name'):
            teacher.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            teacher.user.last_name = self.cleaned_data['last_name']
        if self.cleaned_data.get('email'):
            teacher.user.email = self.cleaned_data['email']
        
        # Guardar usuario y docente
        if commit:
            teacher.user.save()
            teacher.save()
            
            # Actualizar o crear el perfil académico con la especialidad
            speciality = self.cleaned_data.get('speciality')
            if speciality:
                try:
                    academic_teacher, created = AcademicTeacher.objects.get_or_create(
                        user=teacher.user,
                        defaults={
                            'dni': teacher.dni,
                            'speciality': speciality,
                            'phone': teacher.phone,
                            'address': teacher.address,
                            'is_active': teacher.is_active
                        }
                    )
                    
                    # Si ya existía, actualizar sus datos
                    if not created:
                        academic_teacher.speciality = speciality
                        academic_teacher.dni = teacher.dni
                        academic_teacher.phone = teacher.phone
                        academic_teacher.address = teacher.address
                        academic_teacher.is_active = teacher.is_active
                        academic_teacher.save()
                        
                except Exception as e:
                    # Si hay algún error, no fallar la actualización del docente principal
                    print(f"Error al actualizar perfil académico: {e}")
        
        return teacher

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'grade', 'capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        grade = self.cleaned_data.get('grade')
        
        if not name:
            return name
            
        # Verificar si la sección ya existe en este grado
        if grade and Section.objects.filter(name=name, grade=grade).exists():
            # Si estamos editando la misma sección, permitir
            if self.instance and self.instance.pk and self.instance.name == name and self.instance.grade == grade:
                return name
            raise ValidationError(f"Ya existe una sección '{name}' en este grado.")
        
        return name

class StudentForm(forms.ModelForm):
    link_with_google = forms.BooleanField(
        label='Vincular con Google', 
        required=False, 
        initial=True,
        help_text='El estudiante podrá iniciar sesión con su cuenta de Google'
    )
    
    class Meta:
        model = Student
        fields = ['dni', 'birth_date', 'address', 'guardian_name', 'guardian_phone', 'is_active']
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dni'].validators.append(self.validate_dni)
        # Asegurarse que el widget tenga la clase correcta
        if 'link_with_google' in self.fields:
            self.fields['link_with_google'].widget.attrs.update({'class': 'form-check-input'})
    
    def validate_dni(self, value):
        if not value.isdigit() or len(value) != 8:
            raise ValidationError('El DNI debe contener exactamente 8 dígitos.')
        
        # Verificar si ya existe (excluyendo la instancia actual en caso de edición)
        if Student.objects.filter(dni=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise ValidationError('Ya existe un estudiante con este DNI.')
        
        return value

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'section', 'academic_year', 'status', 'enrollment_date', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control select2'}),
            'section': forms.Select(attrs={'class': 'form-control select2'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar secciones activas
        self.fields['section'].queryset = Section.objects.filter(is_active=True).select_related('grade')
        # Filtrar estudiantes activos
        self.fields['student'].queryset = Student.objects.filter(is_active=True).select_related('user')
        
        # Debug: Mostrar información de las secciones
        sections = Section.objects.filter(is_active=True)
        print(f"DEBUG EnrollmentForm: {sections.count()} secciones activas encontradas")
        for s in sections[:5]:  # Mostrar primeras 5
            print(f"  - {s.id}: {s}")
        
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        section = cleaned_data.get('section')
        academic_year = cleaned_data.get('academic_year')
        
        if student and section and academic_year:
            # Verificar si ya existe una matrícula para este estudiante en esta sección y año
            exists = Enrollment.objects.filter(
                student=student,
                section=section,
                academic_year=academic_year
            ).exclude(pk=getattr(self.instance, 'pk', None)).exists()
            
            if exists:
                raise ValidationError('Este estudiante ya está matriculado en esta sección para el año académico indicado.')
            
            # Verificar si la sección tiene capacidad
            if section.is_full() and not hasattr(self.instance, 'pk'):
                raise ValidationError('La sección seleccionada ha alcanzado su capacidad máxima.')
        
        return cleaned_data

class StudentUserForm(forms.ModelForm):
    """Formulario para crear usuario asociado al estudiante"""
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True, link_with_google=False, google_email=None):
        user = super().save(commit=False)
        if link_with_google:
            # Si se vincula con Google, establecer una contraseña inutilizable
            user.set_unusable_password()
        elif "password" in self.cleaned_data and self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        user.role = 'student'
        if commit:
            user.save()
        return user

class CourseAssignmentForm(forms.ModelForm):
    class Meta:
        model = CourseAssignment
        fields = ['section', 'course', 'teacher', 'hours_per_week', 'is_active']
        widgets = {
            'section': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={
                'class': 'form-select',
                'style': 'width: 100%; padding: 0.375rem 0.75rem;'
            }),
            'hours_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '12'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        section_id = kwargs.pop('section_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona un ID de sección, filtrar solo esa sección
        if section_id:
            try:
                section = Section.objects.get(id=section_id)
                self.fields['section'].initial = section
                self.fields['section'].widget.attrs['readonly'] = True
                self.fields['section'].queryset = Section.objects.filter(id=section_id)
            except Section.DoesNotExist:
                pass
        
        # Filtrar solo cursos activos
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        
        # Get ALL teachers from the AcademicTeacher model with proper ordering
        all_teachers = AcademicTeacher.objects.select_related('user').order_by('user__first_name', 'user__last_name')
        
        # Use all teachers (including inactive ones to give more options)
        self.fields['teacher'].queryset = all_teachers
        
        # Add labels to make them clearer
        self.fields['section'].label = 'Sección'
        self.fields['course'].label = 'Curso'
        self.fields['teacher'].label = 'Docente'
        self.fields['hours_per_week'].label = 'Horas por Semana'
        self.fields['is_active'].label = 'Activo'
    
    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data.get('section')
        course = cleaned_data.get('course')
        teacher = cleaned_data.get('teacher')
        
        # Verificar si el curso ya está asignado a la sección (excepto en edición)
        if section and course:
            existing = CourseAssignment.objects.filter(section=section, course=course)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(f"El curso '{course}' ya está asignado a esta sección")
        
        # Verificar que el profesor sea de la especialidad adecuada para el curso
        if teacher and course:
            # Aquí podrías implementar lógica para verificar si el docente tiene la especialidad
            # apropiada para el curso, basándote en alguna convención o regla de tu sistema
            pass
        
        return cleaned_data 

class UserProfileForm(forms.ModelForm):
    """Formulario para actualizar el perfil de usuario"""
    first_name = forms.CharField(
        label='Nombres', 
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellidos', 
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo Electrónico', 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Teléfono', 
        max_length=9, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        label='Dirección', 
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        self.profile_type = kwargs.pop('profile_type', None)
        super().__init__(*args, **kwargs)
        
        # Si el usuario tiene un perfil específico, cargar esos datos
        user = kwargs.get('instance')
        if user:
            if hasattr(user, 'teacher') and self.profile_type == 'teacher':
                self.fields['phone'].initial = user.teacher.phone
                self.fields['address'].initial = user.teacher.address
            elif hasattr(user, 'director') and self.profile_type == 'director':
                self.fields['phone'].initial = user.director.phone
                self.fields['address'].initial = user.director.address
                
    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Actualizar el perfil específico si existe
        if self.profile_type == 'teacher' and hasattr(user, 'teacher'):
            user.teacher.phone = self.cleaned_data['phone']
            user.teacher.address = self.cleaned_data['address']
            if commit:
                user.teacher.save()
        elif self.profile_type == 'director' and hasattr(user, 'director'):
            user.director.phone = self.cleaned_data['phone']
            user.director.address = self.cleaned_data['address']
            if commit:
                user.director.save()
                
        return user 

class CourseForm(forms.ModelForm):
    """Formulario para crear y editar cursos"""
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'credits', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nombre del Curso',
            'code': 'Código',
            'description': 'Descripción',
            'credits': 'Créditos',
            'is_active': 'Curso Activo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es una instancia existente, hay campos que no deben ser editables
        if self.instance and self.instance.pk:
            self.fields['code'].widget.attrs['readonly'] = True 

# Formulario para editar información institucional
class InstitutionEditForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = [
            'name', 'address', 'phone', 'email', 'website', 'logo',
            'mission', 'vision', 'description', 'type', 'established_year'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la institución',
                'required': True
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección de la institución'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@institucion.edu'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.institucion.edu'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/gif',
                'id': 'logo-input'
            }),
            'mission': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Misión de la institución'
            }),
            'vision': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Visión de la institución'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción general de la institución'
            }),
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Educación Secundaria'
            }),
            'established_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Año de fundación',
                'min': '1900',
                'max': '2024'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('El nombre de la institución es obligatorio.')
        
        # Verificar que el nombre no esté ya en uso por otra institución
        if Institution.objects.filter(name__iexact=name.strip()).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('Ya existe una institución con este nombre.')
        
        return name.strip()
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # Solo validar si es un archivo nuevo (recién subido)
            if hasattr(logo, 'content_type'):
                # Verificar el tamaño del archivo (máximo 2MB)
                if hasattr(logo, 'size') and logo.size > 2 * 1024 * 1024:  # 2MB
                    raise forms.ValidationError('El logo no puede exceder los 2MB.')
                
                # Verificar el tipo de archivo
                allowed_types = ['image/jpeg', 'image/png', 'image/gif']
                if logo.content_type not in allowed_types:
                    raise forms.ValidationError('Solo se permiten archivos JPG, PNG o GIF.')
            # Si es un archivo existente (ImageFieldFile), no necesitamos validarlo
            # ya que fue validado cuando se subió originalmente
        
        return logo

# Formulario para configuración de colores institucionales
class InstitutionSettingsForm(forms.ModelForm):
    class Meta:
        model = InstitutionSettings
        fields = ['primary_color', 'secondary_color', 'accent_color', 'logo_enabled']
        widgets = {
            'primary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Selecciona el color primario'
            }),
            'secondary_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Selecciona el color secundario'
            }),
            'accent_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Selecciona el color de acento'
            }),
            'logo_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        } 