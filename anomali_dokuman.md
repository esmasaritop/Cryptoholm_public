# 🕵️‍♂️ ECU Parmak İzi ve Maskeleme Saldırısı Simülasyonu

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Security](https://img.shields.io/badge/Security-CAN%20Bus%20IDS-red)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20WSL2-orange)
![License](https://img.shields.io/badge/License-MIT-green)

> **"CAN veriyolunda gönderici adresi yoktur; bir mesajın kimden geldiğini anlamanın tek yolu, donanımın parmak izini okumaktır."**

## 📖 Proje Hakkında

Bu proje, **Cryptoholm** ekibinin bir parçası olarak, araç içi ağlarda (CAN-Bus) gerçekleşen sofistike siber saldırıları tespit etmek amacıyla geliştirilmiştir.

Geleneksel Saldırı Tespit Sistemleri (IDS), genellikle mesajların sıklığını (frekansını) analiz eder. Ancak CAN-Bus protokolünün **kimlik doğrulama eksikliği**, saldırganların meşru bir ECU'yu (Elektronik Kontrol Ünitesi) taklit etmesine olanak tanır. Bu proje, ECU'ların donanımsal karakteristiği olan **"Saat Kayması" (Clock Skew)** verisini bir parmak izi gibi kullanarak, ağdaki en sinsi saldırı türü olan **Maskeleme Saldırısını (Masquerade Attack)** simüle etmeyi ve tespit etmeyi amaçlar.

## 🎯 Temel Özellikler

* 🧬 **ECU Parmak İzi Çıkarma:** Her ECU'nun benzersiz saat kristali sapmalarını analiz etme.
* 🎭 **Maskeleme Saldırısı Simülasyonu:** Bir ECU'nun susup, diğerinin onun yerine geçtiği senaryonun canlandırılması.
* 📉 **Anomali Tespiti:** Frekans tabanlı IDS'lerin yakalayamadığı saldırıların CIDS (Clock-based IDS) yaklaşımıyla tespiti.
* 📊 **Veri Görselleştirme:** Normal ve saldırı altındaki saat sapmalarının grafiksel analizi.

---

## ⚠️ Seçilen Anomali Senaryosu: Maskeleme Saldırısı (Masquerade Attack)

Bu projede odaklanılan birincil saldırı vektörü, **Cho ve Shin (2016)** tarafından detaylandırılan ve mevcut güvenlik duvarlarını en kolay atlatan **"Maskeleme Saldırısı"** senaryosudur.

### Senaryo Analizi
Standart bir "Fabrikasyon Saldırısı"nda ağa ek mesajlar basılır ve trafik artar. Ancak Maskeleme saldırısında saldırgan, mesaj trafiğini değiştirmeden kaynağı değiştirir.

**Saldırı Adımları:**

1.  **Çift Taraflı Ele Geçirme:** Saldırganın araç ağında iki noktaya erişimi vardır: Biri hedef alınan kurban (Zayıf ECU), diğeri saldırıyı yapacak olan (Güçlü ECU).
2.  **Askıya Alma (Suspension):** Saldırgan, hedeflediği Zayıf ECU'nun mesaj göndermesini durdurur (Susturma).
3.  **Taklit (Masquerade):** Tam olarak Zayıf ECU sustuğu anda, Güçlü ECU devreye girer. Zayıf ECU'nun mesaj ID'sini ve verisini, **birebir aynı frekansta** göndermeye başlar.

**Neden Tehlikeli?**
Ağ trafiğine bakan standart bir güvenlik sistemi, mesajların periyodunda (örn. her 20ms'de bir) hiçbir değişiklik görmez. Trafik "normal" görünür, ancak mesajlar artık saldırganın kontrolündeki cihazdan gelmektedir. Bu proje, bu anomaliyi **donanım parmak izindeki (Clock Skew)** ani değişimden yakalamayı hedefler.

---

## 🛠️ Kurulum ve Gereksinimler

Simülasyon ortamı için aşağıdaki araçlar gereklidir:

### Ön Gereksinimler

* **Python 3.x**
* **matplotlib** (Saat kayması grafiklerini çizdirmek için)
* **python-can** (Sanal CAN trafiği için)
* **scipy & numpy** (İstatistiksel analiz için)

### Kurulum Adımları

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullaniciadi/proje-adi.git](https://github.com/kullaniciadi/proje-adi.git)
    cd proje-adi
    ```

2.  **Sanal Ortamı Kurun:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Sanal CAN Arayüzünü Başlatın (Linux/WSL):**
    ```bash
    sudo modprobe vcan
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0
    ```

---

## 🚀 Simülasyon Akışı

Simülasyonumuz, saldırının tespit edilebilirliğini göstermek için üç aşamada çalışır:

### 1. Aşama: Parmak İzi Öğrenme (Learning Phase)
Ağ normal çalışırken, simülasyonumuz her ECU'nun mesaj aralıklarını kaydeder ve onlara özgü "Saat Kayması" (Clock Skew) değerini hesaplar.
* *Örn: ECU A -> +10ppm sapma, ECU B -> -5ppm sapma.*

### 2. Aşama: Saldırı Başlatma (Attack Phase)
`attacker.py` scripti çalıştırılır.
* Hedef ECU (B) susturulur.
* Saldırgan ECU (A), B'nin ID'si (örn. 0x100) ile mesaj basmaya başlar.
* *Gözlem:* Ağdaki mesaj akışı kesintisiz devam eder, ancak fiziksel kaynak değişmiştir.

### 3. Aşama: Tespit ve Raporlama
IDS modülümüz, 0x100 ID'li mesajların saat sapmasını analiz eder.
* Beklenen Sapma: **-5ppm** (ECU B'nin orijinal imzası)
* Ölçülen Sapma: **+10ppm** (ECU A'nın imzası)
* *Sonuç:* Sistem, "Mesaj içeriği ve frekansı doğru olsa da, gönderici donanım değişmiştir!" uyarısını verir.

---

## 📚 Kaynakça

Bu çalışma, aşağıdaki akademik makalelerdeki bulgular üzerine inşa edilmiştir:

* **[1]** Cho, K. T., & Shin, K. G. (2016). *Fingerprinting electronic control units for vehicle intrusion detection*. USENIX Security Symposium.
* **[2]** Amoozadeh, M., et al. (2015). *Security vulnerabilities of connected vehicle streams and their impact on cooperative driving*. IEEE Communications Magazine.
* **[3]** Miller, C., & Valasek, C. (2015). *Remote exploitation of an unaltered passenger vehicle*.
