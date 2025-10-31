# envanter/admin.py (FINAL DÜZELTME)

from django.contrib import admin
from .models import Demirbas, Zimmet
from kpy_sistemi.admin import kpy_admin_site

@admin.register(Demirbas, site=kpy_admin_site) 
class DemirbasAdmin(admin.ModelAdmin):
    # Modeldeki mevcut alanlar kullanıldı
    list_display = ('ad', 'durum')
    list_filter = ('durum',)
    search_fields = ('ad',)

@admin.register(Zimmet, site=kpy_admin_site) 
class ZimmetAdmin(admin.ModelAdmin):
    # 'kullanici' -> 'personel' olarak düzeltildi
    list_display = ('demirbas', 'personel', 'zimmet_tarihi', 'iade_tarihi')
    list_filter = ('demirbas', 'personel', 'zimmet_tarihi', 'iade_tarihi')
    search_fields = ('demirbas__ad', 'personel__username')