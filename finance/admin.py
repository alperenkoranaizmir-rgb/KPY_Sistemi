# finance/admin.py (DÜZELTİLMİŞ ÇÖZÜM)

from django.contrib import admin
from .models import Maliyet, MaliyetKalemi
from kpy_sistemi.admin import kpy_admin_site 

@admin.register(MaliyetKalemi, site=kpy_admin_site) 
class MaliyetKalemiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)

@admin.register(Maliyet, site=kpy_admin_site) 
class MaliyetAdmin(admin.ModelAdmin):
    # Düzeltme: 'tarih' yerine modeldeki doğru alan adı 'harcama_tarihi' kullanıldı.
    list_display = ('proje', 'maliyet_kalemi', 'tutar', 'harcama_tarihi')
    list_filter = ('proje', 'maliyet_kalemi', 'harcama_tarihi')
    search_fields = ('proje__proje_adi', 'maliyet_kalemi__ad', 'aciklama')
    list_per_page = 20