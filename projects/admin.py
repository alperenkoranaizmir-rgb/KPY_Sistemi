from django.contrib import admin
from django.db.models import Sum

# Kendi modellerimiz
from .models import (
    Proje, 
    ProjeYetkisi, 
    Malik, 
    BagimsizBolum, 
    Hisse, 
    GorusmeKaydi, 
    Evrak
)

# Harici uygulamalardan içe aktarılan Inline sınıfları
# Finance uygulaması (Daha önce finance/admin.py'de tanımlandı)
from finance.admin import ButceInline, MaliyetInline 
# Users uygulaması
from users.models import Gorev
# Envanter uygulaması
from envanter.models import Envanter
# Saha uygulaması
from saha.models import TahliyeTakibi 


# -----------------------------------------------------------------
# INLINE SINIFLARI (İç Yapı)
# -----------------------------------------------------------------

class ProjeYetkisiInline(admin.TabularInline):
    model = ProjeYetkisi
    extra = 0
    fields = ('kullanici', 'rol')
    autocomplete_fields = ('kullanici',)


class GorusmeKaydiInline(admin.TabularInline):
    model = GorusmeKaydi
    extra = 0
    fields = (
        'malik', 
        'gorusme_tarihi', 
        'gorusme_sonucu', 
        'gorusmeyi_yapan_personel', 
        'direnc_nedeni'
    )
    autocomplete_fields = ('malik', 'gorusmeyi_yapan_personel')
    date_hierarchy = 'gorusme_tarihi'
    

class EvrakInline(admin.TabularInline):
    model = Evrak
    extra = 0
    fields = ('evrak_adi', 'evrak_tipi', 'dosya', 'malik', 'aktif_surum_mu')
    autocomplete_fields = ('malik', 'bagimsiz_bolum', 'hisse')
    # Tek seferde çok fazla evrak yüklemeyi önlemek için
    max_num = 5


class HisseInline(admin.TabularInline):
    """Malik formunda hisseleri göstermek için kullanılır."""
    model = Hisse
    extra = 0
    fields = ('bagimsiz_bolum', 'hisse_orani_pay', 'hisse_orani_payda', 'durum', 'imza_tarihi')
    autocomplete_fields = ('bagimsiz_bolum',)


class MalikInline(admin.TabularInline):
    """Proje formunda malikleri göstermek için kullanılır."""
    model = Malik
    extra = 0
    fields = ('ad', 'soyad', 'tc_kimlik_no', 'telefon_1', 'email')
    search_fields = ('ad', 'soyad', 'tc_kimlik_no')
    # Malik detayında hisseleri göstermek için Malik'i ayrı bir admin sınıfında tutmak daha iyidir, 
    # ancak burada temel listeleme için tutulmuştur.


# -----------------------------------------------------------------
# YENİ UYGULAMA INLINE SINIFLARI (Projeye Bağlantı)
# -----------------------------------------------------------------

class GorevInline(admin.TabularInline):
    """Proje ile ilgili görevleri göstermek için."""
    model = Gorev
    extra = 0
    fields = ('baslik', 'atanan_personel', 'durum', 'son_teslim_tarihi', 'oncelik')
    autocomplete_fields = ('atanan_personel',)


class EnvanterInline(admin.TabularInline):
    """Proje için zimmetli/kullanılan envanterleri göstermek için."""
    model = Envanter
    extra = 0
    fields = ('ad', 'seri_no', 'kategori', 'durum', 'sorumlu_personel', 'edinme_maliyeti')
    autocomplete_fields = ('sorumlu_personel', 'kategori')
    verbose_name_plural = "Projeye Tahsis Edilen Envanterler"


class TahliyeTakibiInline(admin.TabularInline):
    """Proje içindeki bağımsız bölümlerin tahliye durumunu göstermek için."""
    model = TahliyeTakibi
    extra = 0
    fields = ('bagimsiz_bolum', 'durum', 'planlanan_tahliye_tarihi', 'gerceklesen_tahliye_tarihi')
    autocomplete_fields = ('bagimsiz_bolum',)
    verbose_name_plural = "Tahliye Süreçleri"


# -----------------------------------------------------------------
# PROJE ANA ADMİN
# -----------------------------------------------------------------

@admin.register(Proje)
class ProjeAdmin(admin.ModelAdmin):
    list_display = (
        'proje_adi', 
        'aktif_mi', 
        'il', 
        'cached_imza_arsa_payi_display',
        'toplam_butce_display',
        'gerceklesen_maliyet_display', # Yeni Metot
        'olusturulma_tarihi'
    )
    list_filter = ('aktif_mi', 'il', 'ilce')
    search_fields = ('proje_adi', 'il', 'ilce', 'mahalle', 'ada_parsel')
    date_hierarchy = 'olusturulma_tarihi'
    
    fieldsets = (
        ('Proje Künyesi ve Konumu', {
            'fields': (
                'proje_adi', 
                'aktif_mi', 
                'aciklama', 
                'proje_amaci', 
                ('il', 'ilce', 'mahalle'), 
                'adres', 
                'ada_parsel'
            ),
        }),
        ('Kentsel Dönüşüm Hesaplamaları', {
            'fields': (
                'cached_toplam_malik_sayisi', 
                'cached_imza_arsa_payi', 
                'arsa_paydasi_ortak'
            ),
        }),
        ('Finansal Özet', {
            'fields': (
                'toplam_butce', 
            ),
        }),
    )

    # Hesaplanan alanları readonly yapıyoruz
    readonly_fields = (
        'cached_toplam_malik_sayisi', 
        'cached_imza_arsa_payi',
    )

    # Entegrasyonlar (Inline'lar)
    inlines = [
        ProjeYetkisiInline, 
        ButceInline,        # Finance
        MaliyetInline,      # Finance
        GorevInline,        # Users
        TahliyeTakibiInline, # Saha
        MalikInline,        # Projects/CRM
        EvrakInline,        # Projects/DMS
    ]

    # Ekran Metotları
    def cached_imza_arsa_payi_display(self, obj):
        return f"%{obj.cached_imza_arsa_payi:.2f}"
    cached_imza_arsa_payi_display.short_description = "İmza Payı (%)"

    def toplam_butce_display(self, obj):
        return f"{obj.toplam_butce:,.2f} TL"
    toplam_butce_display.short_description = "Planlanan Bütçe"

    def gerceklesen_maliyet_display(self, obj):
        """Gerçekleşen toplam maliyeti hesaplar ve gösterir."""
        # Django'nun aggregate fonksiyonu ile ilgili projeye ait Maliyet modelinden tutarlar toplanır.
        toplam = obj.maliyetler.aggregate(Sum('tutar'))['tutar__sum'] or 0.00
        return f"{toplam:,.2f} TL"
    gerceklesen_maliyet_display.short_description = "Gerçekleşen Maliyet"


# -----------------------------------------------------------------
# DİĞER PROJE MODELLERİNİN ADMİN KAYITLARI
# -----------------------------------------------------------------

@admin.register(Malik)
class MalikAdmin(admin.ModelAdmin):
    list_display = ('ad_soyad', 'proje', 'tc_kimlik_no', 'telefon', 'e_posta', 'cinsiyet')
    list_filter = ('proje', 'cinsiyet')
    search_fields = ('ad', 'soyad', 'tc_kimlik_no', 'telefon_1', 'email')
    autocomplete_fields = ('proje',)
    inlines = [HisseInline, GorusmeKaydiInline]


@admin.register(BagimsizBolum)
class BagimsizBolumAdmin(admin.ModelAdmin):
    list_display = ('bolum_no', 'proje', 'nitelik', 'ada', 'parsel', 'tapu_alani_m2', 'arsa_payi_oran_gorunumu')
    list_filter = ('proje', 'nitelik')
    search_fields = ('bolum_no', 'ada', 'parsel')
    autocomplete_fields = ('proje',)


@admin.register(Hisse)
class HisseAdmin(admin.ModelAdmin):
    list_display = ('malik', 'bagimsiz_bolum', 'hisse_oran_gorunumu', 'durum', 'imza_tarihi')
    list_filter = ('durum', 'proje')
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__bolum_no')
    autocomplete_fields = ('proje', 'malik', 'bagimsiz_bolum')


@admin.register(GorusmeKaydi)
class GorusmeKaydiAdmin(admin.ModelAdmin):
    list_display = ('malik', 'proje', 'gorusme_tarihi', 'gorusme_sonucu', 'gorusmeyi_yapan')
    list_filter = ('proje', 'gorusme_sonucu', 'gorusmeyi_yapan_personel')
    search_fields = ('malik__ad', 'malik__soyad', 'gorusme_ozeti')
    date_hierarchy = 'gorusme_tarihi'
    autocomplete_fields = ('proje', 'malik', 'gorusmeyi_yapan_personel')


@admin.register(Evrak)
class EvrakAdmin(admin.ModelAdmin):
    list_display = ('evrak_adi', 'evrak_tipi', 'proje', 'malik', 'yuklenme_tarihi', 'aktif_surum_mu')
    list_filter = ('evrak_tipi', 'proje', 'aktif_surum_mu')
    search_fields = ('evrak_adi', 'aciklama', 'text_content')
    autocomplete_fields = ('proje', 'malik', 'hisse', 'bagimsiz_bolum', 'onceki_surum')
    date_hierarchy = 'olusturulma_tarihi'