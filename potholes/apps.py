from django.apps import AppConfig


class PoththolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'potholes'

    def ready(self):
        import potholes.signals
