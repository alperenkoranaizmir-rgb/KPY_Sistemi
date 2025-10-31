# projects/admin.py (DÜZELTİLMİŞ ÇÖZÜM)

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
    # Modelde 'anlasma_durumu' alanı yok. Hata almamak ve bilgiyi göstermek için bir metot tanımlıyoruz.
    def malik_anlasma_durumu(self, obj):
        # Malik'in en az bir hissesi imzalandıysa "İmzaladı" göster.
        # Aksi takdirde, ilk hissesinin durumunu göster (daha doğru bir raporlama için).
        imzali_hisse = obj.hisse_set.filter(durum='IMZALADI').first()
        if imzali_hisse:
            return imzali_hisse.get_durum_display()
        
        ilk_hisse = obj.hisse_set.first()
        if ilk_hisse:
            return ilk_hisse.get_durum_display()
        return "Hisse Yok"

    malik_anlasma_durumu.short_description = 'Anlaşma Durumu'
    
    # Düzeltme: 'anlasma_durumu' yerine artık metot çağrılıyor. 
    # list_filter için Hisse modelindeki durumu kullanıyoruz.
    list_display = ('ad', 'soyad', 'proje', 'malik_anlasma_durumu')
    list_filter = ('proje', 'hisse__durum')
    search_fields = ('ad', 'soyad', 'proje__proje_adi')

@admin.register(Hisse, site=kpy_admin_site)
class HisseAdmin(admin.ModelAdmin):
    list_display = ('malik', 'bagimsiz_bolum')
    list_filter = ('malik__proje',)
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel')

@admin.register(GorusmeKaydi, site=kpy_admin_site)
class GorusmeKaydiAdmin(admin.ModelAdmin):
    # Düzeltme: 'kullanici' yerine 'gorusmeyi_yapan_personel' ve 'tarih' yerine 'gorusme_tarihi' kullanıldı.
    list_display = ('malik', 'gorusmeyi_yapan_personel', 'gorusme_tarihi', 'gorusme_sonucu', 'direnc_nedeni')
    list_filter = ('malik__proje', 'gorusmeyi_yapan_personel', 'gorusme_sonucu', 'direnc_nedeni')
    search_fields = ('malik__ad', 'malik__soyad', 'gorusme_ozeti') # 'ozet' alanı 'gorusme_ozeti' olarak düzeltildi
    
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