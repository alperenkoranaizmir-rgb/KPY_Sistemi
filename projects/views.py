from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q, F # Tüm gerekli importlar tek satırda toplandı
from django.http import Http404, HttpResponseForbidden 
from django.contrib import admin
from django.contrib.auth.decorators import login_required 

# Modellerin import edilmesi (Huni raporunun çalışması için kritik)
from projects.models import GorusmeKaydi, Proje, Malik, Hisse 
from .choices import DirencNedenleri # projects/choices.py dosyasından import ediliyor


# -----------------------------------------------------------------
# 1. MALİK DİRENÇ ANALİZİ RAPORU
# -----------------------------------------------------------------
@staff_member_required
def direnc_analizi_raporu(request):
    """
    Malik Direnç Analizi Raporu: Sadece Süper Kullanıcılar için, tüm aktif projeleri kapsar.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("Bu sayfayı görüntüleme yetkiniz yok.")
        
    yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)

    if not yetkili_projeler_qs.exists():
        context = {
            **admin.site.each_context(request),
            'baslik': "Genel Malik Direnç Analizi Raporu",
            'hata_mesaji': "Sistemde henüz aktif proje bulunmamaktadır."
        }
        return render(request, 'projects/direnc_analizi.html', context)

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
        
        'baslik': "Genel Malik Direnç Analizi Raporu",
        'rapor_verisi': rapor_verisi,
        'toplam_gorusme': toplam_gorusme,
        'toplam_direnc_sayisi': toplam_direnc_sayisi,
        'yetkili_projeler_qs': yetkili_projeler_qs,
    }

    return render(request, 'projects/direnc_analizi.html', context)


# -----------------------------------------------------------------
# 2. PROJE İLERLEME HUNİSİ RAPORU (Düzeltilmiş ve Temizlenmiş)
# -----------------------------------------------------------------
@login_required 
def ilerleme_hunisi_raporu(request):
    """
    Proje İlerleme Hunisi Raporu: Proje bazında imza ve görüşme akışını izler.
    """
    proje_id = request.GET.get('proje')
    yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
    
    if not proje_id:
        # Eğer proje seçilmezse, kullanıcıya seçim yapması gerektiğini bildiren ekranı göster
        context = {
            **admin.site.each_context(request),
            'baslik': "Proje İlerleme Hunisi Raporu",
            'yetkili_projeler_qs': yetkili_projeler_qs, 
            'hata_mesaji': "Lütfen yukarıdaki menüden bir proje seçerek raporu görüntüleyiniz."
        }
        return render(request, 'projects/ilerleme_hunisi.html', context) 
        
    # Proje Seçimi ve Hata Kontrolü
    try:
        secili_proje = yetkili_projeler_qs.get(id=proje_id)
    except Proje.DoesNotExist:
        context = {
            **admin.site.each_context(request),
            'baslik': "Proje İlerleme Hunisi Raporu",
            'yetkili_projeler_qs': yetkili_projeler_qs,
            'hata_mesaji': "Seçilen proje bulunamadı veya yetkiniz yok."
        }
        return render(request, 'projects/ilerleme_hunisi.html', context)

    # --- RAPOR MANTIĞI: İLERLEME HUNI VERİSİ ---
    
    # 1. TOPLAM MALİK SAYISI
    toplam_malik_sayisi = Malik.objects.filter(proje=secili_proje).count()

    # 2. GÖRÜŞÜLEN MALİK SAYISI
    gorusulen_malik_sayisi = Malik.objects.filter(
        proje=secili_proje,
        gorusmekaydi__isnull=False
    ).distinct().count()

    # 3. OLUMLU BAKAN MALİK SAYISI
    olumlu_bakan_malik_sayisi = Malik.objects.filter(
        proje=secili_proje,
        gorusmekaydi__gorusme_sonucu=GorusmeKaydi.GorusmeSonucu.OLUMLU
    ).distinct().count()

    # 4. İMZALAYAN MALİK SAYISI
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
    
    # Yeni ve doğru template dosyası kullanılıyor
    return render(request, 'projects/ilerleme_hunisi.html', context)