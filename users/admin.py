from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Kullanici, Gorev
from projects.models import ProjeYetkisi # Personelin proje rollerini göstermek için import edildi

# 1. Proje Rollerini Gösteren Inline Sınıfı
class ProjeYetkisiInline(admin.TabularInline):
    """
    Bir kullanıcının hangi projelerde hangi role sahip olduğunu gösterir.
    """
    model = ProjeYetkisi
    extra = 0
    fields = ('proje', 'rol')
    raw_id_fields = ('proje',) # Proje listesi çok uzarsa kolay seçim için

# 2. Kullanıcının Atanan Görevlerini Gösteren Inline Sınıfı
class GorevInline(admin.TabularInline):
    """
    Bir kullanıcıya atanmış olan görevleri gösterir.
    """
    model = Gorev
    extra = 0
    fields = ('proje', 'baslik', 'durum', 'oncelik', 'son_teslim_tarihi')
    raw_id_fields = ('proje', 'ilgili_malik') # İlişkili alanlar için

# 3. Kullanıcı Yönetimi Sınıfı
@admin.register(Kullanici)
class KullaniciAdmin(DefaultUserAdmin):
    """
    Django'nun varsayılan UserAdmin sınıfını genişleterek,
    Kullanici modelindeki özel alanları yönetir.
    """
    # Yeni fieldset'ler ekleyerek özel alanları grupluyoruz
    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('telefon', 'uzmanlik_alani', 'ise_baslangic_tarihi', 'profil_fotografi')}),
        (('Proje/Görev İlişkileri'), {'fields': ()}), # Sadece inlines için başlık
    )
    
    # Listeleme sayfasında gösterilecek alanlar
    list_display = DefaultUserAdmin.list_display + ('telefon', 'uzmanlik_alani', 'ise_baslangic_tarihi')
    
    # Filtreleme ve Arama
    list_filter = DefaultUserAdmin.list_filter + ('uzmanlik_alani',)
    search_fields = DefaultUserAdmin.search_fields + ('telefon', 'uzmanlik_alani')
    
    # Personel detay sayfasında gösterilecek alt tablolar
    inlines = [ProjeYetkisiInline, GorevInline] 
    
    # Listeleme sırası
    ordering = ('-is_active', 'last_name') 

# 4. Görev Yönetimi Sınıfı
@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    list_display = (
        'baslik', 
        'proje', 
        'atanan_personel', 
        'durum', 
        'oncelik', 
        'son_teslim_tarihi', 
        'ilgili_malik'
    )
    list_filter = ('durum', 'oncelik', 'proje', 'atanan_personel')
    search_fields = (
        'baslik', 
        'aciklama', 
        'atanan_personel__username', 
        'proje__proje_adi', 
        'ilgili_malik__ad', 
        'ilgili_malik__soyad'
    )
    date_hierarchy = 'son_teslim_tarihi'
    raw_id_fields = ('atanan_personel', 'proje', 'ilgili_malik')
    ordering = ['durum', 'son_teslim_tarihi']