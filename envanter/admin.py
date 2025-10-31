from django.contrib import admin
from .models import EnvanterKategorisi, Envanter, KullanimKaydi


# 1. Envanter Kategorisi Yönetimi
@admin.register(EnvanterKategorisi)
class EnvanterKategorisiAdmin(admin.ModelAdmin):
    """
    Basit kategori yönetimi
    """
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)


# 2. Envanter Kullanım Kaydı Inline Modeli
# Bir Envanter'in detay sayfasında alt tablo olarak görünür.
class KullanimKaydiInline(admin.TabularInline):
    model = KullanimKaydi
    extra = 0 # Varsayılan olarak boş satır eklenmesini engeller
    fields = ('kullanici', 'kullanim_amaci', 'baslangic_tarihi', 'bitis_tarihi')
    # Sadece envanter.models'da tanımlı olduğu için, eğer isterseniz:
    # readonly_fields = ('baslangic_tarihi',)


# 3. Envanter Ana Modeli Yönetimi
@admin.register(Envanter)
class EnvanterAdmin(admin.ModelAdmin):
    list_display = (
        'ad', 
        'proje', 
        'kategori', 
        'sorumlu_personel', 
        'durum', 
        'edinme_tarihi', 
        'edinme_maliyeti'
    )
    # Hızlı filtreleme ve arama için
    list_filter = ('durum', 'kategori', 'proje', 'edinme_tarihi')
    search_fields = ('ad', 'seri_no', 'proje__proje_adi', 'sorumlu_personel__first_name', 'sorumlu_personel__last_name')
    # Büyük tablolarla çalışırken performansı artırmak için
    raw_id_fields = ('proje', 'sorumlu_personel') 
    date_hierarchy = 'edinme_tarihi'

    # Kullanım Kayıtlarını Envanter sayfasında göster
    inlines = [KullanimKaydiInline]


# 4. KullanimKaydi Ayrı Yönetimi (Detaylı filtreleme ve raporlama için)
@admin.register(KullanimKaydi)
class KullanimKaydiAdmin(admin.ModelAdmin):
    list_display = ('envanter', 'kullanici', 'kullanim_amaci', 'baslangic_tarihi', 'bitis_tarihi', 'kullanim_suresi_hesapla')
    list_filter = ('kullanici', 'baslangic_tarihi')
    search_fields = ('envanter__ad', 'kullanici__username', 'kullanim_amaci')
    date_hierarchy = 'baslangic_tarihi'
    raw_id_fields = ('envanter', 'kullanici')

    def kullanim_suresi_hesapla(self, obj):
        """ Kullanım süresini hesaplayıp gösterir (models.py'de method tanımlı değilse burada görüntüleme amaçlı kalır) """
        if obj.bitis_tarihi:
            delta = obj.bitis_tarihi - obj.baslangic_tarihi
            return f"{delta.days} gün"
        return "Aktif Kullanım"
    kullanim_suresi_hesapla.short_description = "Süre"