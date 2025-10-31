# projects/admin.py (DÜZELTİLMİŞ VE OPTİMİZE EDİLMİŞ ÇÖZÜM)

from django.contrib import admin
from .models import Proje, ProjeYetkisi, Malik, BagimsizBolum, Hisse, GorusmeKaydi, Evrak
from kpy_sistemi.admin import kpy_admin_site 


# -----------------------------------------------------------------
# INLINE TANIMLAMALARI (Optimizasyon için)
# -----------------------------------------------------------------

# Proje Yetkilendirme için Inline (Mevcut)
class ProjeYetkisiInline(admin.TabularInline):
    model = ProjeYetkisi
    extra = 1

# Malik'in Hisselerini Malik değiştirme sayfasında göstermek için
class HisseInline(admin.TabularInline):
    model = Hisse
    extra = 0 # Yeni hisse ekleme varsayılan olarak kapalı (önce BB ve Malik olmalı)
    # Hangi alanların gösterileceğini ve düzenleneceğini belirliyoruz
    fields = ('bagimsiz_bolum', 'hisse_orani', 'durum')
    # Sadece ilgili Bağımsız Bölümleri seçmek için filtreleme sağlar
    raw_id_fields = ('bagimsiz_bolum',) 
    
# Malik'in Görüşme Kayıtlarını Malik değiştirme sayfasında göstermek için (CRM)
class GorusmeKaydiInline(admin.TabularInline):
    model = GorusmeKaydi
    extra = 1
    # Personel ve Tarihi sadece okuma modunda göstererek karmaşıklığı azaltırız
    readonly_fields = ('gorusmeyi_yapan_personel', 'gorusme_tarihi')
    # Sadece malik ve özeti girmesi yeterli
    fields = ('gorusme_ozeti', 'gorusme_sonucu', 'direnc_nedeni')


# -----------------------------------------------------------------
# MODEL ADMIN SINIFLARI
# -----------------------------------------------------------------

@admin.register(Proje, site=kpy_admin_site) 
class ProjeAdmin(admin.ModelAdmin):
    list_display = ('proje_adi', 'aktif_mi', 'proje_konumu', 'cached_imza_arsa_payi', 'cached_toplam_malik_sayisi', 'arsa_paydasi_ortak') # Yeni alan eklendi
    list_filter = ('aktif_mi',)
    search_fields = ('proje_adi', 'proje_konumu')
    # Proje Yetkisi Inline'ı burada kullanılıyor
    inlines = [ProjeYetkisiInline]
    readonly_fields = ('cached_imza_arsa_payi', 'cached_toplam_malik_sayisi')
    fieldsets = (
        (None, {
            'fields': ('proje_adi', 'aktif_mi', 'aciklama'),
        }),
        ('Kentsel Dönüşüm Ayarları', {
            'fields': ('proje_konumu', 'toplam_butce', 'arsa_paydasi_ortak'), # arsa_paydasi_ortak buraya eklendi
            'description': "2/3 hesaplamaları için kritik temel ayarlar.",
        }),
        ('Otomatik İstatistikler', {
            'fields': ('cached_imza_arsa_payi', 'cached_toplam_malik_sayisi'),
        }),
    )

@admin.register(ProjeYetkisi, site=kpy_admin_site)
class ProjeYetkisiAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'proje', 'rol')
    list_filter = ('proje', 'rol', 'kullanici')
    search_fields = ('kullanici__username', 'proje__proje_adi')

@admin.register(Malik, site=kpy_admin_site)
class MalikAdmin(admin.ModelAdmin):
    
    def malik_anlasma_durumu(self, obj):
        imzali_hisse = obj.hisse_set.filter(durum='IMZALADI').first()
        if imzali_hisse:
            return f"✅ {imzali_hisse.get_durum_display()}"
        
        ilk_hisse = obj.hisse_set.first()
        if ilk_hisse:
            return f"🟡 {ilk_hisse.get_durum_display()}"
        return "❌ Hisse Yok"

    malik_anlasma_durumu.short_description = 'Anlaşma Durumu'
    
    # KRİTİK DÜZELTME: inlines eklendi
    inlines = [HisseInline, GorusmeKaydiInline]
    
    list_display = ('ad', 'soyad', 'proje', 'tc_kimlik_no', 'telefon_1', 'malik_anlasma_durumu')
    list_filter = ('proje', 'hisse__durum')
    search_fields = ('ad', 'soyad', 'tc_kimlik_no', 'telefon_1', 'proje__proje_adi')
    
    # Hukuki bilgi, iletişim ve doğum tarihi ayrı fieldset'lere ayrıldı.
    fieldsets = (
        (None, {
            'fields': ('proje', ('ad', 'soyad'), 'tc_kimlik_no'),
        }),
        ('İletişim Bilgileri (CRM)', {
            'fields': (('telefon_1', 'telefon_2'), 'email', 'adres', 'dogum_tarihi'),
            'description': "Doğum tarihi, otomatik SMS otomasyonu için kullanılır."
        }),
    )


@admin.register(Hisse, site=kpy_admin_site)
class HisseAdmin(admin.ModelAdmin):
    # KRİTİK DÜZELTME: list_display güncellendi.
    list_display = ('malik', 'bagimsiz_bolum', 'hisse_orani', 'durum')
    list_filter = ('malik__proje', 'durum') # İmza durumuna göre filtreleme eklendi
    search_fields = ('malik__ad', 'malik__soyad', 'bagimsiz_bolum__ada', 'bagimsiz_bolum__parsel')
    # Malik ve Bağımsız Bölüm ID'leri karmaşık olduğu için raw_id_fields kullanıldı
    raw_id_fields = ('malik', 'bagimsiz_bolum') 
    
    # Hissenin ait olduğu proje otomatik olarak belirlenebilir, ancak manuel girişi de kolaylaştırmak için
    # fieldsets kullanılarak düzenleme yapıldı.
    fieldsets = (
        (None, {
            'fields': (('proje', 'malik'), 'bagimsiz_bolum', 'hisse_orani'),
        }),
        ('Süreç ve Hukuki Durum', {
            'fields': ('durum',),
            'description': "Malik ikna ve imza sürecindeki mevcut durumu."
        }),
    )


@admin.register(GorusmeKaydi, site=kpy_admin_site)
class GorusmeKaydiAdmin(admin.ModelAdmin):
    list_display = ('malik', 'gorusmeyi_yapan_personel', 'gorusme_tarihi', 'gorusme_sonucu', 'direnc_nedeni')
    list_filter = ('malik__proje', 'gorusmeyi_yapan_personel', 'gorusme_sonucu', 'direnc_nedeni')
    search_fields = ('malik__ad', 'malik__soyad', 'gorusme_ozeti')
    
    # Görüşme Kayıtları Admin'inde Malik seçimi kolaylaştırıldı
    raw_id_fields = ('malik', 'gorusmeyi_yapan_personel')
    

@admin.register(Evrak, site=kpy_admin_site)
class EvrakAdmin(admin.ModelAdmin):
    # Düzeltme: 'dosya' yerine Evrak Adı ve Aktif Sürüm durumu eklendi
    list_display = ('evrak_adi', 'proje', 'malik', 'evrak_tipi', 'aktif_surum_mu', 'olusturulma_tarihi')
    list_filter = ('proje', 'evrak_tipi', 'malik', 'aktif_surum_mu')
    search_fields = ('evrak_adi', 'proje__proje_adi', 'malik__ad', 'text_content')
    # İlişkili alanlar için raw_id_fields kullanıldı
    raw_id_fields = ('malik', 'hisse', 'bagimsiz_bolum', 'onceki_surum') 
    
    # Evrak Sürüm Kontrolü alanları ayrı bir başlık altına alındı
    fieldsets = (
        (None, {
            'fields': ('proje', 'evrak_adi', 'evrak_tipi', 'dosya'),
        }),
        ('İlişkisel Bağlantılar', {
            'fields': ('malik', 'hisse', 'bagimsiz_bolum'),
            'description': "Evrağın ilgili olduğu Malik/Hisse/Mülkü seçiniz. Zorunlu değildir."
        }),
        ('Sürüm Kontrolü ve OCR', {
            'fields': ('aktif_surum_mu', 'onceki_surum', 'text_content'),
            'classes': ('collapse',), # Bu alanı varsayılan olarak gizler
            'description': "Sadece aynı evrağın yeni sürümü yüklendiğinde düzenlenir."
        }),
    )


@admin.register(BagimsizBolum, site=kpy_admin_site)
class BagimsizBolumAdmin(admin.ModelAdmin):
    # KRİTİK DÜZELTME: arsa_payi ve arsa_paydasi eklendi
    list_display = ('proje', 'ada', 'parsel', 'nitelik', 'arsa_payi', 'arsa_paydasi')
    list_filter = ('proje', 'nitelik')
    search_fields = ('proje__proje_adi', 'ada', 'parsel', 'pafta')
    
    # Mülkiyet Bilgileri ayrı bir Fieldset altına alındı
    fieldsets = (
        (None, {
            'fields': ('proje', ('ada', 'parsel', 'pafta'), 'nitelik'),
        }),
        ('Arsa Payı Bilgileri (2/3 Hesabı)', {
            'fields': (('arsa_payi', 'arsa_paydasi'), 'tapu_alani_m2'),
            'description': "Projenin 2/3 hesabında kullanılacak ana veriler."
        }),
    )