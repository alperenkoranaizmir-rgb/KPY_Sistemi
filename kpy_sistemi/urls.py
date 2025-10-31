from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Jazzmin Admin paneli rotası
    path('admin/', admin.site.urls),
    
    # Uygulama URL'leri
    path('users/', include('users.urls')),
    path('projects/', include('projects.urls')),
    path('finance/', include('finance.urls')),
    path('envanter/', include('envanter.urls')),
    path('saha/', include('saha.urls')),
    
    # Ana sayfa yönlendirmesi: Kök dizini (/) users uygulamasının URL'lerine yönlendiriyoruz
    path('', include('users.urls')), 
]

if settings.DEBUG:
    # Media dosyaları için URL tanımı
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)