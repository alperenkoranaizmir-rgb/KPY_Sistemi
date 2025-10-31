# projects/choices.py

from django.db import models

class DirencNedenleri(models.TextChoices):
    """
    Maliklerin anlaşmaya direncini sınıflandırmak için kullanılır.
    projects.GorusmeKaydi modelinde kullanılmıştır.
    """
    YOK = 'YOK', 'Anlaşma Yok/Gerekli Değil'
    FIYAT = 'FIYAT', 'Fiyat Teklifi Yetersiz'
    VERASET = 'VERASET', 'Veraset/Miras Sorunu'
    PLAN = 'PLAN', 'Yeni Proje Planını Beğenmeme'
    KIRACI = 'KIRACI', 'Kiracı Sorunu/Tahliye'
    DIGER = 'DIGER', 'Diğer/Özel Durum'
    
# İleride eklenebilecek diğer merkezi choices sınıfları buraya eklenecektir.