"""
OCPP Charging Station
Åarj istasyonu simÃ¼lasyonu - AraÃ§larÄ± ÅŸarj eder ve iletiÅŸim kurar
"""

import json
import time
from datetime import datetime
from typing import Dict, Optional, List


class ChargingStation:
    """
    OCPP Åarj Ä°stasyonu
    AraÃ§larla iletiÅŸim kurar ve ÅŸarj iÅŸlemini yÃ¶netir
    """
    
    def __init__(self, station_id: str, max_power_kw: float = 150.0):
        """
        Args:
            station_id: Ä°stasyon kimliÄŸi
            max_power_kw: Maksimum ÅŸarj gÃ¼cÃ¼ (kW)
        """
        self.station_id = station_id
        self.max_power_kw = max_power_kw
        
        # BaÄŸlÄ± araÃ§lar
        self.connected_vehicles = {}
        
        # Aktif ÅŸarj oturumlarÄ±
        self.active_sessions = {}
        
        # Ä°letiÅŸim logu
        self.message_log = []
        
        # Ä°statistikler
        self.total_energy_delivered = 0.0
        self.total_sessions = 0
        
    def accept_connection(self, vehicle_client) -> bool:
        """AraÃ§ baÄŸlantÄ±sÄ±nÄ± kabul et"""
        vehicle_id = vehicle_client.vehicle_id
        
        if vehicle_id in self.connected_vehicles:
            return False
        
        self.connected_vehicles[vehicle_id] = vehicle_client
        
        self._log_message("VEHICLE_CONNECTED", {
            "vehicle_id": vehicle_id,
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def process_start_transaction(self, message: Dict) -> Dict:
        """Åarj baÅŸlatma talebini iÅŸle"""
        vehicle_id = message["vehicle_id"]
        session_id = message["session_id"]
        requested_power = min(message["requested_power_kw"], self.max_power_kw)
        
        # Oturum oluÅŸtur
        session = {
            "session_id": session_id,
            "vehicle_id": vehicle_id,
            "start_time": datetime.now().isoformat(),
            "power_kw": requested_power,
            "energy_delivered": 0.0,
            "status": "Active"
        }
        
        self.active_sessions[session_id] = session
        self.total_sessions += 1
        
        response = {
            "message_type": "StartTransactionResponse",
            "message_id": f"resp_{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "transaction_id": session_id,
            "status": "Accepted",
            "power_kw": requested_power
        }
        
        self._log_message("START_TRANSACTION_RESPONSE", response)
        
        return response
    
    def process_status_notification(self, message: Dict) -> Dict:
        """
        Durum bildirimini iÅŸle
        
        Args:
            message: AraÃ§tan gelen OCPP mesajÄ±
            
        Returns:
            YanÄ±t mesajÄ±
        """
        vehicle_id = message["vehicle_id"]
        battery_data = message["battery_data"]
        
        # Åarj kararÄ± ver
        soc = battery_data["soc"]
        temperature = battery_data["temperature"]
        
        # Basit kontrol (zafiyet: baÄŸÄ±msÄ±z doÄŸrulama yok)
        continue_charging = True
        reason = "OK"
        
        if soc >= 95.0:
            continue_charging = False
            reason = "SOC limit reached"
        
        if temperature >= 50.0:
            continue_charging = False
            reason = "Temperature limit reached"
        
        response = {
            "message_type": "StatusNotificationResponse",
            "message_id": f"resp_{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "continue_charging": continue_charging,
            "reason": reason,
            "current_power_kw": self.active_sessions.get(
                message.get("session_id"), {}
            ).get("power_kw", 0.0)
        }
        
        self._log_message("STATUS_NOTIFICATION_RESPONSE", response)
        
        return response
    
    def process_stop_transaction(self, message: Dict) -> Dict:
        """Åarj durdurma talebini iÅŸle"""
        session_id = message["session_id"]
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session["status"] = "Completed"
            session["end_time"] = datetime.now().isoformat()
            
            energy = message.get("meter_stop", 0.0)
            self.total_energy_delivered += energy
        
        response = {
            "message_type": "StopTransactionResponse",
            "message_id": f"resp_{int(time.time()*1000)}",
            "timestamp": datetime.now().isoformat(),
            "status": "Accepted"
        }
        
        self._log_message("STOP_TRANSACTION_RESPONSE", response)
        
        return response
    
    def charge_vehicle(self, vehicle_client, duration_seconds: float = 1.0) -> Dict:
        """
        AracÄ± ÅŸarj et
        
        Args:
            vehicle_client: VehicleClient instance
            duration_seconds: Åarj sÃ¼resi
            
        Returns:
            Åarj sonucu
        """
        session_id = vehicle_client.charging_session_id
        
        if session_id not in self.active_sessions:
            raise ValueError("No active charging session")
        
        session = self.active_sessions[session_id]
        power_kw = session["power_kw"]
        
        # BataryayÄ± ÅŸarj et
        battery_status = vehicle_client.battery.charge(power_kw, duration_seconds)
        
        # Enerji miktarÄ±nÄ± kaydet
        energy_kwh = (power_kw * duration_seconds) / 3600.0
        session["energy_delivered"] += energy_kwh
        
        return {
            "session_id": session_id,
            "power_kw": power_kw,
            "energy_delivered": session["energy_delivered"],
            "battery_status": battery_status
        }
    
    def _log_message(self, message_type: str, data: Dict):
        """MesajÄ± kaydet"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": message_type,
            "data": data
        }
        self.message_log.append(log_entry)
    
    def get_statistics(self) -> Dict:
        """Ä°statistikleri dÃ¶ndÃ¼r"""
        return {
            "station_id": self.station_id,
            "max_power_kw": self.max_power_kw,
            "connected_vehicles": len(self.connected_vehicles),
            "active_sessions": len([s for s in self.active_sessions.values() if s["status"] == "Active"]),
            "total_sessions": self.total_sessions,
            "total_energy_delivered": round(self.total_energy_delivered, 2)
        }
    
    def get_message_log(self, limit: int = 10) -> list:
        """Mesaj logunu dÃ¶ndÃ¼r"""
        return self.message_log[-limit:]


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from bms.battery import Battery
    from vehicle_client import VehicleClient
    
    print("=== OCPP Charging Station Test ===\n")
    
    # Åarj istasyonu oluÅŸtur
    station = ChargingStation("STATION-001", max_power_kw=150.0)
    print(f"Charging Station: {station.station_id}")
    print(f"Max Power: {station.max_power_kw} kW\n")
    
    # AraÃ§ oluÅŸtur
    battery = Battery(initial_soc=30.0)
    vehicle = VehicleClient("EV-12345", battery)
    
    # BaÄŸlantÄ± kur
    print("1. Vehicle connecting...")
    vehicle.connect_to_station(station.station_id)
    station.accept_connection(vehicle)
    print("   âœ… Connected\n")
    
    # Åarj baÅŸlat
    print("2. Starting charging session...")
    start_msg = vehicle.request_charging(power_kw=50.0)
    start_resp = station.process_start_transaction(start_msg)
    print(f"   Transaction ID: {start_resp['transaction_id']}")
    print(f"   Approved Power: {start_resp['power_kw']} kW\n")
    
    # Åarj simÃ¼lasyonu
    print("3. Charging simulation (10 seconds)...")
    for i in range(10):
        # Åarj et
        result = station.charge_vehicle(vehicle, duration_seconds=1.0)
        
        # Durum bildir
        status_msg = vehicle.send_status_notification()
        status_resp = station.process_status_notification(status_msg)
        
        if i % 2 == 0:
            print(f"   t={i+1}s: SOC={result['battery_status']['soc']}%, "
                  f"Temp={result['battery_status']['temperature']}Â°C, "
                  f"Continue={status_resp['continue_charging']}")
        
        if not status_resp['continue_charging']:
            print(f"   Charging stopped: {status_resp['reason']}")
            break
    
    print()
    
    # ÅarjÄ± durdur
    print("4. Stopping charging...")
    stop_msg = vehicle.stop_charging_request()
    stop_resp = station.process_stop_transaction(stop_msg)
    print(f"   Status: {stop_resp['status']}\n")
    
    # Ä°statistikler
    print("Station Statistics:")
    stats = station.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
