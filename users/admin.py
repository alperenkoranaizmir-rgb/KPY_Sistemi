# users/admin.py (DÜZELTİLMİŞ)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Kullanici, Gorev
from kpy_sistemi.admin import kpy_admin_site  # <-- 1. ADIM: Özel admin sitemizi import et

# Django'nun varsayılan UserAdmin formunu genişleterek kendi modelimizi kullanıyoruz.
class CustomUserAdmin(UserAdmin):
    model = Kullanici
    # Admin panelinde kullanıcı eklerken/düzenlerken hangi alanların görüneceğini belirtiyoruz.
    # 'projeler' alanını (ProjeYetkisi üzerinden) buraya eklemiyoruz
    # çünkü onu Proje üzerinden (inline) yönetmek daha mantıklı.
    fieldsets = UserAdmin.fieldsets + (
        ('Şirket Bilgileri', {'fields': ('departman', 'unvan', 'telefon')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Şirket Bilgileri', {'fields': ('departman', 'unvan', 'telefon')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'departman', 'unvan', 'is_staff')
    list_filter = ('departman', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'unvan')

# Görev Modeli Admin Arayüzü
@admin.register(Gorev, site=kpy_admin_site) # <-- 2. ADIM: 'site=kpy_admin_site' ekle
class GorevAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'atanan_kullanici', 'proje', 'durum', 'son_tarih')
    list_filter = ('durum', 'proje', 'atanan_kullanici', 'son_tarih')
    search_fields = ('baslik', 'aciklama', 'atanan_kullanici__username', 'proje__proje_adi')

# Kullanıcı modelimizi özel admin arayüzü ile birlikte özel sitemize kaydediyoruz.
kpy_admin_site.register(Kullanici, CustomUserAdmin)