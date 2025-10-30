from django.contrib import admin
from .models import Demirbas, Zimmet
from projects.models import Proje # DÜZELTME: Mixin için Proje import edildi

# --- DÜZELTME BAŞLANGICI: Proje Bazlı Yetki Mixin'i eklendi ---
# (Not: Zimmet modeli 'personel'e bağlı, personel de 'proje'ye bağlı değil.)
# (Ancak Zimmet'in kendisi doğrudan projeye bağlı OLMADIĞI için bu mixin'i buraya eklemek
# şu anki model yapısıyla (Zimmet'te Proje alanı yok) çalışmaz.)
# (Eğer Zimmet'i de projeye bağlarsak bu mixin çalışır, şimdilik Zimmet projeden bağımsız.)

# YENİDEN DEĞERLENDİRME: Zimmet modeliniz projeye değil, personele bağlı.
# Personel de projeden bağımsız. Bu durumda `ProjeYetkiMixin` `envanter/admin.py`'de
# KULLANILAMAZ çünkü 'proje_id__in' filtresi atacak bir 'proje' alanı Zimmet modelinde yok.

# Eğer envanterin de projeye özel olmasını istiyorsanız, 'Zimmet' modeline 'proje' alanı eklenmelidir.
# Şimdilik, envanterin projeden bağımsız olduğunu varsayarak bu dosyayı DEĞİŞTİRMİYORUM.
# Orijinal dosyanız mantıksal olarak (mevcut model yapınıza göre) doğrudur.
# --- DÜZELTME SONU ---


@admin.register(Demirbas)
class DemirbasAdmin(admin.ModelAdmin):
    """
    Demirbaş (Şirket Envanteri) admin paneli görünümü.
    """
    list_display = ('ad', 'seri_no', 'model', 'durum', 'alinma_tarihi')
    search_fields = ('ad', 'seri_no', 'model')
    list_filter = ('durum',) # Durumuna göre filtreleme


@admin.register(Zimmet)
class ZimmetAdmin(admin.ModelAdmin): # DÜZELTME YOK (Model projeye bağlı değil)
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