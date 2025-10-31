# saha/models.py

from django.db import models
from projects.models import Proje, BagimsizBolum
from users.models import Kullanici
from django.conf import settings


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



# -----------------------------------------------------------------
# 1. TAHİLİYE TAKİBİ MODELİ
# -----------------------------------------------------------------

class TahliyeTakibi(models.Model):
    """
    Kentsel Dönüşüm Projelerinde bağımsız bölümlerin tahliye sürecini izler.
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    bagimsiz_bolum = models.ForeignKey(
        BagimsizBolum,
        on_delete=models.PROTECT,
        verbose_name="Takip Edilen Bağımsız Bölüm",
        help_text="Hangi daire, dükkan veya mülkün tahliyesi takip ediliyor."
    )
    
    # Takip Kontrol Listesi
    elektrik_kesildi = models.BooleanField(default=False, verbose_name="Elektrik Kesildi mi?")
    su_kesildi = models.BooleanField(default=False, verbose_name="Su Kesildi mi?")
    gaz_kesildi = models.BooleanField(default=False, verbose_name="Doğalgaz Kesildi mi?")
    malik_tahliye_etti = models.BooleanField(default=False, verbose_name="Malik Tahliyeyi Gerçekleştirdi mi?")
    yikima_hazir = models.BooleanField(default=False, verbose_name="Yıkıma Hazır mı?")
    
    # Tarihler
    son_kontol_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Kontrol Tarihi")
    
    notlar = models.TextField(blank=True, null=True, verbose_name="Tahliye Notları")

    def __str__(self):
        return f"{self.proje} - Tahliye: {self.bagimsiz_bolum}"

    class Meta:
        verbose_name = "Tahliye Takibi"
        verbose_name_plural = "Tahliye Takip Kayıtları"
        unique_together = ('proje', 'bagimsiz_bolum') # Bir projede bir mülk sadece 1 kez takip edilebilir.


# -----------------------------------------------------------------
# 2. GÜNLÜK SAHA RAPORU MODELİ
# -----------------------------------------------------------------

class GunlukSahaRaporu(models.Model):
    """
    Şantiye Şefinin veya Saha Yöneticisinin günlük ilerleme ve sorunları kaydettiği model.
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    rapor_tarihi = models.DateField(verbose_name="Rapor Tarihi", unique=True) # Günde 1 rapor
    
    raporu_hazirlayan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="Raporu Hazırlayan Personel"
    )

    hava_durumu = models.CharField(max_length=50, blank=True, null=True, verbose_name="Hava Durumu (Örn: Güneşli, Yağmurlu)")
    
    # İş gücü takibi
    calisan_sayisi = models.PositiveIntegerField(default=0, verbose_name="Sahadaki Toplam İşçi Sayısı")
    
    # İlerleme Bilgisi
    yapilan_is = models.TextField(verbose_name="Bugün Yapılan İşin Özeti")
    karsilasilan_sorunlar = models.TextField(blank=True, null=True, verbose_name="Karşılaşılan Sorunlar ve Çözümler")
    
    # Saha Fotoğrafı (Evrak Modeline referans da eklenebilir, şimdilik basit tutalım)
    saha_fotografi = models.FileField(
        upload_to='saha_raporlari/%Y/%m/%d/', 
        blank=True, null=True, 
        verbose_name="Günlük Saha Fotoğrafı"
    )

    def __str__(self):
        return f"{self.proje} - Günlük Rapor ({self.rapor_tarihi.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = "Günlük Saha Raporu"
        verbose_name_plural = "Günlük Saha Raporları"
        ordering = ['-rapor_tarihi']