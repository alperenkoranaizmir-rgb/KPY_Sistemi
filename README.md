Elbette. Bu, üzerinde çalıştığımız tüm notların, gereksinimlerin ve stratejik hedeflerin bir birleşimidir.

Bu belge, hem bir **Kentsel Dönüşüm Uzmanının** sahadaki ihtiyaçlarını hem de bir **Yazılım Mühendisinin** bu ihtiyaçları karşılayacak teknik mimarisini birleştiren tam kapsamlı bir proje planıdır.

Aşağıdaki planı doğrudan bir `.md` (Markdown) dosyasına kopyalayabilirsiniz.

---

# Proje Adı: KentselProjeYonetim (KPY) Sistemi - Kapsamlı Proje ve Mimari Planı

**Tarih:** 29 Ekim 2025
**Hazırlayan:** Gemini (AI Asistanı)
**Talep Sahibi:** (Kullanıcı)

## 1. PROJE HEDEFLERİ VE FELSEFESİ

**Ana Problem:** Şirketin birden fazla lokasyonda (uzak ofisler) yürüttüğü kentsel dönüşüm projelerinde yaşanan operasyonel zorluklar. Başlıca sorunlar; evrak (sözleşme, tapu) kayıpları, malik bilgilerinin dağınık ve ulaşılamaz olması, projelerin gidişatının (ilerleme, maliyet, malik ikna durumu) anlık olarak takip edilememesi ve personel zimmetlerinin bilinememesidir.

**Sistemin Felsefesi:** KPY, bir veri depolama aracı değil, bir **Karar Destek ve Operasyon Yönetim** sistemi olacaktır. Sistemin temel amacı, tüm projelerin yasal, finansal ve sosyal (malik) ilerlemesini tek bir ekrandan yönetilebilir hale getirmek, evrak kayıplarını sıfıra indirmek ve sahadaki ekibin verimliliğini artırmaktır.

**Temel İlkeler:**
1.  **Veri Bütünlüğü:** Her veri (evrak, malik, maliyet) mutlaka bir projeye ait olacaktır.
2.  **Mutlak Güvenlik:** Proje verileri tamamen izole edilecektir. `Proje A` ekibi, `Proje B`'nin varlığından bile haberdar olmayacaktır.
3.  **Kullanıcı Odaklılık:** Arayüz, en az teknik bilgiye sahip saha personelinin bile rahatça kullanabileceği (AdminLTE 3) şekilde tasarlanacaktır.
4.  **Proaktif İletişim:** Sistem, pasif bir kayıt tutucu değil, otomatik SMS ve bildirimlerle (örn: doğum günü, toplantı daveti) malik ilişkilerini aktif olarak yönetecektir.

---

## 2. TEKNİK MİMARİ VE TEKNOLOJİ YIĞINI (TECH STACK)

* **Programlama Dili:** Python 3.10+
* **Web Framework:** Django 4.x
* **Veritabanı:** MySQL 8.x
* **Arayüz (UI):** AdminLTE 3 (django-adminlte3 kütüphanesi ile entegre)
* **Asenkron Görevler:** Celery & Redis (Otomatik SMS gönderimi, OCR işlemleri gibi arka plan görevleri için)
* **Arama (İsteğe bağlı):** Elasticsearch veya Django-Haystack (Büyük ölçekli OCR aramaları için)
* **Dağıtım (Deployment):** Nginx (Web Server), Gunicorn (Application Server), Docker (Konteynerleştirme için önerilir)

---

## 3. VERİTABANI MİMARİSİ FELSEFESİ (Django Modelleri)

Sistemin temeli **"Proje"** modeline dayanır. Diğer tüm ana modeller, `Proje` modeline zorunlu bir `ForeignKey` (İlişki) ile bağlanacaktır.

1.  `Proje`: Sistemin ana konteynerı.
2.  `Malik`: Kişinin iletişim bilgileri (DoB, Telefon vb.).
3.  `BagimsizBolum`: Mülkün bilgileri (Ada, Parsel, m2).
4.  `Hisse`: **En kritik tablo.** `Malik` ve `BagimsizBolum`'ü birbirine bağlar. Bir malikin bir mülkteki hissesini, tapu bilgilerini (Pafta, No) saklar.
5.  `Evrak`: Yüklenen dosya. `Proje`'ye (zorunlu), `Malik`'e (opsiyonel), `Taşeron`'a (opsiyonel) bağlanır.
6.  `GorusmeKaydi`: Saha temsilcisinin malik ile yaptığı görüşmenin özeti.
7.  `Maliyet`: Projeye ait bir gider kaydı.
8.  `Demirbas`: Şirket envanteri (Laptop, Telefon).
9.  `Zimmet`: `Demirbas` ile `Kullanici`'yı (Personel) birbirine bağlayan tablo.

---

## 4. ANA MENÜ YAPISI VE İŞLEVSEL KAPSAM

Aşağıda, sistemin AdminLTE 3 arayüzündeki tam menü yapısı ve her bir menünün işlevi (aksiyonu) ve sonucu (çıktısı) detaylandırılmıştır.

### 1. ANA PANEL (Dashboard)

* **Ne İşe Yarar?** Kullanıcının sisteme ilk girdiğinde gördüğü özet ekrandır. Kullanıcıyı yönlendirir.
* **Alt Menüler / Bileşenler:**
    * **Genel Bakış Widget'ları:** Yetkili olduğu projelerdeki toplam malik sayısı, toplam imza oranı ($${ \% }$$), bekleyen görevler.
    * **Bana Atanan Görevler:** Kullanıcıya atanmış (örn: "X Malikini Ara") görevlerin listesi.
    * **Kritik Uyarılar:** (Örn: "Y Projesi bütçesi $${ \% }90$$'a ulaştı", "Z Malikinin tebligat süresi doluyor").
    * **Yaklaşan Otomasyonlar:** (Örn: "Bugün 5 malikin doğum günü (SMS Gönderilecek)").
* **Aksiyon:** Kullanıcı bu ekrana bakar.
* **Sonuç:** Günlük önceliklerini belirler ve anormallikleri anında fark eder.

### 2. PROJELER

* **Ne İşe Yarar?** Tüm kentsel dönüşüm operasyonlarını birbirinden bağımsız "konteyner"lar halinde yönetir.
* **Alt Menüler:**
    * **Tüm Projeler (Liste/Harita):** Yetkili olunan tüm projelerin listesi veya harita üzerinde gösterimi.
    * **Yeni Proje Oluştur:** Yeni bir proje kartı (adı, konumu, ada/parsel bilgileri, proje müdürü ataması) oluşturma sihirbazı.
* **Aksiyon:** Yönetici, "Yeni Proje Oluştur" der ve `Proje A`'yı tanımlar.
* **Sonuç:** `Proje A` için sistemde izole bir çalışma alanı oluşturulur. Diğer tüm modüllerde artık `Proje A` seçilebilir hale gelir.

### 3. HUKUK & MALİK YÖNETİMİ (CRM)

* **Ne İşe Yarar?** Kentsel dönüşümün kalbidir. Tüm malik, mülk ve hisse bilgilerini yönetir. İkna sürecini takip eder.
* **Alt Menüler:**
    * **Malik Veritabanı:** Maliklerin (kişilerin) eklendiği, arandığı ve listelendiği yer.
        * **Aksiyon:** "Yeni Malik Ekle" butonuna basılır. Form (Ad, Soyad, TCKN, Telefon, **Doğum Tarihi**) doldurulur.
        * **Sonuç:** Malik, seçilen projeye kaydedilir. SMS otomasyonu için hazır hale gelir.
    * **Mülk & Parsel Yönetimi:** Projeye ait `Ada`, `Parsel` ve `Bağımsız Bölüm` (daire, dükkan) kayıtlarının yapıldığı yer.
    * **Hisse Yönetimi (Tapu Kaydı):**
        * **Aksiyon:** "Yeni Hisse Kaydı" seçilir. `Malik` seçilir, `Bağımsız Bölüm` seçilir, hisse $${ \% }$$'si ve tapu bilgileri (pafta no, tapu tarihi vb.) girilir.
        * **Sonuç:** Malik ve mülk arasındaki resmi bağ (hissedarlık) kurulur. $${2 \over 3}$$ hesaplamaları için veri hazır olur.
    * **Paydaş Analizi ($${2 \over 3}$$ Takibi):**
        * **Aksiyon:** Proje seçilir ve rapora girilir.
        * **Sonuç:** Anlık olarak o projede "Arsa Payı" ve "Malik Sayısı" bazında imza $${ \% }$$'sini gösteren bir gösterge paneli çıkar. (Örn: "$${ \% }$$55 - Hedef $${ \% }66.7$").
    * **Görüşme & Toplantı Kayıtları:**
        * **Aksiyon:** Saha temsilcisi, malik görüşmesi sonrası bu forma girer (Görüşülen malik, tarih, özet, sonuç: Olumlu/Olumsuz/Kararsız).
        * **Sonuç:** Malik kartında bir "aktivite akışı" oluşur. Çakışan temsilci raporları için veri sağlanır.
    * **Hukuki Süreç Takibi:** Maliklerin "Anlaşma Engeli" (örn: Fiyat), "Hukuki Durum" (örn: Veraset İlamı Bekleniyor) gibi özel durumlarının takip edildiği listeler.

### 4. SAHA & İŞ YÖNETİMİ

* **Ne İşe Yarar?** Projenin fiziksel inşaat ve saha operasyonlarının takibini yapar.
* **Alt Menüler:**
    * **İş Takvimi (Gantt):** Projenin ana aşamalarının (Yıkım, Hafriyat, Kaba İnşaat) takvime işlendiği yer.
    * **Tahliye & Yıkım Takibi:** Bağımsız bölüm bazlı kontrol listesi (Elektrik kesildi mi? Tahliye edildi mi?).
    * **Günlük Saha Raporları:**
        * **Aksiyon:** Şantiye şefi, gün sonunda kısa bir rapor (çalışan sayısı) girer ve sahadan 2-3 fotoğraf yükler.
        * **Sonuç:** Proje ilerlemesi, merkeze görsel kanıtla birlikte raporlanır.
    * **Taşeron Yönetimi:** Projede çalışan alt yüklenicilerin kayıtları ve sözleşmeleri (Arşiv ile ilişkili).

### 5. BÜTÇE & MALİYET

* **Ne İşe Yarar?** Muhasebe programı karmaşıklığında *olmayan*, proje bazlı basit maliyet kontrolü yapar.
* **Alt Menüler:**
    * **Proje Bütçesi:** Projenin ana kalemlerdeki (Hafriyat, Beton, Hukuk Masrafı) planlanan bütçesi.
    * **Maliyet Girişi:**
        * **Aksiyon:** "Yeni Gider Ekle" seçilir. Proje seçilir, maliyet kalemi (örn: "Kira Yardımı") seçilir, tutar girilir.
        * **Sonuç:** Girilen tutar, o projenin "Harcanan" hanesine anında yansır.
    * **Bütçe vs. Fiili Raporu:** Planlanan bütçe ile girilen maliyetlerin karşılaştırıldığı özet ekran.

### 6. DİJİTAL ARŞİV (DMS)

* **Ne İşe Yarar?** Tüm evrak kayıplarını önler. Şirketin kurumsal hafızasıdır.
* **Alt Menüler:**
    * **İlişkisel Evrak Yükle:**
        * **Aksiyon:** Kullanıcı "Yükle" butonuna basar. Dosyayı seçer. Sistem zorunlu olarak sorar: "Hangi Proje?", "Evrak Tipi Nedir? (Tapu, Sözleşme, Ruhsat vb.)". Opsiyonel olarak sorar: "Hangi Malik ile İlgili?".
        * **Sonuç:** Evrak, doğru proje ve malik ile etiketlenerek sisteme kaydedilir. Asla kaybolmaz.
    * **Proje Arşivleri:** Klasör yapısı şeklinde, proje bazlı tüm evrakların gösterimi.
    * **Genel Kurumsal Arşiv:** Projelerle ilgisi olmayan (örn: Ofis kira sözleşmesi, personel yönetmelikleri) firma evraklarının arşivi.
    * **Akıllı Arama (OCR):**
        * **Aksiyon:** Arama kutusuna "Ahmet Yılmaz" veya taranmış bir sözleşmedeki "vekalet" kelimesi yazılır.
        * **Sonuç:** Sistem, OCR ile taradığı PDF'ler dahil, o kelimenin geçtiği tüm belgeleri bulur.

### 7. İLETİŞİM & BİLDİRİMLER

* **Ne İşe Yarar?** Malikler ve personel ile proaktif iletişimi sağlar.
* **Alt Menüler:**
    * **Toplu SMS / E-Posta Gönderimi:**
        * **Aksiyon:** Kullanıcı sihirbazı açar. 1. Kime? (Filtre: "Proje A'daki İmzalamayan Malikler"). 2. Mesaj? (Şablon: "Toplantı Daveti"). 3. "Gönder".
        * **Sonuç:** Hedef kitleye toplu bilgilendirme yapılır.
    * **Otomasyon Yönetimi:**
        * **Aksiyon:** Yönetici, "Doğum Günü Kutlama SMS" otomasyonunu "Aktif" hale getirir.
        * **Sonuç:** Celery/Redis altyapısı, her gün otomatik olarak `Malik` tablosunu kontrol eder ve doğum günü olanlara SMS gönderir.
    * **Gönderim Raporları:** Gönderilen SMS/e-postaların "Ulaştı", "Başarısız" durumlarının takibi.

### 8. ANALİZ & RAPORLAR

* **Ne İşe Yarar?** Girilen tüm verileri, yönetimin "stratejik kararlar" alabilmesi için anlamlı istatistiklere dönüştürür.
* **Alt Menüler:**
    * **Saha Ekibi Aktivite Raporu:**
        * **Aksiyon:** Rapor çalıştırılır.
        * **Sonuç:** Hangi temsilcinin kaç görüşme yaptığı ve **"Çakışan Görüşmeler"** (örn: aynı malikle 3 gün arayla iki farklı temsilcinin görüşmesi) listelenir.
    * **Malik Direnç Analizi (Stratejik Rapor):**
        * **Aksiyon:** Rapor açılır.
        * **Sonuç:** Proje bazında "Anlaşmama Nedenleri"nin grafiği çıkar (Örn: $${ \% }40$$Fiyat,$${ \% }20$$Veraset Sorunu,$${ \% }15$$ Daire Beğenmedi). Yönetim, ikna stratejisini bu veriye göre belirler.
    * **Hukuki Engel Raporu:** Tüm projelerdeki "Veraset İlamı Beklenen", "İpotekli" vb. hukuki sorunu olan maliklerin listesi.
    * **Proje İlerleme Hunisi (Funnel):** Proje bazında (Toplam Malik $\rightarrow$ Görüşülen $\rightarrow$ Olumlu Bakan $\rightarrow$ İmzalayan) akışını gösterir.

### 9. SİSTEM YÖNETİMİ

* **Ne İşe Yarar?** Sistemin ayarlarının, kullanıcılarının ve envanterinin yönetildiği yer.
* **Alt Menüler:**
    * **Kullanıcı & Rol Yönetimi:** Personel (kullanıcı) hesaplarının oluşturulduğu ve "Rol" (Saha Temsilcisi, Proje Müdürü vb.) atandığı yer.
    * **Proje Bazlı Yetkilendirme:**
        * **Aksiyon:** Yönetici, "Ali" kullanıcısını seçer ve "Proje A" ile "Proje C"ye yetki verir.
        * **Sonuç:** "Ali", sisteme girdiğinde *sadece* Proje A ve C'yi görür.
    * **Demirbaş & Zimmet Yönetimi:**
        * **Aksiyon:** "Yeni Demirbaş" (örn: "Laptop X, Seri No: 123") eklenir. Ardından "Zimmetle" butonu ile "Veli" personeline atanır.
        * **Sonuç:** Hangi personelde hangi şirkete ait cihazın olduğu dijital olarak takip edilir.
    * **Sistem Tanımlamaları:** (Evrak Tipleri, Maliyet Kalemleri, Anlaşma Engel Nedenleri gibi) açılır menülerin içeriklerinin yönetildiği yer.

---

## 5. ÇALIŞMA PLANI (GELİŞTİRME YOL HARİTASI)

**Faz 1: Çekirdek ve Altyapı (Sprint 1-2)**
1.  Proje kurulumu (Django, MySQL, AdminLTE entegrasyonu).
2.  `Kullanici` (Personel) modelinin özelleştirilmesi.
3.  `Proje` modelinin oluşturulması.
4.  Çekirdek "Proje Bazlı Yetkilendirme" mantığının (Permissions) oturtulması.
5.  `Sistem Yönetimi` modülünün temel (Kullanıcı ekleme, Proje atama) fonksiyonlarının yapılması.
* **Çıktı:** Kullanıcılar sisteme giriş yapabilir, proje oluşturabilir ve sadece yetkili oldukları projeleri görebilirler.

**Faz 2: Kentsel Dönüşüm Çekirdeği (Sprint 3-5)**
1.  `Hukuk & Malik Yönetimi` modülünün modellenmesi: `Malik`, `BagimsizBolum`, `Hisse` tabloları.
2.  Malik, Mülk ve Hisse ekleme/listeleme arayüzlerinin (AdminLTE) yapılması.
3.  `Dijital Arşiv (DMS)` modülünün temel fonksiyonları: "İlişkisel Evrak Yükleme" ve "Proje Arşivi" görünümü.
* **Çıktı:** Bir projeye malikler, mülkler ve bu ikisini bağlayan hisseler eklenebilir. Bu maliklere ait sözleşme, tapu vb. evraklar sisteme yüklenebilir.

**Faz 3: Operasyon ve Zeka (Sprint 6-8)**
1.  `Görüşme Kayıtları` ve `Hukuki Süreç Takibi` (Malik modülüne ek).
2.  `Paydaş Analizi ($${2 \over 3}$$ Takibi)` raporunun geliştirilmesi.
3.  `İletişim & Bildirimler` modülü (Toplu SMS/E-posta) ve `Celery` altyapısı (Doğum günü otomasyonu).
4.  `Analiz & Raporlar` modülünün geliştirilmesi (Özellikle Malik Direnç Analizi ve Çakışan Temsilci Raporları).
* **Çıktı:** Sistem artık "akıllı" hale gelir. Raporlar üretir, ikna süreçlerini analiz eder ve otomatik iletişim kurar.

**Faz 4: Saha ve Ek Fonksiyonlar (Sprint 9-10)**
1.  `Saha & İş Yönetimi` modülü (Günlük Rapor, Fotoğraf Yükleme).
2.  `Bütçe & Maliyet` modülü (Basit bütçe-maliyet takibi).
3.  `Demirbaş & Zimmet` modülü.
4.  DMS modülüne `Genel Kurumsal Arşiv` ve `Akıllı Arama (OCR)` özelliklerinin eklenmesi.
* **Çıktı:** Saha operasyonları ve ofis içi envanter de sisteme dahil edilir.

**Faz 5: Test, Geri Bildirim ve Dağıtım (Sprint 11-12)**
1.  Tüm modüllerin entegrasyon testi.
2.  Saha ekibinden seçilen pilot kullanıcılarla "Kullanıcı Kabul Testleri (UAT)".
3.  Geri bildirimlere göre düzeltmeler.
4.  Canlı (Production) sunucuya dağıtım (Deployment).
