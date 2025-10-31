# envanter/signals.py - DÜZELTİLMİŞ İÇERİK
from django.db.models.signals import post_save
from django.dispatch import receiver
# Yeni model isimlerini import ediyoruz: Envanter ve KullanimKaydi
from .models import Envanter, KullanimKaydi 
from django.utils import timezone


@receiver(post_save, sender=KullanimKaydi)
def kullanim_kaydi_olusturuldu_veya_guncellendi(sender, instance, created, **kwargs):
    """
    KullanimKaydi (eski Zimmet) oluşturulduğunda veya güncellendiğinde 
    ilgili Envanter'in (eski Demirbas) durumunu otomatik olarak günceller.
    """
    
    # 1. Eğer yeni bir kullanım kaydı oluşturulduysa VEYA 
    #    Kullanım kaydında bitiş tarihi HENÜZ belirlenmediyse (aktif kullanım)
    if created or not instance.bitis_tarihi:
        # Envanterin durumunu "Aktif Kullanımda" olarak ayarla
        if instance.envanter.durum != Envanter.DurumSecenekleri.AKTIF:
            instance.envanter.durum = Envanter.DurumSecenekleri.AKTIF
            instance.envanter.save()
            
    # 2. Eğer kullanım kaydı TAMAMLANDIYSA (bitis_tarihi eklendiyse)
    elif instance.bitis_tarihi:
        
        # Bu envanter için başka aktif bir kullanım kaydı var mı kontrol et
        aktif_kullanim_var_mi = KullanimKaydi.objects.filter(
            envanter=instance.envanter,
            bitis_tarihi__isnull=True # Bitiş tarihi olmayan kayıt
        ).exclude(pk=instance.pk).exists() # Mevcut kaydı hariç tut

        # Eğer başka aktif kullanım yoksa, envanteri 'Depoda' olarak ayarla
        if not aktif_kullanim_var_mi:
            if instance.envanter.durum != Envanter.DurumSecenekleri.DEPO:
                instance.envanter.durum = Envanter.DurumSecenekleri.DEPO
                instance.envanter.save()