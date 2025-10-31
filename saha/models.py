# saha/models.py

from django.db import models
from projects.models import Proje, BagimsizBolum
from users.models import Kullanici

class Taseron(models.Model):
    """ Modül 4: Taşeron Yönetimi """
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='taseronlar')
    firma_adi = models.CharField(max_length=255)
    yetkili_kisi = models.CharField(max_length=150, blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    uzmanlik_alani = models.CharField(max_length=200, blank=True, null=True)
    sozlesme_belgesi = models.FileField(upload_to='uploads/taseron_sozlesmeleri/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.proje.proje_adi} - {self.firma_adi}"
    
    class Meta:
        verbose_name = "Taşeron"
        verbose_name_plural = "Taşeronlar"
        ordering = ['firma_adi']

class SahaRaporu(models.Model):
    """ Modül 4: Günlük Saha Raporları """
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='saha_raporlari')
    raporu_yazan = models.ForeignKey(Kullanici, on_delete=models.SET_NULL, null=True, related_name='saha_raporlari')
    tarih = models.DateField(auto_now_add=True)
    metin = models.TextField(verbose_name="Günlük Rapor Özeti")
    fotograf1 = models.ImageField(upload_to='uploads/saha_fotograflari/', blank=True, null=True)
    fotograf2 = models.ImageField(upload_to='uploads/saha_fotograflari/', blank=True, null=True)
    fotograf3 = models.ImageField(upload_to='uploads/saha_fotograflari/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.proje.proje_adi} - {self.tarih} Raporu"
    
    class Meta:
        verbose_name = "Günlük Saha Raporu"
        verbose_name_plural = "Günlük Saha Raporları"
        ordering = ['-tarih']

class TahliyeTakibi(models.Model):
    """ Modül 4: Tahliye & Yıkım Takibi """
    bagimsiz_bolum = models.OneToOneField(BagimsizBolum, on_delete=models.CASCADE, related_name='tahliye_durumu')
    tahliye_edildi_mi = models.BooleanField(default=False, verbose_name="Tahliye Edildi")
    elektrik_kesildi_mi = models.BooleanField(default=False, verbose_name="Elektrik Kesildi")
    su_kesildi_mi = models.BooleanField(default=False, verbose_name="Su Kesildi")
    dogalgaz_kesildi_mi = models.BooleanField(default=False, verbose_name="Doğalgaz Kesildi")
    notlar = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.bagimsiz_bolum} Tahliye Durumu"
    
    class Meta:
        verbose_name = "Tahliye Takip Kaydı"
        verbose_name_plural = "Tahliye Takip Kayıtları"

class IsTakvimiGorevi(models.Model):
    """ Modül 4: İş Takvimi (Gantt) """
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='is_takvimi')
    gorev_adi = models.CharField(max_length=255)
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField()
    tamamlanma_orani = models.PositiveIntegerField(default=0, help_text="Yüzde (%) olarak")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='alt_gorevler')

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.gorev_adi}"
    
    class Meta:
        verbose_name = "İş Takvimi Görevi"
        verbose_name_plural = "İş Takvimi Görevleri"
        ordering = ['baslangic_tarihi']