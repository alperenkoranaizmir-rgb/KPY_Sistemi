from django.contrib.admin import AdminSite
from django.db.models import Sum, Q
from projects.models import Proje, Malik # Malik modelini import ettik
from users.models import Gorev
from django.db.models.functions import Coalesce

# AdminSite'ı özelleştirme (Dashboard'a özel veri göndermek için)
class KPYAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        
        # -----------------------------------------------------------
        # 1. Proje İzolasyonu: Kullanıcının Yetkili Olduğu Projeleri Filtrele
        # -----------------------------------------------------------
        if request.user.is_superuser:
            yetkili_projeler_qs = Proje.objects.filter(aktif_mi=True)
        else:
            # projects/models.py'den gelen yetki filtresini kullan
            yetkili_projeler_qs = Proje.objects.yetkili_olanlar(request.user).filter(aktif_mi=True)
            
        # Tüm yetkili projelerin ID'leri
        yetkili_proje_idleri = yetkili_projeler_qs.values_list('id', flat=True)

        # -----------------------------------------------------------
        # 2. Widget Verisi 1: 2/3 Çoğunluk Oranı (Önbellek Verisi)
        # -----------------------------------------------------------
        
        # Tüm yetkili projelerdeki cached_imza_arsa_payi'nin toplamını hesapla.
        toplam_imza_payi = yetkili_projeler_qs.aggregate(
            toplam=Sum(Coalesce('cached_imza_arsa_payi', 0.0000)) 
        )['toplam']
        
        if yetkili_projeler_qs.count() > 0 and toplam_imza_payi is not None:
             # Ortalama Imza Oranı: (Projelerin Oranlarının Toplamı) / (Proje Sayısı)
             # Bu bize genelin ortalamasını verir.
             total_imza_orani = toplam_imza_payi / yetkili_projeler_qs.count()
        else:
            total_imza_orani = 0.00
            
        # -----------------------------------------------------------
        # 3. Widget Verisi 2: Bekleyen Görev Sayısı (ÇÖZÜM)
        # -----------------------------------------------------------
        
        # Sadece giriş yapan kullanıcıya atanan ve durumu BEKLEMEDE olan görevleri say.
        bekleyen_gorev_sayisi = Gorev.objects.filter(
            atanan_kullanici=request.user, 
            durum=Gorev.GorevDurumu.BEKLEMEDE
        ).count()
        
        # -----------------------------------------------------------
        # 4. Widget Verisi 3: Toplam Malik Sayısı (ÇÖZÜM)
        # -----------------------------------------------------------
        
        # Yetkili olunan projelerdeki tüm malikleri sayıyoruz.
        # Bu, yetkili_proje_idleri listesi ile yapılır.
        toplam_malik_sayisi = Malik.objects.filter(proje_id__in=yetkili_proje_idleri).count()
        
        
        # -----------------------------------------------------------
        # 5. Context'i Güncelle ve Ana Admin Sitesi'ni Çağır
        # -----------------------------------------------------------
        
        extra_context = extra_context or {}
        extra_context['total_imza_orani'] = total_imza_orani # Değer 0.0050 olacak
        extra_context['bekleyen_gorev_sayisi'] = bekleyen_gorev_sayisi # Sayı 1 veya 0 olacak
        extra_context['toplam_malik_sayisi'] = toplam_malik_sayisi # Sayı 1 olacak
        
        # Orijinal AdminSite index metodunu çağırarak arayüzü döndür.
        return super().index(request, extra_context=extra_context)

# Admin sitesini bizim özelleştirilmiş KPYAdminSite'ımızla değiştir.
admin.site = KPYAdminSite()