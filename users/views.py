from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, F
from django.utils import timezone
from .models import Gorev
from projects.models import Proje
# Finance modelini (Maliyet) kullanmak için import ediyoruz
from finance.models import Maliyet 

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Giriş yapan kullanıcının kişiselleştirilmiş ana sayfa (Dashboard) görünümü.
    Kullanıcının görevlerini, projelerini ve genel KPY metriklerini özetler.
    """
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Görevler Özeti (User Uygulaması)
        gorevler = Gorev.objects.filter(
            atanan_personel=user
        ).exclude(
            durum=Gorev.Durum.TAMAMLANDI
        ).order_by('son_teslim_tarihi')
        
        tamamlanmamis_gorev_sayisi = gorevler.count()
        
        bugun_vadesi_gelen = Gorev.objects.filter(
            atanan_personel=user,
            son_teslim_tarihi=timezone.now().date()
        ).exclude(
            durum=Gorev.Durum.TAMAMLANDI
        ).count()
        
        gecikmis_gorev_sayisi = Gorev.objects.filter(
            atanan_personel=user,
            son_teslim_tarihi__lt=timezone.now().date()
        ).exclude(
            durum=Gorev.Durum.TAMAMLANDI
        ).count()

        # 2. Projeler Özeti (Projects Uygulaması)
        # Kullanıcının yetkili olduğu aktif projeler
        kullanici_projeleri = Proje.objects.filter(
            projeyetkisi__kullanici=user,
            aktif_mi=True
        ).distinct()
        
        # 3. Bütçe Yaklaşan Projeler
        # Kullanıcının projelerinde bütçesi %90'ın üzerinde harcanmış olanlar
        butce_yaklasan_projeler = Proje.objects.filter(
            id__in=kullanici_projeleri.values('id')
        ).annotate(
            gerceklesen=Sum('maliyetler__tutar')
        ).annotate(
            kalan_butce=F('toplam_butce') - F('gerceklesen')
        ).filter(
            Q(gerceklesen__gte=F('toplam_butce') * 0.9) # Gerçekleşen, bütçenin %90'ından büyük veya eşitse
        ).exclude(
            toplam_butce=0 # Bütçesi 0 olan projeleri hariç tut
        ).order_by('kalan_butce')[:5]

        # Context'e ekle
        context['gorevler_kisa_liste'] = gorevler[:5]
        context['tamamlanmamis_gorev_sayisi'] = tamamlanmamis_gorev_sayisi
        context['bugun_vadesi_gelen'] = bugun_vadesi_gelen
        context['gecikmis_gorev_sayisi'] = gecikmis_gorev_sayisi
        context['toplam_aktif_proje_sayisi'] = kullanici_projeleri.count()
        context['butce_yaklasan_projeler'] = butce_yaklasan_projeler
        
        return context