from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear un superusuario admin para el sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nombre de usuario para el admin (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@edugen.com',
            help='Email para el admin (default: admin@edugen.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña para el admin (default: admin123)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Ya existe un superusuario en el sistema.')
            )
            return

        # Verificar si ya existe el usuario
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'El usuario "{username}" ya existe.')
            )
            return

        try:
            # Crear el superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema',
                role='director'  # Asignar rol de director para compatibilidad
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuario creado exitosamente:\n'
                    f'  Username: {username}\n'
                    f'  Email: {email}\n'
                    f'  Password: {password}\n'
                    f'  ¡IMPORTANTE: Cambia la contraseña después del primer login!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear el superusuario: {str(e)}')
            ) 