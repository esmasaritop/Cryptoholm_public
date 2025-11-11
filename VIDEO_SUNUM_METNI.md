# 🎬 VIDEO SUNUM METNİ
## EV Charging SOC Manipulation Attack Simulation

---

## 🎤 BÖLÜM 1: TANITIM (0:00 - 0:30)

### Açılış
"Merhaba, ben **Yağız Enes DOĞAN**, **Ekip 4** üyesiyim. Bugün sizlere elektrikli araç şarj sistemlerindeki kritik bir güvenlik açığını ve bu açığa karşı geliştirdiğimiz simülasyon platformunu tanıtacağım."

---

## 📋 BÖLÜM 2: PROJE TANITIMI (0:30 - 3:00)

### Proje İsmi ve Amacı
"Projenin adı **'EV Charging SOC Manipulation Attack Simulation'** - yani Elektrikli Araç Şarj İstasyonu SOC Manipülasyonu Saldırı Simülasyonu.

Bu proje, elektrikli araç şarj istasyonları ile araç arasındaki iletişimde gerçekleşebilecek **siber saldırıları** simüle eden ve bu saldırılara karşı **güvenlik çözümlerini** gösteren kapsamlı bir eğitim ve araştırma platformudur."

### Problem: Neden Bu Proje Önemli?
"Elektrikli araç pazarı her geçen gün büyüyor. 2025 yılında global EV pazarının 800 milyar doları aşması bekleniyor. Ancak bu hızlı büyüme beraberinde **ciddi güvenlik risklerini** de getiriyor.

Şarj istasyonları ile araçlar arasında **OCPP** - Open Charge Point Protocol - ile iletişim kuruluyor. Ancak bu iletişim kanalı yeterli güvenlik önlemleri alınmadığında **manipülasyona açık** hale geliyor."

### Saldırı Senaryosu
"Haydi senaryo üzerinden gidelim:

**Normal Durum:** Aracınızın bataryası %30 dolulukta. Şarj istasyonuna bağlanıyorsunuz ve şarj başlıyor. Batarya %95'e ulaştığında BMS - Battery Management System - şarjı güvenli bir şekilde durduruyor.

**Saldırı Durumu:** Ancak bir saldırgan, araç ile istasyon arasına girerek - yani **Man-in-the-Middle** saldırısı yaparak - SOC değerlerini manipüle ediyor. Bataryanız gerçekte %95 dolu olmasına rağmen, istasyona '%30 dolu' mesajı gönderiyor.

**Sonuç:** İstasyon bataryanın az dolu olduğunu sanıyor ve şarja devam ediyor. Bu **aşırı şarj** durumu:
- 🔥 Batarya hücrelerinde yangın ve patlama riskine
- 🌡️ Kritik sıcaklık seviyelerine (60°C+)
- 🔋 Batarya ömrünün ciddi şekilde kısalmasına
- ⚡ Şarj istasyonu ekipmanlarında hasara yol açıyor."

---

## 💻 BÖLÜM 3: TEKNİK MİMARİ (3:00 - 5:00)

### Modüler Yapı
"Projemiz **6 ana modülden** oluşuyor:

**1. BMS Modülü** - Battery Management System
- Gerçekçi batarya simülasyonu
- SOC, voltaj, akım, sıcaklık takibi
- Aşırı şarj ve ısınma tespiti
- Batarya sağlık skoru hesaplama

**2. OCPP Modülü** - İletişim Protokolü
- Şarj istasyonu simülasyonu
- Araç istemcisi implementasyonu
- Mesajlaşma protokolü (StatusNotification, StartTransaction, StopTransaction)

**3. Attack Modülü** - Saldırı Simülasyonları
- SOC Manipulator: SOC değerlerini sahte verilerle değiştirir
- MITM Proxy: Mesajları yakalar ve manipüle eder
- Replay attack, slow poison attack gibi çeşitli saldırı vektörleri

**4. Security Modülü** - Güvenlik Mekanizmaları
- **HMAC-SHA256** ile mesaj bütünlüğü kontrolü
- **RSA-2048** ile dijital imzalama
- Timestamp validation ile replay attack koruması
- Anomali tespiti algoritmaları

**5. CAN Bus Modülü** - Araç İçi İletişim
- CAN bus mesaj simülasyonu
- Sahte mesaj enjeksiyonu
- Batarya durumu broadcast'i

**6. Utils Modülü** - Yardımcı Araçlar
- JSON formatında detaylı loglama
- Real-time matplotlib görselleştirme
- Saldırı zaman çizelgesi ve raporlama"

### Teknoloji Stack
"Proje **Python 3.13.7** ile geliştirildi. Kullanılan başlıca kütüphaneler:
- **cryptography** (46.0.3): Kriptografik işlemler
- **numpy** (2.3.4): Sayısal hesaplamalar
- **matplotlib** (3.10.7): Veri görselleştirme
- **websockets** (15.0.1): Async iletişim
- **pytest** (9.0): Test framework

Toplamda **3,500+ satır kod**, **15+ unit test**, ve **kapsamlı dokümantasyon** içeriyor."

---

## 🎯 BÖLÜM 4: DEMO VE ÖZELLİKLER (5:00 - 7:00)

### İki Farklı Demo
"Projemizde **iki farklı demo** bulunuyor:

**Demo 1: Saldırı Demosu** (demo_attack.py)
- Normal şarj başlatılıyor (%30 SOC)
- 10 saniye normal şarj
- Saldırgan MITM proxy'yi aktive ediyor
- SOC değeri %30'da sabitleniyor
- Gerçek SOC %100'ü aşıyor (aşırı şarj!)
- Sıcaklık 60°C+'ı geçiyor (kritik seviye!)
- Grafik üzerinde gerçek vs sahte SOC karşılaştırması

**Demo 2: Güvenli Sistem Demosu** (demo_secure.py)
- Kriptografik koruma aktif
- Normal güvenli şarj (%30 → %95)
- Saldırgan manipülasyon deniyor
- Sistem **üç katmanlı savunma** ile saldırıyı tespit ediyor:
  1. HMAC doğrulaması başarısız
  2. BMS bağımsız sensör validasyonu uyumsuzluk tespit ediyor
  3. Integrity checker anomali buluyor
- Saldırı başarısız oluyor, sistem güvenli kalıyor"

### Görselleştirme
"Her demo sonunda **detaylı grafikler** oluşturuluyor:
- SOC değişimi (gerçek vs manipüle)
- Batarya sıcaklığı
- Voltaj ve akım değerleri
- Kritik eşik uyarıları
- Saldırı zaman çizelgesi

Ayrıca **JSON log dosyaları** ile tüm olaylar kaydediliyor."

---

## 📊 BÖLÜM 5: SWOT ANALİZİ (7:00 - 9:30)

### Giriş
"Şimdi projenin **SWOT analizine** bakalım. SWOT, bir projenin **Güçlü yönlerini** (Strengths), **Zayıf yönlerini** (Weaknesses), **Fırsatlarını** (Opportunities) ve **Tehditlerini** (Threats) değerlendiren stratejik bir analiz metodudur."

### 💪 STRENGTHS - Güçlü Yönler

"**Teknik Üstünlükler:**
- Gerçekçi BMS, OCPP ve CAN Bus simülasyonları
- Çok katmanlı güvenlik: HMAC-SHA256, RSA-2048, timestamp validation
- Modüler mimari sayesinde kolay genişletilebilir
- 15+ unit test ile %80+ code coverage
- Real-time görselleştirme ve detaylı loglama

**Eğitim Değeri:**
- Hands-on learning: Öğrenciler gerçek saldırıları deneyimliyor
- İki taraflı yaklaşım: Hem saldırı hem savunma mekanizmaları
- Detaylı dokümantasyon: README, QuickStart, Usage Examples
- İnteraktif menü ile kolay kullanım
- Siber güvenlik farkındalığı yaratıyor

**Kod Kalitesi:**
- PEP 8 uyumlu, clean code prensipleri
- Object-oriented programming
- Type hints ve error handling
- Modern Python 3.13.7 kullanımı

**Puanlama:** Genel olarak **4.2/5.0 yıldız** aldık. Özellikle eğitim değeri kategorisinde **5/5 tam puan**."

### ⚠️ WEAKNESSES - Zayıf Yönler

"**Teknik Sınırlamalar:**
- Gerçek donanım yok, tamamen simülasyon bazlı
- Tam OCPP 2.0.1 implementasyonu eksik, sadece temel özellikler var
- Gerçek network layer yok, sadece function call'lar
- Tek araç-tek istasyon, multi-vehicle desteği yok
- Database yok, veriler sadece bellekte

**Kullanıcı Deneyimi:**
- Grafik arayüz (GUI) bulunmuyor, sadece command-line
- Configuration dosyası yok, parametreler kod içinde
- Kurulum manuel, automated installer yok

**Dokümantasyon:**
- API documentation (Sphinx) eksik
- UML ve sequence diagram'lar yok
- Video tutorial bulunmuyor

**Test ve DevOps:**
- CI/CD pipeline kurulu değil
- Performance test ve stress test eksik
- Code coverage target belirtilmemiş

Bu zayıf yönler, projenin **geliştirilmesi gereken alanlarını** gösteriyor."

### 🌟 OPPORTUNITIES - Fırsatlar

"**Pazar Fırsatları:**
- EV pazarı 2025'te **$800 milyar+**, yıllık %20 büyüme
- Cybersecurity eğitim talebi hızla artıyor
- ISO 15118 ve NIST standartları zorunlu hale geliyor
- Üniversiteler için araştırma platformu fırsatı
- Şirketlere siber güvenlik eğitimi satış potansiyeli

**Teknolojik Gelişmeler:**
- **Machine Learning** ile anomali tespiti geliştirilebilir
- **Blockchain** ile charging transaction verification
- **Quantum-safe** kriptografi algoritmaları eklenebilir
- **5G/V2X** vehicle-to-everything communication
- **Cloud integration** ile AWS/Azure IoT Core

**Ürün Geliştirme:**
- Commercial enterprise edition
- Cloud-based SaaS platform
- Mobile app (iOS/Android)
- Gerçek hardware integration
- Plugin architecture ile 3rd party extension

**Eğitim ve Sertifikasyon:**
- Udemy, Coursera'da online kurs
- EV Security Certification programı
- Şirket içi workshop'lar
- CTF (Capture The Flag) yarışmaları
- Üniversite müfredat iş birlikleri

**Araştırma:**
- IEEE, ACM konferanslarında akademik yayınlar
- Gerçek sistemlerde CVE (güvenlik açığı) keşfi
- Open source community sponsorship
- Patent fırsatları

Bu fırsatlar, projenin **ticari ve akademik potansiyelini** gösteriyor."

### 🚨 THREATS - Tehditler

"**Yasal ve Etik Riskler:**
- **Kötüye kullanım riski**: Saldırganlar gerçek sistemlerde kullanabilir
- Zarar durumunda sorumluluk belirsizliği
- Dual-use technology: Hem iyi hem kötü amaçla kullanılabilir
- Bazı ülkelerde security tool yasakları

**Rekabet:**
- Tenable, Nessus gibi ticari security toollar
- Benzer açık kaynak projeler ortaya çıkabilir
- OEM'ler (üreticiler) kendi çözümlerini geliştirebilir
- Teknoloji hızla değişiyor, obsolescence riski

**Teknik Riskler:**
- 3rd party library'lerde güvenlik açıkları
- Python 3.13 adoption rate düşük olabilir
- Platform compatibility sorunları
- Tek geliştirici için maintenance burden
- Breaking changes riski

**Pazar Riskleri:**
- Funding challenges
- Karmaşık kurulum ve öğrenme eğrisi
- Enterprise satış için certification gereksinimleri
- 7/24 destek beklentileri
- Ekonomik durgunluk durumunda eğitim bütçeleri kesilebilir

**Güvenlik ve İtibar:**
- Projenin kendisi hack'lenebilir
- False positive'ler güvenilirliği azaltabilir
- Kötüye kullanım durumunda itibar kaybı
- Düzenleyici kurumların dikkatini çekebilir

Bu tehditler, projenin **risk yönetimi stratejisini** oluştururken dikkate alınmalı."

### 📈 SWOT Değerlendirmesi - Özet

"SWOT analizimizin sonuçlarını özetlersek:

**Mevcut Durum:**
- Güçlü teknik temel ✅
- Yüksek eğitim değeri ✅
- Geliştirilebilir alanlar var ⚠️
- Büyük potansiyel fırsatlar 🚀
- Yönetilebilir riskler ⚡

**Stratejik Pozisyon:**
Bu proje, **niche ama büyüyen bir pazarda** konumlanmış durumda. EV security alanı henüz yeni gelişiyor ve bu projede **first-mover advantage** var.

**Öncelikli Aksiyonlar:**
1. **İlk 30 gün**: Yasal uyarıları güçlendir, CI/CD kur
2. **30-90 gün**: Web-based GUI geliştir, API documentation tamamla
3. **90+ gün**: ML entegrasyonu, commercial edition planla

**Sonuç:**
Doğru stratejik adımlarla **12-18 ay içinde** hem akademik hem ticari başarı potansiyeline sahip bir proje."

---

## 🎓 BÖLÜM 6: EĞİTİM VE ÖĞRENME (9:30 - 10:30)

### Öğrenme Hedefleri
"Bu projeyi tamamlayan birisi şunları öğreniyor:

**Siber Güvenlik:**
- MITM (Man-in-the-Middle) saldırıları
- Veri manipülasyonu teknikleri
- Kriptografik koruma mekanizmaları
- Anomali tespiti metodları
- Defense-in-depth prensibi

**EV Sistemleri:**
- Battery Management System (BMS) çalışma prensibi
- OCPP protokolü ve charging workflow
- CAN bus iletişimi
- Şarj istasyonu mimarisi

**Güvenlik Teknolojileri:**
- HMAC-SHA256 message integrity
- RSA-2048 digital signatures
- Timestamp validation
- Replay attack prevention
- Independent sensor verification

**Python Programlama:**
- Object-oriented programming
- Cryptography libraries
- Test-driven development (pytest)
- Data visualization (matplotlib)
- Async programming (websockets)

Bu, sadece bir simülasyon projesi değil, aynı zamanda **kapsamlı bir eğitim platformu**."

---

## 🛡️ BÖLÜM 7: GÜVENLİK ÇÖZÜMLERİ (10:30 - 11:30)

### Çok Katmanlı Savunma
"Projemizde **defense-in-depth** prensibi uygulandı. Üç ana savunma katmanı var:

**1. Katman - Kriptografik Koruma:**
- Her mesaj HMAC-SHA256 ile imzalanıyor
- RSA-2048 digital signature
- Mesaj manipülasyonu anında tespit ediliyor

**2. Katman - BMS Bağımsız Doğrulama:**
- BMS kendi sensörleriyle SOC'u bağımsız ölçüyor
- Gelen mesaj ile gerçek değeri karşılaştırıyor
- %5'ten fazla sapma varsa alarm veriyor
- Şarj istasyonundan bağımsız karar alabiliyor

**3. Katman - Anomali Tespiti:**
- İstatistiksel analiz ile anormal davranışları tespit ediyor
- Fiziksel tutarlılık kontrolleri
- Rate limiting ile DDoS koruması
- Pattern matching ile bilinen saldırı imzaları

Bu üç katman sayesinde, bir katman aşılsa bile diğer katmanlar sistemi koruyor."

### Gerçek Dünya Uygulamaları
"Bu güvenlik çözümleri, gerçek dünyada şu şekilde uygulanabilir:

**OCPP 2.0.1 Compliance:**
- ISO 15118 standardına uyum
- Mutual TLS authentication
- Certificate-based authentication

**Hardware Security:**
- TPM (Trusted Platform Module) kullanımı
- Secure boot mekanizmaları
- Hardware-backed key storage

**Network Security:**
- VPN tunneling
- Network segmentation
- Intrusion Detection Systems (IDS)

**Monitoring:**
- SIEM (Security Information and Event Management)
- Real-time alerting
- Forensic logging"

---

## 🚀 BÖLÜM 8: SONUÇ VE GELECEK (11:30 - 12:30)

### Proje Başarıları
"Bu proje ile:
- ✅ Kritik bir güvenlik açığını simüle ettik
- ✅ Etkili güvenlik çözümlerini gösterdik
- ✅ Kapsamlı bir eğitim platformu oluşturduk
- ✅ 3,500+ satır temiz, modüler kod yazdık
- ✅ 15+ test ile kod kalitesini garantiledik
- ✅ Detaylı dokümantasyon hazırladık

**Genel Puan: 4.2/5.0** ⭐⭐⭐⭐"

### Gelecek Planları
"İlerleye yönelik planlarımız:

**Kısa Vadede (0-6 ay):**
- CI/CD pipeline kurulumu
- Web-based GUI prototipi
- API documentation tamamlama
- Community building

**Orta Vadede (6-12 ay):**
- Machine Learning entegrasyonu
- Multi-vehicle support
- Database layer
- Security audit

**Uzun Vadede (12+ ay):**
- Commercial enterprise edition
- Gerçek hardware integration
- Cloud SaaS platform
- EV Security Certification programı

Bu projede potansiyel çok büyük. EV pazarı büyüdükçe, güvenlik ihtiyacı da artacak."

### Toplumsal Etki
"Bu proje sadece teknik bir çalışma değil, aynı zamanda **toplumsal bir sorumluluk**.

Elektrikli araçlar, sürdürülebilir geleceğin bir parçası. Ancak bu teknolojilerin **güvenli** olması şart. Bir siber saldırı sonucu:
- İnsan hayatı tehlikeye girebilir
- Milyonlarca dolarlık ekonomik kayıp olabilir
- EV teknolojisine güven sarsılabilir

Bu proje ile:
1. Geliştiricilere **farkındalık** kazandırıyoruz
2. Güvenlik açıklarını **proaktif olarak** tespit ediyoruz
3. Etkili çözümleri **paylaşıyoruz**
4. Yeni nesil **güvenlik uzmanları** yetiştiriyoruz"

### Etik Vurgu
"⚠️ **ÖNEMLİ UYARI:**

Bu proje **sadece eğitim ve araştırma amaçlıdır**. Gerçek sistemlerde izinsiz test yapmak **yasa dışıdır** ve ciddi cezai sorumluluklara yol açabilir.

Bu araçları kullanırken:
- ✅ Sadece test ortamlarında kullanın
- ✅ Yetkili olduğunuz sistemlerde test yapın
- ✅ Responsible disclosure prensibine uyun
- ✅ Etik hacking kurallarına riayet edin

Siber güvenlik, **sorumlu bir meslek**tir. Bilgi ile gelen sorumluluğu unutmayalım."

---

## 🎬 BÖLÜM 9: KAPANIŞ (12:30 - 13:00)

### Demo Çağrısı
"Projeyi canlı olarak görmek isterseniz:

```bash
# Kurulum
pip install -r requirements.txt

# Hızlı başlangıç menüsü
python quickstart.py

# Saldırı demosu
python demos/demo_attack.py

# Güvenli sistem demosu
python demos/demo_secure.py
```

GitHub'da proje açık kaynak olarak paylaşılacak. Katkıda bulunmak isteyen herkes davetlidir!"

### Teşekkür
"Bu projeyi geliştirirken:
- **Ekip 4** arkadaşlarıma destekleri için
- Hocalarımıza rehberlik ettikleri için
- Açık kaynak topluluğuna kütüphaneler için
- Ve sizlere dinlediğiniz için teşekkür ederim.

EV güvenliği, hepimizin sorumluluğu. Birlikte daha güvenli bir gelecek inşa edebiliriz."

### Son Mesaj
"**Yağız Enes DOĞAN**, **Ekip 4** - EV Charging SOC Manipulation Attack Simulation projesi. 

Güvenli şarjlar! ⚡🔒"

---

## 📝 SUNUM İPUÇLARI

### Ses ve Diksiyon
- Sakin ve net konuşun
- Teknik terimleri açıklayın
- Canlı ve enerjik olun
- Göz teması kurun (kameraya bakın)

### Görsel Destek
- Demoları ekran kaydı ile gösterin
- Grafikleri büyük gösterin
- SWOT tablosunu görselleştirin
- Kod örneklerini highlight edin

### Zamanlama
- Her bölüme ayrılan süreleri takip edin
- Toplam süre: 12-13 dakika
- Acele etmeyin, önemli noktalara vurgu yapın
- Soru zamanı için 2-3 dakika ayırın

### Enerji
- Başlangıç ve bitiş güçlü olsun
- SWOT analizinde enerjinizi artırın
- Demo bölümünde heyecan katın
- Etik vurgu bölümünde ciddi olun

### Pratik
- Metni ezberlemek yerine doğal konuşun
- Anahtar kelimeleri vurgulayın
- Kendi kelimelerinizle anlatın
- En az 2-3 kez prova yapın

---

## 🎯 ANAHTAR MESAJLAR

Sunumda mutlaka vurgulanması gerekenler:

1. **Problem ciddi**: EV güvenliği kritik bir konu
2. **Çözüm etkili**: Çok katmanlı savunma çalışıyor
3. **Eğitim değerli**: Hands-on öğrenme fırsatı
4. **Potansiyel büyük**: Ticari ve akademik fırsatlar
5. **Etik önemli**: Sadece eğitim amaçlı kullanım

---

**Başarılar! 🚀 Harika bir sunum olacak!**

