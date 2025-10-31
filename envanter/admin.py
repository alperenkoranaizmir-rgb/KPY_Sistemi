# envanter/admin.py (DÜZELTİLMİŞ)

from django.contrib import admin
from .models import Demirbas, Zimmet
# 1. ADIM: Özel admin sitemizi import et
from kpy_sistemi.admin import kpy_admin_site

@admin.register(Demirbas, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class DemirbasAdmin(admin.ModelAdmin):
    list_display = ('ad', 'kategori', 'seri_numarasi', 'mevcut_kullanici', 'durum')
    list_filter = ('kategori', 'durum', 'mevcut_kullanici')
    search_fields = ('ad', 'seri_numarasi', 'mevcut_kullanici__username')

@admin.register(Zimmet, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class ZimmetAdmin(admin.ModelAdmin):
    list_display = ('demirbas', 'kullanici', 'zimmet_tarihi', 'iade_tarihi')
    list_filter = ('demirbas', 'kullanici', 'zimmet_tarihi', 'iade_tarihi')
    search_fields = ('demirbas__ad', 'kullanici__username')