# README.md
# OCPP İletişim Zafiyeti ve Firmware Güncelleme Simülasyonu

## 📋 Proje Hakkında

Bu proje, elektrikli araç (EV) şarj istasyonlarında kullanılan OCPP (Open Charge Point Protocol) 
protokolündeki güvenlik açıklarını eğitim ve test amaçlı simüle eder.

⚠️ **UYARI**: Bu kod sadece eğitim ve araştırma amaçlıdır. Gerçek sistemlerde kullanılmamalıdır.

## 🎯 Senaryo

Saldırgan, şarj istasyonunun OCPP üzerinden merkezi sunucuya bağlandığı iletişim kanalını hedef alır:

1. **Zayıf Şifreleme**: TLS/SSL sertifika doğrulama eksiklikleri
2. **İmza Doğrulama**: Firmware güncellemelerinde imza kontrolü olmaması
3. **Kaynak Doğrulama**: Güncelleme kaynağının kontrolsüz kabulü
4. **Kötü Amaçlı Firmware**: Saldırgan istasyon üzerinde kalıcı kontrol sağlar

## 🔒 Güvenlik Seviyeleri

- **VULNERABLE**: Tüm zafiyetler açık (self-signed sertifika, imzasız firmware)
- **MODERATE**: Kısmi koruma (zayıf kontroller)
- **SECURE**: Tam güvenlik (sertifika pinning, imza doğrulama)

## 🚀 Kurulum

```bash
# Projeyi klonlayın
git clone <repo-url>
cd ocpp-vulnerability-sim

# Gerekli paketleri yükleyin (standart Python yeterli)
# Opsiyonel: Test için pytest
pip install pytest pytest-asyncio

# Programı çalıştırın
python main.py