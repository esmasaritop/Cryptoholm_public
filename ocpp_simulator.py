"""
OCPP (Open Charge Point Protocol) Simülatörü
Elektrikli araç şarj istasyonları ile merkezi sistem arasındaki iletişimi simüle eder.
ANPR tabanlı yetkilendirme ve saldırı senaryolarını içerir.

OCPP 1.6 JSON protokolü temel alınmıştır.

Hazırlayan: Yusuf Kaymaz
Öğrenci No: 230541084
Ders: Bilgi Sistemleri Güvenliği
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import random


class OCPPMessageType(Enum):
    """OCPP mesaj tipleri"""
    CALL = 2  # İstek
    CALL_RESULT = 3  # Başarılı yanıt
    CALL_ERROR = 4  # Hata yanıtı


class OCPPAction(Enum):
    """OCPP işlem tipleri"""
    AUTHORIZE = "Authorize"
    START_TRANSACTION = "StartTransaction"
    STOP_TRANSACTION = "StopTransaction"
    METER_VALUES = "MeterValues"
    STATUS_NOTIFICATION = "StatusNotification"
    HEARTBEAT = "Heartbeat"
    BOOT_NOTIFICATION = "BootNotification"


class ChargePointStatus(Enum):
    """Şarj istasyonu durumları"""
    AVAILABLE = "Available"
    PREPARING = "Preparing"
    CHARGING = "Charging"
    SUSPENDED_EV = "SuspendedEV"
    SUSPENDED_EVSE = "SuspendedEVSE"
    FINISHING = "Finishing"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"


class AuthorizationStatus(Enum):
    """Yetkilendirme durumları"""
    ACCEPTED = "Accepted"
    BLOCKED = "Blocked"
    EXPIRED = "Expired"
    INVALID = "Invalid"
    CONCURRENT_TX = "ConcurrentTx"


@dataclass
class IdTagInfo:
    """Kullanıcı kimlik bilgisi"""
    status: str
    expiry_date: Optional[str] = None
    parent_id_tag: Optional[str] = None


@dataclass
class MeterValue:
    """Enerji sayacı değeri"""
    timestamp: str
    sampled_value: List[Dict]


@dataclass
class OCPPTransaction:
    """OCPP şarj oturumu"""
    transaction_id: int
    id_tag: str  # Kullanıcı plakası veya RFID
    connector_id: int
    meter_start: int
    timestamp: str
    reservation_id: Optional[int] = None
    meter_stop: Optional[int] = None
    timestamp_stop: Optional[str] = None
    reason: Optional[str] = None
    
    # Güvenlik bilgileri
    anpr_confidence: float = 0.0
    anpr_plate: str = ""
    is_fraudulent: bool = False
    authorization_method: str = "ANPR"  # ANPR, RFID, APP, etc.
    user_device_present: bool = False
    gps_verified: bool = False


class OCPPChargePoint:
    """OCPP Şarj İstasyonu Simülatörü"""
    
    def __init__(self, charge_point_id: str, vendor: str = "TurkCharger", model: str = "TC-50kW"):
        """
        Şarj istasyonu başlatma
        
        Args:
            charge_point_id: Şarj istasyonu ID'si
            vendor: Üretici
            model: Model
        """
        self.charge_point_id = charge_point_id
        self.vendor = vendor
        self.model = model
        self.status = ChargePointStatus.AVAILABLE
        self.active_transactions: Dict[int, OCPPTransaction] = {}
        self.transaction_counter = 1000
        self.message_log: List[Dict] = []
        
        # Güvenlik ayarları
        self.require_anpr_confidence = 0.85
        self.enable_multi_factor_auth = True
        self.log_all_attempts = True
        
    def _create_message(self, action: OCPPAction, payload: Dict, message_type: OCPPMessageType = OCPPMessageType.CALL) -> Dict:
        """OCPP mesajı oluştur"""
        message_id = str(uuid.uuid4())
        
        if message_type == OCPPMessageType.CALL:
            message = [
                message_type.value,
                message_id,
                action.value,
                payload
            ]
        elif message_type == OCPPMessageType.CALL_RESULT:
            message = [
                message_type.value,
                message_id,
                payload
            ]
        else:  # CALL_ERROR
            message = [
                message_type.value,
                message_id,
                "GenericError",
                "An error occurred",
                payload
            ]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'charge_point_id': self.charge_point_id,
            'message': message
        }
    
    def _log_message(self, message: Dict, direction: str = "outgoing"):
        """Mesajı logla"""
        log_entry = {
            'direction': direction,
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        self.message_log.append(log_entry)
        
        if self.log_all_attempts:
            print(f"  [{direction.upper()}] {message['message'][2] if len(message['message']) > 2 else 'Response'}")
    
    def boot_notification(self) -> Dict:
        """Şarj istasyonu başlangıç bildirimi"""
        payload = {
            'chargePointVendor': self.vendor,
            'chargePointModel': self.model,
            'chargePointSerialNumber': f"{self.charge_point_id}-SN",
            'firmwareVersion': 'v2.1.3',
            'iccid': '89882050123456789012',
            'imsi': '310150123456789',
            'meterType': 'EnergyMeter-5000',
            'meterSerialNumber': 'EM-' + str(random.randint(100000, 999999))
        }
        
        message = self._create_message(OCPPAction.BOOT_NOTIFICATION, payload)
        self._log_message(message)
        
        # Yanıt simüle et
        response = self._create_message(
            OCPPAction.BOOT_NOTIFICATION,
            {
                'status': 'Accepted',
                'currentTime': datetime.now().isoformat(),
                'interval': 300  # Heartbeat interval (saniye)
            },
            OCPPMessageType.CALL_RESULT
        )
        self._log_message(response, "incoming")
        
        return message
    
    def authorize(self, id_tag: str, anpr_confidence: float = 0.0, anpr_plate: str = "", 
                  device_present: bool = False, gps_verified: bool = False) -> tuple[Dict, IdTagInfo]:
        """
        Yetkilendirme isteği (ANPR tabanlı)
        
        Args:
            id_tag: Kullanıcı kimliği (genelde plaka)
            anpr_confidence: ANPR güven skoru
            anpr_plate: ANPR ile okunan plaka
            device_present: Kullanıcı cihazı mevcut mu (BLE/NFC)
            gps_verified: GPS doğrulaması yapıldı mı
            
        Returns:
            (message, id_tag_info)
        """
        payload = {
            'idTag': id_tag
        }
        
        message = self._create_message(OCPPAction.AUTHORIZE, payload)
        self._log_message(message)
        
        # Güvenlik kontrolleri
        auth_status = AuthorizationStatus.ACCEPTED
        
        # ANPR güven skoru kontrolü
        if self.enable_multi_factor_auth:
            if anpr_confidence < self.require_anpr_confidence:
                auth_status = AuthorizationStatus.INVALID
                print(f"  ⚠️  ANPR güven skoru düşük: {anpr_confidence:.2f} < {self.require_anpr_confidence}")
            
            # Cihaz varlığı kontrolü
            if not device_present:
                print(f"  ⚠️  Kullanıcı cihazı tespit edilmedi")
                if auth_status == AuthorizationStatus.ACCEPTED:
                    auth_status = AuthorizationStatus.BLOCKED
            
            # GPS doğrulaması
            if not gps_verified:
                print(f"  ⚠️  GPS konumu doğrulanamadı")
        
        id_tag_info = IdTagInfo(
            status=auth_status.value,
            expiry_date=(datetime.now() + timedelta(days=365)).isoformat()
        )
        
        # Yanıt simüle et
        response = self._create_message(
            OCPPAction.AUTHORIZE,
            {'idTagInfo': asdict(id_tag_info)},
            OCPPMessageType.CALL_RESULT
        )
        self._log_message(response, "incoming")
        
        return message, id_tag_info
    
    def start_transaction(self, connector_id: int, id_tag: str, meter_start: int = 0,
                         anpr_confidence: float = 0.0, anpr_plate: str = "",
                         is_fraudulent: bool = False, device_present: bool = False,
                         gps_verified: bool = False) -> tuple[Dict, int, str]:
        """
        Şarj oturumu başlat
        
        Returns:
            (message, transaction_id, status)
        """
        timestamp = datetime.now().isoformat()
        
        payload = {
            'connectorId': connector_id,
            'idTag': id_tag,
            'meterStart': meter_start,
            'timestamp': timestamp,
            'reservationId': None
        }
        
        message = self._create_message(OCPPAction.START_TRANSACTION, payload)
        self._log_message(message)
        
        # Yetkilendirme kontrol et
        auth_message, id_tag_info = self.authorize(
            id_tag, anpr_confidence, anpr_plate, device_present, gps_verified
        )
        
        if id_tag_info.status != AuthorizationStatus.ACCEPTED.value:
            # Yetkilendirme başarısız
            response = self._create_message(
                OCPPAction.START_TRANSACTION,
                {
                    'transactionId': 0,
                    'idTagInfo': asdict(id_tag_info)
                },
                OCPPMessageType.CALL_RESULT
            )
            self._log_message(response, "incoming")
            print(f"  ❌ İşlem reddedildi: {id_tag_info.status}")
            return message, 0, id_tag_info.status
        
        # İşlem başarılı - transaction oluştur
        transaction_id = self.transaction_counter
        self.transaction_counter += 1
        
        transaction = OCPPTransaction(
            transaction_id=transaction_id,
            id_tag=id_tag,
            connector_id=connector_id,
            meter_start=meter_start,
            timestamp=timestamp,
            anpr_confidence=anpr_confidence,
            anpr_plate=anpr_plate,
            is_fraudulent=is_fraudulent,
            user_device_present=device_present,
            gps_verified=gps_verified
        )
        
        self.active_transactions[connector_id] = transaction
        self.status = ChargePointStatus.CHARGING
        
        response = self._create_message(
            OCPPAction.START_TRANSACTION,
            {
                'transactionId': transaction_id,
                'idTagInfo': asdict(id_tag_info)
            },
            OCPPMessageType.CALL_RESULT
        )
        self._log_message(response, "incoming")
        
        print(f"  ✅ Şarj başlatıldı: Transaction #{transaction_id}")
        
        return message, transaction_id, id_tag_info.status
    
    def meter_values(self, connector_id: int, transaction_id: int, meter_value: int) -> Dict:
        """Sayaç değeri gönder"""
        timestamp = datetime.now().isoformat()
        
        payload = {
            'connectorId': connector_id,
            'transactionId': transaction_id,
            'meterValue': [{
                'timestamp': timestamp,
                'sampledValue': [{
                    'value': str(meter_value),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Energy.Active.Import.Register',
                    'location': 'Outlet',
                    'unit': 'Wh'
                }]
            }]
        }
        
        message = self._create_message(OCPPAction.METER_VALUES, payload)
        self._log_message(message)
        
        return message
    
    def stop_transaction(self, transaction_id: int, meter_stop: int, reason: str = "Local") -> Dict:
        """Şarj oturumu durdur"""
        timestamp = datetime.now().isoformat()
        
        # Transaction bul
        transaction = None
        connector_id = None
        for conn_id, trans in self.active_transactions.items():
            if trans.transaction_id == transaction_id:
                transaction = trans
                connector_id = conn_id
                break
        
        if not transaction:
            print(f"  ❌ Transaction #{transaction_id} bulunamadı!")
            return {}
        
        payload = {
            'transactionId': transaction_id,
            'timestamp': timestamp,
            'meterStop': meter_stop,
            'reason': reason,
            'idTag': transaction.id_tag
        }
        
        message = self._create_message(OCPPAction.STOP_TRANSACTION, payload)
        self._log_message(message)
        
        # Transaction'ı güncelle
        transaction.meter_stop = meter_stop
        transaction.timestamp_stop = timestamp
        transaction.reason = reason
        
        # Transaction'ı kaldır
        del self.active_transactions[connector_id]
        
        if len(self.active_transactions) == 0:
            self.status = ChargePointStatus.AVAILABLE
        
        # Enerji ve maliyet hesapla
        energy_kwh = (meter_stop - transaction.meter_start) / 1000
        cost = energy_kwh * random.uniform(3.5, 5.0)  # TL/kWh
        
        response = self._create_message(
            OCPPAction.STOP_TRANSACTION,
            {
                'idTagInfo': {
                    'status': 'Accepted'
                }
            },
            OCPPMessageType.CALL_RESULT
        )
        self._log_message(response, "incoming")
        
        print(f"  🛑 Şarj durduruldu: Transaction #{transaction_id}")
        print(f"     Enerji: {energy_kwh:.2f} kWh, Maliyet: {cost:.2f} TL")
        
        if transaction.is_fraudulent:
            print(f"  ⚠️  SALDIRI TESPİT EDİLDİ: Bu işlem sahte plaka ile yapıldı!")
            print(f"     ANPR Güven: {transaction.anpr_confidence:.2f}")
            print(f"     ANPR Plaka: {transaction.anpr_plate}")
        
        return message
    
    def status_notification(self, connector_id: int, error_code: str = "NoError", 
                           status: ChargePointStatus = None) -> Dict:
        """Durum bildirimi gönder"""
        if status is None:
            status = self.status
        
        payload = {
            'connectorId': connector_id,
            'errorCode': error_code,
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }
        
        message = self._create_message(OCPPAction.STATUS_NOTIFICATION, payload)
        self._log_message(message)
        
        return message
    
    def get_transaction_summary(self) -> Dict:
        """Aktif işlem özeti"""
        return {
            'charge_point_id': self.charge_point_id,
            'status': self.status.value,
            'active_transactions': len(self.active_transactions),
            'transactions': [asdict(t) for t in self.active_transactions.values()]
        }


class OCPPCentralSystem:
    """OCPP Merkezi Sistem Simülatörü"""
    
    def __init__(self):
        """Merkezi sistem başlatma"""
        self.charge_points: Dict[str, OCPPChargePoint] = {}
        self.all_transactions: List[OCPPTransaction] = []
        self.fraud_attempts: List[OCPPTransaction] = []
        
    def register_charge_point(self, charge_point: OCPPChargePoint):
        """Şarj istasyonu kaydet"""
        self.charge_points[charge_point.charge_point_id] = charge_point
        print(f"✅ Şarj istasyonu kaydedildi: {charge_point.charge_point_id}")
    
    def simulate_normal_charging_session(self, charge_point_id: str, plate: str, 
                                        anpr_confidence: float, device_present: bool = True,
                                        gps_verified: bool = True) -> Dict:
        """Normal şarj oturumu simüle et"""
        cp = self.charge_points.get(charge_point_id)
        if not cp:
            return {'error': 'Charge point not found'}
        
        print(f"\n{'='*70}")
        print(f"🔋 NORMAL ŞARJ OTURUMU: {plate}")
        print(f"{'='*70}")
        
        # Boot notification
        cp.boot_notification()
        
        # Start transaction
        connector_id = 1
        meter_start = random.randint(1000, 5000)
        
        msg, tx_id, status = cp.start_transaction(
            connector_id=connector_id,
            id_tag=plate,
            meter_start=meter_start,
            anpr_confidence=anpr_confidence,
            anpr_plate=plate,
            is_fraudulent=False,
            device_present=device_present,
            gps_verified=gps_verified
        )
        
        if tx_id == 0:
            print(f"❌ Şarj başlatılamadı: {status}")
            return {'status': 'failed', 'reason': status}
        
        # Şarj süresi simüle et
        charging_time = random.randint(15, 60)  # dakika
        energy_consumed = random.randint(10000, 50000)  # Wh
        
        # Meter values (birkaç kez)
        for i in range(3):
            meter_value = meter_start + (energy_consumed // 3) * (i + 1)
            cp.meter_values(connector_id, tx_id, meter_value)
        
        # Stop transaction
        meter_stop = meter_start + energy_consumed
        cp.stop_transaction(tx_id, meter_stop, reason="Local")
        
        # Transaction'ı kaydet
        if connector_id in cp.active_transactions:
            self.all_transactions.append(cp.active_transactions[connector_id])
        
        return {
            'status': 'success',
            'transaction_id': tx_id,
            'energy_kwh': energy_consumed / 1000
        }
    
    def simulate_attack_session(self, charge_point_id: str, victim_plate: str,
                               spoofed_plate: str, anpr_confidence: float) -> Dict:
        """Saldırı oturumu simüle et (sahte plaka)"""
        cp = self.charge_points.get(charge_point_id)
        if not cp:
            return {'error': 'Charge point not found'}
        
        print(f"\n{'='*70}")
        print(f"🎯 SALDIRI OTURUMU: {spoofed_plate} (Kurban: {victim_plate})")
        print(f"{'='*70}")
        
        # Start transaction - saldırgan cihazı yok, GPS uyuşmuyor
        connector_id = 1
        meter_start = random.randint(1000, 5000)
        
        msg, tx_id, status = cp.start_transaction(
            connector_id=connector_id,
            id_tag=victim_plate,  # Sistem bunu kurbanın plakası sanıyor
            meter_start=meter_start,
            anpr_confidence=anpr_confidence,
            anpr_plate=spoofed_plate,
            is_fraudulent=True,
            device_present=False,  # Kurbanın cihazı yok!
            gps_verified=False  # GPS uyuşmuyor!
        )
        
        if tx_id == 0:
            print(f"✅ SALDIRI ENGELLENDİ: {status}")
            return {'status': 'blocked', 'reason': status}
        
        # Saldırı başarılı - şarj devam ediyor
        print(f"❌ SALDIRI BAŞARILI! Kurban hesabına ücret yansıyacak!")
        
        energy_consumed = random.randint(15000, 80000)  # Wh
        
        # Meter values
        meter_value = meter_start + (energy_consumed // 2)
        cp.meter_values(connector_id, tx_id, meter_value)
        
        # Stop transaction
        meter_stop = meter_start + energy_consumed
        cp.stop_transaction(tx_id, meter_stop, reason="Local")
        
        # Fraud kaydı
        transaction = OCPPTransaction(
            transaction_id=tx_id,
            id_tag=victim_plate,
            connector_id=connector_id,
            meter_start=meter_start,
            timestamp=datetime.now().isoformat(),
            meter_stop=meter_stop,
            anpr_confidence=anpr_confidence,
            anpr_plate=spoofed_plate,
            is_fraudulent=True,
            user_device_present=False,
            gps_verified=False
        )
        self.fraud_attempts.append(transaction)
        
        return {
            'status': 'fraud_successful',
            'transaction_id': tx_id,
            'energy_kwh': energy_consumed / 1000,
            'victim': victim_plate
        }
    
    def get_statistics(self) -> Dict:
        """Sistem istatistikleri"""
        total_transactions = len(self.all_transactions) + len(self.fraud_attempts)
        fraud_count = len(self.fraud_attempts)
        
        return {
            'total_charge_points': len(self.charge_points),
            'total_transactions': total_transactions,
            'fraud_attempts': fraud_count,
            'fraud_rate': (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
        }


def demo_ocpp_simulation():
    """OCPP simülasyon demo'su"""
    print("\n" + "="*70)
    print("🔌 OCPP + ANPR ENTEGRE SİMÜLASYONU")
    print("="*70)
    
    # Merkezi sistem oluştur
    central_system = OCPPCentralSystem()
    
    # Şarj istasyonları oluştur
    cp1 = OCPPChargePoint("AVM-PARK-CP001", "TurkCharger", "TC-50kW")
    cp2 = OCPPChargePoint("SITE-A-CP002", "TurkCharger", "TC-22kW")
    
    central_system.register_charge_point(cp1)
    central_system.register_charge_point(cp2)
    
    print("\n" + "="*70)
    print("📋 TEST SENARYOLARI")
    print("="*70)
    
    # Senaryo 1: Normal şarj (yüksek güven)
    central_system.simulate_normal_charging_session(
        "AVM-PARK-CP001",
        plate="34 ABC 123",
        anpr_confidence=0.95,
        device_present=True,
        gps_verified=True
    )
    
    # Senaryo 2: Normal şarj (orta güven ama cihaz mevcut)
    central_system.simulate_normal_charging_session(
        "SITE-A-CP002",
        plate="06 YK 4444",
        anpr_confidence=0.82,
        device_present=True,
        gps_verified=True
    )
    
    # Senaryo 3: Saldırı - yüksek seviye (başarılı)
    central_system.simulate_attack_session(
        "AVM-PARK-CP001",
        victim_plate="16 XYZ 789",
        spoofed_plate="16 XY2 789",  # Z -> 2
        anpr_confidence=0.88  # Yüksek güven ama sahte
    )
    
    # Senaryo 4: Saldırı - düşük güven (engellendi)
    central_system.simulate_attack_session(
        "SITE-A-CP002",
        victim_plate="35 DEF 456",
        spoofed_plate="35 D3F 456",  # E -> 3
        anpr_confidence=0.72  # Düşük güven
    )
    
    # Senaryo 5: Saldırı - orta seviye (cihaz yok, engellendi)
    cp2.enable_multi_factor_auth = True
    central_system.simulate_attack_session(
        "SITE-A-CP002",
        victim_plate="42 GHI 321",
        spoofed_plate="42 6HI 321",  # G -> 6
        anpr_confidence=0.86  # İyi güven ama cihaz yok
    )
    
    # İstatistikler
    print("\n" + "="*70)
    print("📊 SİSTEM İSTATİSTİKLERİ")
    print("="*70)
    stats = central_system.get_statistics()
    print(f"Toplam Şarj İstasyonu: {stats['total_charge_points']}")
    print(f"Toplam İşlem: {stats['total_transactions']}")
    print(f"Dolandırıcılık Girişimi: {stats['fraud_attempts']}")
    print(f"Dolandırıcılık Oranı: {stats['fraud_rate']:.2f}%")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_ocpp_simulation()

