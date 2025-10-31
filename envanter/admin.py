from django.contrib import admin
from .models import EnvanterKategorisi, Envanter, KullanimKaydi


# 1. Envanter Kategorisi Yönetimi
@admin.register(EnvanterKategorisi)
class EnvanterKategorisiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad',)


# 2. Envanter Kullanım Kaydı Inline Modeli
class KullanimKaydiInline(admin.TabularInline):
    model = KullanimKaydi
    extra = 0
    fields = ('kullanici', 'kullanim_amaci', 'baslangic_tarihi', 'bitis_tarihi')
    # İyileştirme: Kullanıcı seçimini kolaylaştırmak için eklendi
    raw_id_fields = ('kullanici',)


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
    list_filter = ('durum', 'kategori', 'proje', 'edinme_tarihi')
    search_fields = ('ad', 'seri_no', 'proje__proje_adi', 'sorumlu_personel__first_name', 'sorumlu_personel__last_name')
    raw_id_fields = ('proje', 'sorumlu_personel') 
    date_hierarchy = 'edinme_tarihi'
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
        if obj.bitis_tarihi:
            delta = obj.bitis_tarihi - obj.baslangic_tarihi
            # Delta'nın sadece gün olarak gösterilmesi, saat/dakika hassasiyetini kaybetme riskini taşır.
            # Ancak models.py'deki alanlar DateTimeField olduğu için sorun yok.
            return f"{delta.days} gün"
        return "Aktif Kullanım"
    kullanim_suresi_hesapla.short_description = "Süre"