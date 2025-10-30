from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden # DÜZELTME
from django.contrib import admin 

from projects.models import GorusmeKaydi, Proje
from .choices import DirencNedenleri 

@staff_member_required
def direnc_analizi_raporu(request):
    """
    Malik Direnç Analizi Raporu: Artık SADECE SÜPER KULLANICILAR içindir
    ve TÜM PROJELERİ kapsar.
    """
    # KRİTİK DÜZELTME: Sadece süper kullanıcılar bu raporu görebilir.
    if not request.user.is_superuser:
        # Yetkisi yoksa 403 Hatası döndür
        return HttpResponseForbidden("Bu sayfayı görüntüleme yetkiniz yok.")
        
    # KRİTİK DÜZELTME: Rapor artık global. Proje bazlı filtreleme (else bloğu) kaldırıldı.
    # Rapor her zaman TÜM aktif projeleri kapsar.
    yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)

    if not yetkili_projeler_qs.exists():
        return render(request, 'projects/direnc_analizi.html', {'hata_mesaji': "Sistemde henüz aktif proje bulunmamaktadır."})

    # Raporlama mantığı (Tüm projeler üzerinden)
    gorusmeler_qs = GorusmeKaydi.objects.filter(
        proje__in=yetkili_projeler_qs,
    )
    
    toplam_gorusme = gorusmeler_qs.count()
    
    direnc_verileri = gorusmeler_qs.exclude(
        direnc_nedeni=DirencNedenleri.YOK
    ).values('direnc_nedeni').annotate(
        sayi=Count('id')
    ).order_by('-sayi')
    
    rapor_verisi = []
    toplam_direnc_sayisi = sum(item['sayi'] for item in direnc_verileri)

    if toplam_direnc_sayisi > 0:
        for item in direnc_verileri:
            yuzde = (item['sayi'] / toplam_direnc_sayisi) * 100
            rapor_verisi.append({
                'neden_etiketi': DirencNedenleri(item['direnc_nedeni']).label,
                'sayi': item['sayi'],
                'yuzde': round(yuzde, 2)
            })

    context = {
        **admin.site.each_context(request),
        
        'baslik': "Genel Malik Direnç Analizi Raporu", # Başlığı güncelledik
        'rapor_verisi': rapor_verisi,
        'toplam_gorusme': toplam_gorusme,
        'toplam_direnc_sayisi': toplam_direnc_sayisi,
        'yetkili_projeler_qs': yetkili_projeler_qs,
    }

    return render(request, 'projects/direnc_analizi.html', context)