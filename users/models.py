from django.db import models
from django.contrib.auth.models import AbstractUser # Özel kullanıcı modeli için temel
from projects.models import Proje, Malik # Görevleri Proje ve Malik'e bağlamak için


class Kullanici(AbstractUser):
    """
    Sistemin AUTH_USER_MODEL'i. Django'nun varsayılan kullanıcı modelini genişletir.
    Ekstra personel bilgilerini burada tutuyoruz.
    """
    # Varsayılan alanlar (username, email, first_name, last_name, is_active, is_staff vb.) AbstractUser'dan gelir.
    
    telefon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon Numarası")
    
    # Kentsel Dönüşüm uzmanı için birincil uzmanlık alanı
    uzmanlik_alani = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Uzmanlık Alanı"
    )

    # Profil fotoğrafı alanı
    profil_fotografi = models.ImageField(
        upload_to='kullanici_profilleri/', 
        blank=True, 
        null=True, 
        verbose_name="Profil Fotoğrafı"
    )

    # Personel işe başlangıç tarihi
    ise_baslangic_tarihi = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="İşe Başlangıç Tarihi"
    )

    class Meta:
        verbose_name = "Kullanıcı (Personel)"
        verbose_name_plural = "Kullanıcılar (Personeller)"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        # Kullanıcı adının yerine isim soyisim veya sadece isim gösterimi
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username
    
class Gorev(models.Model):
    """
    Kullanıcılara (Personellere) atanan projeyle ilgili görevlerin takibi.
    """
    class OncelikSeviyesi(models.TextChoices):
        ACIL = 'ACIL', 'Acil'
        YUKSEK = 'YUKSEK', 'Yüksek'
        ORTA = 'ORTA', 'Orta'
        DUSUK = 'DUSUK', 'Düşük'

    class Durum(models.TextChoices):
        YENI = 'YENI', 'Yeni'
        DEVAM_EDIYOR = 'DEVAM_EDIYOR', 'Devam Ediyor'
        BEKLEMEDE = 'BEKLEMEDE', 'Beklemede'
        TAMAMLANDI = 'TAMAMLANDI', 'Tamamlandı'
        IPTAL_EDILDI = 'IPTAL_EDILDI', 'İptal Edildi'

    # Görev Bilgileri
    baslik = models.CharField(max_length=255, verbose_name="Görev Başlığı")
    aciklama = models.TextField(verbose_name="Görev Açıklaması")
    
    # İlişkiler
    atanan_personel = models.ForeignKey(
        Kullanici, 
        on_delete=models.PROTECT, 
        related_name='gorevler',
        verbose_name="Atanan Personel"
    )
    
    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        verbose_name="İlgili Proje"
    )
    
    # Malik ile ilgili bir görev ise (Örn: "Ali Yılmaz ile Görüşme Yap")
    ilgili_malik = models.ForeignKey(
        Malik,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='gorevleri', # Çakışmaları önlemek için related_name eklendi
        verbose_name="İlgili Malik (Opsiyonel)"
    )

    # Durum ve Tarihler
    oncelik = models.CharField(
        max_length=20,
        choices=OncelikSeviyesi.choices,
        default=OncelikSeviyesi.ORTA,
        verbose_name="Öncelik Seviyesi"
    )
    
    durum = models.CharField(
        max_length=20,
        choices=Durum.choices,
        default=Durum.YENI,
        verbose_name="Durum"
    )
    
    son_teslim_tarihi = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Son Teslim Tarihi"
    )
    
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.baslik} ({self.get_durum_display()})"

    class Meta:
        verbose_name = "Personel Görevi"
        verbose_name_plural = "Personel Görevleri"
        ordering = ['durum', 'son_teslim_tarihi']