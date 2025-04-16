from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

class VendorConfig(AppConfig):
    name = 'vendor'

    def ready(self):
        import app.signals  # Connect the signal here