from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    Proje, ProjeYetkisi, Malik, BagimsizBolum, Hisse, 
    GorusmeKaydi, Evrak
)

# ----------------------------------------------------------------------
# INLINES
# ----------------------------------------------------------------------

class ProjeYetkisiInline(admin.TabularInline):
    model = ProjeYetkisi
    extra = 1
    raw_id_fields = ('kullanici',)
    verbose_name = "Yetkili Kullanıcı"
    verbose_name_plural = "Proje Yetkilileri"


class HisseInline(admin.TabularInline):
    model = Hisse
    extra = 0
    raw_id_fields = ('bagimsiz_bolum',)
    fields = ('malik', 'hisse_orani_pay', 'hisse_orani_payda', 'durum', 'imza_tarihi')
    readonly_fields = ('arsa_payi_hesapla',)
    
    def arsa_payi_hesapla(self, obj):
        if obj.bagimsiz_bolum and obj.bagimsiz_bolum.arsa_payi and obj.hisse_orani_pay and obj.hisse_orani_payda:
            payi = obj.bagimsiz_bolum.arsa_payi.pay
            paydasi = obj.bagimsiz_bolum.arsa_payi.payda
            hisse_oran_degeri = obj.hisse_orani_pay / obj.hisse_orani_payda if obj.hisse_orani_payda else 0
            arsa_payi = (payi / paydasi) * hisse_oran_degeri
            return format_html(f"**{arsa_payi:.4f}** / {paydasi}")
        return "-"
    arsa_payi_hesapla.short_description = "Hisse Arsa Payı"


class MalikInline(admin.TabularInline):
    model = Malik
    extra = 0
    fields = ('ad_soyad', 'telefon', 'e_posta', 'adres')
    verbose_name = "Malik Bilgisi"
    verbose_name_plural = "Malikler"


# ----------------------------------------------------------------------
# ADMINS
# ----------------------------------------------------------------------

@admin.register(Proje)
class ProjeAdmin(admin.ModelAdmin):
    # Proje listeleme ve filtreleme
    list_display = (
        'proje_adi', 'il', 'ilce', 'aktif_mi', 'toplam_malik_sayisi', 
        'imzali_arsa_payi_gorunumu', 'toplam_butce_gorunumu'
    )
    list_filter = ('aktif_mi', 'il', 'ilce')
    search_fields = ('proje_adi', 'ada_parsel')
    inlines = [ProjeYetkisiInline]
    
    # Detay sayfası alanları
    fieldsets = (
        (None, {
            'fields': ('proje_adi', 'ada_parsel', 'aktif_mi', 'proje_amaci')
        }),
        ('Konum Bilgileri', {
            'fields': ('il', 'ilce', 'mahalle', 'adres')
        }),
        ('Finansal ve İstatistiksel Bilgiler (Otomatik)', {
            'fields': ('toplam_butce_gorunumu', 'toplam_malik_sayisi', 'imzali_arsa_payi_gorunumu', 'arsa_paydasi_ortak'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('toplam_malik_sayisi', 'imzali_arsa_payi_gorunumu', 'toplam_butce_gorunumu', 'arsa_paydasi_ortak')

    def save_model(self, request, obj, form, change):
        # Proje Yetkisi atamadan önce modelin kaydedilmesi
        super().save_model(request, obj, form, change)
        
    def imzali_arsa_payi_gorunumu(self, obj):
        return format_html(f"**{obj.cached_imza_arsa_payi:.4f}** / {obj.arsa_paydasi_ortak}")
    imzali_arsa_payi_gorunumu.short_description = "İmzalı Arsa Payı"

    def toplam_butce_gorunumu(self, obj):
        # Maliyet ve Bütçe modelleri finance uygulamasında olduğu için bu alanı Proje modelinde tutmak daha verimli.
        return format_html(f"<strong>{obj.toplam_butce:,.2f} TL</strong>")
    toplam_butce_gorunumu.short_description = "Toplam Bütçe"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Toplam malik sayısını doğrudan annotate ile çekiyoruz
        qs = qs.annotate(
            _toplam_malik_sayisi=Count('malikler', distinct=True)
        )
        return qs

    def toplam_malik_sayisi(self, obj):
        return obj._toplam_malik_sayisi
    toplam_malik_sayisi.short_description = "Malik Sayısı"
    
    # Change list için kolon sıralaması
    toplam_butce_gorunumu.admin_order_field = 'toplam_butce'
    imzali_arsa_payi_gorunumu.admin_order_field = 'cached_imza_arsa_payi'
    toplam_malik_sayisi.admin_order_field = '_toplam_malik_sayisi'

# ProjeYetkisi modelini doğrudan kaydetmeye gerek yok, çünkü ProjeInline içinde kullanılıyor.

@admin.register(Malik)
class MalikAdmin(admin.ModelAdmin):
    list_display = ('proje', 'ad_soyad', 'telefon', 'e_posta', 'tc_kimlik_no')
    list_filter = ('proje',)
    search_fields = ('ad_soyad', 'tc_kimlik_no', 'telefon', 'e_posta')
    inlines = [HisseInline]
    raw_id_fields = ('proje',) # Proje seçimini kolaylaştırmak için
    
    fieldsets = (
        (None, {
            'fields': ('proje', 'ad_soyad', 'cinsiyet', 'dogum_tarihi')
        }),
        ('İletişim Bilgileri', {
            'fields': ('telefon', 'e_posta', 'adres')
        }),
    )
    
@admin.register(BagimsizBolum)
class BagimsizBolumAdmin(admin.ModelAdmin):
    list_display = ('proje', 'bolum_no', 'kullanim_sekli', 'arsa_payi_oran_gorunumu')
    list_filter = ('proje', 'kullanim_sekli')
    search_fields = ('bolum_no',)
    raw_id_fields = ('proje',)

    def arsa_payi_oran_gorunumu(self, obj):
        if obj.arsa_payi:
            return f"{obj.arsa_payi.pay}/{obj.arsa_payi.payda}"
        return "-"
    arsa_payi_oran_gorunumu.short_description = "Arsa Payı"
    
@admin.register(Hisse)
class HisseAdmin(admin.ModelAdmin):
    list_display = ('malik', 'bagimsiz_bolum', 'hisse_oran_gorunumu', 'durum', 'imza_tarihi', 'son_gorusme_tarihi')
    list_filter = ('durum', 'bagimsiz_bolum__proje')
    search_fields = ('malik__ad_soyad', 'bagimsiz_bolum__bolum_no')
    raw_id_fields = ('malik', 'bagimsiz_bolum')
    
    def hisse_oran_gorunumu(self, obj):
        return f"{obj.hisse_orani_pay}/{obj.hisse_orani_payda}"
    hisse_oran_gorunumu.short_description = "Hisse Oranı"

    def son_gorusme_tarihi(self, obj):
        # Son görüşme kaydını çekiyoruz
        son_gorusme = obj.malik.gorusmekaydi_set.order_by('-gorusme_tarihi').first()
        return son_gorusme.gorusme_tarihi if son_gorusme else 'Görüşme Yok'
    son_gorusme_tarihi.short_description = "Son Görüşme"
    
@admin.register(GorusmeKaydi)
class GorusmeKaydiAdmin(admin.ModelAdmin):
    list_display = ('malik', 'gorusme_tarihi', 'gorusme_sonucu', 'gorusmeyi_yapan')
    list_filter = ('gorusme_sonucu', 'gorusme_tarihi', 'gorusmeyi_yapan')
    search_fields = ('malik__ad_soyad', 'gorusme_metni')
    raw_id_fields = ('malik', 'gorusmeyi_yapan')
    
    fieldsets = (
        (None, {
            'fields': ('malik', 'gorusme_tarihi', 'gorusmeyi_yapan')
        }),
        ('Görüşme Sonucu', {
            'fields': ('gorusme_sonucu', 'direnc_nedeni', 'gorusme_metni')
        }),
    )

@admin.register(Evrak)
class EvrakAdmin(admin.ModelAdmin):
    list_display = ('proje', 'evrak_adi', 'evrak_tipi', 'yuklenme_tarihi', 'dosya_indirme')
    list_filter = ('evrak_tipi', 'proje')
    search_fields = ('evrak_adi', 'aciklama')
    raw_id_fields = ('proje', 'bagimsiz_bolum', 'malik')
    
    def dosya_indirme(self, obj):
        if obj.dosya:
            # Dosya indirme linki oluşturuluyor
            return format_html(f'<a href="{obj.dosya.url}" target="_blank">Dosyayı İndir</a>')
        return "Dosya Yok"
    dosya_indirme.short_description = "Dosya"