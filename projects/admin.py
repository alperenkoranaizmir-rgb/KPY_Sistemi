from django.contrib import admin
from django.utils.html import format_html
# DÜZELTME: Count import edildi
from django.db.models import Sum, Count
from .models import (
    Proje, ProjeYetkisi, Malik, BagimsizBolum, Hisse, 
    GorusmeKaydi, Evrak
)

# KRİTİK EKLEME: Finance uygulamasından inline sınıfları ve Maliyet modelini import edin
from finance.admin import ButceInline, MaliyetInline
from finance.models import Maliyet


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
    raw_id_fields = ('bagimsiz_bolum', 'malik') 
    fields = ('malik', 'hisse_orani_pay', 'hisse_orani_payda', 'durum', 'imza_tarihi')
    readonly_fields = ('arsa_payi_hesapla',)
    
    def arsa_payi_hesapla(self, obj):
        # Modeldeki alan isimlerine göre güncellendi.
        if obj.bagimsiz_bolum and obj.bagimsiz_bolum.arsa_payi and obj.bagimsiz_bolum.arsa_paydasi and obj.hisse_orani_pay and obj.hisse_orani_payda:
            payi = obj.bagimsiz_bolum.arsa_payi
            paydasi = obj.bagimsiz_bolum.arsa_paydasi
            
            # Hissenin Arsa Payı * Hisse Oranı = Toplam Arsa Payı
            arsa_payi_degeri = (payi / paydasi) if paydasi else 0
            hisse_oran_degeri = obj.hisse_orani_pay / obj.hisse_orani_payda if obj.hisse_orani_payda else 0
            
            toplam_arsa_payi = arsa_payi_degeri * hisse_oran_degeri

            return format_html(f"**{toplam_arsa_payi * 100:.2f}%**")
        return "-"
    arsa_payi_hesapla.short_description = "Hisseye Düşen Arsa Payı (%)"


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
    # DÜZELTME: list_display modeldeki alanları kullanıyor
    list_display = (
        'proje_adi', 'il', 'ilce', 'aktif_mi', 'toplam_malik_sayisi', 
        'imzali_arsa_payi_gorunumu', 'toplam_butce_gorunumu'
    )
    # DÜZELTME: list_filter modeldeki alanları kullanıyor
    list_filter = ('aktif_mi', 'il', 'ilce')
    # DÜZELTME: search_fields modeldeki alanları kullanıyor
    search_fields = ('proje_adi', 'ada_parsel', 'il', 'ilce')
    # KRİTİK DÜZELTME: Bütçe ve Maliyet Inline'ları eklendi
    inlines = [ProjeYetkisiInline, ButceInline, MaliyetInline]
    
    # Detay sayfası alanları
    fieldsets = (
        (None, {
            # DÜZELTME: fieldsets modeldeki alanları kullanıyor
            'fields': ('proje_adi', 'ada_parsel', 'aktif_mi', 'proje_amaci', 'aciklama')
        }),
        ('Konum Bilgileri', {
            # DÜZELTME: fieldsets modeldeki alanları kullanıyor
            'fields': ('il', 'ilce', 'mahalle', 'adres')
        }),
        ('Finansal ve İstatistiksel Bilgiler (Otomatik)', {
            # DÜZELTME: toplam_butce_gorunumu yerine toplam_butce alanı kullanıldı, cached alanlar için metodlar kullanıldı.
            'fields': ('toplam_butce', 'toplam_malik_sayisi', 'imzali_arsa_payi_gorunumu', 'arsa_paydasi_ortak'),
            'classes': ('collapse',)
        }),
    )
    
    # DÜZELTME: readonly_fields modeldeki metotları ve alanları kullanıyor.
    readonly_fields = ('toplam_malik_sayisi', 'imzali_arsa_payi_gorunumu', 'toplam_butce_gorunumu', 'arsa_paydasi_ortak')

    def save_model(self, request, obj, form, change):
        # Proje Yetkisi atamadan önce modelin kaydedilmesi
        super().save_model(request, obj, form, change)

    # KRİTİK EKLEME: Maliyet kaydını yapan personeli otomatik atama
    def save_formset(self, request, form, formset, change):
        if formset.model == Maliyet:
            # Maliyet modeline ait inline'ları yakala
            instances = formset.save(commit=False)
            for instance in instances:
                # Sadece yeni oluşturulan veya kullanıcı bilgisi boş olan kayıtlara ata
                if not instance.pk or not instance.kaydi_yapan_personel_id: 
                    instance.kaydi_yapan_personel = request.user
                instance.save()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)
        
    def imzali_arsa_payi_gorunumu(self, obj):
        # Yüzdelik gösterim
        return format_html(f"**%{obj.cached_imza_arsa_payi:.2f}**")
    imzali_arsa_payi_gorunumu.short_description = "İmzalı Arsa Payı (%)"

    def toplam_butce_gorunumu(self, obj):
        # Sadece formatlama için kullanılan metot
        return format_html(f"<strong>{obj.toplam_butce:,.2f} TL</strong>")
    toplam_butce_gorunumu.short_description = "Planlanan Toplam Bütçe"
    
    # DÜZELTME: `cached_toplam_malik_sayisi` alanını kullanmak için metot
    def toplam_malik_sayisi(self, obj):
        # Artık cachelenmiş alanı kullanıyoruz
        return obj.cached_toplam_malik_sayisi
    toplam_malik_sayisi.short_description = "Malik Sayısı"
    
    # Change list için kolon sıralaması (Düzeltildi)
    toplam_butce_gorunumu.admin_order_field = 'toplam_butce'
    imzali_arsa_payi_gorunumu.admin_order_field = 'cached_imza_arsa_payi'
    toplam_malik_sayisi.admin_order_field = 'cached_toplam_malik_sayisi'

@admin.register(Malik)
class MalikAdmin(admin.ModelAdmin):
    # DÜZELTME: list_display modeldeki metotları kullanıyor
    list_display = ('proje', 'ad_soyad', 'telefon', 'e_posta', 'tc_kimlik_no')
    # DÜZELTME: list_filter modeldeki alanı kullanıyor
    list_filter = ('proje', 'cinsiyet')
    # DÜZELTME: search_fields modeldeki alanları kullanıyor
    search_fields = ('ad', 'soyad', 'tc_kimlik_no', 'telefon_1', 'telefon_2', 'email')
    inlines = [HisseInline]
    raw_id_fields = ('proje',) 
    
    fieldsets = (
        (None, {
            # DÜZELTME: fieldsets modeldeki alanları kullanıyor
            'fields': ('proje', ('ad', 'soyad', 'cinsiyet'), 'tc_kimlik_no', 'dogum_tarihi')
        }),
        ('İletişim Bilgileri', {
            # DÜZELTME: fieldsets modeldeki alanları kullanıyor
            'fields': ('telefon_1', 'telefon_2', 'email', 'adres')
        }),
    )
    
@admin.register(BagimsizBolum)
class BagimsizBolumAdmin(admin.ModelAdmin):
    # DÜZELTME: list_display modeldeki metotları kullanıyor
    list_display = ('proje', 'bolum_no', 'kullanim_sekli', 'arsa_payi_oran_gorunumu')
    # DÜZELTME: list_filter modeldeki alanı kullanıyor
    list_filter = ('proje', 'nitelik')
    # DÜZELTME: search_fields modeldeki alanları kullanıyor
    search_fields = ('bolum_no', 'nitelik', 'ada', 'parsel')
    raw_id_fields = ('proje',)


@admin.register(Hisse)
class HisseAdmin(admin.ModelAdmin):
    # DÜZELTME: list_display modeldeki metodu ve yeni alanı kullanıyor
    list_display = ('malik', 'bagimsiz_bolum', 'hisse_oran_gorunumu', 'durum', 'imza_tarihi', 'son_gorusme_tarihi')
    list_filter = ('durum', 'bagimsiz_bolum__proje')
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__bolum_no')
    raw_id_fields = ('malik', 'bagimsiz_bolum')

    def son_gorusme_tarihi(self, obj):
        # Son görüşme kaydını çekiyoruz
        # Düzeltme: Modeldeki related_name'ler kullanıldığı için gorusmekaydi_set kullanılır.
        son_gorusme = obj.malik.gorusmekaydi_set.order_by('-gorusme_tarihi').first() 
        return son_gorusme.gorusme_tarihi if son_gorusme else 'Görüşme Yok'
    son_gorusme_tarihi.short_description = "Son Görüşme"
    
@admin.register(GorusmeKaydi)
class GorusmeKaydiAdmin(admin.ModelAdmin):
    # DÜZELTME: list_display modeldeki metotları kullanıyor
    list_display = ('malik', 'gorusme_tarihi', 'gorusme_sonucu', 'gorusmeyi_yapan', 'direnc_nedeni')
    # DÜZELTME: list_filter modeldeki alanları kullanıyor
    list_filter = ('gorusme_sonucu', 'gorusme_tarihi', 'gorusmeyi_yapan_personel', 'direnc_nedeni')
    # DÜZELTME: search_fields modeldeki alanları kullanıyor
    search_fields = ('malik__ad', 'malik__soyad', 'gorusme_ozeti')
    # DÜZELTME: raw_id_fields modeldeki alanı kullanıyor
    raw_id_fields = ('malik', 'gorusmeyi_yapan_personel')
    
    fieldsets = (
        (None, {
            # DÜZELTME: fieldsets modeldeki alanları kullanıyor
            'fields': ('malik', 'proje', 'gorusme_tarihi', 'gorusmeyi_yapan_personel')
        }),
        ('Görüşme Sonucu', {
            # DÜZELTME: fieldsets modeldeki alanları kullanıyor
            'fields': ('gorusme_sonucu', 'direnc_nedeni', 'gorusme_ozeti')
        }),
    )

@admin.register(Evrak)
class EvrakAdmin(admin.ModelAdmin):
    # DÜZELTME: list_display modeldeki metodu kullanıyor
    list_display = ('proje', 'evrak_adi', 'evrak_tipi', 'yuklenme_tarihi', 'dosya_indirme')
    list_filter = ('evrak_tipi', 'proje')
    # DÜZELTME: search_fields modeldeki alanları kullanıyor
    search_fields = ('evrak_adi', 'aciklama', 'text_content')
    # DÜZELTME: raw_id_fields hisse eklendi
    raw_id_fields = ('proje', 'bagimsiz_bolum', 'malik', 'hisse')
    
    def dosya_indirme(self, obj):
        if obj.dosya:
            # Dosya indirme linki oluşturuluyor
            return format_html(f'<a href="{obj.dosya.url}" target="_blank">Dosyayı İndir</a>')
        return "Dosya Yok"
    dosya_indirme.short_description = "Dosya"

    # Admin formunda tüm alanları göstermek için fieldsets eklendi
    fieldsets = (
        (None, {
            'fields': ('proje', 'evrak_adi', 'evrak_tipi', 'dosya', 'aciklama')
        }),
        ('İlişkili Kayıtlar', {
            'fields': ('malik', 'hisse', 'bagimsiz_bolum')
        }),
        ('Sürüm Kontrolü', {
            'fields': ('aktif_surum_mu', 'onceki_surum'),
            'classes': ('collapse',)
        }),
        ('OCR İçeriği', {
            'fields': ('text_content',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('text_content',)