from django.apps import AppConfig


class HomebuhwebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'homebuhweb'

    def ready(self):
        import homebuhweb.signals  # Подключаем сигналы из homebuhweb
