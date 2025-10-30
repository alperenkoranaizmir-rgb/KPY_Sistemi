from django.contrib import admin
from .models import (
    Proje, ProjeYetkisi, Malik, BagimsizBolum, Hisse, 
    GorusmeKaydi, Evrak
)
from django.db.models import Sum

# --- 1. PROJE YETKİ MIXIN'İ (ModelAdmin'den miras almıyor) ---
# projects/admin.py dosyasındaki ProjeYetkiMixin sınıfının NİHAİ KODU:
class ProjeYetkiMixin: # İlk sütundan başlıyor
    # Satır 12
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
        
        # KRİTİK DÜZELTME: Filtreleme alanını dinamik olarak belirliyoruz
        
        # Eğer model Proje ise (kullanıcının baktığı liste Projeler listesi ise)
        if self.model is Proje:
            filtre_alani = 'id__in'
        # Eğer model Proje'ye bağlı başka bir model ise (Malik, Hisse, Evrak, vs.)
        else:
            filtre_alani = 'proje_id__in'
            
        # Filtreyi uyguluyoruz
        return qs.filter(**{filtre_alani: yetkili_proje_idleri})
# --- ProjeYetkiMixin Sonu ---


@admin.register(Proje)
class ProjeAdmin(ProjeYetkiMixin, admin.ModelAdmin): # İKİ MİRASI BİRDEN ALIYOR
    list_display = ('proje_adi', 'proje_konumu', 'aktif_mi', 'olusturulma_tarihi', 'imza_orani_yuzde')
    search_fields = ('proje_adi', 'proje_konumu') 
    list_filter = ('aktif_mi',)

    def imza_orani_yuzde(self, obj):
        # Projenin toplam hissesini hesapla (pay/payda oranı)
        toplam_arsa_payi = BagimsizBolum.objects.filter(proje=obj).aggregate(Sum('arsa_payi'))['arsa_payi__sum'] or 0
        
        # İmza sayısını hesapla (Durumu 'IMZALANDI' olan hisselerin toplam arsa payını)
        imzalanan_arsa_payi = Hisse.objects.filter(
            proje=obj, durum='IMZALANDI'
        ).values('bagimsiz_bolum').annotate(
            toplam_pay=Sum('bagimsiz_bolum__arsa_payi')
        ).aggregate(
            total=Sum('toplam_pay')
        )['total'] or 0

        if toplam_arsa_payi > 0:
            # 100 ile çarpıp % işaretini ekledik
            oran = (imzalanan_arsa_payi / toplam_arsa_payi) * 100
            return f"{oran:.2f}%"
        return "0.00%"
    
    imza_orani_yuzde.short_description = 'İmza Oranı (2/3)'
    imza_orani_yuzde.admin_order_field = 'id'


@admin.register(ProjeYetkisi)
class ProjeYetkisiAdmin(admin.ModelAdmin):
    # Bu model yetkilendirmeyi tanımladığı için mixin uygulanmaz.
    list_display = ('kullanici', 'proje', 'rol')
    search_fields = ('kullanici__username', 'proje__proje_adi') 
    list_filter = ('proje', 'rol', 'kullanici') 
    autocomplete_fields = ['kullanici', 'proje']


@admin.register(Malik)
class MalikAdmin(ProjeYetkiMixin, admin.ModelAdmin): # İKİ MİRASI BİRDEN ALIYOR
    list_display = ('proje', 'ad', 'soyad', 'telefon_1', 'tc_kimlik_no')
    search_fields = ('ad', 'soyad', 'tc_kimlik_no', 'telefon_1')
    list_filter = ('proje',) 
    autocomplete_fields = ['proje'] 


@admin.register(BagimsizBolum)
class BagimsizBolumAdmin(ProjeYetkiMixin, admin.ModelAdmin): # İKİ MİRASI BİRDEN ALIYOR
    list_display = ('proje', 'nitelik', 'ada', 'parsel', 'arsa_payi', 'arsa_paydasi')
    search_fields = ('nitelik', 'ada', 'parsel')
    list_filter = ('proje', 'nitelik') 
    autocomplete_fields = ['proje']


@admin.register(Hisse)
class HisseAdmin(ProjeYetkiMixin, admin.ModelAdmin): # İKİ MİRASI BİRDEN ALIYOR
    list_display = ('proje', 'malik', 'bagimsiz_bolum', 'hisse_orani', 'durum')
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__nitelik') 
    list_filter = ('proje', 'durum', 'bagimsiz_bolum__nitelik') 
    autocomplete_fields = ['proje', 'malik', 'bagimsiz_bolum']


@admin.register(GorusmeKaydi)
class GorusmeKaydiAdmin(ProjeYetkiMixin, admin.ModelAdmin): # İKİ MİRASI BİRDEN ALIYOR
    list_display = ('proje', 'malik', 'gorusmeyi_yapan_personel', 'gorusme_tarihi', 'gorusme_sonucu')
    search_fields = ('malik__ad', 'malik__soyad', 'gorusme_ozeti') 
    list_filter = ('proje', 'gorusme_sonucu', 'gorusmeyi_yapan_personel') 
    autocomplete_fields = ['proje', 'malik', 'gorusmeyi_yapan_personel']


@admin.register(Evrak)
class EvrakAdmin(ProjeYetkiMixin, admin.ModelAdmin): # İKİ MİRASI BİRDEN ALIYOR
    list_display = ('proje', 'evrak_adi', 'evrak_tipi', 'malik', 'hisse', 'aktif_surum_mu', 'olusturulma_tarihi')
    search_fields = ('evrak_adi', 'malik__ad', 'malik__soyad', 'text_content') 
    list_filter = ('proje', 'evrak_tipi', 'aktif_surum_mu') 
    autocomplete_fields = ['proje', 'malik', 'hisse', 'bagimsiz_bolum', 'onceki_surum']