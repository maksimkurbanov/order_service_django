from django.apps import AppConfig


class SrcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src"
    models_module = "src.infrastructure.orm.models"

    def ready(self):
        # This runs after all apps are loaded and the app registry is ready
        from src.interface.container import Container

        container = Container()
        container.wire(modules=["src.interface.api.views"])
