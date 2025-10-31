from django.db import models
from projects.models import Proje # Projeleri bağlamak için
from users.models import Kullanici # Harcamayı yapan/onaylayan 'Personel'i bağlamak için
# projects.models yerine users.models'dan Kullanici'yi import ediyoruz
from django.conf import settings # Kullanıcı modelini çekmek için


# -----------------------------------------------------------------
# FAZ 1: TEMEL TANIMLAMALAR
# -----------------------------------------------------------------

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


class TedarikciVeyaMusteri(models.Model): # YENİ MODEL
    """
    Proje ile finansal ilişki kurulan tüm kurumlar ve kişiler (CRM/Vendor).
    """
    class TipSecenekleri(models.TextChoices):
        TEDARIKCI = 'TEDARIKCI', 'Tedarikçi (Gelen Fatura)'
        MUSTERI = 'MUSTERI', 'Müşteri (Giden Fatura)'
        HER_IKISI = 'HER_IKISI', 'Her İkisi'
        
    tip = models.CharField(
        max_length=20,
        choices=TipSecenekleri.choices,
        default=TipSecenekleri.TEDARIKCI,
        verbose_name="Taraf Tipi"
    )
    ad = models.CharField(max_length=255, verbose_name="Kurum/Kişi Adı")
    vergi_no = models.CharField(max_length=20, blank=True, null=True, verbose_name="Vergi No / TC Kimlik No")
    adres = models.TextField(blank=True, null=True, verbose_name="Adres")
    telefon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, null=True, verbose_name="E-Posta Adresi")

    def __str__(self):
        return f"{self.ad} ({self.get_tip_display()})"

    class Meta:
        verbose_name = "Tedarikçi/Müşteri"
        verbose_name_plural = "Tedarikçi/Müşteriler"
        ordering = ['ad']


# -----------------------------------------------------------------
# FAZ 2: BÜTÇE, MALİYET VE FATURA TAKİBİ
# -----------------------------------------------------------------

class Butce(models.Model):
    """
    Bir Proje'nin bir Maliyet Kalemi için ayrılan 'Planlanan Bütçesi'.
    """
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        related_name='butceler',
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


class Fatura(models.Model): # YENİ MODEL
    """
    Gelen ve Giden Fatura Kayıtları.
    """
    class FaturaTipi(models.TextChoices):
        GELEN = 'GELEN', 'Gelen Fatura (Gider)'
        GIDEN = 'GIDEN', 'Giden Fatura (Gelir)'
    
    class FaturaDurumu(models.TextChoices):
        ODENDI = 'ODENDI', 'Ödendi / Tahsil Edildi'
        ODENMEDI = 'ODENMEDI', 'Ödenmedi / Tahsil Edilmedi'
        VADESI_GECTI = 'VADESI_GECTI', 'Vadesi Geçti'
        KISMİ = 'KISMI', 'Kısmen Ödendi/Tahsil Edildi'
    
    proje = models.ForeignKey(
        Proje,
        on_delete=models.PROTECT,
        related_name='faturalar',
        verbose_name="İlgili Proje"
    )
    
    tip = models.CharField(
        max_length=10,
        choices=FaturaTipi.choices,
        verbose_name="Fatura Tipi"
    )
    
    fatura_no = models.CharField(max_length=100, unique=True, verbose_name="Fatura Numarası")
    
    tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Fatura Tutarı (TL)"
    )
    
    karsi_taraf = models.ForeignKey(
        TedarikciVeyaMusteri,
        on_delete=models.PROTECT,
        verbose_name="Tedarikçi / Müşteri"
    )
    
    vade_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="Vade Tarihi"
    )
    
    odeme_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="Ödeme / Tahsilat Tarihi"
    )
    
    durum = models.CharField(
        max_length=20,
        choices=FaturaDurumu.choices,
        default=FaturaDurumu.ODENMEDI,
        verbose_name="Durum"
    )
    
    aciklama = models.TextField(blank=True, null=True, verbose_name="Ek Açıklama")
    
    # Evrak yönetimi için dosya alanı
    evrak_dosya = models.FileField(
        upload_to='faturalar/%Y/%m/',
        blank=True, null=True,
        verbose_name="Fatura Dosyası (PDF/Resim)"
    )

    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.fatura_no} - {self.tutar} TL ({self.get_tip_display()})"

    class Meta:
        verbose_name = "Fatura Kaydı"
        verbose_name_plural = "Fatura Kayıtları"
        ordering = ['-vade_tarihi']


class Maliyet(models.Model):
    """
    Bir Proje için yapılan 'Fiili (Gerçekleşen) Harcama'.
    Artık fatura ve onay ile ilişkilendirildi.
    """
    # Mevcut alanlar
    proje = models.ForeignKey(
        Proje,
        on_delete=models.PROTECT,
        related_name='maliyetler',
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
    aciklama = models.TextField(verbose_name="Harcama Açıklaması") # Fatura no artık Fatura modelinde tutulabilir
    harcama_tarihi = models.DateField(verbose_name="Harcama Tarihi")
    kaydi_yapan_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kaydı Yapan Personel"
    )

    # Yeni alanlar
    ilgili_fatura = models.ForeignKey( # YENİ: Maliyetin hangi faturadan kaynaklandığı
        Fatura,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='maliyetleri',
        verbose_name="İlgili Fatura (Opsiyonel)"
    )
    
    class OnayDurumu(models.TextChoices):
        BEKLEMEDE = 'BEKLEMEDE', 'Onay Bekliyor'
        ONAYLANDI = 'ONAYLANDI', 'Onaylandı'
        REDDEDILDI = 'REDDEDILDI', 'Reddedildi'

    onay_durumu = models.CharField( # YENİ: Harcama kaydının onay durumu (Eğer talep yoksa direkt onaylanmış sayılabilir)
        max_length=20,
        choices=OnayDurumu.choices,
        default=OnayDurumu.ONAYLANDI, # Harcama kaydı yapılırken genellikle onaylanmıştır. Harcama Talep varsa o kullanılır.
        verbose_name="Harcama Onay Durumu"
    )

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.tutar} TL ({self.maliyet_kalemi.ad})"

    class Meta:
        verbose_name = "Maliyet (Fiili Harcama)"
        verbose_name_plural = "Maliyetler (Fiili Harcamalar)"
        ordering = ['-harcama_tarihi']
        
        
# -----------------------------------------------------------------
# FAZ 3: HARCAMA TALEP SÜRECİ
# -----------------------------------------------------------------

class HarcamaTalep(models.Model): # YENİ MODEL
    """
    Bir harcama gerçekleşmeden önce yapılan bütçe ön-onay talebi.
    """
    class OnayDurumu(models.TextChoices):
        BEKLEMEDE = 'BEKLEMEDE', 'Onay Bekliyor'
        ONAYLANDI = 'ONAYLANDI', 'Onaylandı'
        REDDEDILDI = 'REDDEDILDI', 'Reddedildi'
        
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    talep_eden_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='yaptigi_talepler',
        verbose_name="Talebi Yapan Personel"
    )
    
    maliyet_kalemi = models.ForeignKey(
        MaliyetKalemi,
        on_delete=models.PROTECT,
        verbose_name="Planlanan Maliyet Kalemi"
    )
    
    tahmini_tutar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tahmini Tutar (TL)"
    )
    
    gerekce = models.TextField(verbose_name="Talep Gerekçesi / Açıklama")
    
    talep_tarihi = models.DateTimeField(auto_now_add=True)
    
    onay_durumu = models.CharField(
        max_length=20,
        choices=OnayDurumu.choices,
        default=OnayDurumu.BEKLEMEDE,
        verbose_name="Onay Durumu"
    )
    
    onaylayan_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='onayladigi_talepler',
        verbose_name="Onaylayan Personel (Opsiyonel)"
    )
    
    onay_tarihi = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Onay/Red Tarihi"
    )
    
    # Harcama gerçekleştiğinde bu taleple ilişkilendirilir.
    gerceklesen_maliyet = models.OneToOneField(
        Maliyet,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Gerçekleşen Maliyet Kaydı (Opsiyonel)"
    )

    def __str__(self):
        return f"Talep: {self.proje.proje_adi} - {self.tahmini_tutar} TL ({self.get_onay_durumu_display()})"

    class Meta:
        verbose_name = "Harcama Talep Formu"
        verbose_name_plural = "Harcama Talep Formları"
        ordering = ['talep_tarihi']