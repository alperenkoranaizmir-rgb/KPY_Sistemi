from django.contrib import admin
from .models import (
    IsTuru,
    GunlukSahaRaporu,
    SahaIlerlemeKaydi,
    SahaPersonelAtamasi,
    SahaEkipmanAtamasi,
    KaliteKontrolFormu,
    IsGuvenligiKaydi,
    TahliyeTakibi
)
from users.models import Kullanici # Personel için


# -----------------------------------------------------------------
# INLINE SINIFLARI (GÜNLÜK RAPOR İÇİN)
# -----------------------------------------------------------------

class SahaIlerlemeKaydiInline(admin.TabularInline):
    """Günlük rapora yapılan iş kalemlerini eklemek için."""
    model = SahaIlerlemeKaydi
    extra = 1
    fields = ('is_turu', 'yapilan_is_ozeti', 'ilerleme_yuzdesi')
    autocomplete_fields = ('is_turu',)


class SahaPersonelAtamasiInline(admin.TabularInline):
    """Günlük rapora çalışan personeli eklemek için."""
    model = SahaPersonelAtamasi
    extra = 1
    fields = ('personel', 'calisma_saati', 'gorev_tanimi')
    autocomplete_fields = ('personel',)


class SahaEkipmanAtamasiInline(admin.TabularInline):
    """Günlük rapora kullanılan ekipman/araçları eklemek için."""
    model = SahaEkipmanAtamasi
    extra = 1
    fields = ('ekipman', 'kullanim_suresi', 'kullanim_birimi', 'aciklama')
    autocomplete_fields = ('ekipman',)


# -----------------------------------------------------------------
# ADMIN SINIFLARI
# -----------------------------------------------------------------

# 1. İş Kalemi (WBS) Yönetimi
@admin.register(IsTuru)
class IsTuruAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)


# 2. Günlük Saha Raporu Yönetimi (Ana Kayıt)
@admin.register(GunlukSahaRaporu)
class GunlukSahaRaporuAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'rapor_tarihi', 
        'hazirlayan_personel', 
        'hava_durumu', 
        'olusturulma_tarihi'
    )
    list_filter = ('proje', 'hazirlayan_personel', 'hava_durumu', 'rapor_tarihi')
    search_fields = ('proje__proje_adi', 'genel_notlar')
    date_hierarchy = 'rapor_tarihi'
    
    autocomplete_fields = ('proje', 'hazirlayan_personel')
    
    inlines = [
        SahaIlerlemeKaydiInline,
        SahaPersonelAtamasiInline,
        SahaEkipmanAtamasiInline,
    ]


# 3. Kalite Kontrol Yönetimi
@admin.register(KaliteKontrolFormu)
class KaliteKontrolFormuAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'denetim_tarihi', 
        'is_kalemi', 
        'denetim_sonucu', 
        'denetleyen_personel', 
        'dof_gerekiyor_mu'
    )
    list_filter = ('denetim_sonucu', 'is_kalemi', 'proje', 'dof_gerekiyor_mu')
    search_fields = ('tespit_edilen_eksikler', 'proje__proje_adi')
    date_hierarchy = 'denetim_tarihi'
    autocomplete_fields = ('proje', 'denetleyen_personel', 'is_kalemi')
    ordering = ['-denetim_tarihi']


# 4. İş Güvenliği Kaydı Yönetimi
@admin.register(IsGuvenligiKaydi)
class IsGuvenligiKaydiAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'kayit_tarihi', 
        'kayit_tipi', 
        'yaralanma_durumu', 
        'raporlayan_personel'
    )
    list_filter = ('kayit_tipi', 'yaralanma_durumu', 'proje')
    search_fields = ('aciklama', 'alınan_onlemler', 'proje__proje_adi')
    date_hierarchy = 'kayit_tarihi'
    autocomplete_fields = ('proje', 'raporlayan_personel')
    ordering = ['-kayit_tarihi']


# 5. Tahliye Takibi Yönetimi
@admin.register(TahliyeTakibi)
class TahliyeTakibiAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'bagimsiz_bolum', 
        'durum', 
        'planlanan_tahliye_tarihi', 
        'gerceklesen_tahliye_tarihi',
        'sorumlu_personel'
    )
    list_filter = ('durum', 'proje', 'sorumlu_personel')
    search_fields = ('bagimsiz_bolum__bolum_no',)
    date_hierarchy = 'planlanan_tahliye_tarihi'
    autocomplete_fields = ('proje', 'bagimsiz_bolum', 'sorumlu_personel')
    ordering = ['durum', 'planlanan_tahliye_tarihi']