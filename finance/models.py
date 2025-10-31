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
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        related_name='butceler', # İyileştirme: related_name eklendi
        verbose_name="Proje"
    )
    maliyet_kalemi = models.ForeignKey(
        MaliyetKalemi,
        on_delete=models.PROTECT,
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
        unique_together = ('proje', 'maliyet_kalemi')


class Maliyet(models.Model):
    """
    Bir Proje için yapılan 'Fiili (Gerçekleşen) Harcama'.
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.PROTECT,
        related_name='maliyetler', # İyileştirme: related_name eklendi
        verbose_name="Proje"
    )
    maliyet_kalemi = models.ForeignKey(
        MaliyetKalemi,
        on_delete=models.PROTECT,
        verbose_name="Maliyet Kalemi"
    )
    
    tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Harcama Tutarı (TL)"
    )
    aciklama = models.TextField(verbose_name="Harcama Açıklaması / Fatura No")
    harcama_tarihi = models.DateField(verbose_name="Harcama Tarihi")
    
    kaydi_yapan_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kaydı Yapan Personel"
    )
    
    # ilgili_evrak opsiyonel olarak tutulmuştur.

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.tutar} TL ({self.maliyet_kalemi.ad})"

    class Meta:
        verbose_name = "Maliyet (Fiili Harcama)"
        verbose_name_plural = "Maliyetler (Fiili Harcamalar)"
        ordering = ['-harcama_tarihi']