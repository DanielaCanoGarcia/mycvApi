from django.apps import AppConfig


class HeaderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'header'

    def ready(self):
        import header.signals
