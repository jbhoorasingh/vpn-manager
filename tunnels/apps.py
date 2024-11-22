from django.apps import AppConfig

class TunnelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tunnels'
    
    def ready(self):
        import tunnels.signals  # Import signals when app is ready