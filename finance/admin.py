# finance/admin.py (FINAL ÇÖZÜM)

from django.contrib import admin
from .models import Maliyet, MaliyetKalemi
from kpy_sistemi.admin import kpy_admin_site 

@admin.register(MaliyetKalemi, site=kpy_admin_site) 
class MaliyetKalemiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)

@admin.register(Maliyet, site=kpy_admin_site) 
class MaliyetAdmin(admin.ModelAdmin):
    # Modeldeki doğru alan adları kullanıldı
    list_display = ('proje', 'maliyet_kalemi', 'tutar', 'tarih')
    list_filter = ('proje', 'maliyet_kalemi', 'tarih')
    search_fields = ('proje__proje_adi', 'maliyet_kalemi__ad', 'aciklama')
    list_per_page = 20