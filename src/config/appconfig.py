from django.apps import AppConfig


class SrcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src"
    models_module = "src.infrastructure.orm.models"

    def ready(self):
        from src.interface.container import Container

        container = Container()
        container.wire(modules=["src.interface.api.views"])
