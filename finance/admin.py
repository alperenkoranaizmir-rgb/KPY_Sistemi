from django.contrib import admin
from .models import MaliyetKalemi, Butce, Maliyet


# 1. Maliyet Kalemi Yönetimi
@admin.register(MaliyetKalemi)
class MaliyetKalemiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)
    ordering = ('ad',)
    

# 2. Bütçe Modeli Yönetimi
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
    raw_id_fields = ('proje', 'maliyet_kalemi') 
    ordering = ('proje', 'maliyet_kalemi')
    

# 3. Maliyet Modeli Yönetimi (Fiili Harcamalar)
@admin.register(Maliyet)
class MaliyetAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'maliyet_kalemi', 
        'tutar', 
        'harcama_tarihi', 
        'kaydi_yapan_personel',
    )
    list_filter = (
        'proje', 
        'maliyet_kalemi', 
        'kaydi_yapan_personel'
    )
    search_fields = (
        'aciklama', 
        'proje__proje_adi', 
        'maliyet_kalemi__ad', 
        'kaydi_yapan_personel__username'
    )
    date_hierarchy = 'harcama_tarihi' 
    raw_id_fields = ('proje', 'maliyet_kalemi', 'kaydi_yapan_personel')
    ordering = ['-harcama_tarihi']


# EK: Maliyet ve Bütçe Inline Sınıfları (projects/admin.py'de kullanılacak)

class ButceInline(admin.TabularInline):
    model = Butce
    extra = 0
    fields = ('maliyet_kalemi', 'planlanan_tutar')
    raw_id_fields = ('maliyet_kalemi',)

class MaliyetInline(admin.TabularInline):
    model = Maliyet
    extra = 0
    fields = ('maliyet_kalemi', 'tutar', 'aciklama', 'harcama_tarihi', 'kaydi_yapan_personel')
    raw_id_fields = ('maliyet_kalemi', 'kaydi_yapan_personel')
    # DÜZELTME: Bu satır kaldırıldı. Otomatik atama projects/admin.py'de yapılacak.
    # readonly_fields = ('kaydi_yapan_personel',)