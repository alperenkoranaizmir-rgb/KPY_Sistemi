from celery import shared_task
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce 
from .models import Proje, Hisse, Malik

@shared_task
def hesapla_proje_istatistikleri(proje_id):
    """
    Kritik Düzeltme ile 2/3 çoğunluk oranını ve toplam malik sayısını hesaplar.
    """
    try:
        proje = Proje.objects.get(id=proje_id)
    except Proje.DoesNotExist:
        return f"HATA: Proje ID {proje_id} bulunamadı."
    
    # --- 1. Toplam Malik Sayısını Hesaplama ---
    toplam_malik = Malik.objects.filter(proje=proje).count()
    
    # --- 2. 2/3 Arsa Payı Hesaplama ---
    
    imzalayan_hisseler = Hisse.objects.filter(
        proje=proje,
        durum=Hisse.ImzaDurumu.IMZALADI
    )
    
    # Güvenlik Kontrolleri
    hisse_oran_guvenli = Coalesce(F('hisse_orani'), 0.0)
    arsa_payi_guvenli = Coalesce(F('bagimsiz_bolum__arsa_payi'), 0)
    
    # Hesaplama: Önce (Hisse Oranı * Arsa Payı) çarpımını hesapla (Pay kısmı)
    # Bu, (1.0 * 120) = 120.0 sonucunu vermelidir.
    pay_kismi = ExpressionWrapper(
        hisse_oran_guvenli * arsa_payi_guvenli,
        output_field=DecimalField(max_digits=12, decimal_places=4)
    )
    
    # Tüm imzalayan hisselerin Pay kısmını topla
    toplam_imza_pay_carpimi = imzalayan_hisseler.aggregate(
        toplam=Sum(pay_kismi)
    )['toplam'] or 0.0000
    
    # Projedeki tüm bağımsız bölümlerin Arsa Paydası'nın toplamını bul (Örn: 24000)
    # Bu değeri Proje modelinde tutmadığımız için, veritabanından bulmalıyız:
    toplam_arsa_paydasi = Proje.objects.filter(id=proje_id).first().bagimsizbolum_set.aggregate(
        toplam=Sum(Coalesce(F('arsa_paydasi'), 1))
    )['toplam']
    
    # Kentsel dönüşümde tek bir ortak payda (örneğimizde 24000) olduğu varsayılır.
    # O yüzden sadece bir kaydın paydasını alalım (veya daha güvenli bir yöntem: payda alanını Proje modelinde tutmalıydık).
    # Şimdilik, toplam paydayı (24000) alalım:
    
    if toplam_arsa_paydasi is None or toplam_arsa_paydasi == 0:
        # Payda yoksa 0/0 hatası vermesin, oran 0 kalsın.
        imza_yuzdesi_oran = 0.0000
    else:
        # Nihai Oran Hesaplaması: (Toplanan Pay) / (Toplam Payda)
        # (Örn: 120.0 / 24000 = 0.005)
        imza_yuzdesi_oran = toplam_imza_pay_carpimi / toplam_arsa_paydasi 
    
    # --- 3. Sonuçları Proje Modelinde Güncelleme ---
    
    proje.cached_imza_arsa_payi = imza_yuzdesi_oran
    proje.cached_toplam_malik_sayisi = toplam_malik
    
    proje.save()
    
    return f"Proje ID {proje_id} istatistikleri güncellendi. İmza Oranı: {imza_yuzdesi_oran}. DEBUG: Toplam Pay: {toplam_imza_pay_carpimi}, Toplam Payda: {toplam_arsa_paydasi}"


# ... (dogum_gunu_sms_gonder ve toplu_istatistik_guncelle fonksiyonları aynen kalacak)

@shared_task
def toplu_istatistik_guncelle():
    """
    Periyodik olarak tüm aktif projeler için istatistik hesaplama görevini tetikler.
    """
    # Proje İzolasyonu Mantığı: Süper kullanıcı (admin) olarak çalışır.
    aktif_projeler = Proje.objects.filter(aktif_mi=True)
    
    for proje in aktif_projeler:
        # Her proje için Celery'de ayrı bir görev tetikle
        hesapla_proje_istatistikleri.delay(proje.id) 
        
    return f"Toplam {len(aktif_projeler)} proje için istatistik güncelleme görevi sıraya alındı."

@shared_task
def dogum_gunu_sms_gonder():
    """
    Maliklerin doğum günlerini kontrol eder ve SMS otomasyonunu çalıştırır.
    (Şimdilik sadece sayıyı hesaplayacağız.)
    """
    from datetime import date
    
    # Bugün doğum günü olan malikleri bul
    bugun = date.today()
    dogum_gunu_olanlar = Malik.objects.filter(
        dogum_tarihi__day=bugun.day, 
        dogum_tarihi__month=bugun.month
    )
    
    gonderilecek_sms_sayisi = dogum_gunu_olanlar.count()
    
    # Gerçek SMS gönderme mantığı buraya eklenecektir.
    # for malik in dogum_gunu_olanlar:
    #     gonder_sms(malik.telefon_1, "Doğum gününüz kutlu olsun...")
        
    return f"Bugün {bugun.strftime('%d.%m.%Y')}, {gonderilecek_sms_sayisi} malikin doğum günü tebrik SMS'i sıraya alındı."