# saha/admin.py (Hata Giderilmiş ve Temizlenmiş Kod)

from django.contrib import admin
# Tüm modeller tek import satırında toplandı.
from .models import Taseron, SahaRaporu, TahliyeTakibi, IsTakvimiGorevi, GunlukSahaRaporu
from kpy_sistemi.admin import kpy_admin_site # Özel Admin Site import edildi


# -----------------------------------------------------------------
# MEVCUT SAHA MODELLERİ (Taseron, SahaRaporu, IsTakvimiGorevi)
# -----------------------------------------------------------------

@admin.register(Taseron, site=kpy_admin_site) 
class TaseronAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'proje', 'yetkili_kisi', 'telefon', 'uzmanlik_alani')
    list_filter = ('proje', 'uzmanlik_alani')
    search_fields = ('firma_adi', 'yetkili_kisi', 'proje__proje_adi')

@admin.register(SahaRaporu, site=kpy_admin_site) 
class SahaRaporuAdmin(admin.ModelAdmin):
    list_display = ('tarih', 'proje', 'raporu_yazan')
    list_filter = ('proje', 'tarih', 'raporu_yazan')
    search_fields = ('proje__proje_adi', 'metin')
    readonly_fields = ('tarih',)

@admin.register(IsTakvimiGorevi, site=kpy_admin_site) 
class IsTakvimiGoreviAdmin(admin.ModelAdmin):
    list_display = ('gorev_adi', 'proje', 'baslangic_tarihi', 'bitis_tarihi', 'tamamlanma_orani', 'parent')
    list_filter = ('proje', 'parent')
    search_fields = ('gorev_adi', 'proje__proje_adi')


# -----------------------------------------------------------------
# HATA VEREN MODEL DÜZELTİLDİ: TahliyeTakibi
# -----------------------------------------------------------------

@admin.register(TahliyeTakibi, site=kpy_admin_site) 
class TahliyeTakibiAdmin(admin.ModelAdmin):
    # Hata Düzeltmesi: list_display modeldeki doğru alan adlarıyla değiştirildi.
    list_display = (
        'proje', # Proje alanı projeler arası filtreleme için eklendi
        'bagimsiz_bolum', 
        'malik_tahliye_etti', # Hatalı 'tahliye_edildi_mi' yerine doğru alan
        'elektrik_kesildi',   # Hatalı 'elektrik_kesildi_mi' yerine doğru alan
        'su_kesildi',         # Hatalı 'su_kesildi_mi' yerine doğru alan
        'gaz_kesildi',        # Hatalı 'dogalgaz_kesildi_mi' yerine doğru alan
        'yikima_hazir',       # Bu alan önemli olduğu için listeye eklendi
    )
    
    # Hata Düzeltmesi: list_filter modeldeki doğru alan adlarıyla değiştirildi.
    list_filter = (
        'bagimsiz_bolum__proje', 
        'malik_tahliye_etti', 
        'elektrik_kesildi', 
        'su_kesildi', 
        'gaz_kesildi',
        'yikima_hazir',
    )
    
    search_fields = ('bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel', 'bagimsiz_bolum__kapi_no')
    
    # Operasyonel verimlilik için hızlı düzenlemeye izin verildi.
    list_editable = ('malik_tahliye_etti', 'elektrik_kesildi', 'su_kesildi', 'gaz_kesildi', 'yikima_hazir')
    
    # Büyük veri setlerinde performans için
    raw_id_fields = ('bagimsiz_bolum',) 


# -----------------------------------------------------------------
# YENİ EKLENEN MODEL: GunlukSahaRaporu
# -----------------------------------------------------------------

@admin.register(GunlukSahaRaporu, site=kpy_admin_site)
class GunlukSahaRaporuAdmin(admin.ModelAdmin):
    list_display = ('proje', 'rapor_tarihi', 'raporu_hazirlayan', 'calisan_sayisi')
    list_filter = ('proje', 'raporu_hazirlayan')
    search_fields = ('proje__proje_adi', 'yapilan_is', 'karsilasilan_sorunlar')
    raw_id_fields = ('raporu_hazirlayan',)
    date_hierarchy = 'rapor_tarihi'