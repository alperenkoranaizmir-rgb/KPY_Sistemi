from django.db import models
from django.conf import settings # AUTH_USER_MODEL'i (Kullanici modelimizi) çekmek için
from .choices import DirencNedenleri # Artık merkezi dosyadan import ediyoruz!

class Proje(models.Model):
    """
    Sistemin ana konteynerı. Tüm veriler (Malik, Evrak, Bütçe) bu modele bağlanacak.
    """
    proje_adi = models.CharField(max_length=255, verbose_name="Proje Adı")
    
    # Proje ile ilgili temel bilgiler (admin.py'ye uyum için güncellendi)
    aciklama = models.TextField(blank=True, null=True, verbose_name="Proje Açıklaması")
    proje_amaci = models.TextField(blank=True, null=True, verbose_name="Proje Amacı")
    
    # Admin'de kullanılan konum ve parsel bilgileri eklendi
    il = models.CharField(max_length=50, blank=True, null=True, verbose_name="İl")
    ilce = models.CharField(max_length=50, blank=True, null=True, verbose_name="İlçe")
    mahalle = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mahalle")
    adres = models.TextField(blank=True, null=True, verbose_name="Proje Adresi")
    ada_parsel = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ada/Parsel Bilgisi")
    
    # Projenin aktif/pasif durumunu belirlemek için
    aktif_mi = models.BooleanField(default=True, verbose_name="Proje Aktif mi?")
    
    # Tarih kayıtları
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme")

    # Mimari Çözüm 4: Performans için Önbelleğe Alınan (Cached) Alanlar (2/3 Takibi için)
    cached_imza_arsa_payi = models.DecimalField(
        max_digits=5,
        decimal_places=2, 
        default=0.00,
        verbose_name="Önbellek: İmza Arsa Payı (%)" 
    )
    cached_toplam_malik_sayisi = models.PositiveIntegerField(
        default=0,
        verbose_name="Önbellek: Toplam Malik Sayısı"
    )
    
    # 2/3 hesaplamasını düzeltmek için ortak payda alanı
    arsa_paydasi_ortak = models.PositiveIntegerField(
        blank=True, null=True, 
        verbose_name="Proje Ortak Arsa Paydası (Örn: 24000)",
        help_text="2/3 hesaplaması için projedeki tüm mülklerin ortak paydası."
    )

    toplam_butce = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Planlanan Toplam Bütçe",
        help_text="Proje için ayrılan toplam bütçe tutarı (TL)"
    )

    def __str__(self):
        return self.proje_adi

    class Meta:
        verbose_name = "Proje"
        verbose_name_plural = "Projeler"
        ordering = ['-olusturulma_tarihi'] # Listelerken en yeni proje en üstte olsun


class ProjeYetkisi(models.Model):
    """
    Mimari Çözüm 1: Proje Bazlı Rol Yönetimi (RBAC) modelimiz.
    """
    class RolSecenekleri(models.TextChoices):
        PROJE_MUDURU = 'PROJE_MUDURU', 'Proje Müdürü'
        SAHA_TEMSILCISI = 'SAHA_TEMSILCISI', 'Saha Temsilcisi'
        HUKUKCU = 'HUKUKCU', 'Hukukçu'
        FINANS = 'FINANS', 'Finans'
        MISAFIR = 'MISAFIR', 'Misafir (Sadece Görüntüleme)'

    kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Personel"
    )
    
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="Yetkili Proje"
    )
    
    rol = models.CharField(
        max_length=50,
        choices=RolSecenekleri.choices,
        default=RolSecenekleri.MISAFIR,
        verbose_name="Projedeki Rolü"
    )

    def __str__(self):
        return f"{self.kullanici} - {self.proje} - {self.get_rol_display()}"

    class Meta:
        verbose_name = "Proje Yetkisi"
        verbose_name_plural = "Proje Yetkileri"
        unique_together = ('kullanici', 'proje')


# -----------------------------------------------------------------
# FAZ 2: KENTSEL DÖNÜŞÜM ÇEKİRDEK MODELLERİ
# -----------------------------------------------------------------

class Malik(models.Model):
    """
    Proje kapsamındaki mülk sahipleri (kişiler). CRM modülünün temelidir.
    """
    proje = models.ForeignKey(
        Proje, 
        on_delete=models.PROTECT,
        related_name='malikler', # ProjeAdmin'deki Count için eklendi
        verbose_name="İlgili Proje"
    )
    
    # Kişisel Bilgiler
    ad = models.CharField(max_length=100, verbose_name="Ad")
    soyad = models.CharField(max_length=100, verbose_name="Soyad")
    tc_kimlik_no = models.CharField(max_length=11, blank=True, null=True, verbose_name="TC Kimlik No")
    
    # Admin'de kullanılan alan eklendi
    cinsiyet = models.CharField(
        max_length=10, 
        choices=[('E', 'Erkek'), ('K', 'Kadın'), ('B', 'Belirtilmemiş')],
        default='B',
        blank=True, null=True,
        verbose_name="Cinsiyet"
    )

    # İletişim Bilgileri
    telefon_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon 1")
    telefon_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon 2")
    email = models.EmailField(blank=True, null=True, verbose_name="E-Posta Adresi")
    adres = models.TextField(blank=True, null=True, verbose_name="Adres")
    
    # Otomatik SMS için (CRM)
    dogum_tarihi = models.DateField(blank=True, null=True, verbose_name="Doğum Tarihi")

    # Admin'deki alanlara karşılık gelen metotlar (E108 hatalarını çözmek için)
    def ad_soyad(self):
        return f"{self.ad} {self.soyad}"
    ad_soyad.short_description = "Ad Soyad"
    
    def telefon(self):
        return self.telefon_1 or self.telefon_2
    telefon.short_description = "Telefon"

    def e_posta(self):
        return self.email
    e_posta.short_description = "E-Posta"


    def __str__(self):
        return f"{self.ad} {self.soyad}"

    class Meta:
        verbose_name = "Malik (Mülk Sahibi)"
        verbose_name_plural = "Malikler (Mülk Sahipleri)"
        unique_together = ('proje', 'tc_kimlik_no')


class BagimsizBolum(models.Model):
    """
    Proje kapsamındaki mülkler (Daire, Dükkan, Arsa vb.).
    """
    proje = models.ForeignKey(
        Proje, 
        on_delete=models.PROTECT,
        verbose_name="İlgili Proje"
    )
    
    # Admin'deki alanlar
    bolum_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="Bağımsız Bölüm Numarası")
    
    # Adres Bilgileri
    ada = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ada")
    parsel = models.CharField(max_length=50, blank=True, null=True, verbose_name="Parsel")
    pafta = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pafta")
    
    # Mülk Bilgileri
    nitelik = models.CharField(max_length=100, verbose_name="Niteliği (Daire, Dükkan, Arsa...)")
    
    # Admin'deki 'kullanim_sekli' alanı için metot (nitelik alanını kullanır)
    def kullanim_sekli(self):
        return self.nitelik
    kullanim_sekli.short_description = "Kullanım Şekli"

    tapu_alani_m2 = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, null=True, 
        verbose_name="Tapu Alanı (m²)"
    )
    
    # Mimari Çözüm 2: 2/3 Hesabı için kritik alanlar
    arsa_payi = models.PositiveIntegerField(
        blank=True, null=True, 
        verbose_name="Arsa Payı (Örn: 120)"
    )
    arsa_paydasi = models.PositiveIntegerField(
        blank=True, null=True, 
        verbose_name="Arsa Paydası (Örn: 24000)"
    )

    # Admin'deki 'arsa_payi_oran_gorunumu' için metot
    def arsa_payi_oran_gorunumu(self):
        if self.arsa_payi and self.arsa_paydasi:
            return f"{self.arsa_payi}/{self.arsa_paydasi}"
        return "-"
    arsa_payi_oran_gorunumu.short_description = "Arsa Payı"


    def __str__(self):
        return f"{self.proje.proje_adi} - Ada:{self.ada} Parsel:{self.parsel} ({self.nitelik})"

    class Meta:
        verbose_name = "Bağımsız Bölüm (Mülk)"
        verbose_name_plural = "Bağımsız Bölümler (Mülkler)"


class Hisse(models.Model):
    """
    Bir Malik'in bir Bağımsız Bölüm'deki mülkiyet payını ve imza durumunu belirler.
    """
    class ImzaDurumu(models.TextChoices):
        IMZALADI = 'IMZALADI', 'İmzaladı'
        BEKLEMEDE = 'BEKLEMEDE', 'Beklemede'
        REDDETTI = 'REDDETTI', 'Reddetti'
        HUKUKI_SURECTE = 'HUKUKI_SURECTE', 'Hukuki Süreçte'

    proje = models.ForeignKey(
        Proje, 
        on_delete=models.PROTECT, 
        verbose_name="İlgili Proje"
    )
    
    malik = models.ForeignKey(
        Malik, 
        on_delete=models.PROTECT,
        related_name='hisseleri', # Related name eklendi
        verbose_name="Hissedar Malik"
    )
    
    bagimsiz_bolum = models.ForeignKey(
        BagimsizBolum,
        on_delete=models.PROTECT,
        verbose_name="İlgili Bağımsız Bölüm"
    )
    
    # Mülkiyet Bilgisi (Admin'e uyum için pay/payda yapısı)
    hisse_orani_pay = models.PositiveIntegerField(
        default=1, 
        verbose_name="Hisse Payı"
    )
    hisse_orani_payda = models.PositiveIntegerField(
        default=1, 
        verbose_name="Hisse Paydası"
    )
    
    # Süreç Takibi
    durum = models.CharField(
        max_length=50,
        choices=ImzaDurumu.choices,
        default=ImzaDurumu.BEKLEMEDE,
        verbose_name="İmza Durumu"
    )

    # Admin'de kullanılan imza_tarihi alanı eklendi
    imza_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="İmza/Red Tarihi"
    )
    
    # Eski hisse_orani alanını hesaplamak için property
    @property
    def hisse_orani(self):
        if self.hisse_orani_payda and self.hisse_orani_payda > 0:
            return self.hisse_orani_pay / self.hisse_orani_payda
        return 0.0

    # Admin'deki 'hisse_oran_gorunumu' için metot
    def hisse_oran_gorunumu(self):
        return f"{self.hisse_orani_pay}/{self.hisse_orani_payda}"
    hisse_oran_gorunumu.short_description = "Hisse Oranı"

    def __str__(self):
        return f"{self.malik} - {self.bagimsiz_bolum.nitelik} ({self.hisse_oran_gorunumu()}) - {self.get_durum_display()}"

    class Meta:
        verbose_name = "Hisse (Mülkiyet Kaydı)"
        verbose_name_plural = "Hisseler (Mülkiyet Kayıtları)"

# -----------------------------------------------------------------
# FAZ 3: OPERASYON VE ZEKA MODELLERİ (GÖRÜŞME VE ARŞİV)
# -----------------------------------------------------------------

class GorusmeKaydi(models.Model):
    """
    Saha temsilcisinin malik ile yaptığı görüşmelerin kaydı.
    """
    
    class GorusmeSonucu(models.TextChoices):
        OLUMLU = 'OLUMLU', 'Olumlu'
        OLUMSUZ = 'OLUMSUZ', 'Olumsuz'
        KARARSIZ = 'KARARSIZ', 'Kararsız'
        TEKRAR_GORUSULECEK = 'TEKRAR_GORUSULECEK', 'Tekrar Görüşülecek'
        ULASILAMADI = 'ULASILAMADI', 'Ulaşılamadı'

    proje = models.ForeignKey(
        Proje, 
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    malik = models.ForeignKey(
        Malik,
        on_delete=models.CASCADE,
        verbose_name="Görüşülen Malik"
    )
    gorusmeyi_yapan_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='yaptigi_gorusmeler', # Admin'deki 'gorusmeyi_yapan' için eklendi
        verbose_name="Görüşmeyi Yapan Personel"
    )
    
    gorusme_tarihi = models.DateTimeField(verbose_name="Görüşme Tarihi ve Saati")
    gorusme_ozeti = models.TextField(verbose_name="Görüşme Özeti / Notlar")
    
    gorusme_sonucu = models.CharField(
        max_length=50,
        choices=GorusmeSonucu.choices,
        blank=True, null=True,
        verbose_name="Görüşme Sonucu"
    )

    # Admin'deki alanlara karşılık gelen metotlar
    def gorusme_metni(self):
        return self.gorusme_ozeti
    gorusme_metni.short_description = "Görüşme Özeti"

    def gorusmeyi_yapan(self):
        return self.gorusmeyi_yapan_personel
    gorusmeyi_yapan.short_description = "Görüşmeyi Yapan"


    # Yeni Analiz Alanı
    direnc_nedeni = models.CharField(
        max_length=50,
        choices=DirencNedenleri.choices, 
        default=DirencNedenleri.YOK,
        verbose_name="Malik Direnç Nedeni"
    )
    
    def __str__(self):
        return f"{self.malik} ile görüşme ({self.gorusme_tarihi.strftime('%d-%m-%Y')})"

    class Meta:
        verbose_name = "Görüşme Kaydı"
        verbose_name_plural = "Görüşme Kayıtları"
        ordering = ['-gorusme_tarihi'] # En yeni görüşme en üstte


class Evrak(models.Model):
    """
    Dijital Arşiv (DMS) ve Evrak Sürüm Kontrolü modelimiz.
    """
    class EvrakTipi(models.TextChoices):
        SOZLESME = 'SOZLESME', 'Sözleşme'
        TAPU = 'TAPU', 'Tapu'
        VEKALETNAME = 'VEKALETNAME', 'Vekaletname'
        RUHSAT = 'RUHSAT', 'Ruhsat (İnşaat/İskan)'
        PROJE_DOSYASI = 'PROJE_DOSYASI', 'Proje Dosyası (Mimari vb.)'
        SAHA_FOTOGRAFI = 'SAHA_FOTOGRAFI', 'Saha Fotoğrafı'
        DIGER = 'DIGER', 'Diğer Resmi Evrak'
    
    proje = models.ForeignKey(
        Proje, 
        on_delete=models.PROTECT,
        verbose_name="İlgili Proje"
    )
    
    malik = models.ForeignKey(
        Malik, 
        on_delete=models.SET_NULL,
        blank=True, null=True, 
        verbose_name="İlgili Malik (Opsiyonel)"
    )
    hisse = models.ForeignKey(
        Hisse, 
        on_delete=models.SET_NULL,
        blank=True, null=True, 
        verbose_name="İlgili Hisse (Opsiyonel)"
    )
    bagimsiz_bolum = models.ForeignKey(
        BagimsizBolum,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="İlgili Bağımsız Bölüm (Opsiyonel)"
    )
    
    # Evrak Bilgileri
    evrak_adi = models.CharField(max_length=255, verbose_name="Evrak Adı / Başlığı")
    evrak_tipi = models.CharField(
        max_length=50,
        choices=EvrakTipi.choices,
        default=EvrakTipi.DIGER,
        verbose_name="Evrak Tipi"
    )

    # Admin'deki 'aciklama' arama alanı için eklendi
    aciklama = models.TextField(
        blank=True, null=True, 
        verbose_name="Ek Açıklama"
    )
    
    # Dosyanın kendisi
    dosya = models.FileField(
        upload_to='evraklar/%Y/%m/%d/',
        verbose_name="Dosya"
    )
    
    aktif_surum_mu = models.BooleanField(default=True, verbose_name="Bu Aktif Sürüm mü?")
    onceki_surum = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Önceki Sürüm"
    )

    text_content = models.TextField(blank=True, null=True, verbose_name="OCR ile Okunan Metin İçerik")

    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    
    # Admin'deki 'yuklenme_tarihi' için metot
    def yuklenme_tarihi(self):
        return self.olusturulma_tarihi
    yuklenme_tarihi.short_description = "Yüklenme Tarihi"

    def __str__(self):
        return self.evrak_adi

    class Meta:
        verbose_name = "Evrak (Dijital Arşiv)"
        verbose_name_plural = "Evraklar (Dijital Arşiv)"
        ordering = ['-olusturulma_tarihi']