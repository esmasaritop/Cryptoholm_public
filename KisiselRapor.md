# 🚗 CAN-Bus Anomali Tespiti ve Güvenlik Simülasyonu

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20WSL2-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

> **"Modern araçlar, tekerlekli bilgisayarlara dönüşmüştür; ancak ağları hala 1980'lerin güvenliğiyle çalışmaktadır."**

## 📖 Proje Hakkında

Bu proje, akıllı ulaşım sistemleri ve bağlantılı araçların (Connected Vehicles) temelini oluşturan **CAN-Bus (Controller Area Network)** protokolü üzerindeki güvenlik açıklarını analiz etmek ve simüle etmek amacıyla geliştirilmiştir.

Modern araçlar ve akıllı şehir altyapıları hızla gelişirken, siber-fiziksel sistemlerin güvenliği kritik bir öneme sahiptir. Ancak, araç içi iletişimde standart olarak kullanılan CAN-Bus protokolü; **kimlik doğrulama (authentication)**, **mesaj şifreleme** ve **mesaj bütünlüğü** kontrollerinden yoksundur. Bu eksiklikler, kötü niyetli aktörlerin araçların kritik sistemlerini (fren, motor, direksiyon) ele geçirmesine olanak tanır.

Bu repo, teorik zafiyetlerin pratik bir simülasyon ortamında nasıl istismar edilebileceğini ve bu anomalilerin nasıl tespit edilebileceğini göstermektedir.

## 🎯 Temel Özellikler

* 📡 **Sanal CAN Ağı:** Donanım gerektirmeden `vcan` üzerinden araç içi ağ simülasyonu.
* 🛑 **Saldırı Simülasyonu:** Gerçek dünya senaryolarına dayalı mesaj enjeksiyonu ve ECU manipülasyonu.
* 🔍 **Trafik Analizi:** CAN trafiğini izleme (Sniffing) ve analiz etme.
* 🛡️ **Anomali Tespiti:** Beklenmeyen mesaj kalıplarının tespiti (Geliştirme aşamasında).

---

## ⚠️ Seçilen Anomali Senaryosu: Güvensiz CAN Mesaj Mantığı ve ECU Susturma

Bu projede odaklanılan birincil saldırı vektörü, **Pundir ve ark. (2022)** ile **Koscher ve ark. (2010)** çalışmalarında detaylandırılan **"Fren Sistemi Manipülasyonu"** senaryosudur.

### Senaryo Analizi
CAN protokolünün "Yayın (Broadcast)" mimarisi nedeniyle, ağa erişimi olan herhangi bir düğüm diğer tüm düğümlere mesaj gönderebilir. Saldırgan, kritik bir ECU'yu (Elektronik Kontrol Ünitesi) hedef alarak fiziksel kontrolü ele geçirebilir.

**Saldırı Adımları:**

1.  **Çelişki Yaratma:** Saldırgan ağa sahte bir "Fren Yap" komutu gönderirken, meşru ECU (Örn: Park Asistan Modülü) "Fren Yapma" komutu göndermeye devam eder. Sistem bu çelişkiyi algılayıp güvenli moda geçebilir[.
2.  **ECU Susturma (Kritik Aşama):** Bu korumayı aşmak için saldırgan, meşru ECU'ya özel bir **Tanılama (Diagnostic)** mesajı göndererek onu geçici olarak devre dışı bırakır veya "susturur".
3.  **Tam Kontrol:** Meşru ECU susturulduğunda, ağdaki tek otorite saldırgan olur. Gönderilen sahte "Frenleri Devre Dışı Bırak" veya "Motoru Durdur" komutları araç tarafından sorgusuz sualsiz uygulanır.

Bu senaryo, 2015 yılında bir Jeep Cherokee üzerinde gerçekleştirilen ve 1.4 milyon aracın geri çağrılmasına neden olan ünlü saldırı ile benzer teknik temellere dayanmaktadır.

---

## 🛠️ Kurulum ve Gereksinimler

Simülasyonu çalıştırmak için Linux tabanlı bir işletim sistemine (veya Windows üzerinde WSL2) ihtiyacınız vardır.

### Ön Gereksinimler

* **Python 3.x**
* **can-utils** (Linux CAN araçları)
* **python-can** kütüphanesi

### Kurulum Adımları

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullaniciadi/proje-adi.git](https://github.com/kullaniciadi/proje-adi.git)
    cd proje-adi
    ```

2.  **Sanal Ortamı Oluşturun (Opsiyonel ama Önerilir):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Eğer requirements dosyası yoksa: `pip install python-can`)*

4.  **Sanal CAN Arayüzünü (vcan0) Başlatın:**
    Bu adım simülasyonun çalışacağı sanal veri yolunu oluşturur.
    ```bash
    sudo modprobe vcan
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0
    ```

---

## 🚀 Simülasyonun Çalıştırılması

Simülasyonumuz üç ana bileşenden oluşur:

1.  **Legitimate_ECU.py:** Aracın normal çalıştığını simüle eder (Düzenli kalp atışı mesajları gönderir).
2.  **Attacker.py:** Saldırıyı gerçekleştirir (Önce mesaj enjekte eder, sonra meşru ECU'yu susturur).
3.  **Sniffer.py:** Ağdaki trafiği anlık olarak izler.

### 1. Adım: Ağı İzlemeye Başlayın
Ayrı bir terminal penceresinde, ağda neler olup bittiğini görmek için dinleyiciyi başlatın:
```bash
candump vcan0
# Veya Python tabanlı izleyicimiz ile:
python sniffer.py
```
