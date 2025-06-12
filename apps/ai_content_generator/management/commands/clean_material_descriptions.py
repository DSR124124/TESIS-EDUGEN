from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from apps.portfolios.models import PortfolioMaterial
import re


class Command(BaseCommand):
    help = 'Limpia las descripciones de materiales que contienen código CSS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar materiales con descripciones que contengan CSS
        materials_with_css = PortfolioMaterial.objects.filter(
            description__icontains='<style'
        )
        
        self.stdout.write(f"Encontrados {materials_with_css.count()} materiales con CSS en la descripción")
        
        updated_count = 0
        
        for material in materials_with_css:
            old_description = material.description
            
            # Limpiar el contenido de HTML y CSS
            clean_content = strip_tags(old_description)
            
            # Remover CSS extra que pueda quedar
            clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r':\s*root\s*{[^}]*}', '', clean_content)
            clean_content = re.sub(r'--[a-zA-Z-]+:\s*[^;]+;', '', clean_content)
            
            # Extraer el título del contenido si está presente
            title_match = re.search(r'Material generado con IA:\s*([^\n]+)', clean_content)
            if title_match:
                ai_title = title_match.group(1).strip()
                # Remover el título del contenido
                clean_content = re.sub(r'Material generado con IA:[^\n]*\n*', '', clean_content)
            else:
                ai_title = material.title
            
            # Limitar la descripción a las primeras 200 palabras
            words = clean_content.split()[:200]
            clean_description = ' '.join(words)
            if len(words) == 200:
                clean_description += '...'
            
            # Crear nueva descripción
            new_description = f"Material generado con IA: {ai_title}\n\n{clean_description}".strip()
            
            if not dry_run:
                material.description = new_description
                material.save()
                updated_count += 1
            
            self.stdout.write(f"Material ID {material.id}: {material.title}")
            if options['verbosity'] >= 2:
                self.stdout.write(f"  Antes: {old_description[:100]}...")
                self.stdout.write(f"  Después: {new_description[:100]}...")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Se habrían actualizado {materials_with_css.count()} materiales")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Actualizados {updated_count} materiales exitosamente")
            ) 