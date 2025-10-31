# kpy_sistemi/admin.py (TAM VE DÜZELTİLMİŞ KOD)

from django.shortcuts import render
from django.db.models import Sum, Q, DecimalField
from projects.models import Proje, Malik
from finance.models import Maliyet
from users.models import Gorev
from saha.models import Taseron, SahaRaporu, TahliyeTakibi, IsTakvimiGorevi # <-- HATA BURADAYDI, DÜZELTİLDİ
from django.contrib.admin import AdminSite
from django.db.models.functions import Coalesce
from django.urls import path
from decimal import Decimal


# AdminSite'ı özelleştirme (Dashboard'a özel veri göndermek için)
class KPYAdminSite(AdminSite):
    
    # 1. Ana Panel (Dashboard) View'i
    def index(self, request, extra_context=None):
        
        # 1.1. Proje İzolasyonu
        if request.user.is_superuser:
            yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
            yetkili_proje_idleri = yetkili_projeler_qs.values_list('id', flat=True)
        else:
            yetkili_proje_idleri = request.user.projeyetkisi_set.values_list('proje_id', flat=True)
            yetkili_projeler_qs = Proje.objects.filter(id__in=yetkili_proje_idleri, aktif_mi=True)
            
        # 1.2. Widget Verisi 1: 2/3 Çoğunluk Oranı
        
        # --- HATA DÜZELTMESİ (Mixed types) ---
        toplam_imza_payi = yetkili_projeler_qs.aggregate(
            toplam=Sum(
                Coalesce('cached_imza_arsa_payi', Decimal('0.00')), # 0.00'ı Decimal'e çevirdik
                output_field=DecimalField()  # Çıktının DecimalField olacağını belirttik
            )
        )['toplam']
        # --- DÜZELTME SONU ---
        
        if yetkili_projeler_qs.count() > 0 and toplam_imza_payi is not None:
              total_imza_orani = toplam_imza_payi / yetkili_projeler_qs.count()
        else:
            total_imza_orani = 0.00
            
        # 1.3. Widget Verisi 2: Bekleyen Görev Sayısı
        bekleyen_gorev_sayisi = Gorev.objects.filter(
            atanan_kullanici=request.user, 
            durum=Gorev.GorevDurumu.BEKLEMEDE
        ).count()
        
        # 1.4. Widget Verisi 3: Toplam Malik Sayısı
        toplam_malik_sayisi = Malik.objects.filter(proje_id__in=yetkili_proje_idleri).count()
        
        
        # 1.5. Context'i Güncelle
        extra_context = extra_context or {}
        extra_context['total_imza_orani'] = total_imza_orani 
        extra_context['bekleyen_gorev_sayisi'] = bekleyen_gorev_sayisi 
        extra_context['toplam_malik_sayisi'] = toplam_malik_sayisi
        
        return super().index(request, extra_context=extra_context)

    # 2. BÜTÇE RAPORU VIEW'İ
    def butce_raporu_view(self, request):
        """ Modül 5: Bütçe vs. Fiili Raporu """
        
        if request.user.is_superuser:
            yetkili_projeler = Proje.objects.all()
        else:
            yetkili_projeler = Proje.objects.filter(projeyetkisi__kullanici=request.user).distinct()

        rapor_verisi = []
        
        for proje in yetkili_projeler:
            toplam_harcama_data = Maliyet.objects.filter(proje=proje).aggregate(toplam=Sum('tutar'))
            fiili_harcama = toplam_harcama_data['toplam'] or 0
            planlanan_butce = proje.toplam_butce
            kalan_butce = planlanan_butce - fiili_harcama
            kullanilan_yuzde = 0
            if planlanan_butce > 0:
                kullanilan_yuzde = (fiili_harcama / planlanan_butce) * 100
            
            rapor_verisi.append({
                'proje_adi': proje.proje_adi,
                'planlanan_butce': planlanan_butce,
                'fiili_harcama': fiili_harcama,
                'kalan_butce': kalan_butce,
                'kullanilan_yuzde': round(kullanilan_yuzde, 2),
            })

        context = self.each_context(request)
        context.update({
            'projeler': rapor_verisi,
            'title': 'Proje Bütçe vs. Fiili Durum Raporu',
        })
        
        return render(request, 'finance/butce_raporu.html', context)

    # 3. URL YÖNLENDİRİCİSİ
    def get_urls(self):
        urls = super().get_urls()
        
        custom_urls = [
            path('finance/butce-raporu/', self.admin_view(self.butce_raporu_view), name='butce_raporu'),
        ]
        
        return custom_urls + urls


# Admin sitesini bizim özelleştirilmiş KPYAdminSite'ımızla değiştir.
kpy_admin_site = KPYAdminSite()