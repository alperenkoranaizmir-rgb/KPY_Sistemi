from django.db import models
from projects.models import Proje, BagimsizBolum # Proje ve mülkleri bağlamak için
from users.models import Kullanici # Personeli bağlamak için
from envanter.models import Envanter # Ekipman/Araçları bağlamak için

# -----------------------------------------------------------------
# FAZ 1: İŞ TANIMLARI VE GÜNLÜK RAPOR YAPISI
# -----------------------------------------------------------------

class IsTuru(models.Model): # YENİ MODEL: WBS/İş Kalemleri
    """
    Saha işlerini sınıflandırmak için kullanılır (Örn: Hafriyat, Kaba İnşaat, Tadilat).
    Proje Yönetimi (WBS) ile entegrasyonun temelidir.
    """
    ad = models.CharField(max_length=255, unique=True, verbose_name="İş Kalemi/Aktivite Adı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = "İş Kalemi (WBS)"
        verbose_name_plural = "İş Kalemleri (WBS Tanımları)"


class GunlukSahaRaporu(models.Model):
    """
    Sahada günlük olarak yapılan işlerin ana kaydı.
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        related_name='saha_raporlari',
        verbose_name="İlgili Proje"
    )
    
    rapor_tarihi = models.DateField(
        unique_for_date='rapor_tarihi', # Aynı güne ait birden fazla rapor olmasın
        verbose_name="Rapor Tarihi"
    )
    
    hazirlayan_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.PROTECT,
        related_name='hazirladigi_saha_raporlari',
        verbose_name="Raporu Hazırlayan Personel"
    )
    
    hava_durumu = models.CharField(
        max_length=50, 
        blank=True, null=True, 
        verbose_name="Hava Durumu"
    )
    
    genel_notlar = models.TextField(blank=True, null=True, verbose_name="Genel Gün Sonu Notları")
    
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.proje.proje_adi} - Günlük Rapor ({self.rapor_tarihi.strftime('%d.%m.%Y')})"
    
    class Meta:
        verbose_name = "Günlük Saha Raporu"
        verbose_name_plural = "Günlük Saha Raporları"
        ordering = ['-rapor_tarihi']
        unique_together = ('proje', 'rapor_tarihi')


class SahaIlerlemeKaydi(models.Model): # YENİ MODEL: Rapor Detayları (İş İlerleme)
    """
    Günlük raporda hangi iş kaleminde ne kadar ilerleme kaydedildiğinin detayı.
    """
    rapor = models.ForeignKey(
        GunlukSahaRaporu,
        on_delete=models.CASCADE,
        related_name='ilerleme_kayitlari',
        verbose_name="Günlük Saha Raporu"
    )
    
    is_turu = models.ForeignKey(
        IsTuru,
        on_delete=models.PROTECT,
        verbose_name="Yapılan İş Kalemi"
    )
    
    yapilan_is_ozeti = models.TextField(verbose_name="Yapılan İşin Özeti")
    
    # İlerleme (WBS/Proje ilerlemesi için kullanılacak)
    ilerleme_yuzdesi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Bu İş Kaleminde Kaydedilen Günlük İlerleme (%)"
    )

    def __str__(self):
        return f"{self.is_turu.ad} - %{self.ilerleme_yuzdesi}"

    class Meta:
        verbose_name = "Saha İlerleme Kaydı"
        verbose_name_plural = "Saha İlerleme Kayıtları"


# -----------------------------------------------------------------
# FAZ 2: KAYNAK ATAMA VE TAKİP
# -----------------------------------------------------------------

class SahaPersonelAtamasi(models.Model): # YENİ MODEL: Kaynak Atama (Personel)
    """
    Günlük raporda hangi personelin kaç saat çalıştığının kaydı.
    """
    rapor = models.ForeignKey(
        GunlukSahaRaporu,
        on_delete=models.CASCADE,
        related_name='personel_atamalari',
        verbose_name="Günlük Saha Raporu"
    )
    
    personel = models.ForeignKey(
        Kullanici,
        on_delete=models.PROTECT,
        verbose_name="Çalışan Personel"
    )
    
    calisma_saati = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Çalışma Saati"
    )
    
    gorev_tanimi = models.CharField(max_length=255, verbose_name="Yaptığı İşin Tanımı")
    
    def __str__(self):
        return f"{self.personel} - {self.calisma_saati} Saat"

    class Meta:
        verbose_name = "Saha Personel Ataması"
        verbose_name_plural = "Saha Personel Atamaları"


class SahaEkipmanAtamasi(models.Model): # YENİ MODEL: Kaynak Atama (Ekipman/Araç)
    """
    Günlük raporda hangi ekipmanın kaç saat/adet kullanıldığının kaydı.
    """
    rapor = models.ForeignKey(
        GunlukSahaRaporu,
        on_delete=models.CASCADE,
        related_name='ekipman_atamalari',
        verbose_name="Günlük Saha Raporu"
    )
    
    ekipman = models.ForeignKey(
        Envanter, # Envanter modelinden geliyor
        on_delete=models.PROTECT,
        verbose_name="Kullanılan Ekipman/Araç"
    )
    
    kullanim_suresi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Kullanım Süresi (Saat/Adet)"
    )
    
    kullanim_birimi = models.CharField(max_length=20, default='Saat', verbose_name="Kullanım Birimi")
    
    aciklama = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kullanım Amacı")

    def __str__(self):
        return f"{self.ekipman.ad} - {self.kullanim_suresi} {self.kullanim_birimi}"

    class Meta:
        verbose_name = "Saha Ekipman Ataması"
        verbose_name_plural = "Saha Ekipman Atamaları"


# -----------------------------------------------------------------
# FAZ 3: KALİTE KONTROL VE İŞ GÜVENLİĞİ
# -----------------------------------------------------------------

class KaliteKontrolFormu(models.Model): # YENİ MODEL: Kalite Kontrol
    """
    Sahada yapılan işlerin kalite standartlarına uygunluğunun denetimi.
    """
    class OnayDurumu(models.TextChoices):
        ONAYLANDI = 'ONAYLANDI', 'Kalite Standartlarına Uygun'
        REDDEDILDI = 'REDDEDILDI', 'Düzeltme Gerekiyor'
        BEKLEMEDE = 'BEKLEMEDE', 'Denetim Bekleniyor'
        
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    denetim_tarihi = models.DateField(verbose_name="Denetim Tarihi")
    
    denetleyen_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.PROTECT,
        related_name='yaptigi_kalite_denetimleri',
        verbose_name="Denetimi Yapan Personel"
    )
    
    is_kalemi = models.ForeignKey(
        IsTuru,
        on_delete=models.PROTECT,
        verbose_name="Denetlenen İş Kalemi"
    )
    
    denetim_sonucu = models.CharField(
        max_length=20,
        choices=OnayDurumu.choices,
        default=OnayDurumu.BEKLEMEDE,
        verbose_name="Sonuç"
    )
    
    tespit_edilen_eksikler = models.TextField(blank=True, null=True, verbose_name="Tespit Edilen Eksikler/Uygunsuzluklar")
    
    dof_gerekiyor_mu = models.BooleanField(
        default=False, 
        verbose_name="Düzeltici Önleyici Faaliyet (DÖF) Gerekiyor mu?"
    )

    def __str__(self):
        return f"QC Formu: {self.proje.proje_adi} - {self.is_kalemi.ad} ({self.get_denetim_sonucu_display()})"

    class Meta:
        verbose_name = "Kalite Kontrol Formu"
        verbose_name_plural = "Kalite Kontrol Formları"
        ordering = ['-denetim_tarihi']


class IsGuvenligiKaydi(models.Model): # YENİ MODEL: İş Güvenliği (Kaza/Olay)
    """
    Sahada meydana gelen iş kazaları, olaylar ve güvenlikle ilgili tespitler.
    """
    class KayitTipi(models.TextChoices):
        KAZA = 'KAZA', 'İş Kazası'
        OLAY = 'OLAY', 'Ramak Kala Olay'
        TESPIT = 'TESPIT', 'Güvenlik İhlali Tespiti'
        
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    kayit_tarihi = models.DateTimeField(verbose_name="Olay Tarihi ve Saati")
    kayit_tipi = models.CharField(
        max_length=20,
        choices=KayitTipi.choices,
        verbose_name="Kayıt Tipi"
    )
    
    aciklama = models.TextField(verbose_name="Olayın/Tespiti Detaylı Açıklaması")
    
    yaralanma_durumu = models.BooleanField(
        default=False, 
        verbose_name="Yaralanma/Hasar Var mı?"
    )
    
    raporlayan_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.PROTECT,
        related_name='is_guvenligi_kayitlari',
        verbose_name="Raporlayan Personel"
    )
    
    alınan_onlemler = models.TextField(blank=True, null=True, verbose_name="Olay Sonrası Alınan Önlemler")
    
    def __str__(self):
        return f"{self.proje.proje_adi} - {self.get_kayit_tipi_display()} ({self.kayit_tarihi.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = "İş Güvenliği Kaydı"
        verbose_name_plural = "İş Güvenliği Kayıtları"
        ordering = ['-kayit_tarihi']


# -----------------------------------------------------------------
# FAZ 4: KENTSEL DÖNÜŞÜM ÇEKİRDEK MODELLERİ (Tahliye Takibi)
# -----------------------------------------------------------------

class TahliyeTakibi(models.Model):
    """
    Kentsel dönüşüm projelerinde mülk tahliye süreçlerinin takibi.
    """
    class TahliyeDurumu(models.TextChoices):
        TAHLIYE_EDILMEDI = 'TAHLIYE_EDILMEDI', 'Tahliye Edilmedi'
        PLANLANIYOR = 'PLANLANIYOR', 'Tahliye Planlanıyor'
        TAHLIYE_EDILDI = 'TAHLIYE_EDILDI', 'Tahliye Edildi'
        YASAL_SUREC = 'YASAL_SUREC', 'Yasal Süreçte'
    
    proje = models.ForeignKey(
        Proje,
        on_delete=models.PROTECT,
        verbose_name="İlgili Proje"
    )
    
    bagimsiz_bolum = models.ForeignKey(
        BagimsizBolum,
        on_delete=models.PROTECT,
        verbose_name="İlgili Bağımsız Bölüm"
    )
    
    durum = models.CharField(
        max_length=50,
        choices=TahliyeDurumu.choices,
        default=TahliyeDurumu.TAHLIYE_EDILMEDI,
        verbose_name="Tahliye Durumu"
    )
    
    planlanan_tahliye_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="Planlanan Tahliye Tarihi"
    )
    
    gerceklesen_tahliye_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="Gerçekleşen Tahliye Tarihi"
    )
    
    sorumlu_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Sorumlu Personel"
    )

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.bagimsiz_bolum.nitelik} ({self.get_durum_display()})"

    class Meta:
        verbose_name = "Tahliye Takibi"
        verbose_name_plural = "Tahliye Takipleri"
        unique_together = ('proje', 'bagimsiz_bolum')