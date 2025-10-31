from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# kpy_sistemi/admin.py dosyasındaki 'index' fonksiyonunu kaldırdık
# çünkü kpy_sistemi.admin modülünde bir 'index' fonksiyonu tanımlı değil.
# path('admin/', kpy_admin_views.index, name='admin:index'), satırını yoruma aldık/sildik.

urlpatterns = [
    # Ana admin URL'si. Özel index.html template'i varsa, Django bunu otomatik kullanır.
    path('admin/', admin.site.urls), 

    # Uygulama URL'lerinin dahil edilmesi
    path('projects/', include('projects.urls')),
    path('finance/', include('finance.urls')),
    path('saha/', include('saha.urls')),
    path('users/', include('users.urls')),
    # 'envanter' uygulaması için bir urls.py dosyası oluşturmadıysanız, 
    # ona ait custom bir URL eklemenize gerek yoktur.

]

# MEDIA_ROOT ve MEDIA_URL ayarları
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Not: settings.py dosyasında DEBUG=True olduğu için static dosyalar için bu yeterlidir.