from django import forms
from tinymce.widgets import TinyMCE
from .models import ContenidoInteractivo, ContenidoRecurso

class PrompterForm(forms.Form):
    """
    Formulario para solicitar un prompt que genere contenido con IA
    """
    prompt = forms.CharField(
        label="Prompt para IA",
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Describe el contenido que necesitas. Por ejemplo: "Explícame el ciclo del agua para estudiantes de primaria con actividades y una imagen representativa por sección."',
            'class': 'form-control'
        }),
        help_text="Describe con detalle el contenido educativo que deseas generar. Puedes solicitar secciones, actividades, imágenes, etc."
    )
    
    nivel_educativo = forms.ChoiceField(
        label="Nivel Educativo",
        choices=[
            ('', '-- Seleccionar nivel --'),
            ('inicial', 'Inicial'),
            ('primaria', 'Primaria'),
            ('secundaria', 'Secundaria'),
            ('superior', 'Educación Superior'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Opcional: Especifica el nivel educativo para adaptar el contenido."
    )
    
    incluir_imagenes = forms.BooleanField(
        label="Incluir sugerencias de imágenes",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="La IA sugerirá imágenes para cada sección del contenido."
    )
    
    incluir_actividades = forms.BooleanField(
        label="Incluir actividades o evaluaciones",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="La IA generará actividades o evaluaciones relacionadas al contenido."
    )


class EditorContenidoForm(forms.ModelForm):
    """
    Formulario para editar el contenido generado con TinyMCE
    """
    class Meta:
        model = ContenidoInteractivo
        fields = ['titulo', 'descripcion', 'contenido_html', 'etiquetas', 'nivel_educativo', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contenido_html': TinyMCE(attrs={
                'cols': 80, 'rows': 30,
                'class': 'form-control',
            }),
            'etiquetas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: matemáticas, geometría, primaria'
            }),
            'nivel_educativo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'titulo': 'Título descriptivo del contenido',
            'descripcion': 'Breve descripción del contenido y su propósito',
            'contenido_html': 'Edita el contenido utilizando el editor visual',
            'etiquetas': 'Palabras clave separadas por comas para facilitar búsquedas',
            'nivel_educativo': 'Nivel educativo al que está dirigido el contenido',
            'estado': 'Estado actual del contenido',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el widget TinyMCE con opciones personalizadas
        self.fields['contenido_html'].widget.mce_attrs.update({
            'plugins': 'advlist autolink lists link image charmap print preview hr anchor searchreplace '
                      'visualblocks visualchars code fullscreen insertdatetime media nonbreaking save table '
                      'directionality emoticons template paste',
            'toolbar': 'undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | '
                      'bullist numlist outdent indent | link image media | forecolor backcolor emoticons',
            'image_advtab': True,
            'height': 500,
            'width': '100%',
            'content_css': [
                'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css',
                '/static/content/css/editor.css',
            ],
            'content_style': 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 16px; }',
            'setup': 'function(editor) { editor.on("change", function() { editor.save(); }); }',
        })


class RecursoForm(forms.ModelForm):
    """
    Formulario para agregar recursos (imágenes, archivos, links) al contenido
    """
    class Meta:
        model = ContenidoRecurso
        fields = ['titulo', 'tipo', 'archivo', 'url', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        archivo = cleaned_data.get('archivo')
        url = cleaned_data.get('url')
        
        # Validar que se proporcione archivo o URL según el tipo
        if tipo in ['imagen', 'documento'] and not archivo and not url:
            raise forms.ValidationError(f"Debe proporcionar un archivo o URL para recursos de tipo {tipo}")
        
        if tipo == 'link' and not url:
            raise forms.ValidationError("Debe proporcionar una URL para recursos de tipo enlace")
        
        return cleaned_data


class BuscarImagenForm(forms.Form):
    """
    Formulario para buscar imágenes en APIs gratuitas
    """
    query = forms.CharField(
        label="Buscar imágenes",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ciclo del agua, planeta tierra, etc.'
        })
    ) 