from django.contrib import admin
from .models import (
    EnvanterKategorisi, 
    DepolamaAlani,         
    SarfMalzemesi,        
    SarfMalzemeHareketi,  
    Envanter,             
    BakimKaydi,           
    KullanimKaydi         
)


# 1. Tanımlamalar
@admin.register(EnvanterKategorisi)
class EnvanterKategorisiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)


@admin.register(DepolamaAlani) # YENİ: Depolama Alanı Yönetimi
class DepolamaAlaniAdmin(admin.ModelAdmin):
    list_display = ('ad', 'adres')
    search_fields = ('ad', 'adres')


# 2. Sarf Malzemesi Yönetimi
@admin.register(SarfMalzemesi) # YENİ: Sarf Malzemesi Ana Kaydı
class SarfMalzemesiAdmin(admin.ModelAdmin):
    list_display = (
        'ad', 
        'kategori', 
        'stok_miktari', 
        'birim', 
        'min_stok_seviyesi', 
        'depolama_alani'
    )
    list_filter = ('kategori', 'depolama_alani')
    search_fields = ('ad', 'birim')
    autocomplete_fields = ('kategori', 'depolama_alani')
    
    # Stok miktarının sadece hareketlerle değişmesi için salt okunur yapıldı
    readonly_fields = ('stok_miktari',)
    
    fieldsets = (
        (None, {
            'fields': ('kategori', 'ad', 'birim', 'depolama_alani'),
        }),
        ('Stok Kontrolü', {
            'fields': ('stok_miktari', 'min_stok_seviyesi'),
        }),
    )


@admin.register(SarfMalzemeHareketi) # YENİ: Stok Giriş/Çıkış Kaydı
class SarfMalzemeHareketiAdmin(admin.ModelAdmin):
    list_display = (
        'malzeme', 
        'hareket_tipi', 
        'miktar', 
        'hareket_tarihi', 
        'yapan_personel', 
        'ilgili_proje'
    )
    list_filter = ('hareket_tipi', 'malzeme', 'ilgili_proje')
    search_fields = ('malzeme__ad', 'aciklama')
    date_hierarchy = 'hareket_tarihi'
    autocomplete_fields = ('malzeme', 'ilgili_proje', 'yapan_personel')
    ordering = ('-hareket_tarihi',)


# 3. Envanter (Demirbaş) Yönetimi Inline Sınıfları
class BakimKaydiInline(admin.TabularInline):
    """Envanter formunda bakım kayıtlarını göstermek için."""
    model = BakimKaydi
    extra = 0
    fields = (
        'tip', 
        'bakim_tarihi', 
        'maliyet', 
        'sonuc', 
        'sorumlu_teknisyen', 
        'bir_sonraki_bakim_tarihi'
    )
    autocomplete_fields = ('sorumlu_teknisyen',)


class KullanimKaydiInline(admin.TabularInline):
    """Envanter formunda zimmet/kullanım kayıtlarını göstermek için."""
    model = KullanimKaydi
    extra = 0
    fields = ('kullanici', 'kullanim_amaci', 'baslangic_tarihi', 'bitis_tarihi')
    autocomplete_fields = ('kullanici',)


@admin.register(Envanter)
class EnvanterAdmin(admin.ModelAdmin):
    list_display = (
        'ad', 
        'proje', 
        'kategori', 
        'seri_no', 
        'durum', 
        'sorumlu_personel', 
        'edinme_maliyeti'
    )
    list_filter = ('durum', 'kategori', 'proje')
    search_fields = ('ad', 'seri_no')
    date_hierarchy = 'edinme_tarihi'
    
    fieldsets = (
        ('Temel Varlık Bilgileri', {
            'fields': ('proje', 'kategori', 'ad', 'seri_no', 'durum'),
        }),
        ('Finans ve Amortisman', {
            'fields': (
                'edinme_tarihi', 
                'edinme_maliyeti', 
                'amortisman_orani',           # Yeni
                'amortisman_baslangic_tarihi', # Yeni
            ),
        }),
        ('Atama ve Lokasyon', {
            'fields': (
                'sorumlu_personel', 
                'depolama_alani', # Yeni
            ),
        }),
    )
    
    autocomplete_fields = ('proje', 'kategori', 'sorumlu_personel', 'depolama_alani')
    
    # Inline Kayıtlar (Bakım ve Zimmet)
    inlines = [KullanimKaydiInline, BakimKaydiInline]


# 4. Bakım ve Kullanım Kayıtları (Standalone)

@admin.register(BakimKaydi) # YENİ: Bakım ve Arıza Kaydı Yönetimi
class BakimKaydiAdmin(admin.ModelAdmin):
    list_display = (
        'envanter', 
        'tip', 
        'bakim_tarihi', 
        'maliyet', 
        'sorumlu_teknisyen', 
        'bir_sonraki_bakim_tarihi'
    )
    list_filter = ('tip', 'envanter__kategori', 'sorumlu_teknisyen')
    search_fields = ('envanter__ad', 'aciklama')
    date_hierarchy = 'bakim_tarihi'
    autocomplete_fields = ('envanter', 'sorumlu_teknisyen')
    ordering = ['-bakim_tarihi']


@admin.register(KullanimKaydi) # Mevcut: Zimmet/Kullanım Kaydı Yönetimi
class KullanimKaydiAdmin(admin.ModelAdmin):
    list_display = (
        'envanter', 
        'kullanici', 
        'kullanim_amaci', 
        'baslangic_tarihi', 
        'bitis_tarihi'
    )
    list_filter = ('kullanici', 'envanter')
    search_fields = ('envanter__ad', 'kullanici__username', 'kullanim_amaci')
    date_hierarchy = 'baslangic_tarihi'
    autocomplete_fields = ('envanter', 'kullanici')
    ordering = ['-baslangic_tarihi']