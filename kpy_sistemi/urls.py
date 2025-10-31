# kpy_sistemi/urls.py

from django.contrib import admin
from django.urls import path, include  # <-- 'include' fonksiyonunu ekledik
from django.conf import settings
from django.conf.urls.static import static

# ÖNEMLİ: Varsayılan admin yerine özel admin sitemizi import ediyoruz
from kpy_sistemi.admin import kpy_admin_site 

urlpatterns = [
    
    # path('admin/', admin.site.urls), # <-- ESKİ YANLIŞ SATIR
    path('admin/', kpy_admin_site.urls), # <-- DOĞRU SATIR (Bizim özel sitemiz)
    
    # Diğer raporların (örn: Direnç Analizi) çalışması için bu satır gerekli
    path('projects/', include('projects.urls')), 
]

# -----------------------------------------------------------------
# MEDYA (DOSYA YÜKLEME) AYARLARI
# -----------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)