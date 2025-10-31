# saha/admin.py (DÜZELTİLMİŞ)

from django.contrib import admin
from .models import Taseron, SahaRaporu, TahliyeTakibi, IsTakvimiGorevi
from kpy_sistemi.admin import kpy_admin_site  # <-- 1. ADIM: Özel admin sitemizi import et

@admin.register(Taseron, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class TaseronAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'proje', 'yetkili_kisi', 'telefon', 'uzmanlik_alani')
    list_filter = ('proje', 'uzmanlik_alani')
    search_fields = ('firma_adi', 'yetkili_kisi', 'proje__proje_adi')

@admin.register(SahaRaporu, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class SahaRaporuAdmin(admin.ModelAdmin):
    list_display = ('tarih', 'proje', 'raporu_yazan')
    list_filter = ('proje', 'tarih', 'raporu_yazan')
    search_fields = ('proje__proje_adi', 'metin')
    readonly_fields = ('tarih',)

@admin.register(TahliyeTakibi, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class TahliyeTakibiAdmin(admin.ModelAdmin):
    list_display = ('bagimsiz_bolum', 'tahliye_edildi_mi', 'elektrik_kesildi_mi', 'su_kesildi_mi', 'dogalgaz_kesildi_mi')
    list_filter = ('bagimsiz_bolum__proje', 'tahliye_edildi_mi', 'elektrik_kesildi_mi', 'su_kesildi_mi', 'dogalgaz_kesildi_mi')
    search_fields = ('bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel', 'bagimsiz_bolum__kapi_no')
    
@admin.register(IsTakvimiGorevi, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class IsTakvimiGoreviAdmin(admin.ModelAdmin):
    list_display = ('gorev_adi', 'proje', 'baslangic_tarihi', 'bitis_tarihi', 'tamamlanma_orani', 'parent')
    list_filter = ('proje', 'parent')
    search_fields = ('gorev_adi', 'proje__proje_adi')