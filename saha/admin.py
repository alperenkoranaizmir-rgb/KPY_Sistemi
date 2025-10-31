# saha/admin.py (DÜZELTİLMİŞ VE EKSİKLERİ TAMAMLANMIŞ KOD)

from django.contrib import admin
from kpy_sistemi.admin import kpy_admin_site 
from .models import Taseron, IsTakvimiGorevi, TahliyeTakibi, GunlukSahaRaporu

# -----------------------------------------------------------------
# 1. TAŞERON YÖNETİMİ
# -----------------------------------------------------------------
@admin.register(Taseron, site=kpy_admin_site)
class TaseronAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'proje', 'yetkili_kisi', 'telefon')
    search_fields = ('firma_adi', 'yetkili_kisi')
    list_filter = ('proje',)
    
# -----------------------------------------------------------------
# 2. İŞ TAKVİMİ GÖREVİ
# -----------------------------------------------------------------
@admin.register(IsTakvimiGorevi, site=kpy_admin_site)
class IsTakvimiGoreviAdmin(admin.ModelAdmin):
    list_display = ('gorev_adi', 'proje', 'baslangic_tarihi', 'bitis_tarihi', 'tamamlanma_orani', 'parent')
    list_filter = ('proje', 'tamamlanma_orani')
    search_fields = ('gorev_adi',)
    ordering = ('baslangic_tarihi',)
    # Ağaç yapısı için parent alanını daha iyi yönetmek üzere filtreleme
    list_display_links = ('gorev_adi',)


# -----------------------------------------------------------------
# 3. TAHİLİYE TAKİBİ
# -----------------------------------------------------------------
@admin.register(TahliyeTakibi, site=kpy_admin_site)
class TahliyeTakibiAdmin(admin.ModelAdmin):
    list_display = ('proje', 'bagimsiz_bolum', 'elektrik_kesildi', 'su_kesildi', 'yikima_hazir', 'son_kontol_tarihi')
    list_filter = ('proje', 'yikima_hazir', 'elektrik_kesildi')
    search_fields = ('bagimsiz_bolum__bolum_adi', 'notlar')
    readonly_fields = ('son_kontol_tarihi',)
    
    # Custom form field order
    fieldsets = (
        (None, {
            'fields': ('proje', 'bagimsiz_bolum', 'notlar')
        }),
        ('Tahliye Kontrol Listesi', {
            'fields': ('elektrik_kesildi', 'su_kesildi', 'gaz_kesildi', 'malik_tahliye_etti', 'yikima_hazir')
        }),
    )

# -----------------------------------------------------------------
# 4. GÜNLÜK SAHA RAPORU (Eskiden SahaRaporu idi)
# -----------------------------------------------------------------
@admin.register(GunlukSahaRaporu, site=kpy_admin_site)
class GunlukSahaRaporuAdmin(admin.ModelAdmin):
    list_display = ('proje', 'rapor_tarihi', 'raporu_hazirlayan', 'calisan_sayisi', 'hava_durumu')
    list_filter = ('proje', 'raporu_hazirlayan', 'hava_durumu')
    search_fields = ('yapilan_is', 'karsilasilan_sorunlar')
    ordering = ('-rapor_tarihi',)
    date_hierarchy = 'rapor_tarihi'

    fieldsets = (
        (None, {
            'fields': ('proje', 'rapor_tarihi', 'raporu_hazirlayan', 'hava_durumu')
        }),
        ('İş Gücü ve İlerleme', {
            'fields': ('calisan_sayisi', 'yapilan_is', 'karsilasilan_sorunlar', 'saha_fotografi')
        }),
    )
    
    # Raporu hazırlayan alanını otomatik doldurmak için 
    def save_model(self, request, obj, form, change):
        if not obj.raporu_hazirlayan_id:
            obj.raporu_hazirlayan = request.user
        super().save_model(request, obj, form, change)