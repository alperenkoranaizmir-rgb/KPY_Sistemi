from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Kullanici, Gorev


# Kullanici Admin Paneli Özelleştirmesi
class CustomKullaniciAdmin(UserAdmin):
    """
    Kullanici (Personel) modelini Django Admin panelinde özelleştirir.
    """
    # Varsayılan UserAdmin fieldsets yapısını kullanıp ek alanlarımızı dahil ediyoruz.
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Personel Bilgileri', {
            'fields': (
                'telefon', 
                'uzmanlik_alani', 
                'profil_fotografi', 
                'ise_baslangic_tarihi'
            ),
        }),
    )

    # Kullanıcı listeleme sayfasında gösterilecek alanlar
    list_display = UserAdmin.list_display + (
        'telefon', 
        'uzmanlik_alani', 
        'ise_baslangic_tarihi'
    )
    
    # Arama yapılabilecek alanlar
    search_fields = (
        'username', 
        'first_name', 
        'last_name', 
        'email', 
        'uzmanlik_alani',
        'telefon'
    )
    
    # Filtrelenebilecek alanlar
    list_filter = UserAdmin.list_filter + (
        'uzmanlik_alani', 
        'ise_baslangic_tarihi'
    )

# -----------------------------------------------------------------
# GÖREV YÖNETİMİ ADMIN
# -----------------------------------------------------------------

class GorevAdmin(admin.ModelAdmin):
    """
    Gorev modelini (İş Akışı) Django Admin panelinde özelleştirir.
    """
    
    # Listeleme görünümü
    list_display = (
        'baslik', 
        'proje', 
        'atanan_personel',
        'get_ust_gorev_baslik', # Yeni metot eklendi
        'durum', 
        'oncelik', 
        'son_teslim_tarihi',
        'olusturulma_tarihi',
        'tamamlanma_tarihi',
    )
    
    # Filtreler
    list_filter = (
        'durum', 
        'oncelik', 
        'proje', 
        'atanan_personel', 
        'olusturulma_tarihi',
        'son_teslim_tarihi',
    )
    
    # Arama alanları
    search_fields = (
        'baslik', 
        'aciklama', 
        'proje__proje_adi', 
        'atanan_personel__username',
        'atanan_personel__first_name',
        'atanan_personel__last_name',
    )
    
    # Admin formundaki alanların gruplanması ve düzenlenmesi
    fieldsets = (
        ('Görev Temel Bilgileri', {
            'fields': ('proje', 'ilgili_malik', 'baslik', 'aciklama'),
        }),
        ('Atama ve Öncelik', {
            'fields': (
                'atanan_personel', 
                'olusturan_personel', # Yeni
                'oncelik', 
                'tahmini_sure_saat', # Yeni
                'son_teslim_tarihi',
            ),
        }),
        ('İş Akışı ve Hiyerarşi', {
            'fields': (
                'durum', 
                'ust_gorev', # Yeni (Hiyerarşi)
                'bagimli_oldugu_gorevler', # Yeni (Bağımlılık)
                'tamamlanma_tarihi', # Yeni
            ),
        }),
    )

    # ManyToMany ilişkileri için yatay filtreleme arayüzü
    filter_horizontal = ('bagimli_oldugu_gorevler',)
    
    # ForeignKey alanları için arama kutusu (performans için önemlidir)
    autocomplete_fields = [
        'proje', 
        'atanan_personel', 
        'olusturan_personel',
        'ilgili_malik',
        'ust_gorev',
    ]

    # Ekstra metotlar (list_display için)
    def get_ust_gorev_baslik(self, obj):
        """Üst görevin sadece başlığını gösterir."""
        return obj.ust_gorev.baslik if obj.ust_gorev else '-'
    get_ust_gorev_baslik.short_description = 'Üst Görev'


# Admin paneline modelleri kaydetme
admin.site.register(Kullanici, CustomKullaniciAdmin)
admin.site.register(Gorev, GorevAdmin)