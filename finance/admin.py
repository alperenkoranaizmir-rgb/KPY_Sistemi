# finance/admin.py (DÜZELTİLMİŞ)

from django.contrib import admin
from .models import Maliyet, MaliyetKalemi
from kpy_sistemi.admin import kpy_admin_site  # <-- 1. ADIM: Özel admin sitemizi import et

@admin.register(MaliyetKalemi, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class MaliyetKalemiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)

@admin.register(Maliyet, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class MaliyetAdmin(admin.ModelAdmin):
    list_display = ('proje', 'kalem', 'tutar', 'tarih', 'odeme_durumu')
    list_filter = ('proje', 'kalem', 'tarih', 'odeme_durumu')
    search_fields = ('proje__proje_adi', 'kalem__ad', 'aciklama')
    list_per_page = 20