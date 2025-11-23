CAN-Bus İletişim Güvenlik Analizi: Kaynak Kimlik Doğrulama Zafiyeti Simülasyonu
1. Özet
Bu rapor, araç içi iletişimde standart olan Controller Area Network (CAN-Bus) protokolünün temel mimari eksikliklerinden biri olan Mesaj Kaynak Kimlik Doğrulama (Authentication) Zafiyetini incelemektedir. CAN protokolü, mesajların kaynağını doğrulamadığı için, yetkisiz bir aktörün meşru bir ECU'yu taklit ederek hayati sistemlere sahte komutlar göndermesine olanak tanıyan "Sahte Giriş (Impersonation) Anomalisi" riskini ortaya koymaktadır. Proje, bu zafiyetin sanal bir ortamda simülasyonunu gerçekleştirerek, savunma mekanizmalarının (IDS) geliştirilmesine zemin hazırlamaktadır.

2. Proje Hedefleri ve Kapsam
CAN-Bus güvenliğindeki kritik boşlukları akademik ve savunma odaklı bir çerçevede göstermektir.

Kategori	Hedeflenen Çözüm/Analiz
Zafiyet Analizi	CAN ID'lerinin mesaj kaynağını doğrulayamamasının neden olduğu güvenlik açığının teorik ve pratik analizi.
Simülasyon Ortamı	Linux'un vcan sanal arayüzü kullanılarak, donanımdan bağımsız ve izole bir CAN iletişim test ortamının oluşturulması.
Saldırı Vektörü	Meşru bir ECU'nun CAN ID'si kullanılarak sahte mesajların enjekte edilmesi (Impersonation Spoofing).
Savunma Mekanizması	Sahte girişten kaynaklanan Frekans Anormalliği ve Veri İçeriği Anormalliği gibi davranışsal parametreler üzerinden tespit stratejilerinin geliştirilmesi.

3. Uygulanan Senaryo: Sahte Giriş (Impersonation) Anomalisi
CAN protokolünün Kimlik Doğrulama eksikliğini göstermek üzere, kritik bir ECU'nun davranışının taklit edilmesi ve bu taklidin ağ trafiğinde anomali olarak tespit edilmesi simüle edilmiştir.

3.1. Senaryo Adımları
Baseline (Normal Davranış) Oluşturma:

Legitimate_ECU.py çalıştırılarak, kritik bir CAN ID'si (Örn: 0x2A0) ile saniyede 10 kez (100ms periyotla) düzenli veri (Örn: Hız: 50 km/h) gönderimi başlatılır. Bu akış, Normal Çalışma Kalıbı olarak belirlenir.

Saldırı Vektörünün Devreye Alınması:

Attacker.py çalıştırılır ve meşru ECU ile aynı CAN ID'sini (0x2A0) kullanır.

Saldırgan, normal frekanstan daha sık (Örn: 10ms'de bir) ve kritik bir komut (Örn: Hız: 0 km/h veya Motor Durdurma Kodu) içeren sahte mesajları ağa enjekte eder.

Anomali Tespiti:

Sniffer.py (IDS simülasyonu), 0x2A0 ID'sine ait gelen mesajları analiz eder.

Sistem, aynı ID'den kısa süre içinde hem 100ms periyotlu hem de 10ms periyotlu mesajların gelmesiyle Frekans Anormalliğini tespit eder. Aynı zamanda, veri alanındaki bilinen normal aralığın dışındaki içeriği tespit ederek Veri İçeriği Anormalliğini de doğrular.

4. Kurulum ve Çalıştırma Talimatları
Simülasyon, sanal bir ortamda güvenli bir şekilde yürütülmek üzere tasarlanmıştır.

4.1. Ön Gereksinimler
İşletim Sistemi: Linux (veya WSL2)

Bağımlılıklar: Python 3.x, can-utils, python-can kütüphanesi.

4.2. Sanal CAN Arayüzünün Başlatılması
Simülasyonun çalışacağı sanal veri yolunu oluşturmak ve etkinleştirmek için aşağıdaki komutlar sırasıyla yürütülür:

Bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
4.3. Simülasyon Bileşenlerinin Çalıştırılması
Simülasyon akışı, üç ayrı terminal penceresinde eş zamanlı olarak gözlemlenmelidir:

Terminal	Komut	Rol
Terminal 1	python legitimate_ecu.py	Normal ECU Davranışı
Terminal 2	python sniffer.py	Saldırı Tespit Sistemi (IDS) ve Anomali İzleme
Terminal 3	python attacker.py	Sahte Giriş (Impersonation) Saldırısı
