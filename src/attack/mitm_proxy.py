"""
MITM Proxy - Man-in-the-Middle SaldÄ±rÄ± Proxy'si
AraÃ§ ve ÅŸarj istasyonu arasÄ±ndaki iletiÅŸimi ele geÃ§irir
"""

from typing import Dict, Optional, Callable
from datetime import datetime
import json


class MITMProxy:
    """
    Man-in-the-Middle Proxy
    
    AraÃ§ ile ÅŸarj istasyonu arasÄ±na girerek iletiÅŸimi dinler
    ve manipÃ¼le eder.
    """
    
    def __init__(self, attacker_id: str = "MITM-Attacker"):
        """
        Args:
            attacker_id: SaldÄ±rgan kimliÄŸi
        """
        self.attacker_id = attacker_id
        self.active = False
        
        # Ä°letiÅŸim logu
        self.intercepted_messages = []
        
        # ManipÃ¼lasyon fonksiyonlarÄ±
        self.manipulation_callbacks = []
        
        # Ä°statistikler
        self.total_intercepted = 0
        self.total_manipulated = 0
        
    def activate(self):
        """Proxy'yi aktif et - MITM saldÄ±rÄ±sÄ±nÄ± baÅŸlat"""
        self.active = True
        print(f"\n{'='*70}")
        print(f"ğŸ•µï¸  MITM PROXY ACTIVATED - {self.attacker_id}")
        print(f"   All communications between vehicle and station are intercepted")
        print(f"{'='*70}\n")
    
    def deactivate(self):
        """Proxy'yi deaktif et"""
        self.active = False
        print(f"\n{'='*70}")
        print(f"ğŸ›¡ï¸  MITM PROXY DEACTIVATED")
        print(f"{'='*70}\n")
    
    def add_manipulation(self, callback: Callable[[Dict], Dict]):
        """
        ManipÃ¼lasyon fonksiyonu ekle
        
        Args:
            callback: MesajÄ± manipÃ¼le eden fonksiyon
        """
        self.manipulation_callbacks.append(callback)
    
    def clear_manipulations(self):
        """TÃ¼m manipÃ¼lasyonlarÄ± temizle"""
        self.manipulation_callbacks.clear()
    
    def intercept_vehicle_to_station(self, message: Dict) -> Dict:
        """
        AraÃ§tan istasyona giden mesajÄ± yakala
        
        Args:
            message: Orijinal mesaj
            
        Returns:
            Ä°ÅŸlenmiÅŸ (muhtemelen manipÃ¼le edilmiÅŸ) mesaj
        """
        if not self.active:
            return message
        
        self.total_intercepted += 1
        
        # Orijinal mesajÄ± kaydet
        self._log_message("VEHICLE_TO_STATION", message, "original")
        
        # ManipÃ¼lasyon fonksiyonlarÄ±nÄ± uygula
        manipulated_message = message
        manipulation_applied = False
        
        for callback in self.manipulation_callbacks:
            try:
                new_message = callback(manipulated_message)
                if new_message != manipulated_message:
                    manipulation_applied = True
                    manipulated_message = new_message
            except Exception as e:
                print(f"âŒ Manipulation error: {e}")
        
        if manipulation_applied:
            self.total_manipulated += 1
            self._log_message("VEHICLE_TO_STATION", manipulated_message, "manipulated")
        
        return manipulated_message
    
    def intercept_station_to_vehicle(self, message: Dict) -> Dict:
        """
        Ä°stasyondan araca giden mesajÄ± yakala
        
        Args:
            message: Orijinal mesaj
            
        Returns:
            Ä°ÅŸlenmiÅŸ mesaj
        """
        if not self.active:
            return message
        
        self.total_intercepted += 1
        self._log_message("STATION_TO_VEHICLE", message, "original")
        
        # Ä°stasyondan araca giden mesajlar genelde manipÃ¼le edilmez
        # ama gerekirse manipÃ¼lasyon yapÄ±labilir
        
        return message
    
    def _log_message(self, direction: str, message: Dict, status: str):
        """MesajÄ± kaydet"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "status": status,
            "message_type": message.get("message_type", "Unknown"),
            "message": message
        }
        self.intercepted_messages.append(log_entry)
    
    def get_statistics(self) -> Dict:
        """Ä°statistikleri dÃ¶ndÃ¼r"""
        return {
            "attacker_id": self.attacker_id,
            "active": self.active,
            "total_intercepted": self.total_intercepted,
            "total_manipulated": self.total_manipulated,
            "manipulation_rate": (
                self.total_manipulated / self.total_intercepted * 100
                if self.total_intercepted > 0 else 0
            ),
            "active_manipulations": len(self.manipulation_callbacks)
        }
    
    def get_intercepted_messages(self, limit: int = 10, status: str = None) -> list:
        """
        Yakalanan mesajlarÄ± dÃ¶ndÃ¼r
        
        Args:
            limit: Maksimum mesaj sayÄ±sÄ±
            status: Durum filtresi ("original", "manipulated", None=hepsi)
        """
        messages = self.intercepted_messages
        
        if status:
            messages = [m for m in messages if m["status"] == status]
        
        return messages[-limit:]
    
    def analyze_attack_success(self) -> Dict:
        """SaldÄ±rÄ± baÅŸarÄ± analizi"""
        manipulated_msgs = [
            m for m in self.intercepted_messages 
            if m["status"] == "manipulated"
        ]
        
        soc_manipulations = []
        temp_manipulations = []
        
        for msg in manipulated_msgs:
            if "battery_data" in msg["message"]:
                battery_data = msg["message"]["battery_data"]
                if "soc" in battery_data:
                    soc_manipulations.append(battery_data["soc"])
                if "temperature" in battery_data:
                    temp_manipulations.append(battery_data["temperature"])
        
        return {
            "total_manipulated_messages": len(manipulated_msgs),
            "soc_manipulations_count": len(soc_manipulations),
            "avg_fake_soc": sum(soc_manipulations) / len(soc_manipulations) if soc_manipulations else 0,
            "temp_manipulations_count": len(temp_manipulations),
            "attack_success_rate": (
                len(manipulated_msgs) / self.total_intercepted * 100
                if self.total_intercepted > 0 else 0
            )
        }
    
    def print_attack_report(self):
        """SaldÄ±rÄ± raporunu yazdÄ±r"""
        print(f"\n{'='*70}")
        print(f"ğŸ“Š MITM ATTACK REPORT - {self.attacker_id}")
        print(f"{'='*70}")
        
        stats = self.get_statistics()
        print(f"\nGeneral Statistics:")
        print(f"   Total Intercepted Messages: {stats['total_intercepted']}")
        print(f"   Total Manipulated Messages: {stats['total_manipulated']}")
        print(f"   Manipulation Rate: {stats['manipulation_rate']:.2f}%")
        print(f"   Active Manipulations: {stats['active_manipulations']}")
        
        analysis = self.analyze_attack_success()
        print(f"\nAttack Analysis:")
        print(f"   SOC Manipulations: {analysis['soc_manipulations_count']}")
        print(f"   Avg Fake SOC: {analysis['avg_fake_soc']:.2f}%")
        print(f"   Temp Manipulations: {analysis['temp_manipulations_count']}")
        print(f"   Attack Success Rate: {analysis['attack_success_rate']:.2f}%")
        
        print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from bms.battery import Battery
    from ocpp.vehicle_client import VehicleClient
    from soc_manipulator import SOCManipulator
    
    print("=== MITM Proxy Attack Test ===\n")
    
    # BileÅŸenleri oluÅŸtur
    battery = Battery(initial_soc=85.0)
    vehicle = VehicleClient("EV-TARGET", battery)
    proxy = MITMProxy("Advanced-Attacker")
    soc_attacker = SOCManipulator()
    
    # MITM proxy'yi aktif et
    proxy.activate()
    
    # SOC manipÃ¼lasyon saldÄ±rÄ±sÄ±nÄ± proxy'ye ekle
    soc_attacker.enable_attack(mode="fixed", fake_soc=25.0)
    proxy.add_manipulation(soc_attacker.intercept_message)
    
    # AraÃ§ baÄŸlantÄ±sÄ±
    vehicle.connect_to_station("STATION-001")
    
    print("\nSimulating 5 status notifications with MITM attack...\n")
    
    for i in range(5):
        # SOC'u artÄ±r (gerÃ§ekte ÅŸarj oluyor)
        battery.soc += 2.0
        
        # AraÃ§ mesaj gÃ¶nderir
        original_msg = vehicle.send_status_notification()
        
        # Proxy mesajÄ± yakalar ve manipÃ¼le eder
        manipulated_msg = proxy.intercept_vehicle_to_station(original_msg)
        
        # Ä°stasyona manipÃ¼le edilmiÅŸ mesaj ulaÅŸÄ±r
        print(f"{i+1}. Real SOC: {original_msg['battery_data']['soc']}% "
              f"â†’ Fake SOC: {manipulated_msg['battery_data']['soc']}%")
    
    # SaldÄ±rÄ± raporu
    proxy.print_attack_report()
    
    # Proxy'yi deaktif et
    proxy.deactivate()
