# /saha/models.py 

from django.db import models
from projects.models import Proje, BagimsizBolum
from users.models import Kullanici
from django.conf import settings
from django.core.exceptions import ValidationError

# -----------------------------------------------------------------
# 1. TAŞERON YÖNETİMİ MODELİ
# -----------------------------------------------------------------
class Taseron(models.Model):
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

# -----------------------------------------------------------------
# 2. İŞ TAKVİMİ GÖREVİ MODELİ
# -----------------------------------------------------------------
class IsTakvimiGorevi(models.Model):
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
# 3. TAHİLİYE TAKİBİ MODELİ
# -----------------------------------------------------------------

class TahliyeTakibi(models.Model):
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
        unique_together = ('proje', 'bagimsiz_bolum')


# -----------------------------------------------------------------
# 4. GÜNLÜK SAHA RAPORU MODELİ
# -----------------------------------------------------------------

class GunlukSahaRaporu(models.Model):
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    # KRİTİK DÜZELTME: unique=True kaldırıldı.
    rapor_tarihi = models.DateField(verbose_name="Rapor Tarihi")
    
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
    
    # Saha Fotoğrafı
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
        # KRİTİK EKLEME: Aynı projede aynı tarihte birden fazla rapor girilemez.
        unique_together = ('proje', 'rapor_tarihi')