# Yetkisiz Log Dosyası Sızıntısı (Gizlilik İhlali)

**🚨 Uyarı:** Bu depo eğitim ve araştırma amaçlıdır. Gerçek dünyadaki sistemlere veya üçüncü taraf ağlara karşı kullanılmamalıdır. Yanlış veya yetkisiz kullanım yasal sorumluluk doğurur.

---

## 🚗 Proje Özeti — "Log Leak Simulator for EVSE"
Bu proje, **Elektrikli Araç Şarj Sistemleri (EVSE)** ve CAN tabanlı iletişim ortamlarında ortaya çıkabilecek **yetkisiz log sızıntıları, mesaj enjeksiyonu ve ağ manipülasyonu** gibi güvenlik olaylarını simüle eden Python tabanlı modüllerden oluşur. Amaç: araştırma, eğitim ve güvenlik testleri için tekrarlanabilir senaryolar sunmak.

**Kapsanan Temalar**
- CAN trafiği üretimi ve sniffing (dinleme)
- Kontrol mesajlarının takibi (RemoteStart/RemoteStop gibi)
- Yetkisiz erişim / saldırı senaryoları ve log sızıntısı simülasyonu
- Temel forensik kurtarma senaryoları

---

## 📋 İçindekiler
- Genel Bakış
- Anomali / Saldırı Senaryoları ve Çözümleri (modül bazlı)
- Kurulum
- Kullanım
- Modül Yapısı & Açıklamalar
- Teknik Detaylar
- Kaynaklar
- Katkıda Bulunma ve Lisans
- İletişim ve Sorumluluk Reddi

---

## 🎯 Genel Bakış (Neden?)
Gerçek EVSE ortamları, araçlar ve merkez sunucular arasında düşük seviyeli CAN mesajları ile iletişim kurar. Bu mesajlar gizli bilgiler, komutlar ve loglar içerir. Bu projeyle amaçlananlar:
- Tipik saldırı yüzeylerini göstermek,
- Güvenlik araştırmacıları için tekrarlanabilir test ortamı sunmak,
- Adli bilişim çalışmalarını taklit ederek veri kurtarma ve analiz stratejileri geliştirmek.

---

## 🔍 Anomali / Saldırı Senaryoları ve Örnek Çözümler (Dosya bazlı)

### Anomali A — Sürekli Arka Plan Trafiği + Bilgi Sızıntısı (`changer_simulator.py`)
**Problem:** Cihazlar sürekli sensör verisi gönderir; yetkisiz erişim halinde bu loglar toplanıp dışarı sızdırılabilir.  
**Simülasyon:** `changer_simulator.py` periyodik CAN mesajları üretir (ör. voltaj, akım, sıcaklık).  
**Çözüm Önerisi:** Trafik şifreleme, mesajların anonimleştirilmesi, yerel log kırpma/rotasyonu, güvenli log aktarımı (TLS).

### Anomali B — Kontrol Noktasından Gelen Komutların İstismarı (`cp_simulator.py`)
**Problem:** CP'den gelen `RemoteStart/RemoteStop` gibi komutlar kötü amaçlı kullanılabilir veya taklit edilebilir.  
**Simülasyon:** `cp_simulator.py` CP davranışını ve komut gönderimini taklit eder.  
**Çözüm Önerisi:** Dijital imza doğrulama, replay attack koruması (nonce/timestamp), erişim kontrolü.

### Anomali C — Merkezi Sunucu ve Log Konsolidasyonu (`csms_simulator.py`)
**Problem:** Merkezi sunucuda toplanan loglar tek noktadan ihlal edilirse büyük veri sızıntıları olur.  
**Simülasyon:** `csms_simulator.py` CSMS ile veri alışverişini taklit eder.  
**Çözüm Önerisi:** Roll-based erişim, log bölümleme, off-chain hassas veri depolama, ZKP/şifreleme ile sorgulama.

### Anomali D — Aktif Saldırı/Sızıntı Senaryosu (`saldırı_simulator.py`)
**Problem:** Kötü niyetli aktörlerin sahte mesaj enjekte etmesi, log toplama veya veri dışa aktarımı.  
**Simülasyon:** `saldırı_simulator.py` saldırgan davranışlarını ve veri sızıntısını canlandırır.  
**Çözüm Önerisi:** Intrusion Detection System (IDS) kuralları, anomaly detection (istatistiksel/ML), imza tabanlı filtreleme.

---

## 💻 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- `python-can` kütüphanesi

`requirements.txt` oluşturmak için (örnek):
```
python-can>=4.0.0
pycryptodome>=3.14.0
numpy
```
Kurulum:
```bash
pip install -r requirements.txt
```

### Linux — Sanal CAN Arayüzü (vcan) kurulum önerisi
```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

> Windows kullanıcıları için `python-can`'in virtual veya SocketCAN benzeri backend seçenekleri araştırılmalıdır.

---

## 🧭 Kullanım

Projeyi çalıştırmak için her modülü ayrı terminalde başlatabilirsiniz:

```bash
# Örnek sıralı çalışma
python changer_simulator.py   # Arka plan CAN trafiği üretir
python cp_simulator.py        # CP komutlarını gönderir
python csms_simulator.py      # Merkezi sunucu iletişimi simüle eder
python saldırı_simulator.py   # Saldırı senaryosunu tetikler
```

### Örnek Senaryo: Uzaktan Başlatma Güvenlik Testi
1. `changer_simulator.py` çalışıyor olsun.
2. `cp_simulator.py` ile `0x200` (RemoteStart) mesajı gönderin.
3. `saldırı_simulator.py` ile aynı ID'yi taklit eden sahte bir mesaj gönderin.
4. `csms_simulator.py` logları toplayıp olay raporu üretsin.
5. Log analizi ile hangi mesajın gerçek hangisinin sahte olduğunu tespit edin.

---

## 📁 Modül Yapısı (Detay)
```
Yetkisiz_Log_Dosyası_Sızıntısı/
├── changer_simulator.py     # Periyodik CAN trafiği üretir (voltaj, sıcaklık vb.)
├── cp_simulator.py          # Charge Point davranışı ve kontrol mesajları
├── csms_simulator.py        # Central System Management Server simülasyonu / log toplama
├── saldırı_simulator.py     # Saldırı ve sızıntı senaryoları
├── README.md                # Proje açıklaması (bu dosya)
├── requirements.txt         # Bağımlılıklar
└── .git/                    # (Opsiyonel) versiyon bilgileri
```

### Her Dosyaya Kısa Notlar
- `changer_simulator.py`: Mesaj formatı ve ID'ler açıkça belgelenmeli; örn: `0x500` voltaj, `0x501` akım.  
- `cp_simulator.py`: Komut ID'leri (`0x200`, `0x201`) ve güvenlik kontrolleri örneklenmeli.  
- `csms_simulator.py`: Log rotasyonu, erişim kontrolü ve raporlama örnekleri eklenebilir.  
- `saldırı_simulator.py`: Sızma kayıtları, veri dışa aktarım testleri ve mitigasyon senaryoları içerir.  

---

## 🔧 Teknik Detaylar & Öneriler
- **Şifreleme:** AES-256 ile lokal log şifreleme ve TLS ile uzak aktarım.  
- **Bütünlük:** SHA-256 ile mesaj hash'leme; dijital imzalar için RSA (simülasyon amaçlı).  
- **Replay Koruması:** Nonce ve timestamp uygulaması.  
- **Saldırı Tespiti:** Temel istatistiksel eşikler + basit ML tabanlı anomali dedektörü (örnek: z-score, EWMA).  
- **Forensic:** Olay sonrası veri kurtarma için ayırdedilmiş klasör yapısı ve meta-veri (timestamp, source_id, raw_payload).

**Performans Örnekleri (simülasyon kıyasları):**  
- Periyodik frame aralığı: 20ms - 100ms aralığında test edilebilir.  
- Log rotasyonu: günlük veya dosya başına 10MB sınırı önerilir.  
- Bulut yedekleme: senkronizasyon aralığı uygulamaya göre 100ms - 5s arasında ayarlanabilir.

---

## 📚 Kaynaklar & İlgili Çalışmalar
- Han, J., et al. (2023) — Connected and Autonomous Vehicles security (özet)  
- Xu, C., et al. (2022) — Blockchain ve IoV mahremiyeti  
- Strandberg, K., et al. (2022) — Automotive digital forensics review

> Bu literatür listesi eğitim amaçlıdır; özgün referanslar README içine eklendiğinde atıf formatı (BibTeX/APA) eklenmesi önerilir.

---

## 🤝 Katkıda Bulunma
- Projeyi fork edin.  
- `feature/<özellik>` branch'i açın.  
- Değişiklikleri test edin, unit test ekleyin.  
- Pull request açarken değişikliklerin amacını ve test adımlarını açıklayan bir açıklama ekleyin.

---

## 📄 Lisans
Bu projenin örnek lisansı: **MIT** (değiştirilebilir). Zararlı veya yetkisiz kullanım tamamen kullanıcı sorumluluğundadır.

---

## 📧 İletişim
Proje sahibi: Mervan Oktan  
E-posta: merwanoktan@gmail.com  
GitHub: github.com/mervanoktan 

---

**Sorumluluk Reddi:** Eğitim/araştırma amaçlıdır; gerçek araçlarda doğrudan kullanılmamalıdır. Yasal/etik sorumluluk kullanıcıya aittir.
