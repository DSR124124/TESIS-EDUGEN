from django.core.management.base import BaseCommand
from apps.ai_content_generator.models import ContentType

class Command(BaseCommand):
    help = 'Configura los tipos de contenido específicos para el sistema reestructurado'

    def handle(self, *args, **options):
        """
        Configura los 5 tipos de contenido específicos con IDs fijos
        """
        
        # Limpiar tipos de contenido existentes
        ContentType.objects.all().delete()
        self.stdout.write("🗑️  Tipos de contenido existentes eliminados")
        
        # Definir los tipos de contenido específicos
        content_types = [
            {
                'id': 1,
                'name': 'Explicación de tema',
                'description': 'Explicación detallada de conceptos con ejemplos y ejercicios de comprensión.',
                'template_prompt': 'Se genera automáticamente con prompts específicos para explicaciones'
            },
            {
                'id': 2,
                'name': 'Ejercicios prácticos',
                'description': 'Conjunto de ejercicios graduados con soluciones paso a paso.',
                'template_prompt': 'Se genera automáticamente con prompts específicos para ejercicios'
            },
            {
                'id': 3,
                'name': 'Evaluación',
                'description': 'Evaluación completa con diferentes tipos de preguntas y rúbrica.',
                'template_prompt': 'Se genera automáticamente con prompts específicos para evaluaciones'
            },
            {
                'id': 4,
                'name': 'Material didáctico',
                'description': 'Material educativo interactivo con actividades y recursos multimedia.',
                'template_prompt': 'Se genera automáticamente con prompts específicos para material didáctico'
            },
            {
                'id': 5,
                'name': 'Resumen',
                'description': 'Síntesis concisa de los conceptos principales con puntos clave.',
                'template_prompt': 'Se genera automáticamente con prompts específicos para resúmenes'
            }
        ]
        
        # Crear los tipos de contenido
        created_count = 0
        for ct_data in content_types:
            content_type, created = ContentType.objects.get_or_create(
                id=ct_data['id'],
                defaults={
                    'name': ct_data['name'],
                    'description': ct_data['description'],
                    'template_prompt': ct_data['template_prompt']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Creado: {ct_data['id']} - {ct_data['name']}")
                )
            else:
                # Actualizar si ya existe
                content_type.name = ct_data['name']
                content_type.description = ct_data['description']
                content_type.template_prompt = ct_data['template_prompt']
                content_type.save()
                self.stdout.write(
                    self.style.WARNING(f"🔄 Actualizado: {ct_data['id']} - {ct_data['name']}")
                )
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"🎉 CONFIGURACIÓN COMPLETADA"))
        self.stdout.write(f"📊 Tipos de contenido creados/actualizados: {len(content_types)}")
        self.stdout.write("="*60)
        
        # Verificar configuración
        self.stdout.write("\n📋 TIPOS DE CONTENIDO CONFIGURADOS:")
        for ct in ContentType.objects.all().order_by('id'):
            self.stdout.write(f"   {ct.id}: {ct.name}")
        
        self.stdout.write("\n🔧 INTEGRACIÓN:")
        self.stdout.write("   - Los prompts se generan automáticamente según el tipo")
        self.stdout.write("   - Cada tipo tiene estructura específica de marcadores")
        self.stdout.write("   - Compatible con el sistema de procesamiento HTML")
        
        self.stdout.write(f"\n✅ Sistema listo para generar contenido estructurado") 