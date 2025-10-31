# kpy_sistemi/urls.py

from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

# ÖNEMLİ: Varsayılan admin yerine özel admin sitemizi import ediyoruz
from kpy_sistemi.admin import kpy_admin_site 

urlpatterns = [
    
    path('admin/', kpy_admin_site.urls), # <-- Bizim özel sitemiz
    
    # Raporlar için Projects URL'leri (Mevcut)
    path('projects/', include('projects.urls')), 
    
    # YENİ EKLENEN: Finance modülündeki raporların çalışması için
    path('finance/', include('finance.urls')),
    
    # YENİ EKLENEN: Saha modülündeki iş takibi ve raporlar için
    path('saha/', include('saha.urls')),
    
    # Users/İletişim modülündeki özel view'lar için (opsiyonel, views.py'den de yapılabilir)
    path('users/', include('users.urls')), # Varsayılan olarak users url'sini de dahil edelim.
]

# -----------------------------------------------------------------
# MEDYA (DOSYA YÜKLEME) AYARLARI
# -----------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)