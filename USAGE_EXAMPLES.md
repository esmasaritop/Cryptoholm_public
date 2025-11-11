# ğŸš€ KULLANIM Ã–RNEKLERÄ° / USAGE EXAMPLES

## ğŸ“‹ Ä°Ã§indekiler
1. [HÄ±zlÄ± BaÅŸlangÄ±Ã§](#hÄ±zlÄ±-baÅŸlangÄ±Ã§)
2. [SaldÄ±rÄ± Senaryosu](#saldÄ±rÄ±-senaryosu)
3. [GÃ¼venli Sistem](#gÃ¼venli-sistem)
4. [ModÃ¼l Testleri](#modÃ¼l-testleri)
5. [Ä°leri DÃ¼zey KullanÄ±m](#ileri-dÃ¼zey-kullanÄ±m)

---

## ğŸ¯ HÄ±zlÄ± BaÅŸlangÄ±Ã§

### 1. Projeyi Ä°ndirin ve Kurun

```bash
cd ev-soc-attack
pip install -r requirements.txt
```

### 2. Ä°nteraktif MenÃ¼yÃ¼ BaÅŸlatÄ±n

```bash
python quickstart.py
```

MenÃ¼den istediÄŸiniz demoyu seÃ§ebilirsiniz.

---

## ğŸ”´ SaldÄ±rÄ± Senaryosu

### Demo 1: SOC ManipÃ¼lasyon SaldÄ±rÄ±sÄ±

```bash
python demos/demo_attack.py
```

**Ne GÃ¶receksiniz:**
- âœ… Normal ÅŸarj baÅŸlangÄ±cÄ± (SOC: %30)
- âš ï¸  MITM proxy aktivasyonu
- ğŸ­ SOC deÄŸerinin %30'da sabit tutulmasÄ± (gerÃ§ekte %95+)
- ğŸ’¥ Batarya aÅŸÄ±rÄ± ÅŸarj olur (SOC > %100)
- ğŸ”¥ SÄ±caklÄ±k kritik seviyelere ulaÅŸÄ±r (>60Â°C)
- ğŸ“Š GÃ¶rselleÅŸtirme: logs/vulnerable_attack_demo.png

**Ã–rnek Ã‡Ä±ktÄ±:**
```
âš ï¸  MESSAGE MANIPULATED:
   Original SOC: 95.2% â†’ Fake SOC: 30.0%

t=40s:
    Real SOC: 105.3%        (OVERCHARGED!)
    Reported SOC: 30.0%     (Fake)
    Temperature: 62.1Â°C     (CRITICAL!)
    Safety: CRITICAL
```

---

## ğŸ›¡ï¸  GÃ¼venli Sistem

### Demo 2: Kriptografik Koruma

```bash
python demos/demo_secure.py
```

**Ne GÃ¶receksiniz:**
- ğŸ”’ Kriptografik imzalama aktif
- âœ… Normal gÃ¼venli ÅŸarj (%30 â†’ %95)
- ğŸ”´ SaldÄ±rÄ± denemesi
- âŒ SaldÄ±rÄ±nÄ±n tespit edilmesi ve engellenmesi
- ğŸ“Š GÃ¶rselleÅŸtirme: logs/secure_system_demo.png

**Ã–rnek Ã‡Ä±ktÄ±:**
```
ğŸ” Security validation...

âŒ ATTACK DETECTED by cryptographic validation!
   Errors: ['HMAC verification failed']

âŒ ATTACK DETECTED by BMS independent sensors!
   Reason: SOC manipulation detected
   Alert: SOC mismatch detected! Reported: 30.0%, Actual: 95.2%

âœ… ATTACK SUCCESSFULLY BLOCKED!
```

---

## ğŸ§ª ModÃ¼l Testleri

### Test 1: TÃ¼m Testleri Ã‡alÄ±ÅŸtÄ±r

```bash
pytest tests/ -v
```

### Test 2: Sadece Zafiyet Testleri

```bash
pytest tests/test_vulnerable.py -v
```

**Test SenaryolarÄ±:**
- âœ… SOC manipÃ¼lasyon baÅŸarÄ±sÄ±
- âœ… AÅŸÄ±rÄ± ÅŸarj zafiyeti
- âœ… MITM proxy yakalama
- âœ… SÄ±caklÄ±k artÄ±ÅŸÄ±
- âœ… Batarya saÄŸlÄ±ÄŸÄ± bozulmasÄ±

### Test 3: Sadece GÃ¼venlik Testleri

```bash
pytest tests/test_secure.py -v
```

**Test SenaryolarÄ±:**
- âœ… HMAC doÄŸrulama
- âœ… Dijital imza
- âœ… Zaman damgasÄ± kontrolÃ¼
- âœ… ManipÃ¼lasyon tespiti
- âœ… AÅŸÄ±rÄ± ÅŸarj Ã¶nleme

---

## ğŸ”¬ Ä°leri DÃ¼zey KullanÄ±m

### Ã–rnek 1: Manuel BMS Testi

```python
from src.bms.battery import Battery
from src.bms.bms_controller import BMSController

# Batarya oluÅŸtur
battery = Battery(initial_soc=30.0)

# BMS oluÅŸtur (gÃ¼venli mod)
bms = BMSController(battery, secure_mode=True)

# Åarj et
battery.charge(power_kw=50.0, duration_seconds=10.0)

# Durum kontrol et
status = battery.get_status()
print(f"SOC: {status['soc']}%")
print(f"Temperature: {status['temperature']}Â°C")
```

### Ã–rnek 2: SOC ManipÃ¼lasyon SaldÄ±rÄ±sÄ±

```python
from src.attack.soc_manipulator import SOCManipulator

# SaldÄ±rgan oluÅŸtur
attacker = SOCManipulator()
attacker.enable_attack(mode="fixed", fake_soc=30.0)

# Mesaj manipÃ¼le et
original_msg = {"battery_data": {"soc": 95.0}}
fake_msg = attacker.intercept_message(original_msg)

print(f"Original: {original_msg['battery_data']['soc']}%")
print(f"Fake: {fake_msg['battery_data']['soc']}%")
```

### Ã–rnek 3: Kriptografik Ä°mzalama

```python
from src.security.crypto_handler import CryptoHandler

crypto = CryptoHandler()

# Mesaj oluÅŸtur
message = {
    "message_type": "StatusNotification",
    "battery_data": {"soc": 50.0}
}

# GÃ¼venli hale getir
secure_msg = crypto.add_security_fields(message)

# DoÄŸrula
verification = crypto.verify_message_security(secure_msg)
print(f"Valid: {verification['valid']}")
```

### Ã–rnek 4: CAN Bus SimÃ¼lasyonu

```python
from src.bms.battery import Battery
from src.can_bus.can_simulator import CANBusSimulator

battery = Battery(initial_soc=50.0)
can_bus = CANBusSimulator(battery)

# CAN mesajlarÄ± gÃ¶nder
messages = can_bus.send_battery_status()
for msg in messages:
    print(msg)

# Sahte mesaj enjekte et
can_bus.inject_fake_soc(fake_soc=30.0)
```

### Ã–rnek 5: GÃ¶rselleÅŸtirme

```python
from src.utils.visualizer import ChargingVisualizer

vis = ChargingVisualizer("Custom Test")

# Veri ekle
for t in range(50):
    vis.add_data_point(
        t,
        soc_real=30 + t,
        soc_fake=30.0,
        temperature=25 + t*0.5
    )

# Grafik oluÅŸtur
vis.plot_static(save_path="my_test.png")
```

---

## ğŸ“Š Ã‡Ä±ktÄ± DosyalarÄ±

### Log DosyalarÄ±
- logs/charging_YYYYMMDD_HHMMSS.log - Ana log
- logs/attack_YYYYMMDD_HHMMSS.log - SaldÄ±rÄ± logu
- logs/alerts_YYYYMMDD_HHMMSS.log - Alarm logu

### GÃ¶rselleÅŸtirme
- logs/vulnerable_attack_demo.png - SaldÄ±rÄ± grafiÄŸi
- logs/secure_system_demo.png - GÃ¼venli sistem grafiÄŸi

---

## ğŸ“ Ã–ÄŸrenme Hedefleri

Bu projeyi tamamladÄ±ktan sonra Ã¶ÄŸrenecekleriniz:

1. **Siber GÃ¼venlik:**
   - MITM saldÄ±rÄ±larÄ±
   - Veri manipÃ¼lasyonu
   - Kriptografik koruma

2. **Elektrikli AraÃ§ Sistemleri:**
   - BMS (Battery Management System)
   - OCPP protokolÃ¼
   - CAN bus iletiÅŸimi

3. **GÃ¼venlik MekanizmalarÄ±:**
   - HMAC-SHA256
   - RSA dijital imza
   - Zaman damgasÄ± doÄŸrulama
   - BÃ¼tÃ¼nlÃ¼k kontrolÃ¼

4. **Python Programlama:**
   - OOP (Object-Oriented Programming)
   - Kriptografi kÃ¼tÃ¼phaneleri
   - Test yazÄ±mÄ± (pytest)
   - Veri gÃ¶rselleÅŸtirme

---

## ğŸ†˜ Sorun Giderme

### Hata: ModuleNotFoundError

```bash
# Ã‡Ã¶zÃ¼m: BaÄŸÄ±mlÄ±lÄ±klarÄ± yÃ¼kleyin
pip install -r requirements.txt
```

### Hata: Permission denied (logs dizini)

```bash
# Ã‡Ã¶zÃ¼m: logs dizinini oluÅŸturun
mkdir logs
```

### Matplotlib gÃ¶sterilmiyor

```bash
# Ã‡Ã¶zÃ¼m: Backend ayarlayÄ±n
export MPLBACKEND=TkAgg  # Linux/Mac
set MPLBACKEND=TkAgg     # Windows
```

---

## ğŸ“ Destek

SorularÄ±nÄ±z iÃ§in:
- Issue aÃ§Ä±n (GitHub)
- DokÃ¼mantasyonu okuyun (README.md)
- Test dosyalarÄ±na bakÄ±n (tests/)

---

**âš ï¸  UnutmayÄ±n:** Bu proje sadece eÄŸitim amaÃ§lÄ±dÄ±r. GerÃ§ek sistemlerde izinsiz test yapmayÄ±n!
