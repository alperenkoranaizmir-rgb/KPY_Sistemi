from django.contrib import admin
from .models import Taseron, IsTakvimiGorevi, TahliyeTakibi, GunlukSahaRaporu


# 1. Taşeron Yönetimi
@admin.register(Taseron)
class TaseronAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'proje', 'yetkili_kisi', 'telefon', 'uzmanlik_alani')
    list_filter = ('proje', 'uzmanlik_alani')
    search_fields = ('firma_adi', 'yetkili_kisi', 'uzmanlik_alani')
    # Proje ID ile hızlı seçim
    raw_id_fields = ('proje',)

# 2. İş Takvimi Görevi Inline (Hiyerarşiyi yönetmek için alt görevleri gösterir)
class AltGorevInline(admin.TabularInline):
    model = IsTakvimiGorevi
    extra = 0 # Varsayılan olarak boş satır eklenmesini engeller
    fk_name = 'parent' # Ana göreve bağlanma alanı
    fields = ('gorev_adi', 'baslangic_tarihi', 'bitis_tarihi', 'tamamlanma_orani')


# 3. İş Takvimi Görevi Yönetimi
@admin.register(IsTakvimiGorevi)
class IsTakvimiGoreviAdmin(admin.ModelAdmin):
    list_display = ('gorev_adi', 'proje', 'parent', 'baslangic_tarihi', 'bitis_tarihi', 'tamamlanma_orani')
    list_filter = ('proje', 'tamamlanma_orani')
    search_fields = ('gorev_adi', 'proje__proje_adi')
    # Tarih hiyerarşisi ile kronolojik gezinme
    date_hierarchy = 'baslangic_tarihi'
    # İlişkili alanlarda ID ile hızlı seçim
    raw_id_fields = ('proje', 'parent')
    ordering = ('baslangic_tarihi',)
    # Alt görevleri detay sayfasında göster
    inlines = [AltGorevInline] 


# 4. Tahliye Takibi Yönetimi
@admin.register(TahliyeTakibi)
class TahliyeTakibiAdmin(admin.ModelAdmin):
    list_display = (
        'proje', 
        'bagimsiz_bolum', 
        'elektrik_kesildi', 
        'su_kesildi', 
        'malik_tahliye_etti', 
        'yikima_hazir', 
        'son_kontol_tarihi'
    )
    # Kritik kontrol listesi maddelerine göre filtreleme
    list_filter = (
        'proje', 
        'elektrik_kesildi', 
        'su_kesildi', 
        'malik_tahliye_etti', 
        'yikima_hazir'
    )
    search_fields = (
        'proje__proje_adi', 
        'bagimsiz_bolum__ada', 
        'bagimsiz_bolum__parsel',
        'notlar'
    )
    raw_id_fields = ('proje', 'bagimsiz_bolum')
    readonly_fields = ('son_kontol_tarihi',) # Otomatik güncellendiği için readonly

# 5. Günlük Saha Raporu Yönetimi
@admin.register(GunlukSahaRaporu)
class GunlukSahaRaporuAdmin(admin.ModelAdmin):
    list_display = (
        'rapor_tarihi', 
        'proje', 
        'raporu_hazirlayan', 
        'hava_durumu', 
        'calisan_sayisi'
    )
    list_filter = ('proje', 'hava_durumu', 'raporu_hazirlayan')
    search_fields = ('yapilan_is', 'karsilasilan_sorunlar', 'proje__proje_adi')
    # Tarih hiyerarşisi ile kronolojik gezinme
    date_hierarchy = 'rapor_tarihi'
    raw_id_fields = ('proje', 'raporu_hazirlayan')
    ordering = ('-rapor_tarihi',)