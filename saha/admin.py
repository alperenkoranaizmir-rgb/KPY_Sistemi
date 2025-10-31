# /saha/admin.py (NİHAİ VE TEMİZLENMİŞ VERSİYON)

from django.contrib import admin
from kpy_sistemi.admin import kpy_admin_site 
from .models import Taseron, TahliyeTakibi, IsTakvimiGorevi, GunlukSahaRaporu # Sadece korunan modeller import edildi


# -----------------------------------------------------------------
# MEVCUT SAHA MODELLERİ (Taseron, IsTakvimiGorevi)
# -----------------------------------------------------------------

@admin.register(Taseron, site=kpy_admin_site) 
class TaseronAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'proje', 'yetkili_kisi', 'telefon', 'uzmanlik_alani')
    list_filter = ('proje', 'uzmanlik_alani')
    search_fields = ('firma_adi', 'yetkili_kisi', 'proje__proje_adi')

# SahaRaporu modelinin admin kaydı kaldırıldı (saha/models.py'den silindi)

@admin.register(IsTakvimiGorevi, site=kpy_admin_site) 
class IsTakvimiGoreviAdmin(admin.ModelAdmin):
    list_display = ('gorev_adi', 'proje', 'baslangic_tarihi', 'bitis_tarihi', 'tamamlanma_orani', 'parent')
    list_filter = ('proje', 'parent')
    search_fields = ('gorev_adi', 'proje__proje_adi')


# -----------------------------------------------------------------
# TAHİLİYE TAKİBİ MODELİ
# -----------------------------------------------------------------

@admin.register(TahliyeTakibi, site=kpy_admin_site) 
class TahliyeTakibiAdmin(admin.ModelAdmin):
    # Modeldeki doğru alan adları kullanıldı
    list_display = (
        'proje', 
        'bagimsiz_bolum', 
        'malik_tahliye_etti', 
        'elektrik_kesildi',   
        'su_kesildi',         
        'gaz_kesildi',        
        'yikima_hazir',       
        'son_kontol_tarihi'   
    )
    
    list_filter = (
        'proje', # Proje filtresi doğrudan eklendi
        'yikima_hazir', 
        'malik_tahliye_etti', 
        'elektrik_kesildi', 
        'su_kesildi', 
        'gaz_kesildi',
    )
    
    search_fields = ('bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel', 'bagimsiz_bolum__kapi_no')
    list_editable = ('malik_tahliye_etti', 'elektrik_kesildi', 'su_kesildi', 'gaz_kesildi', 'yikima_hazir') 
    raw_id_fields = ('bagimsiz_bolum', 'proje') # Proje alanı raw_id olarak eklendi


# -----------------------------------------------------------------
# GÜNLÜK SAHA RAPORU MODELİ
# -----------------------------------------------------------------

@admin.register(GunlukSahaRaporu, site=kpy_admin_site)
class GunlukSahaRaporuAdmin(admin.ModelAdmin):
    list_display = ('proje', 'rapor_tarihi', 'raporu_hazirlayan', 'calisan_sayisi')
    list_filter = ('proje', 'raporu_hazirlayan')
    search_fields = ('proje__proje_adi', 'yapilan_is', 'karsilasilan_sorunlar')
    raw_id_fields = ('raporu_hazirlayan',)
    date_hierarchy = 'rapor_tarihi'