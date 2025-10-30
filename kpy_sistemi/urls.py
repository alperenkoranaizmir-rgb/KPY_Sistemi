from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Ayar dosyasını (settings.py) import ediyoruz
from django.conf.urls.static import static # Statik/Medya dosyalarını sunmak için

urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('projects.urls')), # Yeni rapor URL'lerimizi buraya ekledik
]

# -----------------------------------------------------------------
# MEDYA (DOSYA YÜKLEME) AYARLARI (FAZ 3 - Geliştirme Sunucusu İçin)
# -----------------------------------------------------------------
# Bu ayar, SADECE geliştirme (DEBUG=True) modunda çalışır.
# Canlı (Production) sunucuda dosyaları Nginx sunacaktır.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)