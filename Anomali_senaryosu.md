# Anomali Senaryosu – Yetkisiz Tüketim Deðeri Manipülasyonu (Integrity Ýhlali)

## 1. Temel Taným ve Hedef

Bu anomali, OCPP üzerinden iletilen **MeterValues** mesajlarýnýn bütünlüðünün saldýrgan tarafýndan deðiþtirilmesi sonucunda oluþan bir **Bütünlük (Integrity) Ýhlali** senaryosudur.

**Amaç:**

Þarj istasyonunun (CP) gerçek enerji tüketim deðerini, araya giren saldýrganýn kontrol ettiði **MITM Proxy** üzerinden deðiþtirerek Merkezi Yönetim Sistemi’nin (CSMS) yanlýþ tüketim deðerlerini kabul etmesini saðlamaktýr.

---

## 2. Anomalinin Oluþum Mekanizmasý

### 1. Saldýrganýn MITM Konumlanmasý
CP’nin normalde baðlanmasý gereken WebSocket adresi yerine saldýrganýn kurduðu sahte Proxy sunucusuna (MITM) baðlanmasý saðlanýr.

### 2. CP’nin Gerçek Veriyi Göndermesi
CP, gerçek enerji deðerini (ör. **4500 Wh**) içeren `MeterValues` mesajýný MITM’e yollar.

### 3. MITM Üzerinde Manipülasyon
Saldýrgan bu deðeri örneðin **50 Wh** olacak þekilde deðiþtirir.

### 4. Manipüle Edilmiþ Mesajýn CSMS’e Ýletilmesi
MITM, deðiþtirilmiþ mesajý CSMS’e iletir.

### 5. CSMS’in Yanlýþ Deðere Ýnanmasý
CSMS, CP’nin 4500 Wh yerine **50 Wh** tükettiðini zanneder.

---

## 3. Manipüle Edilen Veri

**Önce (Gerçek Deðer):**
