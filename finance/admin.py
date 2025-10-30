from django.contrib import admin
from .models import MaliyetKalemi, Butce, Maliyet

@admin.register(MaliyetKalemi)
class MaliyetKalemiAdmin(admin.ModelAdmin):
    """
    Maliyet Kalemleri (Tanımlamalar) admin paneli görünümü.
    """
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)


@admin.register(Butce)
class ButceAdmin(admin.ModelAdmin):
    """
    Proje Bütçeleri admin paneli görünümü.
    """
    list_display = ('proje', 'maliyet_kalemi', 'planlanan_tutar')
    search_fields = ('proje__proje_adi', 'maliyet_kalemi__ad')
    list_filter = ('proje', 'maliyet_kalemi')
    
    # Veri girişini kolaylaştırmak için
    autocomplete_fields = ['proje', 'maliyet_kalemi']


@admin.register(Maliyet)
class MaliyetAdmin(admin.ModelAdmin):
    """
    Maliyet (Fiili Harcama) admin paneli görünümü.
    """
    list_display = ('proje', 'maliyet_kalemi', 'tutar', 'harcama_tarihi', 'kaydi_yapan_personel')
    search_fields = ('proje__proje_adi', 'maliyet_kalemi__ad', 'aciklama')
    list_filter = ('proje', 'maliyet_kalemi', 'harcama_tarihi')
    
    # Veri girişini kolaylaştırmak için
    autocomplete_fields = ['proje', 'maliyet_kalemi', 'kaydi_yapan_personel']
    
    # Bu kaydı kimin girdiğini otomatik olarak kaydetmek için
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Eğer bu yeni bir kayıt ise
            obj.kaydi_yapan_personel = request.user # Kaydı yapan personeli o an giriş yapan kullanıcı olarak ata
        super().save_model(request, obj, form, change)