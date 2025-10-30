from django.contrib import admin
from .models import Demirbas, Zimmet

@admin.register(Demirbas)
class DemirbasAdmin(admin.ModelAdmin):
    """
    Demirbaş (Şirket Envanteri) admin paneli görünümü.
    """
    list_display = ('ad', 'seri_no', 'model', 'durum', 'alinma_tarihi')
    search_fields = ('ad', 'seri_no', 'model')
    list_filter = ('durum',) # Durumuna göre filtreleme
    
    # Zimmet kaydına geçmeden önce, demirbaşın durumunu otomatik 'KULLANIMDA' olarak güncelleyebiliriz.
    # Ancak şimdilik bu karmaşık tetikleyiciyi eklemeyip, manuel takibi yapalım.


@admin.register(Zimmet)
class ZimmetAdmin(admin.ModelAdmin):
    """
    Zimmet Kaydı admin paneli görünümü.
    """
    list_display = ('demirbas', 'personel', 'zimmet_tarihi', 'iade_tarihi')
    search_fields = ('demirbas__ad', 'demirbas__seri_no', 'personel__username', 'personel__first_name')
    list_filter = ('zimmet_tarihi', 'iade_tarihi')
    
    # Veri girişini kolaylaştırmak için
    autocomplete_fields = ['demirbas', 'personel']
    
    # Zimmeti iade edilmiş olan kayıtları otomatik olarak filtreleme
    def get_queryset(self, request):
        # Varsayılan olarak iade tarihi boş (halen zimmetli) olanları en üste getiririz.
        qs = super().get_queryset(request)
        return qs.order_by('iade_tarihi')