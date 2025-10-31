from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden 
from django.contrib import admin
from django.contrib.auth.decorators import login_required # Yeni rapor için eklendi

from projects.models import GorusmeKaydi, Proje
from .choices import DirencNedenleri # projects/choices.py dosyasından import ediliyor

from django.db.models import Sum, Q, F # Yeni importlar eklendi

# -----------------------------------------------------------------
# MALİK DİRENÇ ANALİZİ RAPORU (Sizin sağladığınız kod)
# -----------------------------------------------------------------
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
        
    # KRİTİK DÜZELTME: Rapor artık global.
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
        # Admin arayüzü ile uyumluluk için gerekli
        **admin.site.each_context(request), 
        
        'baslik': "Genel Malik Direnç Analizi Raporu",
        'rapor_verisi': rapor_verisi,
        'toplam_gorusme': toplam_gorusme,
        'toplam_direnc_sayisi': toplam_direnc_sayisi,
        'yetkili_projeler_qs': yetkili_projeler_qs,
    }

    return render(request, 'projects/direnc_analizi.html', context)


# -----------------------------------------------------------------
# YENİ EKLENEN RAPOR (HATA KAYNAĞI ÇÖZÜMÜ)
# -----------------------------------------------------------------
@login_required 
def ilerleme_hunisi_raporu(request):
    """
    Proje İlerleme Hunisi Raporu Sayfası için yer tutucu.
    Bu fonksiyonun tanımlanması, 'AttributeError' hatasını giderecektir.
    """
    context = {
        # Admin arayüzü ile uyumluluk için gerekli
        **admin.site.each_context(request), 
        'baslik': "Proje İlerleme Hunisi Raporu",
        'message': "Bu rapor sayfası henüz tamamlanmadı. Proje bazında imza, görüşme ve tahliye akışı (funnel) verileri işlenecektir."
    }
    # Mevcut rapor template'ini (projects/direnc_analizi.html) yeniden kullanarak 
    # görsel tutarlılık sağlandı ve yeni bir template oluşturma ihtiyacı geçici olarak ertelendi.
    return render(request, 'projects/direnc_analizi.html', context)


@login_required 
def ilerleme_hunisi_raporu(request):
    """
    Proje İlerleme Hunisi Raporu: Proje bazında imza ve görüşme akışını izler.
    """
    # Proje Filtresi
    proje_id = request.GET.get('proje')
    yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
    
    if proje_id:
        try:
            secili_proje = yetkili_projeler_qs.get(id=proje_id)
        except Proje.DoesNotExist:
            return render(request, 'projects/direnc_analizi.html', 
                          {'hata_mesaji': "Seçilen proje bulunamadı veya yetkiniz yok."})
    else:
        # Eğer proje seçilmezse, kullanıcıya seçim yapması gerektiğini bildirin
        return render(request, 'projects/direnc_analizi.html', 
                      {'hata_mesaji': "Lütfen bir proje seçerek ilerleme hunisini görüntüleyiniz."})

    # --- RAPOR MANTIĞI: İLERLEME HUNI VERİSİ ---
    
    # 1. TOPLAM MALİK SAYISI
    toplam_malik_sayisi = Malik.objects.filter(proje=secili_proje).count()

    # 2. GÖRÜŞÜLEN MALİK SAYISI
    # (Görüşme kaydı olan tüm malikler)
    gorusulen_malik_sayisi = Malik.objects.filter(
        proje=secili_proje,
        gorusmekaydi__isnull=False
    ).distinct().count()

    # 3. OLUMLU BAKAN MALİK SAYISI
    # (En az bir görüşme kaydı sonucu OLUMLU olan malikler)
    olumlu_bakan_malik_sayisi = Malik.objects.filter(
        proje=secili_proje,
        gorusmekaydi__gorusme_sonucu=GorusmeKaydi.GorusmeSonucu.OLUMLU
    ).distinct().count()

    # 4. İMZALAYAN MALİK SAYISI
    # (En az bir hisse kaydı durumu IMZALADI olan malikler)
    imzalayan_malik_sayisi = Malik.objects.filter(
        proje=secili_proje,
        hisse__durum=Hisse.ImzaDurumu.IMZALADI
    ).distinct().count()
    
    
    # Huniyi oluşturan veriler
    huni_verisi = [
        {'etiket': "Toplam Malik Sayısı", 'sayi': toplam_malik_sayisi, 'yuzde': 100},
        {'etiket': "Görüşülen Malik Sayısı", 'sayi': gorusulen_malik_sayisi, 
         'yuzde': round((gorusulen_malik_sayisi / toplam_malik_sayisi * 100) if toplam_malik_sayisi else 0, 2)},
        {'etiket': "Olumlu Bakan Malik", 'sayi': olumlu_bakan_malik_sayisi, 
         'yuzde': round((olumlu_bakan_malik_sayisi / toplam_malik_sayisi * 100) if toplam_malik_sayisi else 0, 2)},
        {'etiket': "İmzalayan Malik", 'sayi': imzalayan_malik_sayisi, 
         'yuzde': round((imzalayan_malik_sayisi / toplam_malik_sayisi * 100) if toplam_malik_sayisi else 0, 2)},
    ]

    context = {
        **admin.site.each_context(request), 
        'baslik': f"{secili_proje.proje_adi} Projesi İlerleme Hunisi",
        'secili_proje': secili_proje,
        'yetkili_projeler_qs': yetkili_projeler_qs,
        'huni_verisi': huni_verisi
    }
    
    # Mevcut template'i yeniden kullanıldı
    return render(request, 'projects/direnc_analizi.html', context)