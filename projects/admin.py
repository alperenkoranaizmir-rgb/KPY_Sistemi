# projects/admin.py (FINAL ÇÖZÜM)

from django.contrib import admin
from .models import Proje, ProjeYetkisi, Malik, BagimsizBolum, Hisse, GorusmeKaydi, Evrak
from kpy_sistemi.admin import kpy_admin_site 

class ProjeYetkisiInline(admin.TabularInline):
    model = ProjeYetkisi
    extra = 1

@admin.register(Proje, site=kpy_admin_site) 
class ProjeAdmin(admin.ModelAdmin):
    list_display = ('proje_adi', 'aktif_mi', 'proje_konumu', 'cached_imza_arsa_payi', 'cached_toplam_malik_sayisi')
    list_filter = ('aktif_mi',)
    search_fields = ('proje_adi', 'proje_konumu')
    inlines = [ProjeYetkisiInline]
    readonly_fields = ('cached_imza_arsa_payi', 'cached_toplam_malik_sayisi')

@admin.register(ProjeYetkisi, site=kpy_admin_site)
class ProjeYetkisiAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'proje', 'rol')
    list_filter = ('proje', 'rol', 'kullanici')
    search_fields = ('kullanici__username', 'proje__proje_adi')

@admin.register(Malik, site=kpy_admin_site)
class MalikAdmin(admin.ModelAdmin):
    # Modeldeki doğru alan adı 'anlasma_durumu' kullanıldı
    list_display = ('ad', 'soyad', 'proje', 'anlasma_durumu')
    list_filter = ('proje', 'anlasma_durumu')
    search_fields = ('ad', 'soyad', 'proje__proje_adi')

@admin.register(Hisse, site=kpy_admin_site)
class HisseAdmin(admin.ModelAdmin):
    list_display = ('malik', 'bagimsiz_bolum')
    list_filter = ('malik__proje',)
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel')

@admin.register(GorusmeKaydi, site=kpy_admin_site)
class GorusmeKaydiAdmin(admin.ModelAdmin):
    # Modeldeki doğru alan adları 'kullanici' ve 'tarih' kullanıldı
    list_display = ('malik', 'kullanici', 'tarih', 'gorusme_sonucu', 'direnc_nedeni')
    list_filter = ('malik__proje', 'kullanici', 'gorusme_sonucu', 'direnc_nedeni')
    search_fields = ('malik__ad', 'malik__soyad', 'ozet')

@admin.register(Evrak, site=kpy_admin_site)
class EvrakAdmin(admin.ModelAdmin):
    list_display = ('proje', 'malik', 'evrak_tipi', 'dosya', 'olusturulma_tarihi')
    list_filter = ('proje', 'evrak_tipi', 'malik')
    search_fields = ('proje__proje_adi', 'malik__ad', 'dosya')

@admin.register(BagimsizBolum, site=kpy_admin_site)
class BagimsizBolumAdmin(admin.ModelAdmin):
    list_display = ('proje', 'ada', 'parsel', 'nitelik')
    list_filter = ('proje', 'nitelik')
    search_fields = ('proje__proje_adi', 'ada', 'parsel')