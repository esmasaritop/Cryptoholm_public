"""
Test Suite - Vulnerable System Tests
Zafiyet testleri
"""

import sys
import pytest
sys.path.append('..')

from src.bms.battery import Battery
from src.bms.bms_controller import BMSController
from src.ocpp.vehicle_client import VehicleClient
from src.ocpp.charging_station import ChargingStation
from src.attack.soc_manipulator import SOCManipulator
from src.attack.mitm_proxy import MITMProxy


class TestVulnerableSystem:
    \"\"\"Zafiyet sistem testleri\"\"\"
    
    def setup_method(self):
        \"\"\"Her test Ã¶ncesi Ã§alÄ±ÅŸÄ±r\"\"\"
        self.battery = Battery(initial_soc=30.0)
        self.bms = BMSController(self.battery, secure_mode=False)
        self.vehicle = VehicleClient("TEST-VEHICLE", self.battery, self.bms)
        self.station = ChargingStation("TEST-STATION")
        
    def test_battery_charging(self):
        \"\"\"Normal batarya ÅŸarjÄ± testi\"\"\"
        initial_soc = self.battery.soc
        self.battery.charge(power_kw=50.0, duration_seconds=10.0)
        
        assert self.battery.soc > initial_soc
        assert self.battery.is_charging is True
        
    def test_bms_without_security(self):
        \"\"\"BMS gÃ¼venlik kontrolÃ¼ olmadan\"\"\"
        assert self.bms.secure_mode is False
        
        # ManipÃ¼le edilmiÅŸ SOC deÄŸeri
        result = self.bms.validate_charging_request(
            reported_soc=30.0,  # Sahte deÄŸer
            reported_temp=25.0
        )
        
        # GÃ¼venlik kapalÄ± olduÄŸu iÃ§in manipÃ¼lasyonu tespit edemez
        # Sadece eÅŸik deÄŸerlerini kontrol eder
        assert result['allow_charging'] is True
        
    def test_soc_manipulation_attack(self):
        \"\"\"SOC manipÃ¼lasyon saldÄ±rÄ±sÄ± testi\"\"\"
        attacker = SOCManipulator()
        attacker.enable_attack(mode="fixed", fake_soc=30.0)
        
        # GerÃ§ek SOC'u yÃ¼kselt
        self.battery.soc = 95.0
        
        # Mesaj oluÅŸtur
        message = {
            "message_type": "StatusNotification",
            "battery_data": {
                "soc": self.battery.soc,
                "temperature": self.battery.temperature
            }
        }
        
        # SaldÄ±rgan manipÃ¼le eder
        manipulated = attacker.intercept_message(message)
        
        # SOC manipÃ¼le edildi mi?
        assert manipulated['battery_data']['soc'] == 30.0
        assert manipulated['battery_data']['soc'] != self.battery.soc
        
    def test_overcharge_vulnerability(self):
        \"\"\"AÅŸÄ±rÄ± ÅŸarj zafiyeti testi\"\"\"
        # BataryayÄ± %95'e getir
        self.battery.soc = 95.0
        
        # BMS kontrolÃ¼ (gÃ¼venli mod kapalÄ±)
        result = self.bms.validate_charging_request(
            reported_soc=30.0,  # Sahte SOC
            reported_temp=25.0
        )
        
        # GÃ¼venlik kapalÄ± - manipÃ¼lasyonu tespit edemez
        assert result['allow_charging'] is True  # Åarja izin verir!
        
        # Åarj devam eder ve aÅŸÄ±rÄ± ÅŸarj oluÅŸur
        self.battery.charge(power_kw=50.0, duration_seconds=30.0)
        
        # AÅŸÄ±rÄ± ÅŸarj tespit edildi mi?
        assert self.battery.soc > 100.0
        assert self.battery.overcharge_detected is True
        
    def test_mitm_proxy_interception(self):
        \"\"\"MITM proxy yakalama testi\"\"\"
        proxy = MITMProxy("TEST-ATTACKER")
        attacker = SOCManipulator()
        
        proxy.activate()
        attacker.enable_attack(mode="fixed", fake_soc=25.0)
        proxy.add_manipulation(attacker.intercept_message)
        
        # Mesaj oluÅŸtur
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 90.0, "temperature": 30.0}
        }
        
        # Proxy Ã¼zerinden geÃ§ir
        result = proxy.intercept_vehicle_to_station(message)
        
        # ManipÃ¼le edildi mi?
        assert result['battery_data']['soc'] == 25.0
        assert proxy.total_manipulated > 0
        
    def test_temperature_rise_during_overcharge(self):
        \"\"\"AÅŸÄ±rÄ± ÅŸarj sÄ±rasÄ±nda sÄ±caklÄ±k artÄ±ÅŸÄ± testi\"\"\"
        self.battery.soc = 100.0
        initial_temp = self.battery.temperature
        
        # AÅŸÄ±rÄ± ÅŸarj
        self.battery.charge(power_kw=50.0, duration_seconds=10.0)
        
        # SÄ±caklÄ±k arttÄ± mÄ±?
        assert self.battery.temperature > initial_temp
        assert self.battery.soc > 100.0
        
    def test_health_degradation(self):
        \"\"\"Batarya saÄŸlÄ±k bozulmasÄ± testi\"\"\"
        initial_health = self.battery.health_percentage
        self.battery.soc = 100.0
        
        # AÅŸÄ±rÄ± ÅŸarj yap
        for _ in range(10):
            self.battery.charge(power_kw=50.0, duration_seconds=1.0)
        
        # SaÄŸlÄ±k azaldÄ± mÄ±?
        assert self.battery.health_percentage < initial_health


class TestAttackVectors:
    \"\"\"SaldÄ±rÄ± vektÃ¶rÃ¼ testleri\"\"\"
    
    def test_replay_attack(self):
        \"\"\"Replay saldÄ±rÄ±sÄ± testi\"\"\"
        from src.attack.soc_manipulator import AdvancedSOCAttack
        
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 90.0, "temperature": 35.0}
        }
        
        # Replay attack uygula
        result = AdvancedSOCAttack.replay_attack(message, cached_soc=30.0)
        
        assert result['battery_data']['soc'] == 30.0
        
    def test_slow_poison_attack(self):
        \"\"\"YavaÅŸ zehirleme saldÄ±rÄ±sÄ± testi\"\"\"
        from src.attack.soc_manipulator import AdvancedSOCAttack
        
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 92.0, "temperature": 35.0}
        }
        
        # Slow poison (SOC > 90 ise manipÃ¼le et)
        result = AdvancedSOCAttack.slow_poison_attack(message, threshold_soc=90.0)
        
        # SOC yÃ¼ksek olduÄŸu iÃ§in manipÃ¼le edilmeli
        assert result['battery_data']['soc'] < 92.0
        
    def test_temperature_hiding(self):
        \"\"\"SÄ±caklÄ±k gizleme saldÄ±rÄ±sÄ± testi\"\"\"
        from src.attack.soc_manipulator import AdvancedSOCAttack
        
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 85.0, "temperature": 55.0}  # YÃ¼ksek sÄ±caklÄ±k
        }
        
        result = AdvancedSOCAttack.temperature_hiding_attack(message, fake_temp=25.0)
        
        # SÄ±caklÄ±k gizlendi mi?
        assert result['battery_data']['temperature'] == 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
