# users/admin.py (FINAL ÇÖZÜM)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Kullanici, Gorev
from kpy_sistemi.admin import kpy_admin_site 

class CustomUserAdmin(UserAdmin):
    model = Kullanici
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefon', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'telefon')
    
    # Modeldeki doğru alan adı 'telefon' kullanıldı
    fieldsets = UserAdmin.fieldsets + (
        ('Şirket Bilgileri', {'fields': ('telefon',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Şirket Bilgileri', {'fields': ('telefon',)}),
    )


@admin.register(Gorev, site=kpy_admin_site) 
class GorevAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'atanan_kullanici', 'proje', 'durum', 'son_tarih')
    list_filter = ('durum', 'proje', 'atanan_kullanici', 'son_tarih')
    search_fields = ('baslik', 'aciklama', 'atanan_kullanici__username', 'proje__proje_adi')

kpy_admin_site.register(Kullanici, CustomUserAdmin)