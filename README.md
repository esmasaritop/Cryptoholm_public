# EV Charging SOC Manipulation Attack Simulation
# Elektrikli AraÃ§ Åarj Ä°stasyonu - SOC ManipÃ¼lasyonu SaldÄ±rÄ± SimÃ¼lasyonu

## ğŸ“‹ Proje HakkÄ±nda

Bu proje, elektrikli araÃ§ ÅŸarj istasyonlarÄ± ile araÃ§ arasÄ±ndaki iletiÅŸimde gerÃ§ekleÅŸebilecek **State of Charge (SOC) manipÃ¼lasyonu saldÄ±rÄ±sÄ±nÄ±** simÃ¼le eden kapsamlÄ± bir gÃ¼venlik araÅŸtÄ±rma projesidir.

### ğŸ¯ Senaryo
SaldÄ±rgan, araÃ§ ile ÅŸarj istasyonu arasÄ±ndaki OCPP (Open Charge Point Protocol) iletiÅŸim hattÄ±nÄ± manipÃ¼le ederek, bataryanÄ±n doluluk oranÄ± (SOC) hakkÄ±nda hatalÄ± veri iletir. Kimlik doÄŸrulamasÄ± ve veri bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ kontrolÃ¼ eksik olan sistemde, araÃ§ bataryasÄ± zaten dolu olmasÄ±na raÄŸmen ÅŸarj devam eder ve **aÅŸÄ±rÄ± ÅŸarj tehlikesi** oluÅŸur.

### âš ï¸ Tespit Edilen Zafiyetler
- âŒ SOC verilerinde kriptografik bÃ¼tÃ¼nlÃ¼k korumasÄ± eksikliÄŸi
- âŒ Dijital imza ve zaman damgasÄ± mekanizmasÄ± bulunmamasÄ±
- âŒ BMS'in OCPP mesajlarÄ±na karÅŸÄ± baÄŸÄ±msÄ±z doÄŸrulama yapamamasÄ±
- âŒ Man-in-the-Middle (MITM) saldÄ±rÄ±larÄ±na karÅŸÄ± yetersiz koruma

### ğŸ’¥ OlasÄ± SonuÃ§lar
- ğŸ”¥ Batarya hÃ¼crelerinde yangÄ±n ve patlama riski
- ğŸŒ¡ï¸ Kritik sÄ±caklÄ±k seviyelerine ulaÅŸma
- ğŸ”‹ Batarya Ã¶mrÃ¼nÃ¼n ciddi ÅŸekilde kÄ±salmasÄ±
- âš¡ Åarj istasyonu ekipmanlarÄ±nda hasar

## ğŸ—ï¸ Proje YapÄ±sÄ±

```
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ bms/                    # Battery Management System
â”‚   â”‚   â”œâ”€â”€ battery.py          # Batarya simÃ¼lasyonu
â”‚   â”‚   â””â”€â”€ bms_controller.py   # BMS kontrolcÃ¼sÃ¼
â”‚   â”œâ”€â”€ ocpp/                   # OCPP Protocol Implementation
â”‚   â”‚   â”œâ”€â”€ charging_station.py # Åarj istasyonu
â”‚   â”‚   â””â”€â”€ vehicle_client.py   # AraÃ§ istemcisi
â”‚   â”œâ”€â”€ attack/                 # SaldÄ±rÄ± SimÃ¼lasyonlarÄ±
â”‚   â”‚   â”œâ”€â”€ soc_manipulator.py  # SOC manipÃ¼lasyon saldÄ±rÄ±sÄ±
â”‚   â”‚   â””â”€â”€ mitm_proxy.py       # Man-in-the-Middle proxy
â”‚   â”œâ”€â”€ security/               # GÃ¼venlik MekanizmalarÄ±
â”‚   â”‚   â”œâ”€â”€ crypto_handler.py   # Kriptografik iÅŸlemler
â”‚   â”‚   â””â”€â”€ integrity_checker.py # Veri bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ kontrolÃ¼
â”‚   â”œâ”€â”€ can_bus/                # CAN Bus Simulation
â”‚   â”‚   â””â”€â”€ can_simulator.py    # CAN mesaj simÃ¼latÃ¶rÃ¼
â”‚   â””â”€â”€ utils/                  # YardÄ±mcÄ± AraÃ§lar
â”‚       â”œâ”€â”€ logger.py           # Loglama sistemi
â”‚       â””â”€â”€ visualizer.py       # Veri gÃ¶rselleÅŸtirme
â”œâ”€â”€ tests/                      # Test dosyalarÄ±
â”‚   â”œâ”€â”€ test_vulnerable.py      # ZayÄ±f sistem testi
â”‚   â””â”€â”€ test_secure.py          # GÃ¼venli sistem testi
â”œâ”€â”€ demos/                      # Demo scriptleri
â”‚   â”œâ”€â”€ demo_attack.py          # SaldÄ±rÄ± demosu
â”‚   â””â”€â”€ demo_secure.py          # GÃ¼venli versiyon demosu
â”œâ”€â”€ logs/                       # Log dosyalarÄ±
â”œâ”€â”€ requirements.txt            # Python baÄŸÄ±mlÄ±lÄ±klarÄ±
â””â”€â”€ README.md                   # Bu dosya
```

## ğŸš€ Kurulum

### Gereksinimler
- Python 3.8+
- pip package manager

### Kurulum AdÄ±mlarÄ±

```bash
# Repository'yi klonlayÄ±n
git clone <repository-url>
cd ev-soc-attack

# Virtual environment oluÅŸturun (opsiyonel ama Ã¶nerilir)
python -m venv venv
venv\Scripts\activate     # Windows

# BaÄŸÄ±mlÄ±lÄ±klarÄ± yÃ¼kleyin
pip install -r requirements.txt
```

## ğŸ“– KullanÄ±m

### 1ï¸âƒ£ Zafiyet Demosu - SOC ManipÃ¼lasyonu SaldÄ±rÄ±sÄ±

```bash
python demos/demo_attack.py
```

Bu demo:
- âœ… Normal ÅŸarj iletiÅŸimini baÅŸlatÄ±r
- âš ï¸ MITM proxy ile iletiÅŸimi ele geÃ§irir
- ğŸ­ SOC deÄŸerlerini manipÃ¼le eder
- ğŸ’¥ AÅŸÄ±rÄ± ÅŸarj durumunu simÃ¼le eder
- ğŸ“Š Batarya sÄ±caklÄ±k ve gerilim deÄŸiÅŸimlerini gÃ¶sterir

### 2ï¸âƒ£ GÃ¼venli Sistem Demosu

```bash
python demos/demo_secure.py
```

Bu demo:
- ğŸ”’ Kriptografik imzalama ile mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼
- ğŸ• Zaman damgasÄ± kontrolÃ¼ ile replay attack korumasÄ±
- âœ… Dijital imza doÄŸrulamasÄ±
- ğŸ›¡ï¸ BMS baÄŸÄ±msÄ±z doÄŸrulama mekanizmasÄ±

### 3ï¸âƒ£ CAN Bus SimÃ¼lasyonu

```bash
python src/can_bus/can_simulator.py
```

### 4ï¸âƒ£ Birim Testleri

```bash
# TÃ¼m testleri Ã§alÄ±ÅŸtÄ±r
pytest tests/

# Sadece saldÄ±rÄ± testleri
pytest tests/test_vulnerable.py

# Sadece gÃ¼venlik testleri
pytest tests/test_secure.py
```

## ğŸ”¬ Teknik Detaylar

### OCPP Mesaj YapÄ±sÄ±

```json
{
  "message_type": "StatusNotification",
  "timestamp": "2025-11-11T10:30:00Z",
  "connector_id": 1,
  "status": "Charging",
  "battery_data": {
    "soc": 85.0,
    "voltage": 380.5,
    "current": 125.0,
    "temperature": 35.2
  },
  "signature": "..."  // GÃ¼venli versiyonda
}
```

### SaldÄ±rÄ± VektÃ¶rÃ¼

```python
# SaldÄ±rgan proxy Ã¼zerinden SOC deÄŸerini manipÃ¼le eder
original_soc = 95.0  # GerÃ§ek deÄŸer: %95 dolu
manipulated_soc = 30.0  # ManipÃ¼le deÄŸer: %30 dolu
# Åarj istasyonu bataryanÄ±n az dolu olduÄŸunu sanÄ±r
# ve ÅŸarja devam eder â†’ AÅIRI ÅARj!
```

### GÃ¼venlik Ã‡Ã¶zÃ¼mleri

1. **Kriptografik Ä°mzalama**: HMAC-SHA256 ile mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼
2. **Dijital Sertifikalar**: X.509 sertifikalar ile kimlik doÄŸrulama
3. **Zaman DamgasÄ±**: Replay attack'lara karÅŸÄ± koruma
4. **BMS BaÄŸÄ±msÄ±z DoÄŸrulama**: Harici sensÃ¶rlerle SOC kontrolÃ¼

## ğŸ“Š GÃ¶rselleÅŸtirme

Proje, matplotlib kullanarak gerÃ§ek zamanlÄ± grafik gÃ¶rselleÅŸtirme saÄŸlar:
- ğŸ”‹ SOC seviyesi (gerÃ§ek vs manipÃ¼le)
- âš¡ Gerilim ve akÄ±m deÄŸerleri
- ğŸŒ¡ï¸ Batarya sÄ±caklÄ±ÄŸÄ±
- âš ï¸ Kritik eÅŸik uyarÄ±larÄ±

## ğŸ›¡ï¸ GÃ¼venlik Ã–nerileri

1. **OCPP 2.0.1 KullanÄ±mÄ±**: GeliÅŸtirilmiÅŸ gÃ¼venlik Ã¶zellikleri
2. **TLS/SSL Åifreleme**: Ä°letiÅŸim kanallarÄ±nÄ±n ÅŸifrelenmesi
3. **Mutual Authentication**: KarÅŸÄ±lÄ±klÄ± kimlik doÄŸrulama
4. **Mesaj Ä°mzalama**: Her mesajÄ±n dijital imzalanmasÄ±
5. **Anomali Tespiti**: ML tabanlÄ± anormal davranÄ±ÅŸ tespiti
6. **BMS GÃ¼ncelleme**: BaÄŸÄ±msÄ±z doÄŸrulama mekanizmalarÄ±
7. **Network Segmentation**: Ä°zole edilmiÅŸ ÅŸarj aÄŸÄ±
8. **Rate Limiting**: DDoS korumasÄ±

## ğŸ“š Referanslar

- [OCPP Protocol Specification](https://www.openchargealliance.org/)
- [ISO 15118 - Vehicle-to-Grid Communication](https://www.iso.org/)
- [OWASP IoT Security](https://owasp.org/www-project-internet-of-things/)

## âš–ï¸ Yasal UyarÄ±

Bu proje sadece **eÄŸitim ve araÅŸtÄ±rma amaÃ§lÄ±dÄ±r**. GerÃ§ek sistemlerde izinsiz test yapmak yasa dÄ±ÅŸÄ±dÄ±r. LÃ¼tfen sadece test ortamlarÄ±nda ve yetkili sistemlerde kullanÄ±n.

## ğŸ“„ Lisans

Bu proje MIT lisansÄ± altÄ±nda lisanslanmÄ±ÅŸtÄ±r.

---

**âš ï¸ Bu proje, elektrikli araÃ§ ÅŸarj istasyonlarÄ±ndaki gÃ¼venlik aÃ§Ä±klarÄ±nÄ± anlamak ve Ã¶nlemek amacÄ±yla geliÅŸtirilmiÅŸtir.**
