from django.db import models
from projects.models import Proje
from users.models import Kullanici # Sorumlu personeli bağlamak için


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


class Envanter(models.Model):
    """
    Proje bazlı fiziksel veya yazılımsal varlıkların detaylı kaydı.
    """
    class DurumSecenekleri(models.TextChoices):
        AKTIF = 'AKTIF', 'Aktif Kullanımda'
        DEPO = 'DEPO', 'Depoda / Yedekte'
        BAKIM = 'BAKIM', 'Bakımda / Arızalı'
        HURDA = 'HURDA', 'Hurda / Kullanım Dışı'

    proje = models.ForeignKey(
        Proje,
        on_delete=models.CASCADE,
        related_name='envanterler', # İyileştirme: related_name eklendi
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

    durum = models.CharField(
        max_length=50,
        choices=DurumSecenekleri.choices,
        default=DurumSecenekleri.DEPO,
        verbose_name="Mevcut Durumu"
    )
    
    # Atama Bilgisi (Varlığın mevcut sorumlusu)
    sorumlu_personel = models.ForeignKey(
        Kullanici,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="Mevcut Sorumlu Personel",
        related_name='sorumlu_envanterler'
    )

    def __str__(self):
        return f"{self.proje.proje_adi} - {self.ad} ({self.seri_no or 'SN Yok'})"

    class Meta:
        verbose_name = "Envanter (Varlık)"
        verbose_name_plural = "Envanterler (Varlıklar)"
        ordering = ['ad']


class KullanimKaydi(models.Model):
    """
    Bir Envanterin zaman içinde kimin tarafından, ne amaçla ve ne zaman kullanıldığının kaydı.
    """
    envanter = models.ForeignKey(
        Envanter,
        on_delete=models.CASCADE,
        related_name='kullanim_kayitlari', # İyileştirme: related_name eklendi
        verbose_name="Kullanılan Envanter"
    )
    
    kullanici = models.ForeignKey(
        Kullanici,
        on_delete=models.PROTECT,
        related_name='envanter_kullanimlari', # İyileştirme: related_name eklendi
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
        verbose_name = "Envanter Kullanım Kaydı"
        verbose_name_plural = "Envanter Kullanım Kayıtları"
        ordering = ['-baslangic_tarihi']