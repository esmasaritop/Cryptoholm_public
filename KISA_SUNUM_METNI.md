# 🎬 KISA VIDEO SUNUM METNİ (3-4 Dakika)
## EV Charging SOC Manipulation Attack Simulation

---

## 🎤 GİRİŞ (30 saniye)

"Merhaba, ben **Yağız Enes DOĞAN**, **Ekip 4** üyesiyim. 

Bugün sizlere elektrikli araç şarj sistemlerindeki kritik bir güvenlik açığını ve geliştirdiğimiz simülasyon platformunu tanıtacağım. Projenin adı: **EV Charging SOC Manipulation Attack Simulation**."

---

## 📋 PROJE VE PROBLEM (1 dakika)

### Problem
"Elektrikli araç pazarı hızla büyüyor - 2025'te 800 milyar doları aşması bekleniyor. Ancak bu büyüme beraberinde **ciddi güvenlik risklerini** getiriyor.

Şarj istasyonları ile araçlar **OCPP protokolü** ile iletişim kuruyor. Ancak bu iletişim **manipülasyona açık**.

### Saldırı Senaryosu
Bir saldırgan, araç ile istasyon arasına girerek - **Man-in-the-Middle saldırısı** yaparak - bataryanın doluluk oranını manipüle ediyor. 

**Normal:** Batarya %95 dolu → Şarj duruyor  
**Saldırı:** Gerçekte %95 ama istasyona '%30 dolu' gösteriyor → Şarj devam ediyor → **AŞIRI ŞARJ!**

**Sonuç:** Yangın riski, batarya hasarı, ekipman arızası."

---

## 💻 TEKNİK DETAYLAR (45 saniye)

"Projemiz **6 ana modülden** oluşuyor:

1. **BMS** - Batarya yönetim sistemi simülasyonu
2. **OCPP** - İstasyon-araç iletişim protokolü  
3. **Attack** - SOC manipülasyonu ve MITM proxy
4. **Security** - HMAC-SHA256, RSA-2048 ile kriptografik koruma
5. **CAN Bus** - Araç içi iletişim simülasyonu
6. **Utils** - Loglama ve görselleştirme

**3,500+ satır Python kodu**, **15+ test**, modern kütüphaneler ile geliştirildi."

---

## 📊 SWOT ANALİZİ (1.5 dakika)

### Güçlü Yönler (20 saniye)
"**Güçlü yönlerimiz:**
- Gerçekçi BMS, OCPP ve CAN Bus simülasyonları
- Çok katmanlı güvenlik: HMAC, RSA, anomali tespiti
- Hem saldırı hem savunma mekanizmalarını gösteriyor
- Yüksek eğitim değeri - hands-on öğrenme
- Modüler, genişletilebilir mimari

**Genel puan: 4.2/5.0** - özellikle eğitim değeri kategorisinde tam puan aldık."

### Zayıf Yönler (15 saniye)
"**Geliştirilebilir alanlar:**
- Grafik arayüz (GUI) bulunmuyor
- Gerçek donanım desteği yok, tamamen simülasyon
- CI/CD pipeline kurulu değil
- Multi-vehicle desteği sınırlı"

### Fırsatlar (20 saniye)
"**Büyük fırsatlar var:**
- EV pazarı yılda %20 büyüyor
- Cybersecurity eğitim talebi artıyor
- ISO 15118 standartları zorunlu hale geliyor
- Machine Learning entegrasyonu potansiyeli
- Commercial SaaS platform ve sertifikasyon programı fırsatları

Bu, sadece akademik bir proje değil - **ticari potansiyeli** de çok yüksek."

### Tehditler (15 saniye)
"**Riskler de var:**
- Kötüye kullanım riski - bu yüzden güçlü yasal uyarılar koyduk
- Ticari rakipler ve teknoloji değişim hızı
- Funding ve maintenance zorlukları

Ancak bu riskler **yönetilebilir** ve projenin değerini azaltmıyor."

### Stratejik Yol Haritası (20 saniye)
"**İleriye dönük planlarımız:**

**Kısa vadede:** CI/CD kurulumu, web-based GUI prototipi  
**Orta vadede:** Machine Learning entegrasyonu, database layer  
**Uzun vadede:** Enterprise edition, gerçek hardware entegrasyonu, cloud platform

12-18 ay içinde hem akademik hem ticari başarı hedefliyoruz."

---

## 🛡️ GÜVENLİK ÇÖZÜMLERİ (30 saniye)

"Projemizde **3 katmanlı savunma** var:

**1. Katman:** Kriptografik koruma - Her mesaj HMAC-SHA256 ile imzalanıyor  
**2. Katman:** BMS bağımsız doğrulama - Kendi sensörleriyle ölçüm yapıyor  
**3. Katman:** Anomali tespiti - İstatistiksel analiz ve pattern matching

Bir katman aşılsa bile, diğer katmanlar sistemi koruyor. Bu **defense-in-depth** prensibi."

---

## 🚀 SONUÇ VE ETİK VURGU (30 saniye)

"Bu proje ile:
- ✅ Kritik bir güvenlik açığını görünür kıldık
- ✅ Etkili çözümler gösterdik  
- ✅ Kapsamlı bir eğitim platformu oluşturduk

**Önemli:** Bu proje **sadece eğitim ve araştırma amaçlıdır**. Gerçek sistemlerde izinsiz test yapmak yasa dışıdır.

EV güvenliği hepimizin sorumluluğu. Birlikte daha güvenli bir gelecek inşa edebiliriz.

**Yağız Enes DOĞAN - Ekip 4**

Teşekkürler! Güvenli şarjlar! ⚡🔒"

---

## ⏱️ ZAMAN DAĞILIMI

| Bölüm | Süre |
|-------|------|
| Giriş | 30 saniye |
| Proje ve Problem | 1 dakika |
| Teknik Detaylar | 45 saniye |
| **SWOT Analizi** | **1.5 dakika** |
| Güvenlik Çözümleri | 30 saniye |
| Sonuç ve Etik | 30 saniye |
| **TOPLAM** | **~4 dakika** |

---

## 💡 SUNUM İPUÇLARI

### Enerji Noktaları
- 🔥 SWOT fırsatlar bölümünde enerjini artır
- ⚠️ Etik vurgu bölümünde ciddi ol
- 🎯 Sayıları net vurgula: 800 milyar, 4.2/5.0, %20 büyüme

### Vurgulanacak Kelimeler
- **Man-in-the-Middle**
- **AŞIRI ŞARJ**
- **3 katmanlı savunma**
- **4.2/5.0**
- **Eğitim amaçlı**

### Görsel Destek
- SWOT tablosunu göster
- Demo video klipleri ekle (5-10 saniye)
- Grafikleri vurgula

---

## 📝 EK NOTLAR

Bu metin **3-4 dakikalık** konuşma için optimize edilmiştir. Eğer daha fazla zaman varsa:
- Demo detaylarını ekleyebilirsiniz
- Toplumsal etki bölümünü genişletebilirsiniz
- Soru-cevap için zaman ayırabilirsiniz

**Pratik Önerisi:** 
- Metni 2-3 kez sesli oku
- Zamanlama yap
- Kendi kelimelerinle söyle (ezber değil!)
- Doğal ve samimi ol

**Başarılar! 🚀**

