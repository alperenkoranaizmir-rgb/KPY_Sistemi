from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings # AUTH_USER_MODEL'i kullanmak için
# KRİTİK IMPORT'lar: Görevleri Proje ve Malik'e bağlamak için
from projects.models import Proje, Malik 


class Kullanici(AbstractUser):
    """
    Mimari planda kararlaştırdığımız, projeye özel Kullanıcı (Personel) modeli.
    """
    unvan = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Unvan (Şirket İçi)"
    )
    
    telefon_numarasi = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Telefon Numarası"
    )

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    class Meta:
        verbose_name = "Personel"
        verbose_name_plural = "Personel Listesi"


class Gorev(models.Model):
    """
    Personellere atanacak saha görevleri (task management).
    """
    class GorevDurumu(models.TextChoices):
        BEKLEMEDE = 'BEKLEMEDE', 'Beklemede'
        YAPILDI = 'YAPILDI', 'Yapıldı'
        ERTELENDI = 'ERTELENDI', 'Ertelendi'
        IPTAL_EDILDI = 'IPTAL_EDILDI', 'İptal Edildi'

    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    malik = models.ForeignKey(
        Malik,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="İlgili Malik (Opsiyonel)"
    )
    
    atanan_kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL, # users.Kullanici
        on_delete=models.CASCADE,
        related_name='atanan_gorevler',
        verbose_name="Atanan Personel"
    )

    baslik = models.CharField(max_length=255, verbose_name="Görev Başlığı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Detaylı Açıklama")
    son_tarih = models.DateField(blank=True, null=True, verbose_name="Son Teslim Tarihi")
    
    durum = models.CharField(
        max_length=50,
        choices=GorevDurumu.choices,
        default=GorevDurumu.BEKLEMEDE,
        verbose_name="Durum"
    )

    def __str__(self):
        return f"[{self.get_durum_display()}] {self.baslik}"

    class Meta:
        verbose_name = "Görev (Task)"
        verbose_name_plural = "Görev Yönetimi"
        ordering = ['son_tarih']