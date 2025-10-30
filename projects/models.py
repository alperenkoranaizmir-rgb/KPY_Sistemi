from django.db import models
from django.conf import settings # AUTH_USER_MODEL'i (Kullanici modelimizi) çekmek için

class Proje(models.Model):

    # ... (Diğer alanlar)

    # Projenin aktif/pasif durumunu belirlemek için
    aktif_mi = models.BooleanField(default=True, verbose_name="Proje Aktif mi?")
    
    # Mimari Çözüm 4: Performans için Önbelleğe Alınan (Cached) Alanlar (2/3 Takibi için)
    # Bu alanları Celery görevi otomatik olarak güncelleyecek.
    cached_imza_arsa_payi = models.DecimalField(
        max_digits=5,
        # KRİTİK DÜZELTME: 2 yerine 4 yapıyoruz.
        decimal_places=4, 
        default=0.0000,
        verbose_name="Önbellek: İmza Arsa Payı (%)" 
    )
    # Ayrıca default değerini de 4 haneli yapalım
    # ... (Diğer alanlar aynı kalacak)
    cached_toplam_malik_sayisi = models.PositiveIntegerField(
        default=0,
        verbose_name="Önbellek: Toplam Malik Sayısı"
    )

    # Tarih kayıtları
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    # ... (Diğer alanlar)


    """
    Sistemin ana konteynerı. Tüm veriler (Malik, Evrak, Bütçe) bu modele bağlanacak.
    """
    proje_adi = models.CharField(max_length=255, verbose_name="Proje Adı")
    
    # Proje ile ilgili temel bilgiler (opsiyonel)
    aciklama = models.TextField(blank=True, null=True, verbose_name="Proje Açıklaması")
    proje_konumu = models.CharField(max_length=255, blank=True, null=True, verbose_name="Proje Konumu (İl/İlçe)")
    
    # Projenin aktif/pasif durumunu belirlemek için
    aktif_mi = models.BooleanField(default=True, verbose_name="Proje Aktif mi?")
    
    # Tarih kayıtları
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme")

    def __str__(self):
        return self.proje_adi

    class Meta:
        verbose_name = "Proje"
        verbose_name_plural = "Projeler"
        ordering = ['-olusturulma_tarihi'] # Listelerken en yeni proje en üstte olsun


class ProjeYetkisi(models.Model):
    """
    Mimari Çözüm 1: Proje Bazlı Rol Yönetimi (RBAC) modelimiz.
    Bir Kullanici'nın (Personel) bir Proje'deki Rolü'nü belirler.
    """
    class RolSecenekleri(models.TextChoices):
        PROJE_MUDURU = 'PROJE_MUDURU', 'Proje Müdürü'
        SAHA_TEMSILCISI = 'SAHA_TEMSILCISI', 'Saha Temsilcisi'
        HUKUKCU = 'HUKUKCU', 'Hukukçu'
        FINANS = 'FINANS', 'Finans'
        MISAFIR = 'MISAFIR', 'Misafir (Sadece Görüntüleme)'

    kullanici = models.ForeignKey(
        settings.AUTH_USER_MODEL, # users.Kullanici modelimiz
        on_delete=models.CASCADE, # Kullanıcı silinirse bu yetki kaydı da silinsin
        verbose_name="Personel"
    )
    
    proje = models.ForeignKey(
        Proje, # Yukarıdaki Proje modeli
        on_delete=models.CASCADE, # Proje silinirse bu yetki kaydı da silinsin
        verbose_name="Yetkili Proje"
    )
    
    rol = models.CharField(
        max_length=50,
        choices=RolSecenekleri.choices,
        default=RolSecenekleri.MISAFIR,
        verbose_name="Projedeki Rolü"
    )

    def __str__(self):
        # Admin panelinde "Ali Yılmaz - Proje A - Proje Müdürü" olarak görünür
        return f"{self.kullanici} - {self.proje} - {self.get_rol_display()}"

    class Meta:
        verbose_name = "Proje Yetkisi"
        verbose_name_plural = "Proje Yetkileri"
        # Bir kullanıcı bir projede sadece 1 role sahip olabilir (unique)
        unique_together = ('kullanici', 'proje')


# ... (Proje ve ProjeYetkisi modelleri bu dosyanın üst kısmında kalacak)

# -----------------------------------------------------------------
# FAZ 2: KENTSEL DÖNÜŞÜM ÇEKİRDEK MODELLERİ
# -----------------------------------------------------------------

class Malik(models.Model):
    """
    Proje kapsamındaki mülk sahipleri (kişiler). CRM modülünün temelidir.
    """
    proje = models.ForeignKey(
        Proje, 
        on_delete=models.PROTECT, # Projeye bağlı Malik varken Proje silinemez (Önemli veri koruması)
        verbose_name="İlgili Proje"
    )
    
    # Kişisel Bilgiler
    ad = models.CharField(max_length=100, verbose_name="Ad")
    soyad = models.CharField(max_length=100, verbose_name="Soyad")
    tc_kimlik_no = models.CharField(max_length=11, blank=True, null=True, verbose_name="TC Kimlik No")
    
    # İletişim Bilgileri
    telefon_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon 1")
    telefon_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon 2")
    email = models.EmailField(blank=True, null=True, verbose_name="E-Posta Adresi")
    adres = models.TextField(blank=True, null=True, verbose_name="Adres")
    
    # Otomatik SMS için (CRM)
    dogum_tarihi = models.DateField(blank=True, null=True, verbose_name="Doğum Tarihi")

    # Süreç Takibi
    # (Bu kısmı daha sonra 'GorusmeKaydi' modeli ile ilişkilendireceğiz)
    
    def __str__(self):
        return f"{self.ad} {self.soyad}"

    class Meta:
        verbose_name = "Malik (Mülk Sahibi)"
        verbose_name_plural = "Malikler (Mülk Sahipleri)"
        # Bir malik (aynı TCKN) bir projeye sadece 1 kez kaydedilebilmeli
        unique_together = ('proje', 'tc_kimlik_no')


class BagimsizBolum(models.Model):
    """
    Proje kapsamındaki mülkler (Daire, Dükkan, Arsa vb.).
    """
    proje = models.ForeignKey(
        Proje, 
        on_delete=models.PROTECT, # İçinde Bağımsız Bölüm varken Proje silinemez
        verbose_name="İlgili Proje"
    )
    
    # Adres Bilgileri
    ada = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ada")
    parsel = models.CharField(max_length=50, blank=True, null=True, verbose_name="Parsel")
    pafta = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pafta")
    
    # Mülk Bilgileri
    nitelik = models.CharField(max_length=100, verbose_name="Niteliği (Daire, Dükkan, Arsa...)")
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

    def __str__(self):
        return f"{self.proje.proje_adi} - Ada:{self.ada} Parsel:{self.parsel} ({self.nitelik})"

    class Meta:
        verbose_name = "Bağımsız Bölüm (Mülk)"
        verbose_name_plural = "Bağımsız Bölümler (Mülkler)"


class Hisse(models.Model):
    """
    Mimari Çözüm 2 ve 3: En kritik tablo. 
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
        on_delete=models.PROTECT, # Hisse varken Malik silinemez
        verbose_name="Hissedar Malik"
    )
    
    bagimsiz_bolum = models.ForeignKey(
        BagimsizBolum,
        on_delete=models.PROTECT, # Hisse varken Bağımsız Bölüm silinemez
        verbose_name="İlgili Bağımsız Bölüm"
    )
    
    # Mülkiyet Bilgisi (Mimari Çözüm 2)
    hisse_orani = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.0, # Varsayılan olarak %100 (1.0)
        verbose_name="Hisse Oranı (Örn: 0.50 = %50)"
    )
    
    # Süreç Takibi (Mimari Çözüm 2)
    durum = models.CharField(
        max_length=50,
        choices=ImzaDurumu.choices,
        default=ImzaDurumu.BEKLEMEDE,
        verbose_name="İmza Durumu"
    )
    
    # (Mimari Çözüm 3'ü desteklemek için 'Evrak' modeli buraya bağlanacak, şimdilik değil)
    
    def __str__(self):
        return f"{self.malik} - {self.bagimsiz_bolum.nitelik} (%{self.hisse_orani * 100}) - {self.get_durum_display()}"

    class Meta:
        verbose_name = "Hisse (Mülkiyet Kaydı)"
        verbose_name_plural = "Hisseler (Mülkiyet Kayıtları)"

# -----------------------------------------------------------------
# FAZ 3: OPERASYON VE ZEKA MODELLERİ (GÖRÜŞME VE ARŞİV)
# -----------------------------------------------------------------

class GorusmeKaydi(models.Model):
    """
    Saha temsilcisinin malik ile yaptığı görüşmelerin kaydı.
    CRM modülünün en aktif kullanılan parçası olacaktır.
    """
    # projects/models.py dosyasında, GorusmeKaydi'nın üstüne ekleyin

    class DirencNedenleri(models.TextChoices):
        YOK = 'YOK', 'Anlaşma Yok/Gerekli Değil'
        FIYAT = 'FIYAT', 'Fiyat Teklifi Yetersiz'
        VERASET = 'VERASET', 'Veraset/Miras Sorunu'
        PLAN = 'PLAN', 'Yeni Proje Planını Beğenmeme'
        KIRACI = 'KIRACI', 'Kiracı Sorunu/Tahliye'
        DIGER = 'DIGER', 'Diğer/Özel Durum'

    class GorusmeSonucu(models.TextChoices):
        OLUMLU = 'OLUMLU', 'Olumlu'
        OLUMSUZ = 'OLUMSUZ', 'Olumsuz'
        KARARSIZ = 'KARARSIZ', 'Kararsız'
        TEKRAR_GORUSULECEK = 'TEKRAR_GORUSULECEK', 'Tekrar Görüşülecek'
        ULASILAMADI = 'ULASILAMADI', 'Ulaşılamadı'

    proje = models.ForeignKey(
        Proje, 
        on_delete=models.CASCADE, # Proje silinirse görüşme kayıtları da silinsin
        verbose_name="İlgili Proje"
    )
    malik = models.ForeignKey(
        Malik,
        on_delete=models.CASCADE, # Malik silinirse görüşme kayıtları da silinsin
        verbose_name="Görüşülen Malik"
    )
    gorusmeyi_yapan_personel = models.ForeignKey(
        settings.AUTH_USER_MODEL, # users.Kullanici modelimiz
        on_delete=models.SET_NULL, # Personel işten ayrılsa bile kayıt kalsın
        null=True,
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
    Mimari Çözüm 3 & 7: Dijital Arşiv (DMS) ve Evrak Sürüm Kontrolü modelimiz.
    Tüm tapu, sözleşme, vekaletname vb. belgeleri tutar.
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
        on_delete=models.PROTECT, # İçinde evrak varken proje silinemez
        verbose_name="İlgili Proje"
    )
    
    # Mimari Çözüm 3: Gelişmiş İlişkilendirme (Evrağı ilgili olduğu her şeye bağlama)
    malik = models.ForeignKey(
        Malik, 
        on_delete=models.SET_NULL, # Malik silinse bile evrak (örn: vekalet) kalsın
        blank=True, null=True, 
        verbose_name="İlgili Malik (Opsiyonel)"
    )
    hisse = models.ForeignKey(
        Hisse, 
        on_delete=models.SET_NULL, # Hisse silinse bile evrak (örn: tapu) kalsın
        blank=True, null=True, 
        verbose_name="İlgili Hisse (Opsiyonel)"
    )
    bagimsiz_bolum = models.ForeignKey(
        BagimsizBolum,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="İlgili Bağımsız Bölüm (Opsiyonel)"
    )
    # (Daha sonra 'Taseron' modeli eklediğimizde buraya onu da ekleyeceğiz)
    
    # Evrak Bilgileri
    evrak_adi = models.CharField(max_length=255, verbose_name="Evrak Adı / Başlığı")
    evrak_tipi = models.CharField(
        max_length=50,
        choices=EvrakTipi.choices,
        default=EvrakTipi.DIGER,
        verbose_name="Evrak Tipi"
    )
    
    # Dosyanın kendisi
    # Not: Dosya yükleme (FileField/ImageField) medya ayarları (MEDIA_ROOT) gerektirir.
    # Şimdilik FileField kullanalım, ayarlarını bir sonraki adımda yapacağız.
    dosya = models.FileField(
        upload_to='evraklar/%Y/%m/%d/', # Yıl/Ay/Gün bazlı klasörleme yapar
        verbose_name="Dosya"
    )
    
    # Mimari Çözüm 7: Evrak Sürüm Kontrolü
    aktif_surum_mu = models.BooleanField(default=True, verbose_name="Bu Aktif Sürüm mü?")
    onceki_surum = models.ForeignKey(
        'self', # Modelin kendisine (Evrak'a) bağlanır
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Önceki Sürüm"
    )

    # Mimari Çözüm 4: OCR (Akıllı Arama) için
    text_content = models.TextField(blank=True, null=True, verbose_name="OCR ile Okunan Metin İçerik")

    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.evrak_adi

    class Meta:
        verbose_name = "Evrak (Dijital Arşiv)"
        verbose_name_plural = "Evraklar (Dijital Arşiv)"
        ordering = ['-olusturulma_tarihi']