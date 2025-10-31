# kpy_sistemi/urls.py
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

# KPY'deki özel admin sitesini içeri aktarın
from kpy_sistemi.admin import kpy_admin_site 

urlpatterns = [
    # KRİTİK DÜZELTME: Varsayılan admin.site.urls yerine kpy_admin_site kullanıldı.
    path('admin/', kpy_admin_site.urls),  

    # Uygulama URL'leri
    path('users/', include('users.urls')),
    path('projects/', include('projects.urls')),
    path('finance/', include('finance.urls')),
    path('saha/', include('saha.urls')),
    # Envanter uygulaması için de URL tanımlamayı unutmayın (Eğer varsa).
    # path('envanter/', include('envanter.urls')),
]

# Geliştirme ortamı için Medya dosyalarını sunma ayarı
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Not: settings.py'de ROOT_URLCONF = 'kpy_sistemi.urls' ayarının doğru olduğundan emin olun.