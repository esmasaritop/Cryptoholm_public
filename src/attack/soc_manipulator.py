"""
SOC Manipulator - SaldÄ±rÄ± ModÃ¼lÃ¼
SOC deÄŸerlerini manipÃ¼le ederek aÅŸÄ±rÄ± ÅŸarj saldÄ±rÄ±sÄ± gerÃ§ekleÅŸtirir
"""

import random
from typing import Dict, Callable
from datetime import datetime


class SOCManipulator:
    """
    State of Charge (SOC) ManipÃ¼lasyon SaldÄ±rÄ±sÄ±
    
    Bu saldÄ±rÄ± modÃ¼lÃ¼, araÃ§ ile ÅŸarj istasyonu arasÄ±ndaki
    OCPP iletiÅŸimini ele geÃ§irerek SOC deÄŸerlerini deÄŸiÅŸtirir.
    """
    
    def __init__(self, attack_enabled: bool = False):
        """
        Args:
            attack_enabled: SaldÄ±rÄ± aktif mi?
        """
        self.attack_enabled = attack_enabled
        self.manipulation_mode = "fixed"  # "fixed", "random", "gradual"
        
        # SaldÄ±rÄ± parametreleri
        self.fake_soc_value = 30.0  # Sahte SOC deÄŸeri
        self.fake_temp_value = None  # None ise deÄŸiÅŸtirme
        
        # Ä°statistikler
        self.total_messages_intercepted = 0
        self.total_messages_manipulated = 0
        self.manipulation_log = []
        
    def enable_attack(self, mode: str = "fixed", fake_soc: float = 30.0):
        """
        SaldÄ±rÄ±yÄ± aktif et
        
        Args:
            mode: ManipÃ¼lasyon modu ("fixed", "random", "gradual")
            fake_soc: Sahte SOC deÄŸeri (mode="fixed" iÃ§in)
        """
        self.attack_enabled = True
        self.manipulation_mode = mode
        self.fake_soc_value = fake_soc
        print(f"\n{'='*60}")
        print(f"ğŸ”´ ATTACK ENABLED")
        print(f"   Mode: {mode}")
        print(f"   Fake SOC: {fake_soc}%")
        print(f"{'='*60}\n")
    
    def disable_attack(self):
        """SaldÄ±rÄ±yÄ± deaktif et"""
        self.attack_enabled = False
        print(f"\n{'='*60}")
        print(f"ğŸŸ¢ ATTACK DISABLED")
        print(f"{'='*60}\n")
    
    def intercept_message(self, message: Dict) -> Dict:
        """
        OCPP mesajÄ±nÄ± yakala ve manipÃ¼le et
        
        Args:
            message: Orijinal OCPP mesajÄ±
            
        Returns:
            ManipÃ¼le edilmiÅŸ mesaj
        """
        self.total_messages_intercepted += 1
        
        if not self.attack_enabled:
            return message
        
        # Sadece StatusNotification mesajlarÄ±nÄ± manipÃ¼le et
        if message.get("message_type") != "StatusNotification":
            return message
        
        if "battery_data" not in message:
            return message
        
        # Orijinal deÄŸerleri kaydet
        original_soc = message["battery_data"]["soc"]
        original_temp = message["battery_data"]["temperature"]
        
        # ManipÃ¼lasyon uygula
        manipulated_message = message.copy()
        manipulated_message["battery_data"] = message["battery_data"].copy()
        
        if self.manipulation_mode == "fixed":
            # Sabit deÄŸer
            manipulated_message["battery_data"]["soc"] = self.fake_soc_value
            
        elif self.manipulation_mode == "random":
            # Rastgele dÃ¼ÅŸÃ¼k deÄŸer (20-40 arasÄ±)
            manipulated_message["battery_data"]["soc"] = random.uniform(20.0, 40.0)
            
        elif self.manipulation_mode == "gradual":
            # Kademeli manipÃ¼lasyon (gerÃ§ek deÄŸerden yavaÅŸÃ§a uzaklaÅŸ)
            if hasattr(self, '_last_fake_soc'):
                self._last_fake_soc = max(20.0, self._last_fake_soc - 0.5)
            else:
                self._last_fake_soc = original_soc * 0.8
            manipulated_message["battery_data"]["soc"] = self._last_fake_soc
        
        # SÄ±caklÄ±k manipÃ¼lasyonu (opsiyonel)
        if self.fake_temp_value is not None:
            manipulated_message["battery_data"]["temperature"] = self.fake_temp_value
        
        # ManipÃ¼lasyonu kaydet
        self.total_messages_manipulated += 1
        self._log_manipulation(
            original_soc=original_soc,
            fake_soc=manipulated_message["battery_data"]["soc"],
            original_temp=original_temp,
            fake_temp=manipulated_message["battery_data"].get("temperature", original_temp)
        )
        
        # Konsola yazdÄ±r
        print(f"âš ï¸  MESSAGE MANIPULATED:")
        print(f"   Original SOC: {original_soc}% â†’ Fake SOC: {manipulated_message['battery_data']['soc']}%")
        if self.fake_temp_value is not None:
            print(f"   Original Temp: {original_temp}Â°C â†’ Fake Temp: {manipulated_message['battery_data']['temperature']}Â°C")
        
        return manipulated_message
    
    def _log_manipulation(self, original_soc: float, fake_soc: float, 
                         original_temp: float, fake_temp: float):
        """ManipÃ¼lasyonu kaydet"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_soc": original_soc,
            "fake_soc": fake_soc,
            "soc_diff": original_soc - fake_soc,
            "original_temp": original_temp,
            "fake_temp": fake_temp,
            "temp_diff": original_temp - fake_temp
        }
        self.manipulation_log.append(log_entry)
    
    def get_statistics(self) -> Dict:
        """SaldÄ±rÄ± istatistiklerini dÃ¶ndÃ¼r"""
        return {
            "attack_enabled": self.attack_enabled,
            "manipulation_mode": self.manipulation_mode,
            "total_messages_intercepted": self.total_messages_intercepted,
            "total_messages_manipulated": self.total_messages_manipulated,
            "manipulation_rate": (
                self.total_messages_manipulated / self.total_messages_intercepted * 100
                if self.total_messages_intercepted > 0 else 0
            )
        }
    
    def get_manipulation_log(self, limit: int = 10) -> list:
        """ManipÃ¼lasyon logunu dÃ¶ndÃ¼r"""
        return self.manipulation_log[-limit:]
    
    def clear_log(self):
        """Logu temizle"""
        self.manipulation_log.clear()
        self.total_messages_intercepted = 0
        self.total_messages_manipulated = 0


class AdvancedSOCAttack:
    """
    GeliÅŸmiÅŸ SOC SaldÄ±rÄ± SenaryolarÄ±
    """
    
    @staticmethod
    def slow_poison_attack(message: Dict, threshold_soc: float = 90.0) -> Dict:
        """
        YavaÅŸ zehirleme saldÄ±rÄ±sÄ±
        SOC yÃ¼ksek olana kadar normal davran, sonra manipÃ¼le et
        """
        if "battery_data" not in message:
            return message
        
        real_soc = message["battery_data"]["soc"]
        
        if real_soc >= threshold_soc:
            # SOC yÃ¼ksekse, dÃ¼ÅŸÃ¼k gÃ¶ster
            message["battery_data"]["soc"] = threshold_soc - 20.0
            print(f"ğŸ•·ï¸  SLOW POISON: Real SOC {real_soc}% â†’ Fake {message['battery_data']['soc']}%")
        
        return message
    
    @staticmethod
    def replay_attack(message: Dict, cached_soc: float = 30.0) -> Dict:
        """
        Replay saldÄ±rÄ±sÄ±
        Eski (dÃ¼ÅŸÃ¼k) SOC deÄŸerini tekrar gÃ¶nder
        """
        if "battery_data" in message:
            original_soc = message["battery_data"]["soc"]
            message["battery_data"]["soc"] = cached_soc
            print(f"ğŸ” REPLAY: Real SOC {original_soc}% â†’ Cached {cached_soc}%")
        
        return message
    
    @staticmethod
    def temperature_hiding_attack(message: Dict, fake_temp: float = 25.0) -> Dict:
        """
        SÄ±caklÄ±k gizleme saldÄ±rÄ±sÄ±
        YÃ¼ksek sÄ±caklÄ±ÄŸÄ± dÃ¼ÅŸÃ¼k gÃ¶ster
        """
        if "battery_data" in message:
            original_temp = message["battery_data"]["temperature"]
            if original_temp > 40.0:
                message["battery_data"]["temperature"] = fake_temp
                print(f"ğŸŒ¡ï¸  TEMP HIDING: Real {original_temp}Â°C â†’ Fake {fake_temp}Â°C")
        
        return message


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from bms.battery import Battery
    from ocpp.vehicle_client import VehicleClient
    
    print("=== SOC Manipulation Attack Test ===\n")
    
    # Test 1: Fixed mode saldÄ±rÄ±
    print("TEST 1: Fixed Mode Attack")
    print("-" * 50)
    
    battery = Battery(initial_soc=85.0)
    vehicle = VehicleClient("EV-VICTIM", battery)
    attacker = SOCManipulator()
    
    vehicle.connect_to_station("STATION-001")
    
    # SaldÄ±rÄ±yÄ± aktif et
    attacker.enable_attack(mode="fixed", fake_soc=30.0)
    
    # Mesaj gÃ¶nder (saldÄ±rgan proxy Ã¼zerinden)
    original_msg = vehicle.send_status_notification()
    manipulated_msg = attacker.intercept_message(original_msg)
    
    print(f"\nOriginal Message SOC: {original_msg['battery_data']['soc']}%")
    print(f"Manipulated Message SOC: {manipulated_msg['battery_data']['soc']}%")
    print(f"âš ï¸  Difference: {original_msg['battery_data']['soc'] - manipulated_msg['battery_data']['soc']}%\n")
    
    # Test 2: Random mode saldÄ±rÄ±
    print("\nTEST 2: Random Mode Attack")
    print("-" * 50)
    
    attacker.disable_attack()
    attacker.enable_attack(mode="random")
    
    print("\n5 random manipulations:")
    for i in range(5):
        battery.soc = 90.0 + i  # SOC'u artÄ±r
        original_msg = vehicle.send_status_notification()
        manipulated_msg = attacker.intercept_message(original_msg)
        print(f"  {i+1}. Real: {original_msg['battery_data']['soc']}% â†’ Fake: {manipulated_msg['battery_data']['soc']}%")
    
    # Ä°statistikler
    print("\n\nAttack Statistics:")
    stats = attacker.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
