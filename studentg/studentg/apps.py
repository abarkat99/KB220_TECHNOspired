from django.apps import AppConfig


class StudentgConfig(AppConfig):
    name = 'studentg'

    def ready(self):
        import studentg.signals
