from django.apps import AppConfig


class EnvanterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'envanter'
    
# Sinyal dosyalarımızı yüklemek için bu metodu ekliyoruz (Çok Önemli)
    def ready(self):
        import envanter.signals