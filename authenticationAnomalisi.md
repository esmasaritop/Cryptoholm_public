CAN-Bus Güvenlik Analizi ve Savunma Simülasyonu
📖 Proje Özeti
Bu proje, Akıllı Ulaşım Sistemlerinin (ITS) ve Bağlantılı Araçların (Connected Vehicles) omurgasını oluşturan CAN-Bus (Controller Area Network) protokolünün mimari zafiyetlerini analiz etmek ve bu zafiyetlerin potansiyel istismar senaryolarını güvenli bir sanal ortamda simüle etmek amacıyla geliştirilmiştir. Modern araçların siber-fiziksel sistemler haline gelmesiyle birlikte, bu sistemlerin güvenliği kritik önem taşımaktadır. Proje, CAN-Bus'ın kimlik doğrulama, şifreleme ve mesaj bütünlüğü kontrollerinden yoksun olmasının yarattığı risklere dikkat çekmekte ve savunma mekanizmalarının geliştirilmesine odaklanmaktadır.

⚠️ Odaklanılan Güvenlik Senaryosu: Güvensiz Mesaj Mantığı ve ECU Susturma
Bu projenin temel senaryosu, CAN protokolünün Yayın (Broadcast) mimarisinden kaynaklanan zafiyetleri kullanarak, kritik araç işlevlerinin (Örn: Fren Sistemi) nasıl manipüle edilebileceğini göstermektedir.

Senaryo Adımlarının Savunma Perspektifinden İncelenmesi:
Çelişkili Mesaj Enjeksiyonu (Conflicting Message Injection):

Zafiyet: CAN protokolü, aynı ID'ye sahip birden fazla mesajı ayırt etmek için güvenlik mekanizmalarına sahip değildir.

Simülasyon: Saldırgan (eğitsel amaçlı simülasyon), kritik bir ID (Örn: Fren komutu ID'si) kullanarak ağa sahte ve meşru komutla çelişen bir mesaj gönderir. Bu durum, aracın güvenli moda geçmesine neden olabilir.

ECU Susturma (Bus-Off/Suppressing):

Zafiyet: Kritik sistemlerin geçici olarak devre dışı bırakılması için kullanılan Tanılama (Diagnostic) protokollerinin (UDS gibi) yetersiz kimlik doğrulama kontrolleri.

Simülasyon: Saldırgan, meşru ECU'yu geçici olarak susturmak veya Bus-Off durumuna sokmak için özel olarak hazırlanmış bir Tanılama (Diagnostic Session Control) paketi gönderir. Bu, meşru ECU'nun savunma mekanizmalarını aşmanın bir yoludur.

Tek Otorite Kontrolü ve Manipülasyon:

Zafiyet: Susturulan meşru ECU'nun yokluğunda, ağdaki diğer düğümler (ECU'lar) sadece saldırganın gönderdiği mesajlara güvenmek zorunda kalır.

Simülasyon: Saldırgan, kritik komutları (Örn: Frenleri Devre Dışı Bırak, Motoru Durdur) göndererek araç sistemlerinin tam kontrolünü ele geçirdiğini simüle eder.

Kurulum ve Test Ortamı
Simülasyonun güvenli bir şekilde ve donanımdan bağımsız çalıştırılması için Linux tabanlı bir işletim sistemi (veya WSL2) ve sanal CAN arayüzü kullanılmaktadır.

Ön Gereksinimler
Python 3.x

can-utils (Linux CAN araçları)

python-can kütüphanesi

Sanal CAN Arayüzü (vcan0) Başlatma
Aşağıdaki komutlar, simülasyonun çalışacağı sanal veri yolunu oluşturur:

Bash

sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

Savunma Amaçlı Simülasyon Akışı
Simülasyon, bir savunma araştırmacısının gözünden üç ana bileşenin etkileşimini izler:

Sniffer.py (Gözlemci): Saldırı öncesi, sırası ve sonrasındaki tüm CAN trafiğini kaydeder ve anormal durumları tespit etmeye çalışır. Bu bileşen, savunma çözümünün temelidir.

Legitimate_ECU.py (Meşru Kontrol Ünitesi): Normal araç operasyonunu (düzenli kalp atışı mesajları) temsil eder.

Attacker.py (Anomali Kaynağı): Güvenlik açıklarını kullanarak sisteme çelişkili veya susturucu mesajları enjekte eden, kontrol edilebilir bir anomaliyi simüle eder.

Bu yapı, araştırmacıların ve öğrencilerin CAN trafiğindeki anormallikleri tanıma ve bunlara karşı filtreleme, kimlik doğrulama veya yapay zeka tabanlı anomali tespit mekanizmaları geliştirmesi için ideal bir test ortamı sunar.
