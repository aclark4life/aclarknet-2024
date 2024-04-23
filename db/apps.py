from django.apps import AppConfig


class DBConfig(AppConfig):
    name = "db"

    def ready(self):
        import db.signals  # noqa
