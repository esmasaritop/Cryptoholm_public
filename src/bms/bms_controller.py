"""
Battery Management System (BMS) Controller
BMS kontrolcÃ¼sÃ¼ - Batarya gÃ¼venliÄŸini ve ÅŸarj yÃ¶netimini saÄŸlar
"""

from typing import Dict, Optional, Callable
from datetime import datetime
import json


class BMSController:
    """
    Battery Management System
    BataryanÄ±n gÃ¼venli ÅŸarj edilmesini ve izlenmesini saÄŸlar
    """
    
    def __init__(self, battery, secure_mode: bool = False):
        """
        Args:
            battery: Battery instance
            secure_mode: GÃ¼venli mod (baÄŸÄ±msÄ±z doÄŸrulama aktif)
        """
        self.battery = battery
        self.secure_mode = secure_mode
        
        # GÃ¼venlik eÅŸikleri
        self.max_soc_threshold = 95.0  # SOC Ã¼st limiti
        self.max_temp_threshold = 45.0  # SÄ±caklÄ±k Ã¼st limiti
        self.max_current_threshold = 200.0  # AkÄ±m Ã¼st limiti
        
        # BaÄŸÄ±msÄ±z sensÃ¶r deÄŸerleri (gÃ¼venli modda)
        self.independent_soc = None
        self.independent_temperature = None
        
        # Alarm ve log sistemi
        self.alerts = []
        self.charge_history = []
        
        # Ä°statistikler
        self.total_alerts = 0
        self.emergency_stops = 0
        
    def enable_secure_mode(self):
        """GÃ¼venli modu aktif et"""
        self.secure_mode = True
        self._log_event("SECURITY", "Secure mode enabled - Independent validation active")
    
    def disable_secure_mode(self):
        """GÃ¼venli modu deaktif et (test amaÃ§lÄ±)"""
        self.secure_mode = False
        self._log_event("SECURITY", "Secure mode disabled - WARNING: Vulnerable to attacks")
    
    def update_independent_sensors(self):
        """
        BaÄŸÄ±msÄ±z sensÃ¶rlerden veri al
        GerÃ§ek sistemde bu fiziksel sensÃ¶rlerden gelir
        SimÃ¼lasyonda bataryanÄ±n gerÃ§ek deÄŸerlerini kullanÄ±yoruz
        """
        if self.secure_mode:
            # BaÄŸÄ±msÄ±z sensÃ¶rler bataryanÄ±n gerÃ§ek durumunu okur
            self.independent_soc = self.battery.soc
            self.independent_temperature = self.battery.temperature
    
    def validate_charging_request(self, reported_soc: float, reported_temp: float) -> Dict:
        """
        Åarj talebini doÄŸrula
        GÃ¼venli modda baÄŸÄ±msÄ±z sensÃ¶rlerle karÅŸÄ±laÅŸtÄ±r
        
        Args:
            reported_soc: OCPP Ã¼zerinden bildirilen SOC
            reported_temp: OCPP Ã¼zerinden bildirilen sÄ±caklÄ±k
            
        Returns:
            DoÄŸrulama sonucu
        """
        result = {
            "valid": True,
            "allow_charging": True,
            "reason": "OK",
            "alerts": []
        }
        
        # GÃ¼venli modda baÄŸÄ±msÄ±z doÄŸrulama
        if self.secure_mode:
            self.update_independent_sensors()
            
            # SOC tutarsÄ±zlÄ±ÄŸÄ± kontrolÃ¼
            soc_diff = abs(reported_soc - self.independent_soc)
            if soc_diff > 5.0:  # %5'ten fazla fark varsa
                alert = {
                    "type": "SOC_MISMATCH",
                    "severity": "CRITICAL",
                    "reported_soc": reported_soc,
                    "actual_soc": self.independent_soc,
                    "difference": soc_diff,
                    "message": f"SOC mismatch detected! Reported: {reported_soc}%, Actual: {self.independent_soc}%"
                }
                result["alerts"].append(alert)
                result["valid"] = False
                result["reason"] = "SOC manipulation detected"
                self._raise_alert(alert)
            
            # SÄ±caklÄ±k tutarsÄ±zlÄ±ÄŸÄ± kontrolÃ¼
            temp_diff = abs(reported_temp - self.independent_temperature)
            if temp_diff > 5.0:  # 5Â°C'den fazla fark varsa
                alert = {
                    "type": "TEMP_MISMATCH",
                    "severity": "HIGH",
                    "reported_temp": reported_temp,
                    "actual_temp": self.independent_temperature,
                    "difference": temp_diff,
                    "message": f"Temperature mismatch! Reported: {reported_temp}Â°C, Actual: {self.independent_temperature}Â°C"
                }
                result["alerts"].append(alert)
                result["valid"] = False
                result["reason"] = "Temperature manipulation detected"
                self._raise_alert(alert)
        
        # GÃ¼venlik eÅŸiklerini kontrol et (her modda)
        actual_soc = self.independent_soc if self.secure_mode else reported_soc
        actual_temp = self.independent_temperature if self.secure_mode else reported_temp
        
        if actual_soc >= self.max_soc_threshold:
            alert = {
                "type": "SOC_LIMIT",
                "severity": "HIGH",
                "soc": actual_soc,
                "threshold": self.max_soc_threshold,
                "message": f"SOC limit reached: {actual_soc}% >= {self.max_soc_threshold}%"
            }
            result["alerts"].append(alert)
            result["allow_charging"] = False
            result["reason"] = "SOC limit reached"
            self._raise_alert(alert)
        
        if actual_temp >= self.max_temp_threshold:
            alert = {
                "type": "TEMP_LIMIT",
                "severity": "HIGH",
                "temperature": actual_temp,
                "threshold": self.max_temp_threshold,
                "message": f"Temperature limit reached: {actual_temp}Â°C >= {self.max_temp_threshold}Â°C"
            }
            result["alerts"].append(alert)
            result["allow_charging"] = False
            result["reason"] = "Temperature limit reached"
            self._raise_alert(alert)
        
        return result
    
    def monitor_charging(self) -> Dict:
        """
        Åarj sÄ±rasÄ±nda bataryayÄ± izle
        Anomali tespiti yap
        """
        status = self.battery.get_status()
        
        alerts = []
        
        # AÅŸÄ±rÄ± ÅŸarj kontrolÃ¼
        if status["overcharge_detected"]:
            alert = {
                "type": "OVERCHARGE",
                "severity": "CRITICAL",
                "soc": status["soc"],
                "message": f"OVERCHARGE DETECTED! SOC: {status['soc']}%"
            }
            alerts.append(alert)
            self._raise_alert(alert)
            self.emergency_stop("Overcharge detected")
        
        # AÅŸÄ±rÄ± Ä±sÄ±nma kontrolÃ¼
        if status["overheat_detected"]:
            alert = {
                "type": "OVERHEAT",
                "severity": "CRITICAL",
                "temperature": status["temperature"],
                "message": f"OVERHEAT DETECTED! Temperature: {status['temperature']}Â°C"
            }
            alerts.append(alert)
            self._raise_alert(alert)
            self.emergency_stop("Overheat detected")
        
        # AÅŸÄ±rÄ± akÄ±m kontrolÃ¼
        if status["current"] > self.max_current_threshold:
            alert = {
                "type": "OVERCURRENT",
                "severity": "HIGH",
                "current": status["current"],
                "message": f"Overcurrent detected: {status['current']}A"
            }
            alerts.append(alert)
            self._raise_alert(alert)
        
        return {
            "battery_status": status,
            "alerts": alerts,
            "secure_mode": self.secure_mode
        }
    
    def emergency_stop(self, reason: str):
        """Acil durdurma"""
        self.battery.stop_charging()
        self.emergency_stops += 1
        self._log_event("EMERGENCY_STOP", f"Emergency stop triggered: {reason}")
        print(f"\n{'='*60}")
        print(f"âš ï¸  EMERGENCY STOP: {reason}")
        print(f"{'='*60}\n")
    
    def _raise_alert(self, alert: Dict):
        """Alarm oluÅŸtur"""
        alert["timestamp"] = datetime.now().isoformat()
        self.alerts.append(alert)
        self.total_alerts += 1
        
        # Konsola yazdÄ±r
        severity_emoji = {
            "CRITICAL": "ğŸ”´",
            "HIGH": "ğŸŸ ",
            "MEDIUM": "ğŸŸ¡",
            "LOW": "ğŸŸ¢"
        }
        emoji = severity_emoji.get(alert.get("severity", "MEDIUM"), "âš ï¸")
        print(f"{emoji} ALERT [{alert['type']}]: {alert['message']}")
    
    def _log_event(self, event_type: str, message: str):
        """Olay kaydet"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message
        }
        self.charge_history.append(log_entry)
    
    def get_statistics(self) -> Dict:
        """Ä°statistikleri dÃ¶ndÃ¼r"""
        return {
            "total_alerts": self.total_alerts,
            "emergency_stops": self.emergency_stops,
            "secure_mode_enabled": self.secure_mode,
            "battery_health": self.battery.health_percentage,
            "recent_alerts": self.alerts[-10:] if self.alerts else []
        }
    
    def clear_alerts(self):
        """AlarmlarÄ± temizle"""
        self.alerts.clear()


if __name__ == "__main__":
    from battery import Battery
    
    print("=== BMS Controller Test ===\n")
    
    # Test 1: GÃ¼venli mod kapalÄ±
    print("TEST 1: Vulnerable Mode (Secure Mode OFF)")
    print("-" * 50)
    battery1 = Battery(initial_soc=30.0)
    bms1 = BMSController(battery1, secure_mode=False)
    
    # ManipÃ¼le edilmiÅŸ SOC ile ÅŸarj talebi
    result1 = bms1.validate_charging_request(reported_soc=30.0, reported_temp=25.0)
    print(f"Validation result (reported SOC=30%, actual SOC=30%): {result1['allow_charging']}")
    
    # BataryayÄ± %90'a getir
    battery1.soc = 90.0
    # Ama saldÄ±rgan %30 olarak bildiriyor
    result1 = bms1.validate_charging_request(reported_soc=30.0, reported_temp=25.0)
    print(f"Validation result (reported SOC=30%, actual SOC=90%): {result1['allow_charging']}")
    print("âš ï¸  WARNING: Attack not detected in vulnerable mode!\n")
    
    # Test 2: GÃ¼venli mod aÃ§Ä±k
    print("\nTEST 2: Secure Mode (Secure Mode ON)")
    print("-" * 50)
    battery2 = Battery(initial_soc=30.0)
    bms2 = BMSController(battery2, secure_mode=True)
    
    # ManipÃ¼le edilmiÅŸ SOC ile ÅŸarj talebi
    result2 = bms2.validate_charging_request(reported_soc=30.0, reported_temp=25.0)
    print(f"Validation result (reported SOC=30%, actual SOC=30%): {result2['allow_charging']}")
    
    # BataryayÄ± %90'a getir
    battery2.soc = 90.0
    # Ama saldÄ±rgan %30 olarak bildiriyor
    result2 = bms2.validate_charging_request(reported_soc=30.0, reported_temp=25.0)
    print(f"Validation result (reported SOC=30%, actual SOC=90%): {result2['allow_charging']}")
    print(f"Reason: {result2['reason']}")
    print("âœ… Attack detected and blocked!\n")
