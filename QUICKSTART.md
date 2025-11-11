# Quick Start Guide

## HÄ±zlÄ± Kurulum

1. BaÄŸÄ±mlÄ±lÄ±klarÄ± yÃ¼kleyin:
```bash
pip install -r requirements.txt
```

2. Quick start menÃ¼sÃ¼nÃ¼ baÅŸlatÄ±n:
```bash
python quickstart.py
```

## Manuel Ã‡alÄ±ÅŸtÄ±rma

### SaldÄ±rÄ± Demosu
```bash
python demos/demo_attack.py
```

### GÃ¼venli Sistem Demosu
```bash
python demos/demo_secure.py
```

### Testler
```bash
pytest tests/ -v
```

## Proje Ã–zeti

Bu proje, elektrikli araÃ§ ÅŸarj sistemlerinde SOC (State of Charge) manipÃ¼lasyonu 
saldÄ±rÄ±sÄ±nÄ± simÃ¼le eder ve kriptografik gÃ¼venlik Ã§Ã¶zÃ¼mlerini gÃ¶sterir.

### ModÃ¼ller:

- **BMS (Battery Management System)**: Batarya yÃ¶netimi ve gÃ¼venlik
- **OCPP**: Åarj istasyonu iletiÅŸim protokolÃ¼
- **Attack**: SaldÄ±rÄ± simÃ¼lasyonlarÄ± (SOC manipÃ¼lasyon, MITM)
- **Security**: GÃ¼venlik mekanizmalarÄ± (Kriptografi, bÃ¼tÃ¼nlÃ¼k kontrolÃ¼)
- **CAN Bus**: AraÃ§ iÃ§i iletiÅŸim simÃ¼lasyonu
- **Utils**: YardÄ±mcÄ± araÃ§lar (Logger, Visualizer)

### Ã–nemli Notlar:

âš ï¸  Bu proje sadece **eÄŸitim ve araÅŸtÄ±rma amaÃ§lÄ±dÄ±r**.
ğŸ”’ GerÃ§ek sistemlerde yetkisiz test yapmayÄ±n.
ğŸ“š Siber gÃ¼venlik Ã¶ÄŸrenim amacÄ±yla kullanÄ±n.
