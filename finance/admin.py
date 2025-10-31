from django.contrib import admin
from .models import MaliyetKalemi, Butce, Maliyet


# 1. Maliyet Kalemi Yönetimi
@admin.register(MaliyetKalemi)
class MaliyetKalemiAdmin(admin.ModelAdmin):
    """
    Sistemdeki harcama türlerinin (Kira, Hafriyat vb.) tanımlandığı panel.
    """
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)
    ordering = ('ad',)
    

# 2. Bütçe Modeli Yönetimi
# (Proje bazlı planlanan bütçelerin takibi)
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
        'proje__proje_adi', # Proje adına göre arama
        'maliyet_kalemi__ad' # Maliyet Kalemi adına göre arama
    )
    # Proje ve Maliyet Kalemi seçimlerini daha verimli hale getirir
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
    # Harcamaları tarihe göre hiyerarşik (yıl/ay/gün) olarak gruplayarak gösterir
    date_hierarchy = 'harcama_tarihi' 
    
    # ForeignKey alanlarında id ile hızlı seçim kutucukları kullanır
    raw_id_fields = ('proje', 'maliyet_kalemi', 'kaydi_yapan_personel')
    
    # Harcama Tarihine göre azalan sırada listele
    ordering = ['-harcama_tarihi']


# EK (İleriye Yönelik): Maliyet ve Bütçe Inline Sınıfları
# Bu sınıflar, Proje detay sayfasında (projects/admin.py'de) alt tablo olarak harcamaları ve bütçeleri göstermek için kullanılacaktır.

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
    readonly_fields = ('kaydi_yapan_personel',) # Harcama kaydını sistem otomatik yapmalı