# Sahte LİDAR Verisi Enjeksiyonu Anomalisi

## I. Projenin Amacı ve Önemi

### 1. Proje Amacı
Bu projenin temel amacı, modern akıllı araçların en kritik güvenlik açıklarından biri olan **Araç İçi Ağ Güvenliği** sorununu, **Blokzincir Tabanlı Güvenlik Katmanı** geliştirerek çözmek ve bu sistemlerin daha güvenilir hâle gelmesini sağlamaktır.

### 2. Güvenlik İhtiyacı
Araç içi ağların omurgası olan **CAN-Bus** protokolü, düşük maliyetli ve verimli olmasına rağmen **kimlik doğrulama, şifreleme ve mesaj bütünlüğü** gibi temel güvenlik önlemlerinden yoksundur. Bu durum, özellikle otonom sürüş sistemlerinde hayati tehlike yaratabilecek **sahte mesaj enjeksiyonu** ve **sensör verisi manipülasyonu** gibi siber saldırılara karşı araçları savunmasız bırakmaktadır.

### 3. Blokzincir Çözümü
Proje, Blokzincir/DLT'nin merkeziyetsiz, değiştirilemez ve izlenebilir yapısından faydalanarak; mesajların kaynağını **Dijital İmza** ile doğrulama, mesaj içeriğinin bütünlüğünü **Hash Fonksiyonları** ile garanti altına alma ve tüm işlemleri zincirleme ile **izlenebilir** kılma işlevlerini CAN-Bus trafiği üzerine entegre etmiştir.

---

## II. Projenin Yapım Aşamaları (Adım Adım Kılavuz)

Bu bölüm, Mac/PyCharm ortamında projenin teknik kurulum ve kodlama adımlarını detaylandırır.

### Aşama 1: Geliştirme Ortamının Kurulumu

| Adım | İşlem | Açıklama |
| :--- | :--- | :--- |
| **1.1** | **Proje Oluşturma (PyCharm)** | PyCharm IDE kullanılarak projeye özel bir klasör oluşturulmuş ve otomatik olarak izole bir Python **Sanal Ortam (Virtualenv)** kurulmuştur. |
| **1.2** | **Kütüphane Kurulumu** | Kriptografik işlemler için gerekli olan `cryptography` kütüphanesi sanal ortama `pip install cryptography` komutu ile kurulmuştur. |
| **1.3** | **Ana Dosya Yapısının Kurulması** | Projenin çekirdeğini oluşturan `crypto_utils.py`, `light_blockchain.py`, `dlt_manager.py`, `decision_ecu.py` ve `lidar_simulator.py` dosyaları oluşturulmuştur. |

### Aşama 2: Kriptografik ve Blokzincir Temellerinin Kodlanması

| Adım | Dosya | Fonksiyon ve Görevi |
| :--- | :--- | :--- |
| **2.1** | **`crypto_utils.py`** | **Anahtar Çifti Üretimi:** ECDSA (elliptic curve digital signature algorithm) kullanarak Gizli/Açık anahtar çiftleri üretildi. |
| **2.2** | **`crypto_utils.py`** | **Hash Hesaplama:** Gelen mesajın içeriği ve **zaman damgası** eklenerek SHA256 Hash'i hesaplandı. (`H = SHA256(Mesaj \|\| Zaman)`) |
| **2.3** | **`crypto_utils.py`** | **İmzalama/Doğrulama:** Gizli anahtar ile Hash imzalandı ve alıcı tarafında Açık anahtar ile imza doğrulaması yapıldı. |
| **2.4** | **`light_blockchain.py`** | **Blok ve Zincir Sınıfları:** Blokların indeks, zaman damgası, işlemler ve önceki Hash'i tutan temel DLT yapısı kodlandı. Zincir, bir Genesis Blok ile başlatıldı. |

### Aşama 3: ECU Simülasyonu ve Entegrasyon

Bu aşamada iki ana bileşen (LiDAR Simülatörü ve Karar Verici ECU) arasındaki CAN-Bus trafiği simüle edilmiştir.

| Adım | Dosya | İşlem ve Entegrasyon Mantığı |
| :--- | :--- | :--- |
| **3.1** | **Anahtar Üretimi** | LiDAR (Gönderici) ve Karar Verici ECU (Alıcı) için kalıcı Gizli/Açık anahtar çiftleri üretildi. |
| **3.2** | **`dlt_manager.py`** | **Düğüm Yönetimi:** ECU'ların Açık Anahtarları (kimlikleri) DLT ağına kaydedildi. Bu, Alıcı ECU'nun Gönderici ECU'nun kimliğini bilmesini sağladı. |
| **3.3** | **`lidar_simulator.py`** | **Veri Üretimi:** Simülatör, LiDAR sensöründen gelen yasal veriyi (`{"object": "car"}`) üretti, hash'ledi ve kendi Gizli Anahtarı ile imzalayarak DLT'ye kaydetti. |
| **3.4** | **`decision_ecu.py`** | **Doğrulama Mekanizması:** Alıcı ECU, gelen veriyi işlerken öncelikle DLT'deki en son kaydı kontrol etti. Bu kontrol, dijital imza (kaynak güvenilirliği) ve Hash (mesaj bütünlüğü) kontrolünü içerdi. |

### Aşama 4: Anomali Testi ve Sonuçların Alınması

Projenin başarısını kanıtlamak için **"Sahte LiDAR Verisi Enjeksiyonu"** anomalisi simüle edilmiştir.

| Adım | Test Senaryosu | Eylem | Savunma Mekanizması | Sonuç |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | **Yasal Akış (Senaryo 1)** | LiDAR, yolda "araç" olduğunu belirten veriyi imzalayıp DLT'ye kaydeder. | ECU, DLT kaydını doğrular. | **BAŞARILI.** `[ECU KARAR]: Kritik Tehdit Algılandı! ACİL FRENLEME BAŞLATILDI.` |
| **4.2** | **Anomali Testi (Senaryo 2)** | Saldırgan, yasal veriyi `{"object": "none"}` (Yol Boş) olarak değiştirip, **eski yasal imzayı** kullanarak gönderir. | ECU, sahte verinin Hash'i ($H'_{Sahte}$) ile DLT'deki orijinal Hash ($H_{Yasal}$) arasındaki **uyuşmazlığı** tespit eder. | **TEST BAŞARILI.** `GÜVENLİK REDDİ: Mesaj içeriği DLT'deki kayıt ile UYUŞMUYOR.` |

---

## III. Matematiksel Model Özeti (Teknik Analiz)

Sistemin güvenliği, aşağıdaki matematiksel koşula bağlıdır. ECU'nun bir kararı kabul etmesi için, **gelen mesajın Hash'i (H')** ile **DLT'deki yasal mesajın Hash'i ($H_{\text{DLT}}$)** birebir aynı olmalıdır.

$$\text{Karar} = \begin{cases} \text{Kabul Et}, & \text{eğer } H' = H_{\text{DLT}} \text{ ve İmza Doğru} \\ \text{Reddet}, & \text{aksi takdirde (Güvenlik İhlali)} \end{cases}$$

Bu model sayesinde:

* **Veri Değiştirilemezliği:** Saldırganın mesaj içeriğini değiştirmesi ($H' \neq H_{\text{DLT}}$), anında reddedilmeye yol açar.
* **Kaynak Güvenilirliği:** Yalnızca LiDAR'ın Gizli Anahtarı ile üretilmiş geçerli imzalar kabul edilir.
