from django.contrib import admin
# Admin'in temel User model yönetimini ve formunu kullanmak için import edin
from django.contrib.auth.admin import UserAdmin 
from .models import Kullanici, Gorev


# 1. Kullanici Yönetimi
# Django'nun varsayılan UserAdmin'ini Kullanici modelimiz için kullanıyoruz.
@admin.register(Kullanici)
class KullaniciAdmin(UserAdmin):
    
    # UserAdmin'in default fieldsets'ini geçersiz kılarak ekstra alanları ekliyoruz.
    # Bu, şifre ve kritik alanların güvenli bir şekilde yönetilmesini sağlar.
    def get_fieldsets(self, request, obj=None):
        if not obj:
            # Yeni kullanıcı oluştururken
            return self.add_fieldsets
        
        # Mevcut kullanıcıyı düzenlerken
        # Kullanicinin özel alanları eklenmiş fieldsets tanımı
        fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email', 'telefon', 'profil_fotografi', 'uzmanlik_alani', 'ise_baslangic_tarihi')}),
            ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
            ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
        )
        return fieldsets

    # Yeni kullanıcı ekleme formu için alanlar (UserAdmin'den gelir)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ek Personel Bilgileri', {
            'fields': ('telefon', 'uzmanlik_alani', 'profil_fotografi', 'ise_baslangic_tarihi'),
            'classes': ('wide',),
        }),
    )

    # Detay sayfasında gösterilecek alanlar
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'uzmanlik_alani')
    # Filtreleme
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'uzmanlik_alani')
    # Arama
    search_fields = ('username', 'first_name', 'last_name', 'email', 'telefon')
    

# 2. Görev Yönetimi
@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    # DÜZELTME: list_display, Gorev modelinin görünümünü iyileştirmek için güncellendi.
    list_display = (
        'baslik', 
        'proje', 
        'atanan_personel', 
        'durum', 
        'oncelik', 
        'son_teslim_tarihi', 
        'olusturulma_tarihi'
    )
    # DÜZELTME: list_filter, görev durumuna ve önceliğe göre filtrelemeyi kolaylaştırır.
    list_filter = ('durum', 'oncelik', 'proje', 'atanan_personel', 'son_teslim_tarihi')
    # Arama
    search_fields = ('baslik', 'aciklama', 'proje__proje_adi', 'atanan_personel__first_name', 'atanan_personel__last_name')
    # Tarih hiyerarşisi
    date_hierarchy = 'son_teslim_tarihi'
    
    # KRİTİK EKLEME: Büyük verilerde hızlı arama için raw_id_fields kullanıldı.
    raw_id_fields = ('atanan_personel', 'proje', 'ilgili_malik')
    
    # Detay sayfasında düzenli bir görünüm için fieldsets
    fieldsets = (
        (None, {
            'fields': ('baslik', 'aciklama', 'proje', 'ilgili_malik')
        }),
        ('Atama ve Zamanlama', {
            'fields': ('atanan_personel', 'son_teslim_tarihi')
        }),
        ('Durum ve Öncelik', {
            'fields': ('durum', 'oncelik')
        }),
    )
    
    # Otomatik oluşturulan ve güncellenen alanlar gizlenmeli
    readonly_fields = ('olusturulma_tarihi', 'guncellenme_tarihi') 
    
    ordering = ['durum', '-oncelik', 'son_teslim_tarihi']