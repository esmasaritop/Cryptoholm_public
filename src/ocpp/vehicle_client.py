"""
OCPP Vehicle Client
AraÃ§ tarafÄ± OCPP istemcisi - Åarj istasyonu ile iletiÅŸim kurar
"""

import json
import time
from datetime import datetime
from typing import Dict, Optional, Callable


class VehicleClient:
    """
    Elektrikli araÃ§ OCPP istemcisi
    Batarya durumunu ÅŸarj istasyonuna bildirir
    """
    
    def __init__(self, vehicle_id: str, battery, bms_controller=None):
        """
        Args:
            vehicle_id: AraÃ§ kimliÄŸi
            battery: Battery instance
            bms_controller: BMS Controller (opsiyonel)
        """
        self.vehicle_id = vehicle_id
        self.battery = battery
        self.bms_controller = bms_controller
        self.connected = False
        self.charging_session_id = None
        
        # Ä°letiÅŸim logu
        self.message_log = []
        
    def connect_to_station(self, station_id: str) -> bool:
        """Åarj istasyonuna baÄŸlan"""
        self.connected = True
        self.charging_session_id = f"{self.vehicle_id}_{int(time.time())}"
        
        self._log_message("CONNECT", {
            "vehicle_id": self.vehicle_id,
            "station_id": station_id,
            "session_id": self.charging_session_id,
            "status": "Connected"
        })
        
        return True
    
    def disconnect_from_station(self):
        """Åarj istasyonundan ayrÄ±l"""
        self.connected = False
        self._log_message("DISCONNECT", {
            "vehicle_id": self.vehicle_id,
            "session_id": self.charging_session_id,
            "status": "Disconnected"
        })
        self.charging_session_id = None
    
    def send_status_notification(self, proxy_callback: Optional[Callable] = None) -> Dict:
        """
        Durum bildirimi gÃ¶nder
        
        Args:
            proxy_callback: MesajÄ± manipÃ¼le edebilecek proxy fonksiyonu
            
        Returns:
            GÃ¶nderilen mesaj
        """
        if not self.connected:
            raise ConnectionError("Not connected to charging station")
        
        # GerÃ§ek batarya durumunu oku
        battery_status = self.battery.get_status()
        
        # OCPP mesajÄ± oluÅŸtur
        message = {
            "message_type": "StatusNotification",
            "message_id": f"msg_{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.vehicle_id,
            "session_id": self.charging_session_id,
            "connector_id": 1,
            "status": "Charging" if battery_status["is_charging"] else "Available",
            "battery_data": {
                "soc": battery_status["soc"],
                "voltage": battery_status["voltage"],
                "current": battery_status["current"],
                "temperature": battery_status["temperature"],
                "capacity_kwh": battery_status["capacity_kwh"]
            },
            "error_code": "NoError"
        }
        
        # Proxy varsa mesajÄ± manipÃ¼le et
        if proxy_callback:
            message = proxy_callback(message)
        
        self._log_message("STATUS_NOTIFICATION", message)
        
        return message
    
    def request_charging(self, power_kw: float = 50.0) -> Dict:
        """Åarj talebi gÃ¶nder"""
        if not self.connected:
            raise ConnectionError("Not connected to charging station")
        
        message = {
            "message_type": "StartTransaction",
            "message_id": f"msg_{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.vehicle_id,
            "session_id": self.charging_session_id,
            "connector_id": 1,
            "requested_power_kw": power_kw,
            "id_tag": self.vehicle_id
        }
        
        self._log_message("START_TRANSACTION", message)
        
        return message
    
    def stop_charging_request(self) -> Dict:
        """Åarj durdurma talebi"""
        battery_status = self.battery.get_status()
        
        message = {
            "message_type": "StopTransaction",
            "message_id": f"msg_{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": self.vehicle_id,
            "session_id": self.charging_session_id,
            "transaction_id": self.charging_session_id,
            "meter_stop": battery_status["total_energy_charged"],
            "reason": "Local"
        }
        
        self._log_message("STOP_TRANSACTION", message)
        
        return message
    
    def _log_message(self, message_type: str, data: Dict):
        """MesajÄ± kaydet"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": message_type,
            "data": data
        }
        self.message_log.append(log_entry)
    
    def get_message_log(self, limit: int = 10) -> list:
        """Mesaj logunu dÃ¶ndÃ¼r"""
        return self.message_log[-limit:]
    
    def clear_log(self):
        """Logu temizle"""
        self.message_log.clear()


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from bms.battery import Battery
    
    print("=== OCPP Vehicle Client Test ===\n")
    
    # Batarya ve araÃ§ oluÅŸtur
    battery = Battery(initial_soc=30.0)
    vehicle = VehicleClient("EV-12345", battery)
    
    # Åarj istasyonuna baÄŸlan
    print("1. Connecting to charging station...")
    vehicle.connect_to_station("STATION-001")
    print("   âœ… Connected\n")
    
    # Durum bildirimi gÃ¶nder
    print("2. Sending status notification...")
    status_msg = vehicle.send_status_notification()
    print(f"   SOC: {status_msg['battery_data']['soc']}%")
    print(f"   Temperature: {status_msg['battery_data']['temperature']}Â°C\n")
    
    # Åarj talebi
    print("3. Requesting charging...")
    charge_msg = vehicle.request_charging(power_kw=50.0)
    print(f"   Requested power: {charge_msg['requested_power_kw']} kW\n")
    
    # Åarj simÃ¼lasyonu
    print("4. Charging simulation...")
    battery.charge(power_kw=50.0, duration_seconds=5.0)
    status_msg = vehicle.send_status_notification()
    print(f"   SOC: {status_msg['battery_data']['soc']}%")
    print(f"   Temperature: {status_msg['battery_data']['temperature']}Â°C\n")
    
    # ÅarjÄ± durdur
    print("5. Stopping charging...")
    stop_msg = vehicle.stop_charging_request()
    vehicle.disconnect_from_station()
    print("   âœ… Disconnected\n")
    
    # Mesaj logunu gÃ¶ster
    print("Message Log:")
    for log in vehicle.get_message_log():
        print(f"   [{log['type']}] {log['timestamp']}")
