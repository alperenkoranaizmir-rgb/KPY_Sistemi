from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import admin # Admin context için
from django.db.models import Sum

# KRİTİK IMPORTLAR (Bu view'in çalışması için finance ve projects modelleri gereklidir)
from projects.models import Proje 
from finance.models import Maliyet # Maliyet modelinin finance/models.py'de olduğunu varsayıyoruz

@login_required
def butce_vs_fiili_raporu(request):
    """
    Bütçe vs. Fiili Raporu: Planlanan Bütçe ile Gerçekleşen Maliyeti karşılaştırır.
    """
    # Yetkisi olan (veya tüm) projeleri getir
    yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
    
    rapor_tablosu = []
    toplam_butce_genel = 0
    toplam_maliyet_genel = 0
    
    for proje in yetkili_projeler_qs:
        # Projeye ait tüm maliyetlerin toplamını al
        fiili_maliyet_sum = Maliyet.objects.filter(proje=proje).aggregate(
            toplam=Sum('tutar')
        )['toplam'] or 0.00
        
        planlanan_butce = proje.toplam_butce
        
        toplam_butce_genel += planlanan_butce
        toplam_maliyet_genel += fiili_maliyet_sum
        
        fark = planlanan_butce - fiili_maliyet_sum
        
        rapor_tablosu.append({
            'proje_adi': proje.proje_adi,
            'planlanan_butce': planlanan_butce,
            'fiili_maliyet': fiili_maliyet_sum,
            'fark': fark,
            'durum': 'Aşımda' if fark < 0 else 'Bütçe Dahilinde'
        })
        
    context = {
        **admin.site.each_context(request),
        'baslik': "Bütçe vs. Fiili Maliyet Raporu",
        'rapor_tablosu': rapor_tablosu,
        'toplam_butce_genel': toplam_butce_genel,
        'toplam_maliyet_genel': toplam_maliyet_genel,
        'toplam_fark': toplam_butce_genel - toplam_maliyet_genel,
    }
    
    # Template'i projects/direnc_analizi.html gibi mevcut bir yapıyı temel almalıdır
    return render(request, 'finance/butce_raporu.html', context)