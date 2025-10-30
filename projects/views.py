from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import Http404 # 404 Hatası için
# KRİTİK DÜZELTME: Importları fonksiyonun DIŞINDAN kaldırdık
# (Döngüsel hatayı önlemek için)

@staff_member_required
def direnc_analizi_raporu(request):
    """
    Malik Direnç Analizi Raporu: Kullanıcının yetkili olduğu projelerdeki
    tüm görüşme kayıtlarından direnç nedenlerinin yüzdesini hesaplar.
    """
    
    # KRİTİK DÜZELTME: Importları fonksiyonun İÇİNE taşıdık
    from projects.models import GorusmeKaydi, Proje, DirencNedenleri

    if not request.user.is_authenticated:
        raise Http404
        
    # Proje İzolasyonu: Kullanıcının yetkili olduğu projelerin ID'lerini al
    if request.user.is_superuser:
        yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
    else:
        yetkili_projeler_qs = Proje.objects.yetkili_olanlar(request.user).filter(aktif_mi=True)

    if not yetkili_projeler_qs.exists():
        return render(request, 'projects/direnc_analizi.html', {'hata_mesaji': "Yetkili olduğunuz aktif proje bulunmamaktadır."})

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
        'baslik': "Malik Direnç Analizi Raporu",
        'rapor_verisi': rapor_verisi,
        'toplam_gorusme': toplam_gorusme,
        'toplam_direnc_sayisi': toplam_direnc_sayisi,
    }

    return render(request, 'projects/direnc_analizi.html', context)