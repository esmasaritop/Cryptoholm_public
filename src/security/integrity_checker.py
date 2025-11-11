"""
Integrity Checker - Veri BÃ¼tÃ¼nlÃ¼ÄŸÃ¼ KontrolÃ¼
Mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ ve tutarlÄ±lÄ±k kontrolÃ¼
"""

from typing import Dict, List, Optional
from datetime import datetime
import json


class IntegrityChecker:
    """
    Veri bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ ve tutarlÄ±lÄ±k kontrolÃ¼
    - Mesaj doÄŸrulama
    - Anomali tespiti
    - TutarlÄ±lÄ±k kontrolleri
    """
    
    def __init__(self):
        """Initialize integrity checker"""
        # GeÃ§miÅŸ deÄŸerler (anomali tespiti iÃ§in)
        self.history = {
            "soc": [],
            "temperature": [],
            "voltage": [],
            "current": []
        }
        
        # Anomali eÅŸikleri
        self.thresholds = {
            "soc_jump": 10.0,  # SOC'da ani deÄŸiÅŸim eÅŸiÄŸi (%)
            "temp_jump": 10.0,  # SÄ±caklÄ±kta ani deÄŸiÅŸim eÅŸiÄŸi (Â°C)
            "voltage_jump": 50.0,  # Voltajda ani deÄŸiÅŸim eÅŸiÄŸi (V)
        }
        
        # Fiziksel limitler
        self.limits = {
            "soc_min": 0.0,
            "soc_max": 100.0,
            "temp_min": -20.0,
            "temp_max": 100.0,
            "voltage_min": 200.0,
            "voltage_max": 500.0,
            "current_min": 0.0,
            "current_max": 300.0
        }
        
        # Tespit edilen anomaliler
        self.detected_anomalies = []
        
    def check_message_integrity(self, message: Dict) -> Dict:
        """
        Mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼nÃ¼ kontrol et
        
        Args:
            message: OCPP mesajÄ±
            
        Returns:
            Kontrol sonucu
        """
        result = {
            "valid": True,
            "checks": {},
            "anomalies": [],
            "warnings": []
        }
        
        # Gerekli alanlarÄ± kontrol et
        required_fields = ["message_type", "timestamp"]
        for field in required_fields:
            if field not in message:
                result["valid"] = False
                result["anomalies"].append(f"Missing required field: {field}")
        
        # Batarya verilerini kontrol et
        if "battery_data" in message:
            battery_check = self._check_battery_data(message["battery_data"])
            result["checks"]["battery_data"] = battery_check
            
            if not battery_check["valid"]:
                result["valid"] = False
                result["anomalies"].extend(battery_check["anomalies"])
            
            if battery_check.get("warnings"):
                result["warnings"].extend(battery_check["warnings"])
        
        return result
    
    def _check_battery_data(self, battery_data: Dict) -> Dict:
        """Batarya verilerini kontrol et"""
        result = {
            "valid": True,
            "anomalies": [],
            "warnings": []
        }
        
        # SOC kontrolÃ¼
        if "soc" in battery_data:
            soc = battery_data["soc"]
            
            # Limit kontrolÃ¼
            if soc < self.limits["soc_min"] or soc > self.limits["soc_max"]:
                result["valid"] = False
                result["anomalies"].append(
                    f"SOC out of range: {soc}% (valid: {self.limits['soc_min']}-{self.limits['soc_max']}%)"
                )
            
            # Ani deÄŸiÅŸim kontrolÃ¼
            if self.history["soc"]:
                last_soc = self.history["soc"][-1]
                soc_change = abs(soc - last_soc)
                
                if soc_change > self.thresholds["soc_jump"]:
                    result["warnings"].append(
                        f"Sudden SOC change: {last_soc}% â†’ {soc}% (change: {soc_change}%)"
                    )
                    result["anomalies"].append({
                        "type": "SOC_JUMP",
                        "previous": last_soc,
                        "current": soc,
                        "change": soc_change
                    })
            
            # GeÃ§miÅŸe ekle
            self.history["soc"].append(soc)
            if len(self.history["soc"]) > 100:
                self.history["soc"].pop(0)
        
        # SÄ±caklÄ±k kontrolÃ¼
        if "temperature" in battery_data:
            temp = battery_data["temperature"]
            
            # Limit kontrolÃ¼
            if temp < self.limits["temp_min"] or temp > self.limits["temp_max"]:
                result["valid"] = False
                result["anomalies"].append(
                    f"Temperature out of range: {temp}Â°C (valid: {self.limits['temp_min']}-{self.limits['temp_max']}Â°C)"
                )
            
            # Ani deÄŸiÅŸim kontrolÃ¼
            if self.history["temperature"]:
                last_temp = self.history["temperature"][-1]
                temp_change = abs(temp - last_temp)
                
                if temp_change > self.thresholds["temp_jump"]:
                    result["warnings"].append(
                        f"Sudden temperature change: {last_temp}Â°C â†’ {temp}Â°C (change: {temp_change}Â°C)"
                    )
                    result["anomalies"].append({
                        "type": "TEMP_JUMP",
                        "previous": last_temp,
                        "current": temp,
                        "change": temp_change
                    })
            
            # GeÃ§miÅŸe ekle
            self.history["temperature"].append(temp)
            if len(self.history["temperature"]) > 100:
                self.history["temperature"].pop(0)
        
        # Voltaj kontrolÃ¼
        if "voltage" in battery_data:
            voltage = battery_data["voltage"]
            
            if voltage < self.limits["voltage_min"] or voltage > self.limits["voltage_max"]:
                result["valid"] = False
                result["anomalies"].append(
                    f"Voltage out of range: {voltage}V (valid: {self.limits['voltage_min']}-{self.limits['voltage_max']}V)"
                )
            
            self.history["voltage"].append(voltage)
            if len(self.history["voltage"]) > 100:
                self.history["voltage"].pop(0)
        
        # AkÄ±m kontrolÃ¼
        if "current" in battery_data:
            current = battery_data["current"]
            
            if current < self.limits["current_min"] or current > self.limits["current_max"]:
                result["valid"] = False
                result["anomalies"].append(
                    f"Current out of range: {current}A (valid: {self.limits['current_min']}-{self.limits['current_max']}A)"
                )
            
            self.history["current"].append(current)
            if len(self.history["current"]) > 100:
                self.history["current"].pop(0)
        
        # Fiziksel tutarlÄ±lÄ±k kontrolÃ¼
        if "soc" in battery_data and "voltage" in battery_data:
            # SOC ve voltaj arasÄ±ndaki iliÅŸki
            soc = battery_data["soc"]
            voltage = battery_data["voltage"]
            
            # Basit lineer model (gerÃ§ekte daha karmaÅŸÄ±k olur)
            expected_voltage = self.limits["voltage_min"] + (
                (soc / 100.0) * (self.limits["voltage_max"] - self.limits["voltage_min"])
            )
            
            voltage_diff = abs(voltage - expected_voltage)
            if voltage_diff > 50.0:  # 50V tolerans
                result["warnings"].append(
                    f"SOC-Voltage inconsistency: SOC={soc}%, Voltage={voltage}V, "
                    f"Expectedâ‰ˆ{expected_voltage:.1f}V"
                )
        
        return result
    
    def detect_manipulation_patterns(self, messages: List[Dict]) -> Dict:
        """
        ManipÃ¼lasyon paternlerini tespit et
        
        Args:
            messages: Mesaj listesi
            
        Returns:
            Tespit edilen paternler
        """
        patterns = {
            "suspicious_patterns": [],
            "manipulation_likelihood": 0.0
        }
        
        if len(messages) < 3:
            return patterns
        
        # Pattern 1: SOC sÃ¼rekli dÃ¼ÅŸÃ¼k kalÄ±yor
        soc_values = []
        for msg in messages:
            if "battery_data" in msg and "soc" in msg["battery_data"]:
                soc_values.append(msg["battery_data"]["soc"])
        
        if len(soc_values) >= 3:
            # SOC deÄŸiÅŸmiyorsa ÅŸÃ¼pheli
            soc_variance = max(soc_values) - min(soc_values)
            if soc_variance < 1.0:  # %1'den az deÄŸiÅŸim
                patterns["suspicious_patterns"].append({
                    "type": "STATIC_SOC",
                    "description": "SOC values remain constant",
                    "severity": "HIGH"
                })
                patterns["manipulation_likelihood"] += 0.4
            
            # SOC azalÄ±yorsa (ÅŸarj sÄ±rasÄ±nda)
            if all(soc_values[i] >= soc_values[i+1] for i in range(len(soc_values)-1)):
                patterns["suspicious_patterns"].append({
                    "type": "DECREASING_SOC",
                    "description": "SOC decreasing during charging",
                    "severity": "CRITICAL"
                })
                patterns["manipulation_likelihood"] += 0.5
        
        # Pattern 2: Ani SOC dÃ¼ÅŸÃ¼ÅŸÃ¼
        for i in range(1, len(soc_values)):
            if soc_values[i-1] - soc_values[i] > 20.0:
                patterns["suspicious_patterns"].append({
                    "type": "SUDDEN_SOC_DROP",
                    "description": f"SOC dropped from {soc_values[i-1]}% to {soc_values[i]}%",
                    "severity": "CRITICAL"
                })
                patterns["manipulation_likelihood"] += 0.3
        
        # Manipulation likelihood hesapla
        patterns["manipulation_likelihood"] = min(1.0, patterns["manipulation_likelihood"])
        
        return patterns
    
    def get_statistics(self) -> Dict:
        """Ä°statistikleri dÃ¶ndÃ¼r"""
        return {
            "history_size": {
                "soc": len(self.history["soc"]),
                "temperature": len(self.history["temperature"]),
                "voltage": len(self.history["voltage"]),
                "current": len(self.history["current"])
            },
            "detected_anomalies": len(self.detected_anomalies)
        }
    
    def clear_history(self):
        """GeÃ§miÅŸi temizle"""
        for key in self.history:
            self.history[key].clear()
        self.detected_anomalies.clear()


if __name__ == "__main__":
    print("=== Integrity Checker Test ===\n")
    
    checker = IntegrityChecker()
    
    # Test 1: Normal mesaj
    print("TEST 1: Normal message")
    print("-" * 50)
    normal_msg = {
        "message_type": "StatusNotification",
        "timestamp": datetime.now().isoformat(),
        "battery_data": {
            "soc": 50.0,
            "voltage": 350.0,
            "current": 100.0,
            "temperature": 30.0
        }
    }
    
    result = checker.check_message_integrity(normal_msg)
    print(f"Valid: {result['valid']}")
    print(f"Anomalies: {len(result['anomalies'])}")
    print()
    
    # Test 2: ManipÃ¼le edilmiÅŸ mesaj (SOC jump)
    print("\nTEST 2: Manipulated message (SOC jump)")
    print("-" * 50)
    
    # BirkaÃ§ normal mesaj ekle
    for soc in [50, 51, 52]:
        msg = normal_msg.copy()
        msg["battery_data"] = {"soc": soc, "voltage": 350.0, "temperature": 30.0}
        checker.check_message_integrity(msg)
    
    # Ani SOC dÃ¼ÅŸÃ¼ÅŸÃ¼
    manipulated_msg = {
        "message_type": "StatusNotification",
        "timestamp": datetime.now().isoformat(),
        "battery_data": {
            "soc": 25.0,  # 52'den 25'e dÃ¼ÅŸtÃ¼!
            "voltage": 350.0,
            "temperature": 30.0
        }
    }
    
    result = checker.check_message_integrity(manipulated_msg)
    print(f"Valid: {result['valid']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Anomalies: {result['anomalies']}")
    print()
    
    # Test 3: Pattern detection
    print("\nTEST 3: Manipulation pattern detection")
    print("-" * 50)
    
    messages = []
    for i in range(5):
        messages.append({
            "battery_data": {"soc": 30.0}  # SOC sabit kalÄ±yor
        })
    
    patterns = checker.detect_manipulation_patterns(messages)
    print(f"Suspicious patterns: {len(patterns['suspicious_patterns'])}")
    print(f"Manipulation likelihood: {patterns['manipulation_likelihood']*100:.1f}%")
    
    for pattern in patterns['suspicious_patterns']:
        print(f"\n  Pattern: {pattern['type']}")
        print(f"  Description: {pattern['description']}")
        print(f"  Severity: {pattern['severity']}")
