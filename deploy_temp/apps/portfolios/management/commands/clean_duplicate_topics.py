from django.core.management.base import BaseCommand
from django.db import transaction
from apps.portfolios.utils import clean_duplicate_portfolio_topics

class Command(BaseCommand):
    help = 'Limpia temas duplicados en los portafolios de estudiantes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se eliminaría sin hacer cambios reales',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Ejecutando en modo DRY-RUN - No se harán cambios reales')
            )
        
        try:
            with transaction.atomic():
                if dry_run:
                    # En modo dry-run, hacer rollback al final
                    cleaned_count = clean_duplicate_portfolio_topics()
                    transaction.set_rollback(True)
                else:
                    cleaned_count = clean_duplicate_portfolio_topics()
                
                if cleaned_count > 0:
                    message = f'Se {"eliminarían" if dry_run else "eliminaron"} {cleaned_count} temas duplicados'
                    self.stdout.write(self.style.SUCCESS(message))
                else:
                    self.stdout.write(
                        self.style.SUCCESS('No se encontraron temas duplicados para limpiar')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la limpieza: {str(e)}')
            ) 