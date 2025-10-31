from django.db import models
from projects.models import Proje
from users.models import Kullanici # Sorumlu personeli bağlamak için


# -----------------------------------------------------------------
# FAZ 1: TEMEL TANIMLAMALAR
# -----------------------------------------------------------------

class DepolamaAlani(models.Model): # YENİ MODEL
    """
    Sarf malzemelerinin veya yedek envanterin tutulduğu fiziksel lokasyon.
    """
    ad = models.CharField(max_length=150, unique=True, verbose_name="Depo/Lokasyon Adı")
    adres = models.TextField(blank=True, null=True, verbose_name="Adres/Konum")

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = "Depolama Alanı"
        verbose_name_plural = "Depolama Alanları"


class EnvanterKategorisi(models.Model):
    """
    Envanter/Varlık tiplerinin sınıflandırılması (Örn: Ofis Ekipmanı, Saha Aracı, Yazılım Lisansı).
    """
    ad = models.CharField(max_length=150, unique=True, verbose_name="Kategori Adı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = "Envanter Kategorisi"
        verbose_name_plural = "Envanter Kategorileri"


# -----------------------------------------------------------------
# FAZ 2: SARF MALZEMESİ VE STOK YÖNETİMİ
# -----------------------------------------------------------------

class SarfMalzemesi(models.Model): # YENİ MODEL
    """
    Stok takibi yapılması gereken sarf malzemeleri (Örn: Vida, Kağıt, Yedek Parça).
    """
    kategori = models.ForeignKey(
        EnvanterKategorisi,
        on_delete=models.PROTECT,
        verbose_name="Kategori"
    )
    ad = models.CharField(max_length=255, verbose_name="Malzeme Adı")
    
    stok_miktari = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name="Mevcut Stok Miktarı"
    )
    birim = models.CharField(max_length=20, default='Adet', verbose_name="Birim (Adet, kg, litre)")
    
    # Stok Kontrolü
    min_stok_seviyesi = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name="Minimum Stok Seviyesi (Uyarı Tetikleyici)"
    )
    
    depolama_alani = models.ForeignKey(
        DepolamaAlani,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Bulunduğu Depo/Lokasyon"
    )

    def __str__(self):
        return f"{self.ad} ({self.stok_miktari} {self.birim})"

    class Meta:
        verbose_name = "Sarf Malzemesi"
        verbose_name_plural = "Sarf Malzemeleri"
        ordering = ['ad']


class SarfMalzemeHareketi(models.Model): # YENİ MODEL
    """
    Sarf malzemelerinin stok giriş ve çıkış hareketleri.
    Not: Gerçek stok miktarı bir sinyal (signals.py) ile güncellenmelidir.
    """
    class HareketTipi(models.TextChoices):
        GIRIS = 'GIRIS', 'Stok Girişi (Satın Alma/Üretim)'
        CIKIS = 'CIKIS', 'Stok Çıkışı (Kullanım/Zimmet)'
        
    malzeme = models.ForeignKey(
        SarfMalzemesi,
        on_delete=models.PROTECT,
        related_name='stok_hareketleri',
        verbose_name="Sarf Malzemesi"
    )
    
    hareket_tipi = models.CharField(
        max_length=10,
        choices=HareketTipi.choices,
        verbose_name="Hareket Tipi"
    )
    
    miktar = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Hareket Miktarı"
    )
    
    hareket_tarihi = models.DateTimeField(auto_now_add=True)
    
    ilgili_proje = models.ForeignKey(
        Proje,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="İlgili Proje (Opsiyonel)"
    )
    
    yapan_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="İşlemi Yapan Personel"
    )
    
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama/Belge Referansı")

    def __str__(self):
        return f"{self.malzeme.ad} - {self.get_hareket_tipi_display()}: {self.miktar} {self.malzeme.birim}"

    class Meta:
        verbose_name = "Sarf Malzeme Hareketi"
        verbose_name_plural = "Sarf Malzeme Hareketleri"
        ordering = ['-hareket_tarihi']

# -----------------------------------------------------------------
# FAZ 3: ENVANTER (DEMİRBAŞ) YÖNETİMİ VE BAKIM TAKİBİ
# -----------------------------------------------------------------

class Envanter(models.Model):
    """
    Proje bazlı fiziksel veya yazılımsal varlıkların detaylı kaydı (Demirbaş).
    Amortisman ve lokasyon takibi için geliştirildi.
    """
    class DurumSecenekleri(models.TextChoices):
        AKTIF = 'AKTIF', 'Aktif Kullanımda'
        DEPO = 'DEPO', 'Depoda / Yedekte'
        BAKIM = 'BAKIM', 'Bakımda / Arızalı'
        HURDA = 'HURDA', 'Hurda / Kullanım Dışı'

    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        related_name='envanterler',
        verbose_name="İlgili Proje"
    )

    kategori = models.ForeignKey(
        EnvanterKategorisi,
        on_delete=models.PROTECT,
        verbose_name="Kategori"
    )
    
    # Varlık Bilgileri
    ad = models.CharField(max_length=255, verbose_name="Varlık Adı/Modeli")
    seri_no = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name="Seri/Stok Numarası"
    )
    
    edinme_tarihi = models.DateField(verbose_name="Edinme Tarihi")
    edinme_maliyeti = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Edinme Maliyeti (TL)"
    )

    # Amortisman Alanları (YENİ)
    amortisman_orani = models.DecimalField(
        max_digits=5, # %100'e kadar
        decimal_places=2,
        default=0.00,
        verbose_name="Yıllık Amortisman Oranı (%)",
        help_text="Envanterin yıllık amortisman yüzdesi."
    )
    amortisman_baslangic_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="Amortisman Başlangıç Tarihi"
    )
    
    durum = models.CharField(
        max_length=50,
        choices=DurumSecenekleri.choices,
        default=DurumSecenekleri.DEPO,
        verbose_name="Mevcut Durumu"
    )
    
    # Atama ve Lokasyon Bilgisi
    sorumlu_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Mevcut Sorumlu Personel",
        related_name='sorumlu_envanterler'
    )
    
    depolama_alani = models.ForeignKey( # Eğer zimmetli değilse nerede tutulduğu
        DepolamaAlani,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='envanter_stoklari',
        verbose_name="Bulunduğu Depo/Lokasyon (Zimmetli değilse)"
    )

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.ad} ({self.seri_no or 'SN Yok'})"

    class Meta:
        verbose_name = "Envanter (Varlık/Demirbaş)"
        verbose_name_plural = "Envanterler (Varlıklar/Demirbaşlar)"
        ordering = ['ad']


class BakimKaydi(models.Model): # YENİ MODEL
    """
    Envanter/Varlıklar için yapılan planlı/plansız bakım, onarım veya arıza kayıtları.
    """
    class BakimTipi(models.TextChoices):
        PLANLI = 'PLANLI', 'Planlı Bakım'
        ARIZA = 'ARIZA', 'Arıza Onarım'
        KALIBRASYON = 'KALIBRASYON', 'Kalibrasyon'
        
    envanter = models.ForeignKey(
        Envanter,
        on_delete=models.CASCADE,
        related_name='bakim_kayitlari',
        verbose_name="İlgili Envanter"
    )
    
    tip = models.CharField(
        max_length=20,
        choices=BakimTipi.choices,
        verbose_name="Bakım Tipi"
    )
    
    bakim_tarihi = models.DateField(verbose_name="Bakım/Arıza Tarihi")
    aciklama = models.TextField(verbose_name="Yapılan İşlem/Arıza Açıklaması")
    
    maliyet = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name="Bakım Maliyeti (TL)"
    )
    
    sonuc = models.CharField(max_length=255, verbose_name="Bakım Sonucu (Örn: Tamir Edildi, Parça Değişti)")
    
    sorumlu_teknisyen = models.ForeignKey(
        Kullanici,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Sorumlu Teknisyen/Personel"
    )
    
    bir_sonraki_bakim_tarihi = models.DateField(
        blank=True, null=True,
        verbose_name="Planlanan Sonraki Bakım Tarihi"
    )
    
    def __str__(self):
        return f"{self.envanter.ad} - {self.get_tip_display()} ({self.bakim_tarihi.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = "Bakım/Arıza Kaydı"
        verbose_name_plural = "Bakım/Arıza Kayıtları"
        ordering = ['-bakim_tarihi']


class KullanimKaydi(models.Model):
    """
    Bir Envanterin zaman içinde kimin tarafından, ne amaçla ve ne zaman kullanıldığının kaydı (Zimmet).
    """
    envanter = models.ForeignKey(
        Envanter,
        on_delete=models.CASCADE,
        related_name='kullanim_kayitlari',
        verbose_name="Kullanılan Envanter"
    )
    
    kullanici = models.ForeignKey(
        Kullanici,
        on_delete=models.PROTECT,
        related_name='envanter_kullanimlari',
        verbose_name="Kullanan Personel"
    )
    
    kullanim_amaci = models.CharField(max_length=255, verbose_name="Kullanım Amacı/Yeri")
    
    baslangic_tarihi = models.DateTimeField(verbose_name="Kullanım Başlangıç Tarihi")
    bitis_tarihi = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Kullanım Bitiş Tarihi (Boş ise hala kullanılıyor)"
    )

    def __str__(self):
        # Eğer bitiş tarihi yoksa aktif kullanımı belirt
        bitis = self.bitis_tarihi.strftime('%d.%m.%Y') if self.bitis_tarihi else "Aktif"
        return f"{self.envanter.ad} - {self.kullanici} ({self.baslangic_tarihi.strftime('%d.%m.%Y')} - {bitis})"

    class Meta:
        verbose_name = "Envanter Kullanım Kaydı (Zimmet)"
        verbose_name_plural = "Envanter Kullanım Kayıtları (Zimmetler)"
        ordering = ['-baslangic_tarihi']