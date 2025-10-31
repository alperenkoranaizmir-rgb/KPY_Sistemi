from django.contrib import admin
from .models import (
    MaliyetKalemi, 
    Butce, 
    Maliyet, 
    TedarikciVeyaMusteri, # Yeni
    Fatura,             # Yeni
    HarcamaTalep        # Yeni
)


# 1. Maliyet Kalemi Yönetimi
@admin.register(MaliyetKalemi)
class MaliyetKalemiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)
    ordering = ('ad',)
    

# 2. Tedarikçi/Müşteri Yönetimi (YENİ)
@admin.register(TedarikciVeyaMusteri)
class TedarikciVeyaMusteriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'tip', 'vergi_no', 'telefon', 'email')
    list_filter = ('tip',)
    search_fields = ('ad', 'vergi_no', 'telefon', 'email')
    ordering = ('ad',)


# 3. Bütçe Modeli Yönetimi
@admin.register(Butce)
class ButceAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'maliyet_kalemi', 
        'planlanan_tutar',
    )
    list_filter = (
        'proje', 
        'maliyet_kalemi'
    )
    search_fields = (
        'proje__proje_adi', 
        'maliyet_kalemi__ad'
    )
    # Performans için raw_id_fields yerine autocomplete_fields kullanıldı
    autocomplete_fields = ('proje', 'maliyet_kalemi') 
    ordering = ('proje', 'maliyet_kalemi')


# 4. Fatura Modeli Yönetimi (YENİ)
@admin.register(Fatura)
class FaturaAdmin(admin.ModelAdmin):
    list_display = (
        'fatura_no',
        'proje', 
        'karsi_taraf', 
        'tip',
        'tutar',
        'vade_tarihi',
        'durum',
    )
    list_filter = (
        'tip',
        'durum',
        'proje',
    )
    search_fields = (
        'fatura_no',
        'aciklama',
        'karsi_taraf__ad',
        'proje__proje_adi',
    )
    date_hierarchy = 'vade_tarihi'
    
    fieldsets = (
        (None, {
            'fields': ('proje', 'karsi_taraf', 'tip', 'fatura_no', 'tutar'),
        }),
        ('Ödeme ve Durum Bilgileri', {
            'fields': ('vade_tarihi', 'durum', 'odeme_tarihi', 'aciklama', 'evrak_dosya'),
        }),
    )
    
    autocomplete_fields = ('proje', 'karsi_taraf')
    ordering = ['-vade_tarihi']


# 5. Maliyet Modeli Yönetimi (Fiili Harcamalar)
@admin.register(Maliyet)
class MaliyetAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'maliyet_kalemi', 
        'tutar', 
        'harcama_tarihi', 
        'kaydi_yapan_personel',
        'ilgili_fatura', 
        'onay_durumu',   
    )
    list_filter = (
        'proje', 
        'maliyet_kalemi', 
        'kaydi_yapan_personel',
        'onay_durumu', 
    )
    search_fields = (
        'aciklama', 
        'proje__proje_adi', 
        'maliyet_kalemi__ad', 
        'kaydi_yapan_personel__username',
        'ilgili_fatura__fatura_no',
    )
    date_hierarchy = 'harcama_tarihi' 
    
    # raw_id_fields yerine autocomplete_fields kullanıldı
    autocomplete_fields = ('proje', 'maliyet_kalemi', 'kaydi_yapan_personel', 'ilgili_fatura') 
    
    ordering = ['-harcama_tarihi']
    
    fieldsets = (
        (None, {
            'fields': ('proje', 'maliyet_kalemi', 'tutar', 'aciklama', 'harcama_tarihi'),
        }),
        ('İlişkiler ve Onay', {
            'fields': ('kaydi_yapan_personel', 'ilgili_fatura', 'onay_durumu'),
        }),
    )


# 6. Harcama Talep Yönetimi (YENİ)
@admin.register(HarcamaTalep)
class HarcamaTalepAdmin(admin.ModelAdmin):
    list_display = (
        'proje',
        'maliyet_kalemi',
        'tahmini_tutar',
        'talep_eden_personel',
        'talep_tarihi',
        'onay_durumu',
        'onaylayan_personel',
        'gerceklesen_maliyet',
    )
    list_filter = (
        'onay_durumu',
        'proje',
        'maliyet_kalemi',
        'talep_eden_personel',
    )
    search_fields = (
        'gerekce',
        'proje__proje_adi',
        'talep_eden_personel__username',
    )
    date_hierarchy = 'talep_tarihi'
    
    fieldsets = (
        ('Talep Bilgileri', {
            'fields': ('proje', 'maliyet_kalemi', 'talep_eden_personel', 'tahmini_tutar', 'gerekce'),
        }),
        ('Onay Süreci', {
            'fields': ('onay_durumu', 'onaylayan_personel', 'onay_tarihi', 'gerceklesen_maliyet'),
        }),
    )
    
    readonly_fields = ('onay_tarihi',) 
    
    autocomplete_fields = (
        'proje', 
        'maliyet_kalemi', 
        'talep_eden_personel', 
        'onaylayan_personel', 
        'gerceklesen_maliyet'
    )
    
    ordering = ['talep_tarihi']


# EK: Maliyet ve Bütçe Inline Sınıfları (projects/admin.py'de kullanılacak)

class ButceInline(admin.TabularInline):
    model = Butce
    extra = 0
    fields = ('maliyet_kalemi', 'planlanan_tutar')
    autocomplete_fields = ('maliyet_kalemi',)

class MaliyetInline(admin.TabularInline):
    model = Maliyet
    extra = 0
    fields = (
        'maliyet_kalemi', 
        'tutar', 
        'aciklama', 
        'harcama_tarihi', 
        'kaydi_yapan_personel', 
        'ilgili_fatura', 
        'onay_durumu'
    )
    autocomplete_fields = ('maliyet_kalemi', 'kaydi_yapan_personel', 'ilgili_fatura')