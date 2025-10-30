from django.contrib import admin
from .models import MaliyetKalemi, Butce, Maliyet
from projects.models import Proje # DÜZELTME: Mixin için Proje import edildi

# --- DÜZELTME BAŞLANGICI: Proje Bazlı Yetki Mixin'i eklendi ---
class ProjeYetkiMixin:
    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.projeyetkisi_set.exists()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs 
        
        yetkili_proje_idleri = request.user.projeyetkisi_set.values_list('proje_id', flat=True)
        
        if self.model is Proje:
            filtre_alani = 'id__in'
        else:
            filtre_alani = 'proje_id__in'
            
        return qs.filter(**{filtre_alani: yetkili_proje_idleri})
# --- DÜZELTME SONU ---


@admin.register(MaliyetKalemi)
class MaliyetKalemiAdmin(admin.ModelAdmin):
    """
    Maliyet Kalemleri (Tanımlamalar) admin paneli görünümü.
    (Bu model projeye bağlı olmadığı için Mixin'e ihtiyaç duymaz)
    """
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)


@admin.register(Butce)
class ButceAdmin(ProjeYetkiMixin, admin.ModelAdmin): # DÜZELTME: Mixin eklendi
    """
    Proje Bütçeleri admin paneli görünümü.
    """
    list_display = ('proje', 'maliyet_kalemi', 'planlanan_tutar')
    search_fields = ('proje__proje_adi', 'maliyet_kalemi__ad')
    list_filter = ('proje', 'maliyet_kalemi')
    
    # Veri girişini kolaylaştırmak için
    autocomplete_fields = ['proje', 'maliyet_kalemi']


@admin.register(Maliyet)
class MaliyetAdmin(ProjeYetkiMixin, admin.ModelAdmin): # DÜZELTME: Mixin eklendi
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