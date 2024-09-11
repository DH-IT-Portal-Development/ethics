from django.apps import AppConfig


class StudiesConfig(AppConfig):
    name = "studies"
    verbose_name = "studies"

    def ready(self):
        import studies.signals.handlers  # noqa
