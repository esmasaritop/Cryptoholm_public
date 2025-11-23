# CAN-Bus İletişim Güvenlik Analizi: Kaynak Kimlik Doğrulama Zafiyeti Simülasyonu

### 1\. Özet

Bu rapor, araç içi iletişimde standart olan **Controller Area Network (CAN-Bus)** protokolünün mimari bir zafiyeti olan **Mesaj Kaynak Kimlik Doğrulama (Authentication) Eksikliğini** incelemektedir. CAN protokolünün mesaj kaynağını doğrulama mekanizmasından yoksun olması, yetkisiz bir aktörün meşru bir **Elektronik Kontrol Ünitesini (ECU)** taklit ederek hayati sistemlere sahte komutlar göndermesine olanak tanıyan **"Sahte Giriş (Impersonation) Anomalisi"** riskini göstermektedir. Proje, bu zafiyetin sanal bir ortamda simülasyonunu gerçekleştirerek, davranış tabanlı **Saldırı Tespit Sistemleri (IDS)** geliştirme çalışmalarına temel oluşturmayı hedeflemektedir.

### 2\. Proje Hedefleri ve Kapsam

Projenin temel hedefleri, CAN-Bus güvenliğindeki kritik boşlukları akademik bir yaklaşımla analiz etmek ve savunma mekanizmalarının etkinliğini kanıtlamaktır.

| Kategori | Hedeflenen Çözüm/Analiz |
| :--- | :--- |
| **Zafiyet Analizi** | CAN ID'lerinin mesaj kaynağını doğrulayamamasından kaynaklanan güvenlik açığının teorik ve pratik analizi. |
| **Simülasyon Ortamı** | Linux'un **`vcan`** sanal arayüzü kullanılarak, donanımdan bağımsız ve izole bir test ortamının oluşturulması. |
| **Saldırı Vektörü** | Meşru bir ECU'nun CAN ID'si kullanılarak sahte, yüksek öncelikli komutların enjekte edilmesi (**Impersonation Spoofing**). |
| **Savunma Mekanizması** | Sahte girişten kaynaklanan **Frekans Anormalliği** ve **Veri İçeriği Anormalliği** gibi davranışsal parametreler üzerinden tespit stratejilerinin uygulanması. |


### 3\. Uygulanan Senaryo: Sahte Giriş (Impersonation) Anomalisi

Bu senaryo, **CAN ID'sinin sadece öncelik belirttiğini, kimlik doğrulaması yapmadığını** göstererek kritik bir sistemin manipülasyonunu simüle etmektedir.

#### 3.1. Senaryo Akışı

1.  **Normal Çalışma Kalıbının Oluşturulması (Baseline):**
      * `Legitimate_ECU.py` modülü, kritik bir CAN ID'si (Örn: `0x2A0`) ile **düzenli bir periyotla** (Örn: **100ms**) sürekli veri akışı sağlayarak Baseline davranışını tanımlar.
2.  **Saldırgan Mesajının Enjeksiyonu (Impersonation):**
      * `Attacker.py` modülü devreye girer ve meşru ECU ile aynı CAN ID'sini (`0x2A0`) kullanarak mesaj göndermeye başlar.
      * Saldırgan, normal periyottan **daha kısa aralıklarla** (Örn: **10ms**) ve **anormal bir veri içeriğiyle** (Örn: Kritik bir Hata Komutu) mesajları ağa enjekte eder.
3.  **Anomali Tespiti ve Raporlama:**
      * `Sniffer.py` (IDS) modülü, ağ trafiğini anlık analiz eder.
      * IDS, aynı CAN ID'si için **beklenmeyen bir frekans artışı** ve **normal veri aralığının dışına çıkan içeriği** tespit ederek bu durumu **"Sahte Giriş Girişimi"** olarak raporlar.


### 4\. Kurulum ve Çalıştırma Talimatları

Simülasyonun güvenli ve tekrarlanabilir bir ortamda yürütülmesini sağlamak için aşağıdaki adımlar izlenmelidir.

#### 4.1. Ön Gereksinimler

  * **İşletim Sistemi:** Linux dağıtımları (veya WSL2)
  * **Yazılım:** Python 3.x, `can-utils`, `python-can` kütüphanesi.

#### 4.2. Sanal CAN Arayüzünün Başlatılması

Simülasyonun çalışacağı sanal veri yolu olan `vcan0` arayüzünü oluşturmak ve etkinleştirmek için aşağıdaki komutlar sırasıyla terminalde yürütülmelidir:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

#### 4.3. Simülasyon Bileşenlerinin Eş Zamanlı Çalıştırılması

Simülasyon akışının bütünsel gözlemlenmesi için **üç ayrı terminal penceresi** kullanılmalıdır:

| Terminal | Komut | Modülün Rolü |
| :--- | :--- | :--- |
| **Terminal 1** | `python legitimate_ecu.py` | Normal ECU Davranışı (Baseline Mesaj Üretimi) |
| **Terminal 2** | `python sniffer.py` | Saldırı Tespit Sistemi (IDS) ve Anomali İzleme Motoru |
| **Terminal 3** | `python attacker.py` | Sahte Giriş (Impersonation) Saldırısı Simülatörü |


### 5\. Sonuç ve Akademik Çıkarımlar

Bu çalışma, **CAN-Bus protokolünün Kimlik Doğrulama eksikliğinin** doğrudan ve pratik bir güvenlik zafiyetine dönüştüğünü kanıtlamaktadır. Elde edilen sonuçlar, gelecekteki **Araç İçi Siber Güvenlik** çalışmalarında, kriptografik doğrulama mekanizmaları yerine koymak üzere **Davranışsal Anomali Tespiti** üzerine kurulu savunma çözümlerinin hayati önem taşıdığını göstermektedir.
