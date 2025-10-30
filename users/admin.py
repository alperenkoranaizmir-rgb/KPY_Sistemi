from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Kullanici, Gorev 
from projects.models import Proje, Malik # Görevlerde kullanılacak


# Proje Yetki Mixin'i ve KullaniciAdmin tanımı (Önceki Adımlardan)
class GorevProjeYetkiMixin:
    # ... (Bu Mixin'in içeriği aynen kalmalı)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs 
        
        yetkili_proje_idleri = request.user.projeyetkisi_set.values_list('proje_id', flat=True)
        return qs.filter(atanan_kullanici=request.user, proje_id__in=yetkili_proje_idleri)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "proje" and not request.user.is_superuser:
            yetkili_proje_idleri = request.user.projeyetkisi_set.values_list('proje_id', flat=True)
            kwargs["queryset"] = db_field.related_model.objects.filter(id__in=yetkili_proje_idleri)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Kullanici)
class KullaniciAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'unvan', 'is_staff')
    
    fieldsets = UserAdmin.fieldsets[:2] + (
        ("Proje Bilgileri", {'fields': ('unvan', 'telefon_numarasi')}),
    ) + UserAdmin.fieldsets[2:]


@admin.register(Gorev)
class GorevAdmin(GorevProjeYetkiMixin, admin.ModelAdmin):
    list_display = ('proje', 'baslik', 'atanan_kullanici', 'son_tarih', 'durum')
    search_fields = ('baslik', 'aciklama')
    list_filter = ('proje', 'durum', 'atanan_kullanici')
    autocomplete_fields = ['proje', 'malik', 'atanan_kullanici']
    ordering = ['son_tarih']