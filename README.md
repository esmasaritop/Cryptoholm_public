# 🚗 ANPR (Plaka Tanıma) Yanıltma Saldırısı Simülasyonu

**Hazırlayan:** Yusuf Kaymaz  
**Öğrenci No:** 230541084  
**Ders:** Bilgi Sistemleri Güvenliği  
**Tarih:** 11 Kasım 2025

---

## 📋 Proje Hakkında

Bu proje, AVM/site otoparklarında ve şarj istasyonlarında kullanılan **ANPR (Automatic Number Plate Recognition)** sistemlerine yönelik **plaka yanıltma (spoofing) saldırılarını** simüle eder ve anomali tespit yöntemlerini test eder.

### Senaryo Özeti
Saldırgan, hedef aracın plakasını geçici manyetik kaplama veya yansıtıcı film ile taklit eder. ANPR sistemi hatalı eşleştirme yapar; şarj oturumu kurban hesabı üzerinden başlatılır ve faturalandırılır.

---

## 🎯 Proje Amaçları

1. ✅ ANPR sistemlerindeki güvenlik açıklarını göstermek
2. ✅ Plaka yanıltma saldırılarını farklı seviyelerde simüle etmek
3. ✅ Çoklu faktörlü anomali tespit algoritması geliştirmek
4. ✅ Saldırı tespit başarısını ölçümlemek (accuracy, precision, recall, F1)
5. ✅ Finansal etkileri analiz etmek
6. ✅ Görselleştirmeler ile sonuçları sunmak

---

## 🛠️ Teknolojiler

- **Python 3.8+**
- **NumPy** - Sayısal hesaplamalar
- **Pandas** - Veri analizi
- **Matplotlib** - Grafikler
- **Seaborn** - Gelişmiş görselleştirme
- **OCPP 1.6** - Open Charge Point Protocol simülasyonu

---

## 📦 Kurulum

### 1. Depoyu klonlayın veya dosyaları indirin

```bash
cd /home/batu/Masaüstü/plaka
```

### 2. Gerekli paketleri yükleyin

```bash
pip install -r requirements.txt
```

veya tek tek:

```bash
pip install numpy pandas matplotlib seaborn
```

---

## 🚀 Kullanım

### 1. Tam Test Suite (Önerilen)

```bash
python run_complete_test.py
```

**Çıktı:**
- Terminal çıktısında performans metrikleri
- `simulation_results.json` dosyası
- **9 adet grafik** (PNG formatında)

### 2. OCPP Protokol Simülasyonu

```bash
python ocpp_simulator.py
```

**Çıktı:**
- OCPP mesaj logları
- Normal ve saldırı senaryoları
- Yetkilendirme akışları

### 3. Entegre ANPR + OCPP Testi

```bash
python integrated_anpr_ocpp_test.py
```

**Çıktı:**
- ANPR ve OCPP birlikte çalışma testi
- Gerçekçi şarj oturumu simülasyonu

### 4. Sadece Simülasyon (Grafiksiz)

```bash
python anpr_attack_simulation.py
```

**Çıktı:**
- Terminal çıktısında performans metrikleri
- `simulation_results.json` dosyası

### 5. Sadece Grafikler

```bash
python visualization.py
```

**Çıktı:**
- **9 adet grafik** (PNG formatında):
  1. `confusion_matrix.png` - Karmaşıklık matrisi
  2. `performance_metrics.png` - Accuracy, Precision, Recall, F1
  3. `anpr_confidence_dist.png` - ANPR güven skoru dağılımı
  4. `risk_score_dist.png` - Risk skoru dağılımı
  5. `anomaly_types.png` - Tespit edilen anomali tipleri
  6. `weather_impact.png` - Hava koşullarının etkisi
  7. `financial_impact.png` - Finansal etki analizi
  8. `detection_by_level.png` - Saldırı seviyesine göre tespit
  9. `roc_curve.png` - ROC eğrisi

---

## 📊 Simülasyon Parametreleri

### Varsayılan Ayarlar

```python
# Kullanıcı ve istasyon sayıları
num_legitimate_users = 100
num_stations = 10

# Oturum sayıları
num_normal = 800
num_attacks = 200

# Saldırı seviye dağılımı
attack_distribution = {
    'low': 50,      # Düşük seviye saldırı
    'medium': 100,  # Orta seviye saldırı
    'high': 50      # Yüksek seviye saldırı
}

# Güvenlik eşikleri
anpr_confidence_threshold = 0.85  # ANPR güven eşiği
gps_proximity_threshold = 100     # GPS yakınlık eşiği (metre)
risk_block_threshold = 60         # Otomatik engelleme risk skoru
```

### Parametreleri Özelleştirme

`anpr_attack_simulation.py` dosyasında `main()` fonksiyonunu düzenleyin:

```python
simulator = ANPRAttackSimulator(
    num_legitimate_users=200,  # Kullanıcı sayısını artır
    num_stations=20            # İstasyon sayısını artır
)

results = simulator.run_simulation(
    num_normal=1500,           # Normal oturum sayısı
    num_attacks=500,           # Saldırı oturum sayısı
    attack_distribution={
        'low': 100,
        'medium': 250,
        'high': 150
    }
)
```

---

## 🔍 Anomali Tespit Algoritması

Sistem, aşağıdaki faktörleri değerlendirerek **risk skoru** hesaplar:

| Anomali Tipi | Risk Puanı | Açıklama |
|--------------|-----------|----------|
| **LOW_ANPR_CONFIDENCE** | +30 | ANPR güven skoru < 0.85 |
| **GPS_MISMATCH** | +40 | Kullanıcı cihazı istasyona 100m+ uzakta |
| **DEVICE_NOT_PRESENT** | +25 | BLE/NFC cihaz sinyali yok |
| **WEATHER_LOW_CONFIDENCE** | +15 | Kötü hava + düşük güven skoru |
| **AMBIGUOUS_CHARACTERS** | +20 | Plakada belirsiz karakterler (O/0, B/8) |

**Risk Skoruna Göre Aksiyon:**
- **0-40:** ✅ Güvenli - İşleme izin ver
- **41-60:** ⚠️ Manuel doğrulama gerekli
- **61-100:** 🚫 Otomatik engelle

---

## 📈 Örnek Sonuçlar

Varsayılan simülasyon sonuçları:

```
📈 PERFORMANS METRİKLERİ
============================================================
Toplam Oturum: 1000
Sahte Oturum: 200
Engellenen Oturum: 185

Doğru Pozitif (TP): 175
Yanlış Pozitif (FP): 10
Doğru Negatif (TN): 790
Yanlış Negatif (FN): 25

Doğruluk (Accuracy): 96.50%
Kesinlik (Precision): 94.59%
Duyarlılık (Recall): 87.50%
F1 Skoru: 90.91%

💰 FİNANSAL ETKİ
Toplam Dolandırıcılık Maliyeti: 48,732.45 TL
Önlenen Dolandırıcılık: 42,741.90 TL
Tespit Edilemeyen Kayıp: 5,990.55 TL
Dolandırıcılık Önleme Oranı: 87.71%
============================================================
```

---

## 📊 Grafik Açıklamaları

### 1. Confusion Matrix
- True Positive, False Positive, True Negative, False Negative değerlerini gösterir
- Modelin hangi sınıfları karıştırdığını görselleştirir

### 2. Performance Metrics
- Accuracy, Precision, Recall, F1 skorlarını bar grafikte gösterir
- Genel sistem başarısını özetler

### 3. ANPR Confidence Distribution
- Normal oturumlar vs saldırı oturumlarında ANPR güven skoru dağılımı
- Histogram ve box plot kombinasyonu

### 4. Risk Score Distribution
- Hesaplanan risk skorlarının dağılımı
- Risk eşiklerini (40, 60) gösterir

### 5. Anomaly Types
- Saldırı oturumlarında hangi anomali tiplerinin tespit edildiği
- Horizontal bar chart

### 6. Weather Impact
- Hava koşullarının (normal, yağmur, gece, sis, kirli plaka) ANPR performansına etkisi
- Violin plot

### 7. Financial Impact
- Önlenen vs tespit edilemeyen dolandırıcılık maliyeti
- Pie chart + bar chart

### 8. Detection by Attack Level
- Düşük/orta/yüksek seviye saldırılarda tespit başarı oranı
- Grouped bar chart

### 9. ROC Curve
- Receiver Operating Characteristic eğrisi
- AUC (Area Under Curve) metriği

---

## 📄 SWOT Analizi

`swot_analizi.md` dosyasında kapsamlı SWOT analizi bulunmaktadır:

- **Güçlü Yönler (Strengths):** Kullanıcı konforu, olgun teknoloji, otomasyon
- **Zayıf Yönler (Weaknesses):** Plaka yanıltma riski, hava koşulu hassasiyeti
- **Fırsatlar (Opportunities):** AI/ML, çoklu faktör otorizasyon, veri analitiği
- **Tehditler (Threats):** Gelişen saldırı teknikleri, organize fraud, yasal riskler

---

## 🔐 Güvenlik Önerileri

### 1. **Çok Faktörlü Otorizasyon (ZORUNLU)**
- ✅ ANPR + BLE/NFC yakınlık kanıtı
- ✅ Mobil uygulama push notification onayı
- ✅ GPS lokasyon doğrulaması

### 2. **ANPR Güven Skoru Eşiği**
- ✅ Confidence < 0.85 ise otomatik başlatma yapma
- ✅ Kullanıcıdan QR kod veya PIN iste

### 3. **Görsel Kanıt ve Kullanıcı Onayı**
- ✅ Oturum başında plaka fotoğrafını uygulamada göster
- ✅ 5 saniye içinde kullanıcı onayı al (varsayılan: reddet)

### 4. **Veri Füzyonu**
- ✅ Kamera zamanı ile bariyer dedektörü korele et
- ✅ Eşzamanlı iki lokasyonda aynı plaka kontrolü

### 5. **Sahtecilik Önleme**
- ✅ IR/UV kombinasyonu ile yansıtıcı malzeme tespiti
- ✅ Folyo/kaplama tespiti için görüntü analizi

### 6. **Muhasebe Güvencesi**
- ✅ İlk 1-2 dakikada akım yoksa oturumu iptal et
- ✅ Ön-otorizasyonu otomatik geri al

---

## 📚 Dosya Yapısı

```
plaka/
├── anpr_attack_simulation.py      # Ana ANPR simülasyon kodu
├── ocpp_simulator.py              # OCPP protokol simülatörü
├── integrated_anpr_ocpp_test.py   # Entegre ANPR+OCPP testi
├── visualization.py               # Görselleştirme modülü
├── run_complete_test.py           # Tam test suite
├── swot_analizi.md               # SWOT analizi belgesi
├── requirements.txt              # Python paket gereksinimleri
├── README.md                     # Bu dosya
├── simulation_results.json       # Simülasyon sonuçları (oluşturulacak)
└── *.png                         # Grafikler (oluşturulacak)
```

---

## 🎓 Akademik Kullanım

Bu proje, **Bilgi Sistemleri Güvenliği** dersi kapsamında hazırlanmıştır. 

### Referans Verme

```
Kaymaz, Y. (2025). ANPR (Plaka Tanıma) Yanıltma Saldırısı Simülasyonu. 
Bilgi Sistemleri Güvenliği Dersi Projesi, Öğrenci No: 230541084.
```

---

## ⚠️ Yasal Uyarı

Bu proje **yalnızca eğitim amaçlıdır**. Gerçek sistemlere karşı izinsiz test yapılmamalıdır. Plaka sahteciliği **suçtur** ve ciddi cezai yaptırımları vardır.

---

## 📧 İletişim

**Yusuf Kaymaz**  
Öğrenci No: 230541084  
Ders: Bilgi Sistemleri Güvenliği

---

## 📝 Lisans

Bu proje akademik kullanım içindir. Ticari kullanım için izin alınması gerekmektedir.

---

## 🙏 Teşekkürler

Bu projeyi incelediğiniz için teşekkür ederiz!

---

**Son Güncelleme:** 11 Kasım 2025

