import os
from celery import Celery

# Django ayarlarını Celery için tanımla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kpy_sistemi.settings')

# Celery uygulamasını oluştur
app = Celery('kpy_sistemi')

# Django ayarlarını Celery'ye yükle (Ayarlarımız settings.py'deki CELERY_... ile başlayacak)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django uygulamalarını (users, projects, finance vb.) otomatik olarak görevler için tara
app.autodiscover_tasks()

# Bu dosya Celery'nin başlatılması için gereklidir.
# Celery worker'ı başlatırken bu dosyayı kullanacağız.