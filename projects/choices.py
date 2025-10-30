from django.db import models

# DirencNedenleri sınıfı models.py'den buraya taşındı.
class DirencNedenleri(models.TextChoices):
    YOK = 'YOK', 'Anlaşma Yok/Gerekli Değil'
    FIYAT = 'FIYAT', 'Fiyat Teklifi Yetersiz'
    VERASET = 'VERASET', 'Veraset/Miras Sorunu'
    PLAN = 'PLAN', 'Yeni Proje Planını Beğenmeme'
    KIRACI = 'KIRACI', 'Kiracı Sorunu/Tahliye'
    DIGER = 'DIGER', 'Diğer/Özel Durum'