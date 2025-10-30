from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import Http404

# KRİTİK DÜZELTME: Modelleri ve Seçenekleri (Choices) ayrı ayrı import ediyoruz.
from projects.models import GorusmeKaydi, Proje
from .choices import DirencNedenleri 

@staff_member_required
def direnc_analizi_raporu(request):
    """
    Malik Direnç Analizi Raporu: Artık doğru import ile çalışıyor.
    """
    if not request.user.is_authenticated:
        raise Http404
        
    if request.user.is_superuser:
        yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
    else:
        # --- DÜZELTME BAŞLANGICI ---
        # 'yetkili_olanlar' metodu yerine doğrudan filtreleme yapıyoruz.
        yetkili_proje_idleri = request.user.projeyetkisi_set.values_list('proje_id', flat=True)
        yetkili_projeler_qs = Proje.objects.filter(id__in=yetkili_proje_idleri, aktif_mi=True)
        # --- DÜZELTME SONU ---

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
        'yetkili_projeler_qs': yetkili_projeler_qs, # Özete eklemek için context'e ekledik
    }

    return render(request, 'projects/direnc_analizi.html', context)