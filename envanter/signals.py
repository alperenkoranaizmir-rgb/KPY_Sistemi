from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Zimmet, Demirbas

@receiver(post_save, sender=Zimmet)
def zimmet_kaydi_guncellendi(sender, instance, created, **kwargs):
    """
    Zimmet kaydı oluşturulduğunda (created=True) veya güncellendiğinde (created=False) çalışır.
    İlgili Demirbaş'ın durumunu otomatik olarak günceller.
    """
    demirbas = instance.demirbas
    
    if instance.iade_tarihi is None:
        # Zimmet kaydı, iade tarihi boşsa (yani zimmetliyse)
        yeni_durum = Demirbas.DemirbasDurumu.KULLANIMDA
    else:
        # Zimmet kaydı, iade tarihi doluysa (yani iade edilmişse)
        yeni_durum = Demirbas.DemirbasDurumu.DEPO
        
    # Sadece durum değişmişse veritabanını güncelleyerek gereksiz kaydetme işlemini önle
    if demirbas.durum != yeni_durum:
        demirbas.durum = yeni_durum
        demirbas.save()


@receiver(post_delete, sender=Zimmet)
def zimmet_kaydi_silindi(sender, instance, **kwargs):
    """
    Zimmet kaydı silindiğinde (post_delete), ilgili Demirbaş'ın durumunu Depoya döndürür.
    """
    # Silme işlemi gerçekleştiği anda demirbaşı depoya döndür.
    demirbas = instance.demirbas
    demirbas.durum = Demirbas.DemirbasDurumu.DEPO
    demirbas.save()
    
    # HATA AYIKLAMA İÇİN EK NOT (SİLİN): Silme işlemi çalışmazsa bu print terminalde görünür:
    # print(f"DEBUG: Zimmet silindi. {demirbas.ad} Depoya döndürüldü.")