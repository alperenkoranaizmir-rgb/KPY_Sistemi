# projects/admin.py (DÜZELTİLMİŞ)

from django.contrib import admin
from .models import Proje, ProjeYetkisi, Malik, BagimsizBolum, Hisse, GorusmeKaydi, Evrak
# 1. ADIM: Django'nun varsayılan admin'i yerine bizim özel sitemizi import et
from kpy_sistemi.admin import kpy_admin_site 

# Proje içindeki yetkileri inline (iç içe) göstermek için
class ProjeYetkisiInline(admin.TabularInline):
    model = ProjeYetkisi
    extra = 1

# Proje Modeli Admin Arayüzü
# 2. ADIM: Modeli 'site=kpy_admin_site' parametresi ile özel sitemize kaydet
@admin.register(Proje, site=kpy_admin_site) 
class ProjeAdmin(admin.ModelAdmin):
    list_display = ('proje_adi', 'aktif_mi', 'proje_konumu', 'get_imza_orani_display', 'get_malik_sayisi_display')
    list_filter = ('aktif_mi',)
    search_fields = ('proje_adi', 'proje_konumu')
    inlines = [ProjeYetkisiInline]
    readonly_fields = ('cached_imza_arsa_payi', 'cached_toplam_malik_sayisi')

# ProjeYetkisi Modeli Admin Arayüzü
@admin.register(ProjeYetkisi, site=kpy_admin_site) # <-- DÜZELTME
class ProjeYetkisiAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'proje', 'rol')
    list_filter = ('proje', 'rol', 'kullanici')
    search_fields = ('kullanici__username', 'proje__proje_adi')

# Malik Modeli Admin Arayüzü
@admin.register(Malik, site=kpy_admin_site) # <-- DÜZELTME
class MalikAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'proje', 'telefon', 'anlasma_durumu')
    list_filter = ('proje', 'anlasma_durumu')
    search_fields = ('ad', 'soyad', 'telefon', 'proje__proje_adi')

# Hisse Modeli Admin Arayüzü
@admin.register(Hisse, site=kpy_admin_site) # <-- DÜZELTME
class HisseAdmin(admin.ModelAdmin):
    list_display = ('malik', 'bagimsiz_bolum', 'hisse_payi', 'hisse_paydasi', 'arsa_payi_yuzdesi')
    list_filter = ('malik__proje',)
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel')

# GörüşmeKaydi Modeli Admin Arayüzü
@admin.register(GorusmeKaydi, site=kpy_admin_site) # <-- DÜZELTME
class GorusmeKaydiAdmin(admin.ModelAdmin):
    list_display = ('malik', 'gorusen_kullanici', 'tarih', 'sonuc', 'direnc_nedeni')
    list_filter = ('malik__proje', 'gorusen_kullanici', 'sonuc', 'direnc_nedeni')
    search_fields = ('malik__ad', 'malik__soyad', 'ozet')

# Evrak Modeli Admin Arayüzü
@admin.register(Evrak, site=kpy_admin_site) # <-- DÜZELTME
class EvrakAdmin(admin.ModelAdmin):
    list_display = ('proje', 'malik', 'evrak_tipi', 'dosya', 'olusturulma_tarihi')
    list_filter = ('proje', 'evrak_tipi', 'malik')
    search_fields = ('proje__proje_adi', 'malik__ad', 'dosya')

# BağımsızBölüm Modeli Admin Arayüzü
@admin.register(BagimsizBolum, site=kpy_admin_site) # <-- DÜZELTME
class BagimsizBolumAdmin(admin.ModelAdmin):
    list_display = ('proje', 'ada', 'parsel', 'nitelik', 'kapi_no', 'toplam_arsa_payi')
    list_filter = ('proje', 'nitelik')
    search_fields = ('proje__proje_adi', 'ada', 'parsel', 'kapi_no')