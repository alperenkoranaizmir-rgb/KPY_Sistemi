# kpy_sistemi/admin.py (TAM VE DÜZELTİLMİŞ KOD)

from django.shortcuts import render
from django.db.models import Sum, Q, DecimalField, Count
from django.db.models.functions import Coalesce, TruncMonth
from django.contrib.admin import AdminSite
from django.urls import path
from decimal import Decimal

# Modelleri yeni ve doğru isimlerle import et
from projects.models import Proje, Malik
from finance.models import Maliyet
from users.models import Kullanici, Gorev 
from envanter.models import Envanter, KullanimKaydi # Yeni envanter modelleri


# -----------------------------------------------------------------
# 1. KPY Admin Sitesi - Özelleştirilmiş Ana Sayfa (Dashboard)
# -----------------------------------------------------------------

class KPYAdminSite(AdminSite):
    """
    Sistemin ana yönetim paneli (Admin) sayfasıdır.
    Dashboard'daki istatistikleri ve kısayolları hazırlar.
    """
    site_header = "KPY Yönetim Sistemi"
    site_title = "KPY Admin"
    index_title = "Ana Yönetim Paneli (Dashboard)"

    def index(self, request, extra_context=None):
        # Admin index'i (dashboard) için ek contextler
        extra_context = extra_context or {}
        
        # 1.1. Proje İzolasyonu
        if request.user.is_superuser:
            yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
            yetkili_proje_idleri = yetkili_projeler_qs.values_list('id', flat=True)
        else:
            # Kullanıcının yetkili olduğu projeleri al
            yetkili_proje_idleri = request.user.projeyetkisi_set.values_list('proje_id', flat=True)
            yetkili_projeler_qs = Proje.objects.filter(id__in=yetkili_proje_idleri, aktif_mi=True)
            
        # 1.2. Widget Verisi 1: 2/3 Çoğunluk Oranı
        
        # Proje modelindeki `cached_imza_arsa_payi` zaten yüzde olduğu için ortalaması alınır.
        toplam_imza_payi = yetkili_projeler_qs.aggregate(
            toplam=Sum(
                Coalesce('cached_imza_arsa_payi', Decimal('0.00')), 
                output_field=DecimalField() 
            )
        )['toplam']
        
        if yetkili_projeler_qs.count() > 0 and toplam_imza_payi is not None:
            # İmza payları zaten yüzde (0-100) olarak tutuluyor. Ortalama yüzdeyi alırız.
            total_imza_orani = toplam_imza_payi / yetkili_projeler_qs.count() 
        else:
            total_imza_orani = 0.00
            
        # 1.3. Widget Verisi 2: Bekleyen Görev Sayısı
        
        # HATA DÜZELTME: Gorev.GorevDurumu -> Gorev.Durum olarak değiştirildi.
        # HATA DÜZELTME: atanan_kullanici -> atanan_personel olarak değiştirildi.
        bekleyen_gorev_sayisi = Gorev.objects.filter(
            # atanan_kullanici -> atanan_personel
            atanan_personel=request.user, 
            # Gorev.GorevDurumu.BEKLEMEDE -> Gorev.Durum.BEKLEMEDE
            durum=Gorev.Durum.BEKLEMEDE 
        ).count()
        
        # 1.4. Widget Verisi 3: Toplam Malik Sayısı
        toplam_malik_sayisi = Malik.objects.filter(proje_id__in=yetkili_proje_idleri).count()
        
        # 1.5. Widget Verisi 4: Aktif Envanter Sayısı
        # HATA DÜZELTME: Envanter modelindeki DurumSecenekleri kullanıldı
        aktif_envanter_sayisi = Envanter.objects.aggregate(
            aktif_sayi=Count('pk', filter=Q(durum=Envanter.DurumSecenekleri.AKTIF)) 
        )['aktif_sayi'] or 0

        # 1.6. Context'i Güncelle
        extra_context['total_imza_orani'] = total_imza_orani 
        extra_context['bekleyen_gorev_sayisi'] = bekleyen_gorev_sayisi 
        extra_context['toplam_malik_sayisi'] = toplam_malik_sayisi
        extra_context['aktif_envanter_sayisi'] = aktif_envanter_sayisi
        
        # ------------------- 2. FİNANS İSTATİSTİKLERİ (GRAFİK İÇİN) ------------------
        
        # Proje filtrelemesi Maliyet'e uygulandı
        aylik_maliyet = Maliyet.objects.filter(proje_id__in=yetkili_proje_idleri).annotate(
            ay=TruncMonth('harcama_tarihi')
        ).values('ay').annotate(
            toplam_tutar=Sum('tutar')
        ).order_by('-ay')[:6] # Son 6 ayı al
        
        extra_context['aylik_maliyet'] = aylik_maliyet
        
        
        # Django'nun varsayılan admin template'ini çağır
        return super().index(request, extra_context=extra_context)

    # 3. BÜTÇE RAPORU VIEW'İ
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
            planlanan_butce = proje.toplam_butce or 0
            kalan_butce = planlanan_butce - fiili_harcama
            kullanilan_yuzde = 0
            if planlanan_butce > 0:
                kullanilan_yuzde = (fiili_harcama / planlanan_butce) * Decimal(100) # Decimal dönüşümü
            
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

    # 4. URL YÖNLENDİRİCİSİ
    def get_urls(self):
        urls = super().get_urls()
        
        custom_urls = [
            # Bu, JAZZMIN_SETTINGS içindeki URL ile eşleşmelidir
            path('finance/butce-raporu/', self.admin_view(self.butce_raporu_view), name='butce_raporu'), 
        ]
        
        return custom_urls + urls


# Admin sitesini bizim özelleştirilmiş KPYAdminSite'ımızla değiştir.
kpy_admin_site = KPYAdminSite()


# -----------------------------------------------------------------
# 5. ÜÇÜNCÜ TARAF MODÜLLERİNİ VE APP'LERİN ADMİN KAYITLARINI ÇEKME
# -----------------------------------------------------------------

# Admin panelinde görünmesini istediğiniz tüm uygulamaların admin.py içeriğini import edin.
# Django bu admin sınıflarını bizim custom admin sitesi (kpy_admin_site) içinde otomatik olarak kaydeder.

from projects.admin import *
from users.admin import *
from finance.admin import *
from saha.admin import *
from envanter.admin import *