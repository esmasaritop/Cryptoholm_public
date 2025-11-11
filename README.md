# 🚗 CypherCar: Otonom Araç Güvenlik Anomalilerinin Python Çözümleri

Bağlantılı ve otonom araçlarda (CAV - Connected and Autonomous Vehicles) tespit edilen üç kritik güvenlik anomalisinin kapsamlı Python çözümleri.

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Anomaliler ve Çözümleri](#anomaliler-ve-çözümleri)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Modül Yapısı](#modül-yapısı)
- [Teknik Detaylar](#teknik-detaylar)
- [Kaynaklar](#kaynaklar)

## 🎯 Genel Bakış

Bu proje, akademik literatürde tanımlanan üç kritik otonom araç güvenlik anomalisine yenilikçi çözümler sunar:

1. **Güvenlik ve Gecikme Paradoksu** (Security vs. Latency Paradox)
2. **Mahremiyet için Kalıcılık Kullanımı** (Privacy vs. Immutability Anomaly)
3. **Kanıtın Kendi Kendini Yok Etmesi** (Self-Destructing Evidence Anomaly)

Her anomali için tam işlevli Python implementasyonları ve interaktif demonstrasyonlar içerir.

## 🔍 Anomaliler ve Çözümleri

### Anomali 1: Güvenlik ve Gecikme Paradoksu

**Kaynak:** Han, J., et al. (2023) - Secure Operations in Connected and Autonomous Vehicles

#### Problem
Otonom araçlarda siber güvenlik kontrolleri (şifreleme, dijital imza doğrulama) işlem süresi gerektirir. Bu gecikme, acil durumlarda (örn. ani fren) fiziksel kaza riskini artırır. Aracı siber saldırılardan korumak için eklenen güvenlik katmanları, paradoksal olarak fiziksel emniyeti tehlikeye atar.

#### Çözüm: Adaptif Risk Tabanlı Güvenlik Sistemi
```
Kritik Tehdit (Çarpışma Riski)    → Minimal Güvenlik  → 1-2ms gecikme
Normal Sürüş (GPS Güncelleme)     → Maximum Güvenlik  → 50-100ms gecikme
```

**Temel Özellikler:**
- Risk seviyesine göre dinamik güvenlik seviyesi seçimi
- Güvenilir kaynaklar için cache mekanizması
- 4 seviyeli güvenlik katmanı (MINIMAL, STANDARD, ENHANCED, MAXIMUM)
- Gerçek zamanlı tehdit değerlendirmesi

**Dosya:** `anomaly1_security_latency.py`

---

### Anomali 2: Mahremiyet için Kalıcılık Kullanımı

**Kaynak:** Xu, C., et al. (2022) - Blockchain and Privacy in Internet of Vehicles

#### Problem
Blockchain teknolojisi, verilerin değişmezliğini (immutability) garanti eder - veriler bir kez kaydedilince asla silinemez. Ancak modern veri koruma yasaları (GDPR, KVKK) kullanıcılara "unutulma hakkı" tanır. Blockchain tabanlı bir sistemde, kullanıcı verilerini silmek teknik olarak imkansızdır.

#### Çözüm: Hibrit Off-Chain Storage + Zero-Knowledge Proof Blockchain
```
Hassas Veriler    → Off-Chain Storage  → SİLİNEBİLİR (Unutulma Hakkı)
Veri Hash'leri    → On-Chain Blockchain → DEĞİŞMEZ (Bütünlük Korunur)
Sorgulama         → Zero-Knowledge Proofs → MAHREMİYET (Veri Açığa Çıkmaz)
```

**Temel Özellikler:**
- Hibrit depolama mimarisi (on-chain + off-chain)
- Zero-Knowledge Proof ile gizli sorgulama
- Unutulma hakkı implementasyonu
- Blockchain bütünlüğü korunarak veri silme

**Dosya:** `anomaly2_privacy_blockchain.py`

---

### Anomali 3: Kanıtın Kendi Kendini Yok Etmesi

**Kaynak:** Strandberg, K., et al. (2022) - Automotive Digital Forensics

#### Problem
Adli bilişimde, kaza sonrası dijital kanıtlara (hız, frenleme, sistem logları) ihtiyaç duyulur. Ancak kazalar genellikle yüksek fiziksel darbe, yangın veya su hasarı içerir. Kanıta en çok ihtiyaç duyulan an (kaza anı), kanıtın yok olma olasılığının en yüksek olduğu andır.

#### Çözüm: Çok Katmanlı Dayanıklı Veri Saklama Sistemi
```
4 Paralel Depolama Katmanı:
1. Volatile Memory (RAM)        → Hızlı erişim, güç kaybında kayıp
2. Non-Volatile Memory (Flash)  → Kalıcı, fiziksel hasara karşı savunmasız
3. Black Box (Kara Kutu)        → Darbe dayanımlı, %95+ koruma
4. Cloud Storage (Bulut)        → Uzak yedek, fiziksel hasardan bağımsız
```

**Temel Özellikler:**
- 4 redundant (yedekli) depolama sistemi
- Gerçek zamanlı bulut senkronizasyonu
- Kaza simülasyonu ve veri kurtarma
- Adli bilişim zaman çizelgesi oluşturma

**Dosya:** `anomaly3_forensic_evidence.py`

## 💻 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Repository'yi İndirin veya Klonlayın
```bash
git clone https://github.com/username/cyphercar.git
cd cyphercar
```

### Adım 2: Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

**Gerekli Paketler:**
- `cryptography` - AES şifreleme ve dijital imza
- `pycryptodome` - Kriptografik işlemler
- `numpy` - Numerik hesaplamalar
- `colorama` - Renkli terminal çıktısı
- `tabulate` - Tablo formatında çıktı

## 🚀 Kullanım

### Ana Program (İnteraktif Menü)
```bash
python main.py
```

İnteraktif menüden istediğiniz anomali demonstrasyonunu seçebilirsiniz:
- **1:** Anomali 1 demonstrasyonu
- **2:** Anomali 2 demonstrasyonu
- **3:** Anomali 3 demonstrasyonu
- **4:** Tüm anomalileri sırayla göster
- **5:** Hakkında bilgisi
- **0:** Çıkış

### Bireysel Modülleri Çalıştırma

Her anomali modülü bağımsız olarak çalıştırılabilir:

```bash
# Anomali 1: Güvenlik ve Gecikme Paradoksu
python anomaly1_security_latency.py

# Anomali 2: Mahremiyet için Kalıcılık Kullanımı
python anomaly2_privacy_blockchain.py

# Anomali 3: Kanıtın Kendi Kendini Yok Etmesi
python anomaly3_forensic_evidence.py
```

## 📁 Modül Yapısı

```
CypherCar/
│
├── main.py                          # Ana demonstrasyon programı (interaktif menü)
├── anomaly1_security_latency.py     # Anomali 1: Adaptif Güvenlik Sistemi
├── anomaly2_privacy_blockchain.py   # Anomali 2: Hibrit Blockchain Sistemi
├── anomaly3_forensic_evidence.py    # Anomali 3: Redundant Storage Sistemi
├── requirements.txt                 # Python bağımlılıkları
└── README.md                        # Bu dosya
```

### Modül Detayları

#### `anomaly1_security_latency.py`
**Sınıflar:**
- `ThreatLevel` - Tehdit seviyeleri (LOW, MEDIUM, HIGH, CRITICAL)
- `SecurityLevel` - Güvenlik seviyeleri (MINIMAL, STANDARD, ENHANCED, MAXIMUM)
- `VehicleSignal` - Araç sinyali veri yapısı
- `AdaptiveSecuritySystem` - Ana adaptif güvenlik sistemi

**Ana Fonksiyon:**
- `process_signal()` - Sinyali tehdit seviyesine göre işle
- `assess_threat_level()` - Tehdit seviyesini değerlendir
- `select_security_level()` - Uygun güvenlik seviyesini seç

#### `anomaly2_privacy_blockchain.py`
**Sınıflar:**
- `VehicleData` - Araç verisi
- `OffChainStorage` - Off-chain depolama sistemi
- `Block` - Blockchain bloğu
- `ZeroKnowledgeProofSystem` - Zero-knowledge proof sistemi
- `PrivacyPreservingBlockchain` - Mahremiyet koruyan blockchain

**Ana Fonksiyonlar:**
- `add_vehicle_data()` - Veriyi sisteme ekle
- `exercise_right_to_be_forgotten()` - Unutulma hakkını kullan
- `query_with_zkp()` - Zero-knowledge proof ile sorgula

#### `anomaly3_forensic_evidence.py`
**Sınıflar:**
- `StorageType` - Depolama türleri (VOLATILE, NON_VOLATILE, CLOUD, BLACK_BOX)
- `EventSeverity` - Olay ciddiyeti
- `ForensicData` - Adli bilişim verisi
- `RedundantStorageSystem` - Redundant depolama sistemi
- `RealTimeSyncSystem` - Gerçek zamanlı senkronizasyon

**Ana Fonksiyonlar:**
- `write_data()` - Veriyi tüm sistemlere yaz
- `simulate_crash()` - Kaza simülasyonu
- `recover_data()` - Veri kurtarma

## 🔧 Teknik Detaylar

### Güvenlik Özellikleri
- **AES-256 Şifreleme** - Veri gizliliği
- **SHA-256/SHA-512 Hash** - Veri bütünlüğü
- **RSA Dijital İmzalar** - Kimlik doğrulama (simüle edilmiş)
- **Zero-Knowledge Proofs** - Mahremiyet korumalı sorgulama

### Performans Optimizasyonları
- **Cache Mekanizması** - Güvenilir kaynakları hatırlama
- **Paralel Yazma** - Redundant sistemlere eşzamanlı yazma
- **Adaptive Processing** - Risk bazlı kaynak tahsisi
- **Real-Time Sync** - Anlık bulut yedekleme (100ms interval)

### Simülasyon Parametreleri

#### Anomali 1
- Minimal güvenlik: ~1-2ms gecikme
- Standard güvenlik: ~5-10ms gecikme
- Enhanced güvenlik: ~20-40ms gecikme
- Maximum güvenlik: ~50-100ms gecikme

#### Anomali 2
- Off-chain storage: Sınırsız silme
- On-chain hashes: Değişmez kayıtlar
- ZKP verification: 2-5ms

#### Anomali 3
- Volatile write: 0.1ms
- Non-volatile write: 2ms
- Black box write: 5ms
- Cloud sync: 50ms (network latency)

## 📚 Kaynaklar

1. **Han, J., et al. (2023)**
   "Secure Operations in Connected and Autonomous Vehicles"
   - Güvenlik ve gecikme dengesini inceler
   - Gerçek zamanlı sistemlerde siber güvenlik zorlukları

2. **Xu, C., et al. (2022)**
   "Blockchain and Privacy in Internet of Vehicles"
   - IoV'de blockchain kullanımı
   - Mahremiyet koruma teknikleri
   - GDPR uyumluluğu

3. **Strandberg, K., et al. (2022)**
   "Automotive Digital Forensics: A Literature Review"
   - Otomotiv adli bilişimi
   - Veri toplama ve koruma teknikleri
   - Kaza sonrası kanıt analizi

## 🎓 Eğitim Amaçlı Kullanım

Bu proje, aşağıdaki konularda eğitim materyali olarak kullanılabilir:
- Siber güvenlik
- Blockchain teknolojisi
- Adli bilişim
- Otonom araç sistemleri
- Risk yönetimi
- Python programlama

## 🤝 Katkıda Bulunma

Katkılarınızı memnuniyetle karşılıyoruz! Lütfen şu adımları izleyin:
1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/YeniOzellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.

## 📧 İletişim

- **GitHub:** github.com/cyphercar
- **E-posta:** info@cyphercar.com
- **Web:** www.cyphercar.com

## ⚠️ Sorumluluk Reddi

Bu proje eğitim ve araştırma amaçlıdır. Gerçek otonom araç sistemlerinde kullanılmadan önce kapsamlı test ve doğrulama gereklidir. Üretim ortamlarında kullanımdan doğacak sorumluluk tamamen kullanıcıya aittir.

---

**CypherCar Security Research Team © 2025**

🚗 Güvenli ve akıllı sürüş için!

