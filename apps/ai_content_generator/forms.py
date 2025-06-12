from django import forms
from .models import ContentRequest, ContentType, Course
from apps.academic.models import Grade

class ContentRequestForm(forms.ModelForm):
    """
    Formulario para crear solicitudes de generación de contenido
    """
    
    topic_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    # Definir explícitamente grade_level como un ChoiceField
    grade_level = forms.ChoiceField(
        choices=[('', '-- Seleccione un grado --')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Campo para subir PDF (no está asociado directamente con el modelo)
    pdf_file = forms.FileField(
        label="Archivo PDF para análisis",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control', 
            'accept': 'application/pdf'
        })
    )
    
    # Campo para controlar si se debe agregar automáticamente al portafolio
    add_to_portfolio = forms.BooleanField(
        label="Agregar automáticamente al portafolio",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = ContentRequest
        fields = ['course', 'content_type', 'topic', 'grade_level', 'additional_instructions', 'related_topic']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control select2'}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'related_topic': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar los cursos para mostrar solo los asignados al profesor
        if user and hasattr(user, 'teacher_profile'):
            # Obtener IDs únicos de cursos para evitar duplicados
            course_ids = Course.objects.filter(
                course_assignments__teacher=user.teacher_profile
            ).values_list('id', flat=True).distinct()
            
            # Usar QuerySet con distinct() para evitar cursos duplicados
            self.fields['course'].queryset = Course.objects.filter(id__in=course_ids)
        else:
            self.fields['course'].queryset = Course.objects.none()
        
        # Configurar las opciones del grado
        grade_choices = [('', '-- Seleccione un grado --')]
        grades = Grade.objects.filter(is_active=True).order_by('level', 'name')
        for grade in grades:
            grade_choices.append((grade.name, f"{grade.name} - {grade.get_level_display()}"))
        
        # Asignar las opciones al campo
        self.fields['grade_level'].choices = grade_choices
        self.fields['grade_level'].label = "Nivel/Grado"
        
        # Configurar las opciones del tipo de contenido
        self.fields['content_type'].queryset = ContentType.objects.all()
        self.fields['content_type'].empty_label = "-- Seleccione un tipo de contenido --"
        self.fields['content_type'].label = "Tipo de Contenido"
        
        # Mostrar información de diagnóstico
        print(f"Opciones de grado disponibles: {grade_choices}")
        print(f"Tipos de contenido disponibles: {list(ContentType.objects.values_list('name', flat=True))}")
        print(f"Initial data: {self.initial}")
        
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name not in ['topic_id', 'related_topic']:
                field.widget.attrs['class'] = 'form-control'
                
    def clean_course(self):
        course_id = self.cleaned_data.get('course')
        if course_id:
            try:
                # Para prevenir el error de múltiples objetos, usamos filter().first()
                # En lugar de intentar acceder a course_id.id, que podría ser ya un objeto Course
                if hasattr(course_id, 'id'):
                    # Si course_id ya es un objeto Course, usamos su ID
                    course_pk = course_id.id
                else:
                    # Si course_id es un ID (int o str), lo usamos directamente
                    course_pk = course_id
                
                course = Course.objects.filter(id=course_pk).first()
                if not course:
                    raise forms.ValidationError("El curso seleccionado no existe")
                return course
            except Exception as e:
                print(f"Error al limpiar el campo course: {str(e)}")
                raise forms.ValidationError(f"Error al procesar el curso: {str(e)}")
        return course_id 
    
    def clean_pdf_file(self):
        """Validar que el archivo sea un PDF y tenga un tamaño adecuado"""
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            # Verificar que sea un PDF
            if not pdf_file.name.endswith('.pdf'):
                raise forms.ValidationError("El archivo debe ser un PDF")
            # Verificar tamaño (máximo 10 MB)
            if pdf_file.size > 10 * 1024 * 1024:  # 10 MB
                raise forms.ValidationError("El tamaño del archivo no debe exceder 10 MB")
        return pdf_file 