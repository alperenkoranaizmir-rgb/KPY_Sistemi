from django.db import models
from projects.models import Proje # Harcamaları 'Proje' modeline bağlamak için import ediyoruz
from django.conf import settings # Harcamayı yapan 'Personel'i bağlamak için

class MaliyetKalemi(models.Model):
    """
    Sistem Tanımlamaları: Harcama türleri (Kira Yardımı, Hafriyat, Hukuk vb.)
    """
    ad = models.CharField(max_length=255, unique=True, verbose_name="Maliyet Kalemi Adı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = "Maliyet Kalemi"
        verbose_name_plural = "Maliyet Kalemleri (Tanımlamalar)"


class Butce(models.Model):
    """
    Bir Proje'nin bir Maliyet Kalemi için ayrılan 'Planlanan Bütçesi'.
    Örn: Proje A -> Kira Yardımı -> 5.000.000 TL
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="Proje"
    )
    maliyet_kalemi = models.ForeignKey(
        MaliyetKalemi,
        on_delete=models.PROTECT, # Bu kalemde bütçe varken kalem silinemez
        verbose_name="Maliyet Kalemi"
    )
    planlanan_tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Planlanan Tutar (TL)"
    )

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.maliyet_kalemi.ad}: {self.planlanan_tutar} TL"

    class Meta:
        verbose_name = "Proje Bütçesi"
        verbose_name_plural = "Proje Bütçeleri"
        # Bir proje için bir maliyet kalemi sadece 1 kez tanımlanabilir
        unique_together = ('proje', 'maliyet_kalemi')


class Maliyet(models.Model):
    """
    Bir Proje için yapılan 'Fiili (Gerçekleşen) Harcama'.
    Örn: Proje A -> Kira Yardımı -> Ali Yılmaz'a 5.000 TL ödendi.
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.PROTECT, # Harcama varken proje silinemez
        verbose_name="Proje"
    )
    maliyet_kalemi = models.ForeignKey(
        MaliyetKalemi,
        on_delete=models.PROTECT, # Harcama varken kalem silinemez
        verbose_name="Maliyet Kalemi"
    )
    
    tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Harcama Tutarı (TL)"
    )
    aciklama = models.TextField(verbose_name="Harcama Açıklaması / Fatura No")
    harcama_tarihi = models.DateField(verbose_name="Harcama Tarihi")
    
    # Harcamayı sisteme giren personel
    kaydi_yapan_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL, # users.Kullanici
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kaydı Yapan Personel"
    )
    
    # (Opsiyonel: Harcamanın evrağını (fatura) bağlamak için)
    # ilgili_evrak = models.ForeignKey(
    #     'projects.Evrak', 
    #     on_delete=models.SET_NULL, 
    #     blank=True, null=True, 
    #     verbose_name="İlgili Evrak (Fatura)"
    # )

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.tutar} TL ({self.maliyet_kalemi.ad})"

    class Meta:
        verbose_name = "Maliyet (Fiili Harcama)"
        verbose_name_plural = "Maliyetler (Fiili Harcamalar)"
        ordering = ['-harcama_tarihi']