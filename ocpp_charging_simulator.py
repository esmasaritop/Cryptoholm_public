"""
OCPP 1.6 Elektrikli Araç Şarj İstasyonu Simulator
Open Charge Point Protocol - Otonom Araçlar için Şarj Altyapısı

Bu modül, elektrikli otonom araçların şarj istasyonları ile
iletişimini simüle eder (OCPP 1.6 protokolü).
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

# OCPP kütüphanesi yerine basit WebSocket implementasyonu kullanacağız
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OCPP_Simulator')


class OCPPMessageType(Enum):
    """OCPP Mesaj Türleri"""
    CALL = 2          # İstek
    CALL_RESULT = 3   # Başarılı Yanıt
    CALL_ERROR = 4    # Hata Yanıti


class ChargePointStatus(Enum):
    """Şarj İstasyonu Durumları"""
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
    """Yetkilendirme Durumları"""
    ACCEPTED = "Accepted"
    BLOCKED = "Blocked"
    EXPIRED = "Expired"
    INVALID = "Invalid"
    CONCURRENT_TX = "ConcurrentTx"


@dataclass
class Transaction:
    """Şarj İşlemi Verisi"""
    transaction_id: int
    id_tag: str
    connector_id: int
    start_time: datetime
    meter_start: int
    meter_current: int = 0
    stop_time: Optional[datetime] = None
    
    def get_energy_consumed(self) -> float:
        """Tüketilen enerji (kWh)"""
        return (self.meter_current - self.meter_start) / 1000.0


class CentralSystem:
    """
    Merkezi Sistem (Central System / CSMS)
    
    Şarj istasyonlarını yönetir, yetkilendirme yapar,
    şarj işlemlerini takip eder.
    """
    
    def __init__(self):
        self.charge_points: Dict[str, Dict] = {}
        self.transactions: Dict[int, Transaction] = {}
        self.transaction_counter = 1000
        
        # Yetkili kullanıcı ID'leri (RFID kartlar)
        self.authorized_users = {
            'ARAC_001': {'name': 'Tesla Model 3', 'balance': 500.0},
            'ARAC_002': {'name': 'Nissan Leaf', 'balance': 300.0},
            'ARAC_003': {'name': 'BMW i3', 'balance': 450.0},
        }
        
        # Tarife bilgisi (TL/kWh)
        self.price_per_kwh = 3.50
    
    async def handle_boot_notification(self, charge_point_id: str, payload: Dict) -> Dict:
        """
        BootNotification: Şarj istasyonu başlatma bildirimi
        İstasyon açılışta kendini tanıtır
        """
        logger.info(f"📡 BootNotification alındı: {charge_point_id}")
        logger.info(f"   Vendor: {payload.get('chargePointVendor')}")
        logger.info(f"   Model: {payload.get('chargePointModel')}")
        
        # İstasyonu kaydet
        self.charge_points[charge_point_id] = {
            'vendor': payload.get('chargePointVendor'),
            'model': payload.get('chargePointModel'),
            'serial': payload.get('chargePointSerialNumber'),
            'firmware': payload.get('firmwareVersion'),
            'status': ChargePointStatus.AVAILABLE,
            'connected_time': datetime.now()
        }
        
        return {
            'status': 'Accepted',
            'currentTime': datetime.now(timezone.utc).isoformat(),
            'interval': 300  # Heartbeat interval (saniye)
        }
    
    async def handle_authorize(self, charge_point_id: str, payload: Dict) -> Dict:
        """
        Authorize: Kullanıcı yetkilendirme
        RFID kart veya mobil uygulama ile kimlik doğrulama
        """
        id_tag = payload.get('idTag')
        logger.info(f"🔐 Yetkilendirme isteği: {id_tag}")
        
        if id_tag in self.authorized_users:
            user_info = self.authorized_users[id_tag]
            logger.info(f"   ✓ Yetkili: {user_info['name']} - Bakiye: {user_info['balance']} TL")
            
            return {
                'idTagInfo': {
                    'status': AuthorizationStatus.ACCEPTED.value,
                    'expiryDate': '2025-12-31T23:59:59Z'
                }
            }
        else:
            logger.warning(f"   ✗ Yetkisiz: {id_tag}")
            return {
                'idTagInfo': {
                    'status': AuthorizationStatus.INVALID.value
                }
            }
    
    async def handle_start_transaction(self, charge_point_id: str, payload: Dict) -> Dict:
        """
        StartTransaction: Şarj işlemini başlat
        Kullanıcı yetkiliyse işlem başlatılır
        """
        connector_id = payload.get('connectorId')
        id_tag = payload.get('idTag')
        meter_start = payload.get('meterStart')
        timestamp = payload.get('timestamp')
        
        logger.info(f"⚡ Şarj başlatma: Connector {connector_id}, Kullanıcı: {id_tag}")
        
        if id_tag in self.authorized_users:
            # Transaction oluştur
            transaction = Transaction(
                transaction_id=self.transaction_counter,
                id_tag=id_tag,
                connector_id=connector_id,
                start_time=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                meter_start=meter_start,
                meter_current=meter_start
            )
            
            self.transactions[self.transaction_counter] = transaction
            self.transaction_counter += 1
            
            logger.info(f"   ✓ İşlem ID: {transaction.transaction_id}")
            logger.info(f"   Başlangıç sayaç: {meter_start} Wh")
            
            return {
                'transactionId': transaction.transaction_id,
                'idTagInfo': {
                    'status': AuthorizationStatus.ACCEPTED.value
                }
            }
        else:
            logger.warning(f"   ✗ Yetkisiz kullanıcı: {id_tag}")
            return {
                'transactionId': 0,
                'idTagInfo': {
                    'status': AuthorizationStatus.INVALID.value
                }
            }
    
    async def handle_stop_transaction(self, charge_point_id: str, payload: Dict) -> Dict:
        """
        StopTransaction: Şarj işlemini durdur
        Tüketilen enerji ve maliyet hesaplanır
        """
        transaction_id = payload.get('transactionId')
        meter_stop = payload.get('meterStop')
        timestamp = payload.get('timestamp')
        
        logger.info(f"🛑 Şarj durdurma: İşlem ID {transaction_id}")
        
        if transaction_id in self.transactions:
            transaction = self.transactions[transaction_id]
            transaction.meter_current = meter_stop
            transaction.stop_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Hesaplamalar
            energy_kwh = transaction.get_energy_consumed()
            cost = energy_kwh * self.price_per_kwh
            duration = (transaction.stop_time - transaction.start_time).total_seconds() / 60
            
            logger.info(f"   📊 İşlem Özeti:")
            logger.info(f"      Kullanıcı: {transaction.id_tag}")
            logger.info(f"      Tüketilen Enerji: {energy_kwh:.2f} kWh")
            logger.info(f"      Süre: {duration:.1f} dakika")
            logger.info(f"      Maliyet: {cost:.2f} TL")
            
            # Kullanıcı bakiyesinden düş
            if transaction.id_tag in self.authorized_users:
                self.authorized_users[transaction.id_tag]['balance'] -= cost
                new_balance = self.authorized_users[transaction.id_tag]['balance']
                logger.info(f"      Kalan Bakiye: {new_balance:.2f} TL")
            
            return {
                'idTagInfo': {
                    'status': AuthorizationStatus.ACCEPTED.value
                }
            }
        else:
            logger.warning(f"   ✗ Geçersiz işlem ID: {transaction_id}")
            return {
                'idTagInfo': {
                    'status': AuthorizationStatus.INVALID.value
                }
            }
    
    async def handle_heartbeat(self, charge_point_id: str, payload: Dict) -> Dict:
        """
        Heartbeat: Bağlantı kontrolü
        İstasyon periyodik olarak canlı olduğunu bildirir
        """
        logger.info(f"💓 Heartbeat: {charge_point_id}")
        
        return {
            'currentTime': datetime.now(timezone.utc).isoformat()
        }
    
    async def handle_status_notification(self, charge_point_id: str, payload: Dict) -> Dict:
        """
        StatusNotification: Durum bildirimi
        İstasyon durumu değiştiğinde bildirir
        """
        connector_id = payload.get('connectorId')
        status = payload.get('status')
        error_code = payload.get('errorCode', 'NoError')
        
        logger.info(f"📊 Durum Bildirimi: {charge_point_id}")
        logger.info(f"   Connector: {connector_id}, Durum: {status}, Hata: {error_code}")
        
        # İstasyon durumunu güncelle
        if charge_point_id in self.charge_points:
            self.charge_points[charge_point_id]['status'] = status
        
        return {}
    
    async def handle_message(self, charge_point_id: str, message: str) -> str:
        """OCPP mesajını işle"""
        try:
            data = json.loads(message)
            message_type = data[0]
            message_id = data[1]
            
            if message_type == OCPPMessageType.CALL.value:
                action = data[2]
                payload = data[3]
                
                # Action'a göre handler çağır
                handler_map = {
                    'BootNotification': self.handle_boot_notification,
                    'Authorize': self.handle_authorize,
                    'StartTransaction': self.handle_start_transaction,
                    'StopTransaction': self.handle_stop_transaction,
                    'Heartbeat': self.handle_heartbeat,
                    'StatusNotification': self.handle_status_notification,
                }
                
                if action in handler_map:
                    response_payload = await handler_map[action](charge_point_id, payload)
                    
                    # CALL_RESULT oluştur
                    response = [
                        OCPPMessageType.CALL_RESULT.value,
                        message_id,
                        response_payload
                    ]
                    
                    return json.dumps(response)
                else:
                    logger.warning(f"Bilinmeyen action: {action}")
                    
                    # CALL_ERROR oluştur
                    error_response = [
                        OCPPMessageType.CALL_ERROR.value,
                        message_id,
                        "NotImplemented",
                        f"Action {action} desteklenmiyor",
                        {}
                    ]
                    return json.dumps(error_response)
            
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {e}")
            error_response = [
                OCPPMessageType.CALL_ERROR.value,
                "error",
                "InternalError",
                str(e),
                {}
            ]
            return json.dumps(error_response)
    
    async def start_server(self, host='localhost', port=9000):
        """WebSocket sunucusunu başlat"""
        async def handler(websocket):
            # Path'i websocket.request.path'ten al
            path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
            charge_point_id = path.strip('/')
            logger.info(f"🔌 Şarj istasyonu bağlandı: {charge_point_id}")
            
            try:
                async for message in websocket:
                    response = await self.handle_message(charge_point_id, message)
                    await websocket.send(response)
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"🔌 Şarj istasyonu bağlantısı kesildi: {charge_point_id}")
        
        logger.info(f"🚀 OCPP Merkezi Sistem başlatılıyor: ws://{host}:{port}")
        logger.info(f"📡 Şarj istasyonları bekleniyor...")
        
        async with websockets.serve(handler, host, port, subprotocols=['ocpp1.6']):
            await asyncio.Future()  # Run forever


class ChargePoint:
    """
    Şarj İstasyonu (Charge Point)
    
    Elektrikli araçları şarj eder, merkezi sistem ile iletişim kurar.
    """
    
    def __init__(self, charge_point_id: str, websocket_url: str):
        self.charge_point_id = charge_point_id
        self.websocket_url = websocket_url
        self.websocket = None
        self.message_id_counter = 1
        
        # İstasyon özellikleri
        self.vendor = "CypherCar Industries"
        self.model = "SmartCharger Pro"
        self.serial_number = f"CC-{charge_point_id}-2024"
        self.firmware_version = "1.6.0"
        
        # Durum
        self.status = ChargePointStatus.AVAILABLE
        self.current_transaction_id = None
        self.meter_value = 0  # Wh cinsinden
    
    async def send_call(self, action: str, payload: Dict) -> Dict:
        """OCPP CALL mesajı gönder ve yanıt bekle"""
        message_id = str(self.message_id_counter)
        self.message_id_counter += 1
        
        call_message = [
            OCPPMessageType.CALL.value,
            message_id,
            action,
            payload
        ]
        
        await self.websocket.send(json.dumps(call_message))
        response = await self.websocket.recv()
        
        response_data = json.loads(response)
        
        if response_data[0] == OCPPMessageType.CALL_RESULT.value:
            return response_data[2]  # Payload
        else:
            logger.error(f"Hata alındı: {response_data}")
            return {}
    
    async def boot_notification(self):
        """BootNotification gönder"""
        logger.info(f"📤 BootNotification gönderiliyor...")
        
        payload = {
            'chargePointVendor': self.vendor,
            'chargePointModel': self.model,
            'chargePointSerialNumber': self.serial_number,
            'firmwareVersion': self.firmware_version
        }
        
        response = await self.send_call('BootNotification', payload)
        logger.info(f"📥 Yanıt: {response.get('status')}")
        return response
    
    async def authorize(self, id_tag: str):
        """Authorize isteği gönder"""
        logger.info(f"📤 Authorize gönderiliyor: {id_tag}")
        
        payload = {'idTag': id_tag}
        response = await self.send_call('Authorize', payload)
        
        status = response.get('idTagInfo', {}).get('status')
        logger.info(f"📥 Yetkilendirme: {status}")
        return response
    
    async def start_transaction(self, connector_id: int, id_tag: str):
        """StartTransaction isteği gönder"""
        logger.info(f"📤 StartTransaction gönderiliyor...")
        
        payload = {
            'connectorId': connector_id,
            'idTag': id_tag,
            'meterStart': self.meter_value,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        response = await self.send_call('StartTransaction', payload)
        
        if 'transactionId' in response:
            self.current_transaction_id = response['transactionId']
            self.status = ChargePointStatus.CHARGING
            logger.info(f"📥 İşlem başlatıldı: ID {self.current_transaction_id}")
        
        return response
    
    async def stop_transaction(self, reason='Local'):
        """StopTransaction isteği gönder"""
        if not self.current_transaction_id:
            logger.warning("Aktif işlem yok!")
            return
        
        logger.info(f"📤 StopTransaction gönderiliyor...")
        
        payload = {
            'transactionId': self.current_transaction_id,
            'meterStop': self.meter_value,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'reason': reason
        }
        
        response = await self.send_call('StopTransaction', payload)
        
        self.current_transaction_id = None
        self.status = ChargePointStatus.AVAILABLE
        logger.info(f"📥 İşlem durduruldu")
        
        return response
    
    async def simulate_charging(self, duration_seconds: int):
        """Şarj simülasyonu - enerji tüketimi artır"""
        logger.info(f"⚡ Şarj simülasyonu başladı ({duration_seconds} saniye)...")
        
        for i in range(duration_seconds):
            await asyncio.sleep(1)
            # 7.4 kW şarj gücü = 7400 W = 7400 Wh/saat = ~2 Wh/saniye
            self.meter_value += 2050  # 2.05 Wh/saniye (7.4 kW şarj)
            
            if (i + 1) % 10 == 0:
                energy_kwh = self.meter_value / 1000
                logger.info(f"   ⚡ {i+1}s - Tüketilen: {energy_kwh:.3f} kWh")
        
        logger.info(f"✓ Şarj simülasyonu tamamlandı")
    
    async def run_test_scenario(self):
        """Test senaryosu çalıştır"""
        try:
            # WebSocket bağlantısı
            logger.info(f"🔌 Bağlantı kuruluyor: {self.websocket_url}")
            async with websockets.connect(
                self.websocket_url,
                subprotocols=['ocpp1.6']
            ) as websocket:
                self.websocket = websocket
                
                logger.info("=" * 70)
                logger.info("TEST SENARYOSU BAŞLADI")
                logger.info("=" * 70)
                
                # 1. Boot Notification
                await self.boot_notification()
                await asyncio.sleep(2)
                
                # 2. Authorize
                id_tag = 'ARAC_001'
                await self.authorize(id_tag)
                await asyncio.sleep(2)
                
                # 3. Start Transaction
                await self.start_transaction(connector_id=1, id_tag=id_tag)
                await asyncio.sleep(2)
                
                # 4. Şarj simülasyonu (30 saniye)
                await self.simulate_charging(duration_seconds=30)
                await asyncio.sleep(2)
                
                # 5. Stop Transaction
                await self.stop_transaction(reason='Local')
                
                logger.info("=" * 70)
                logger.info("TEST SENARYOSU TAMAMLANDI")
                logger.info("=" * 70)
                
        except Exception as e:
            logger.error(f"Hata: {e}")


async def run_demo():
    """OCPP Demo - Server ve Client birlikte çalışır"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                  OCPP 1.6 ŞARJ İSTASYONU SİMÜLATÖRÜ                ║
║             Open Charge Point Protocol - Demo Test                ║
╚════════════════════════════════════════════════════════════════════╝

Bu demo, elektrikli otonom araçların şarj istasyonları ile
nasıl iletişim kurduğunu gösterir (OCPP 1.6 protokolü).

Demo akışı:
1. Merkezi Sistem başlatılacak (Central System)
2. Şarj İstasyonu bağlanacak (Charge Point)
3. Test senaryosu çalışacak:
   - BootNotification (İstasyon tanıtımı)
   - Authorize (Kullanıcı yetkilendirme)
   - StartTransaction (Şarj başlatma)
   - Charging Simulation (Şarj simülasyonu - 30 saniye)
   - StopTransaction (Şarj durdurma ve fatura)
    """)
    
    try:
        input("Başlatmak için Enter'a basın...")
    except EOFError:
        pass  # Automated test mode
    print("\n")
    
    # Central System başlat
    central_system = CentralSystem()
    
    # Server'ı arka planda çalıştır
    server_task = asyncio.create_task(central_system.start_server())
    
    # Server'ın başlaması için bekle
    await asyncio.sleep(2)
    
    # Charge Point oluştur ve test et
    charge_point = ChargePoint(
        charge_point_id='CP_001',
        websocket_url='ws://localhost:9000/CP_001'
    )
    
    await charge_point.run_test_scenario()
    
    print("\n✅ Demo tamamlandı!")
    print("\nMerkezi Sistemdeki veriler:")
    print(f"  Kayıtlı İstasyonlar: {len(central_system.charge_points)}")
    print(f"  Toplam İşlem Sayısı: {len(central_system.transactions)}")
    
    # Server'ı durdur
    server_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından durduruldu.")

