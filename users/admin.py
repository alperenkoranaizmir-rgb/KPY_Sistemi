# users/admin.py (DÜZELTİLMİŞ)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Kullanici, Gorev
# 1. ADIM: Özel admin sitemizi import et
from kpy_sistemi.admin import kpy_admin_site 

# Django'nun varsayılan UserAdmin formunu genişleterek kendi modelimizi kullanıyoruz.
class CustomUserAdmin(UserAdmin):
    model = Kullanici
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

# 3. ADIM: Modeli varsayılan 'admin.site' yerine 'kpy_admin_site' ile kaydet
kpy_admin_site.register(Kullanici, CustomUserAdmin)