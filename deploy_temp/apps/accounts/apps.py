from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'  # Debe incluir 'apps.' como prefijo
    verbose_name = 'Cuentas de Usuario'

    def ready(self):
        # Import signals to register them
        import apps.accounts.signals

