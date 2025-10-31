# users/admin.py (TAM VE DÜZELTİLMİŞ)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Kullanici, Gorev
from kpy_sistemi.admin import kpy_admin_site 

class CustomUserAdmin(UserAdmin):
    model = Kullanici
    
    # 'telefon' -> 'tel_no' olarak düzeltildi. Diğer olmayan alanlar kaldırıldı.
    fieldsets = UserAdmin.fieldsets + (
        ('Şirket Bilgileri', {'fields': ('tel_no',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Şirket Bilgileri', {'fields': ('tel_no',)}),
    )
    # 'departman' ve 'unvan' kaldırıldı
    list_display = ('username', 'email', 'first_name', 'last_name', 'tel_no', 'is_staff')
    # 'departman' kaldırıldı
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'tel_no')

@admin.register(Gorev, site=kpy_admin_site) 
class GorevAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'atanan_kullanici', 'proje', 'durum', 'son_tarih')
    list_filter = ('durum', 'proje', 'atanan_kullanici', 'son_tarih')
    search_fields = ('baslik', 'aciklama', 'atanan_kullanici__username', 'proje__proje_adi')

kpy_admin_site.register(Kullanici, CustomUserAdmin)