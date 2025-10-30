from django.db import models
from django.conf import settings # Zimmeti 'Personel'e (Kullanici) bağlamak için

class Demirbas(models.Model):
    """
    Şirket envanterine kayıtlı varlıklar (Laptop, Telefon, Araç vb.)
    """
    class DemirbasDurumu(models.TextChoices):
        KULLANIMDA = 'KULLANIMDA', 'Kullanımda (Zimmetli)'
        DEPO = 'DEPO', 'Depoda (Kullanıma Hazır)'
        ARIZALI = 'ARIZALI', 'Arızalı'
        HURDA = 'HURDA', 'Hurda (Kullanım Dışı)'

    ad = models.CharField(max_length=255, verbose_name="Demirbaş Adı (Örn: Dell Laptop)")
    model = models.CharField(max_length=255, blank=True, null=True, verbose_name="Model")
    seri_no = models.CharField(max_length=255, unique=True, verbose_name="Seri Numarası")
    
    alinma_tarihi = models.DateField(blank=True, null=True, verbose_name="Satın Alınma Tarihi")
    
    durum = models.CharField(
        max_length=50,
        choices=DemirbasDurumu.choices,
        default=DemirbasDurumu.DEPO,
        verbose_name="Demirbaş Durumu"
    )

    def __str__(self):
        return f"{self.ad} ({self.seri_no})"

    class Meta:
        verbose_name = "Demirbaş"
        verbose_name_plural = "Demirbaş Listesi"


class Zimmet(models.Model):
    """
    Bir Demirbaş'ın bir Kullanici'ya (Personel) atanma (zimmetlenme) kaydı.
    """
    demirbas = models.ForeignKey(
        Demirbas,
        on_delete=models.PROTECT, # Zimmet kaydı varken demirbaş silinemez
        verbose_name="Zimmetlenen Demirbaş"
    )
    
    personel = models.ForeignKey(
        settings.AUTH_USER_MODEL, # users.Kullanici
        on_delete=models.PROTECT, # Zimmet kaydı varken personel silinemez
        verbose_name="Zimmetlenen Personel"
    )
    
    zimmet_tarihi = models.DateField(verbose_name="Zimmet Tarihi")
    
    iade_tarihi = models.DateField(
        blank=True, null=True, 
        verbose_name="İade Tarihi (Boşsa halen zimmetlidir)"
    )
    
    aciklama = models.TextField(blank=True, null=True, verbose_name="Zimmet Notları (Teslimat vb.)")

    def __str__(self):
        return f"{self.demirbas} -> {self.personel}"

    class Meta:
        verbose_name = "Zimmet Kaydı"
        verbose_name_plural = "Zimmet Kayıtları"
        ordering = ['-zimmet_tarihi']