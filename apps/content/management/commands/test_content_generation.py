import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.content.views import get_openai_service
from apps.ai_content_generator.services.llm_service import DeepSeekService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Prueba la generación de contenido para diagnosticar problemas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prompt',
            type=str,
            default='Explica qué es la fotosíntesis y su importancia para la vida en la Tierra',
            help='Prompt para generar contenido'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando diagnóstico de generación de contenido...'))
        
        # 1. Verificar variables de entorno
        self.stdout.write('\n📋 Verificando configuración:')
        
        deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        if deepseek_key:
            self.stdout.write(f'✅ DEEPSEEK_API_KEY configurada (longitud: {len(deepseek_key)})')
        else:
            self.stdout.write('❌ DEEPSEEK_API_KEY no encontrada en variables de entorno')
            
        from django.conf import settings
        settings_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if settings_key:
            self.stdout.write(f'✅ DEEPSEEK_API_KEY en settings (longitud: {len(settings_key)})')
        else:
            self.stdout.write('❌ DEEPSEEK_API_KEY no encontrada en settings')
        
        # 2. Probar inicialización del servicio
        self.stdout.write('\n🚀 Probando inicialización del servicio:')
        try:
            service = DeepSeekService()
            self.stdout.write(f'✅ Servicio inicializado')
            self.stdout.write(f'📡 API disponible: {service.api_available}')
            self.stdout.write(f'🔑 Tiene API key: {bool(service.api_key)}')
            self.stdout.write(f'🌐 URL base: {service.base_url}')
            self.stdout.write(f'🤖 Modelo: {service.model}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al inicializar servicio: {e}'))
            return
        
        # 3. Probar get_openai_service()
        self.stdout.write('\n🔧 Probando get_openai_service():')
        try:
            service_from_views = get_openai_service()
            if service_from_views:
                self.stdout.write('✅ get_openai_service() retorna servicio')
                self.stdout.write(f'📡 API disponible desde views: {service_from_views.api_available}')
            else:
                self.stdout.write('❌ get_openai_service() retorna None')
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en get_openai_service(): {e}'))
            return
        
        # 4. Probar generación de contenido
        self.stdout.write('\n📝 Probando generación de contenido:')
        prompt = options['prompt']
        self.stdout.write(f'📋 Prompt: {prompt}')
        
        try:
            resultado = service.generate_content(prompt)
            
            if resultado:
                self.stdout.write('✅ Contenido generado exitosamente')
                self.stdout.write(f'📏 Longitud: {len(resultado)} caracteres')
                
                # Mostrar una vista previa
                preview = resultado[:500] if len(resultado) > 500 else resultado
                self.stdout.write(f'\n👀 Vista previa del contenido:')
                self.stdout.write('-' * 50)
                self.stdout.write(preview)
                if len(resultado) > 500:
                    self.stdout.write('...')
                self.stdout.write('-' * 50)
                
                # Verificar si es JSON válido
                try:
                    import json
                    contenido_json = json.loads(resultado)
                    self.stdout.write('✅ Contenido es JSON válido')
                    self.stdout.write(f'📊 Claves encontradas: {list(contenido_json.keys())}')
                except json.JSONDecodeError:
                    self.stdout.write('⚠️ Contenido no es JSON válido')
                    
            else:
                self.stdout.write('❌ No se generó contenido')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al generar contenido: {e}'))
            logger.exception("Error detallado en generación de contenido:")
            
        # 5. Probar conversión a HTML
        self.stdout.write('\n🌐 Probando conversión a HTML:')
        try:
            from apps.content.views import convertir_json_a_html
            import json
            
            # Crear un JSON de prueba
            test_json = {
                "titulo": "Prueba de Conversión",
                "descripcion": "Prueba de la función de conversión JSON a HTML",
                "secciones": [
                    {
                        "titulo": "Sección de Prueba",
                        "contenido": "Este es contenido de prueba",
                        "imagen_sugerida": "Imagen de prueba"
                    }
                ]
            }
            
            html_resultado = convertir_json_a_html(test_json)
            if html_resultado:
                self.stdout.write('✅ Conversión JSON a HTML exitosa')
                self.stdout.write(f'📏 Longitud HTML: {len(html_resultado)} caracteres')
            else:
                self.stdout.write('❌ Error en conversión JSON a HTML')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en conversión HTML: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Diagnóstico completado')) 