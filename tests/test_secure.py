"""
Test Suite - Secure System Tests
GÃ¼venli sistem testleri
"""

import sys
import pytest
sys.path.append('..')

from src.bms.battery import Battery
from src.bms.bms_controller import BMSController
from src.security.crypto_handler import CryptoHandler
from src.security.integrity_checker import IntegrityChecker
from datetime import datetime, timedelta


class TestSecureSystem:
    \"\"\"GÃ¼venli sistem testleri\"\"\"
    
    def setup_method(self):
        \"\"\"Her test Ã¶ncesi Ã§alÄ±ÅŸÄ±r\"\"\"
        self.battery = Battery(initial_soc=30.0)
        self.bms = BMSController(self.battery, secure_mode=True)
        self.crypto = CryptoHandler(secret_key="test-secret-key")
        self.integrity_checker = IntegrityChecker()
        
    def test_bms_secure_mode(self):
        \"\"\"BMS gÃ¼venli mod testi\"\"\"
        assert self.bms.secure_mode is True
        
        # BaÄŸÄ±msÄ±z sensÃ¶r gÃ¼ncellemesi
        self.bms.update_independent_sensors()
        assert self.bms.independent_soc is not None
        assert self.bms.independent_temperature is not None
        
    def test_soc_manipulation_detection(self):
        \"\"\"SOC manipÃ¼lasyonu tespit testi\"\"\"
        # Batarya SOC'u yÃ¼ksek
        self.battery.soc = 90.0
        
        # Ama saldÄ±rgan dÃ¼ÅŸÃ¼k bildiriyor
        result = self.bms.validate_charging_request(
            reported_soc=30.0,  # Sahte SOC
            reported_temp=25.0
        )
        
        # GÃ¼venli mod - manipÃ¼lasyonu tespit etmeli
        assert result['valid'] is False
        assert result['reason'] == "SOC manipulation detected"
        assert len(result['alerts']) > 0
        
    def test_hmac_verification(self):
        \"\"\"HMAC doÄŸrulama testi\"\"\"
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 50.0}
        }
        
        # HMAC hesapla
        hmac_value = self.crypto.calculate_hmac(message)
        
        # DoÄŸrula
        assert self.crypto.verify_hmac(message, hmac_value) is True
        
        # ManipÃ¼le edilmiÅŸ mesaj
        manipulated = message.copy()
        manipulated['battery_data'] = {"soc": 30.0}
        
        # HMAC uyuÅŸmamalÄ±
        assert self.crypto.verify_hmac(manipulated, hmac_value) is False
        
    def test_digital_signature(self):
        \"\"\"Dijital imza testi\"\"\"
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 50.0}
        }
        
        # Ä°mzala
        signature = self.crypto.sign_message(message)
        
        # DoÄŸrula
        assert self.crypto.verify_signature(message, signature) is True
        
        # ManipÃ¼le edilmiÅŸ mesaj
        manipulated = message.copy()
        manipulated['battery_data'] = {"soc": 30.0}
        
        # Ä°mza geÃ§ersiz olmalÄ±
        assert self.crypto.verify_signature(manipulated, signature) is False
        
    def test_security_fields(self):
        \"\"\"GÃ¼venlik alanlarÄ± testi\"\"\"
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 50.0}
        }
        
        # GÃ¼venlik alanlarÄ± ekle
        secure_msg = self.crypto.add_security_fields(message)
        
        # Alanlar eklendi mi?
        assert 'timestamp' in secure_msg
        assert 'nonce' in secure_msg
        assert 'hmac' in secure_msg
        assert 'signature' in secure_msg
        
        # DoÄŸrula
        verification = self.crypto.verify_message_security(secure_msg)
        assert verification['valid'] is True
        assert verification['checks']['hmac'] is True
        assert verification['checks']['signature'] is True
        
    def test_timestamp_validation(self):
        \"\"\"Zaman damgasÄ± doÄŸrulama testi (replay attack korumasÄ±)\"\"\"
        message = {
            "message_type": "StatusNotification",
            "timestamp": (datetime.now() - timedelta(seconds=120)).isoformat(),
            "battery_data": {"soc": 50.0}
        }
        
        # GÃ¼venlik alanlarÄ± ekle
        msg_for_hmac = {k: v for k, v in message.items() if k not in ['hmac', 'signature']}
        message['hmac'] = self.crypto.calculate_hmac(msg_for_hmac)
        signature = self.crypto.sign_message(msg_for_hmac)
        message['signature'] = signature.hex()
        
        # DoÄŸrula
        verification = self.crypto.verify_message_security(message)
        
        # Zaman aÅŸÄ±mÄ± nedeniyle geÃ§ersiz olmalÄ±
        assert verification['valid'] is False
        assert verification['checks']['timestamp'] is False
        
    def test_manipulation_after_signing(self):
        \"\"\"Ä°mzalama sonrasÄ± manipÃ¼lasyon testi\"\"\"
        message = {
            "message_type": "StatusNotification",
            "battery_data": {"soc": 90.0, "temperature": 35.0}
        }
        
        # GÃ¼venli mesaj oluÅŸtur
        secure_msg = self.crypto.add_security_fields(message)
        
        # DoÄŸrulama baÅŸarÄ±lÄ±
        assert self.crypto.verify_message_security(secure_msg)['valid'] is True
        
        # Åimdi saldÄ±rgan manipÃ¼le etmeye Ã§alÄ±ÅŸÄ±r
        secure_msg['battery_data']['soc'] = 30.0
        
        # DoÄŸrulama baÅŸarÄ±sÄ±z olmalÄ±
        verification = self.crypto.verify_message_security(secure_msg)
        assert verification['valid'] is False
        
    def test_integrity_checking(self):
        \"\"\"Veri bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ kontrolÃ¼ testi\"\"\"
        message = {
            "message_type": "StatusNotification",
            "timestamp": datetime.now().isoformat(),
            "battery_data": {
                "soc": 50.0,
                "voltage": 350.0,
                "current": 100.0,
                "temperature": 30.0
            }
        }
        
        result = self.integrity_checker.check_message_integrity(message)
        
        assert result['valid'] is True
        assert 'battery_data' in result['checks']
        
    def test_anomaly_detection(self):
        \"\"\"Anomali tespiti testi\"\"\"
        # Normal deÄŸerler
        for soc in [50, 51, 52, 53]:
            message = {
                "battery_data": {"soc": soc, "temperature": 30.0, "voltage": 350.0}
            }
            self.integrity_checker.check_message_integrity(message)
        
        # Ani SOC dÃ¼ÅŸÃ¼ÅŸÃ¼
        abnormal_message = {
            "battery_data": {"soc": 25.0, "temperature": 30.0, "voltage": 350.0}
        }
        
        result = self.integrity_checker.check_message_integrity(abnormal_message)
        
        # UyarÄ± olmalÄ±
        assert len(result['warnings']) > 0
        
    def test_pattern_detection(self):
        \"\"\"ManipÃ¼lasyon pattern tespiti testi\"\"\"
        messages = []
        
        # SOC sabit kalÄ±yor (manipÃ¼lasyon!)
        for i in range(10):
            messages.append({
                "battery_data": {"soc": 30.0}
            })
        
        patterns = self.integrity_checker.detect_manipulation_patterns(messages)
        
        # Pattern tespit edilmeli
        assert len(patterns['suspicious_patterns']) > 0
        assert patterns['manipulation_likelihood'] > 0.0
        
    def test_overcharge_prevention(self):
        \"\"\"AÅŸÄ±rÄ± ÅŸarj Ã¶nleme testi\"\"\"
        # BataryayÄ± %95'e getir
        self.battery.soc = 95.0
        
        # BMS kontrolÃ¼ (gÃ¼venli mod aÃ§Ä±k)
        result = self.bms.validate_charging_request(
            reported_soc=95.0,
            reported_temp=30.0
        )
        
        # Åarja izin vermemeli
        assert result['allow_charging'] is False
        assert result['reason'] == "SOC limit reached"


class TestCryptographicAttackResistance:
    \"\"\"Kriptografik saldÄ±rÄ± direnci testleri\"\"\"
    
    def setup_method(self):
        self.crypto = CryptoHandler()
        
    def test_hmac_tampering_resistance(self):
        \"\"\"HMAC deÄŸiÅŸtirme direnci\"\"\"
        message = {"data": "test"}
        hmac_value = self.crypto.calculate_hmac(message)
        
        # HMAC'i deÄŸiÅŸtir
        fake_hmac = "0" * 64
        
        assert self.crypto.verify_hmac(message, fake_hmac) is False
        
    def test_signature_forgery_resistance(self):
        \"\"\"Ä°mza sahteciliÄŸi direnci\"\"\"
        message = {"data": "test"}
        
        # Sahte imza
        fake_signature = b"fake_signature"
        
        assert self.crypto.verify_signature(message, fake_signature) is False
        
    def test_replay_attack_resistance(self):
        \"\"\"Replay attack direnci\"\"\"
        message = {
            "timestamp": (datetime.now() - timedelta(seconds=200)).isoformat(),
            "data": "test"
        }
        
        secure_msg = self.crypto.add_security_fields(message)
        
        # Eski mesaj reddedilmeli
        verification = self.crypto.verify_message_security(secure_msg, check_timestamp=True)
        assert verification['valid'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
