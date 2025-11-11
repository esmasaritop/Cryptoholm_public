"""
Logger Module
GeliÅŸmiÅŸ loglama sistemi
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class EVLogger:
    """
    Elektrikli araÃ§ ÅŸarj sistemi logger'Ä±
    """
    
    def __init__(self, log_dir: str = "logs", enable_console: bool = True):
        """
        Args:
            log_dir: Log dosyalarÄ±nÄ±n kaydedileceÄŸi dizin
            enable_console: Konsola da yazdÄ±r
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_console = enable_console
        
        # Log dosyalarÄ±
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.main_log_file = self.log_dir / f"charging_{timestamp}.log"
        self.attack_log_file = self.log_dir / f"attack_{timestamp}.log"
        self.alert_log_file = self.log_dir / f"alerts_{timestamp}.log"
        
    def log(self, level: str, category: str, message: str, data: Optional[Dict] = None):
        """
        Genel loglama fonksiyonu
        
        Args:
            level: Log seviyesi (INFO, WARNING, ERROR, CRITICAL)
            category: Kategori (BATTERY, BMS, OCPP, ATTACK, SECURITY)
            message: Log mesajÄ±
            data: Ek veri (dict)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "category": category,
            "message": message
        }
        
        if data:
            log_entry["data"] = data
        
        # JSON formatÄ±nda kaydet
        log_line = json.dumps(log_entry) + "\n"
        
        # Ana log dosyasÄ±na yaz
        with open(self.main_log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
        
        # Konsola yazdÄ±r
        if self.enable_console:
            emoji = {
                "INFO": "â„¹ï¸",
                "WARNING": "âš ï¸",
                "ERROR": "âŒ",
                "CRITICAL": "ğŸ”´"
            }.get(level, "ğŸ“")
            
            print(f"{emoji} [{level}] {category}: {message}")
            if data and level in ["ERROR", "CRITICAL"]:
                print(f"   Data: {data}")
    
    def log_attack(self, attack_type: str, details: Dict):
        """SaldÄ±rÄ± logu"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "attack_type": attack_type,
            "details": details
        }
        
        log_line = json.dumps(log_entry) + "\n"
        
        with open(self.attack_log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
        
        self.log("CRITICAL", "ATTACK", f"Attack detected: {attack_type}", details)
    
    def log_alert(self, alert_type: str, severity: str, message: str, data: Optional[Dict] = None):
        """Alarm logu"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": alert_type,
            "severity": severity,
            "message": message
        }
        
        if data:
            log_entry["data"] = data
        
        log_line = json.dumps(log_entry) + "\n"
        
        with open(self.alert_log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
        
        self.log(severity, "ALERT", f"{alert_type}: {message}", data)
    
    def log_battery_status(self, battery_status: Dict):
        """Batarya durumu logu"""
        self.log("INFO", "BATTERY", "Battery status update", battery_status)
    
    def log_charging_session(self, session_id: str, event: str, data: Dict):
        """Åarj oturumu logu"""
        self.log("INFO", "CHARGING", f"Session {session_id}: {event}", data)
    
    def log_ocpp_message(self, direction: str, message: Dict):
        """OCPP mesaj logu"""
        self.log("INFO", "OCPP", f"Message {direction}", {
            "message_type": message.get("message_type"),
            "vehicle_id": message.get("vehicle_id")
        })
    
    def info(self, category: str, message: str, data: Optional[Dict] = None):
        """Info seviyesi log"""
        self.log("INFO", category, message, data)
    
    def warning(self, category: str, message: str, data: Optional[Dict] = None):
        """Warning seviyesi log"""
        self.log("WARNING", category, message, data)
    
    def error(self, category: str, message: str, data: Optional[Dict] = None):
        """Error seviyesi log"""
        self.log("ERROR", category, message, data)
    
    def critical(self, category: str, message: str, data: Optional[Dict] = None):
        """Critical seviyesi log"""
        self.log("CRITICAL", category, message, data)
    
    def get_log_files(self) -> Dict[str, Path]:
        """Log dosyalarÄ±nÄ±n yollarÄ±nÄ± dÃ¶ndÃ¼r"""
        return {
            "main": self.main_log_file,
            "attack": self.attack_log_file,
            "alert": self.alert_log_file
        }
    
    def read_logs(self, log_type: str = "main", limit: int = 50) -> list:
        """
        Log dosyasÄ±nÄ± oku
        
        Args:
            log_type: Log tipi (main, attack, alert)
            limit: Maksimum satÄ±r sayÄ±sÄ±
            
        Returns:
            Log kayÄ±tlarÄ±
        """
        log_files = {
            "main": self.main_log_file,
            "attack": self.attack_log_file,
            "alert": self.alert_log_file
        }
        
        log_file = log_files.get(log_type)
        if not log_file or not log_file.exists():
            return []
        
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                except:
                    pass
        
        return logs[-limit:]
    
    def generate_report(self) -> Dict:
        """Log Ã¶zetini oluÅŸtur"""
        main_logs = self.read_logs("main", limit=1000)
        attack_logs = self.read_logs("attack", limit=1000)
        alert_logs = self.read_logs("alert", limit=1000)
        
        report = {
            "total_logs": len(main_logs),
            "total_attacks": len(attack_logs),
            "total_alerts": len(alert_logs),
            "level_breakdown": {},
            "category_breakdown": {},
            "alert_severity_breakdown": {}
        }
        
        # Seviye daÄŸÄ±lÄ±mÄ±
        for log in main_logs:
            level = log.get("level", "UNKNOWN")
            report["level_breakdown"][level] = report["level_breakdown"].get(level, 0) + 1
        
        # Kategori daÄŸÄ±lÄ±mÄ±
        for log in main_logs:
            category = log.get("category", "UNKNOWN")
            report["category_breakdown"][category] = report["category_breakdown"].get(category, 0) + 1
        
        # Alert severity daÄŸÄ±lÄ±mÄ±
        for alert in alert_logs:
            severity = alert.get("severity", "UNKNOWN")
            report["alert_severity_breakdown"][severity] = report["alert_severity_breakdown"].get(severity, 0) + 1
        
        return report


if __name__ == "__main__":
    print("=== Logger Test ===\n")
    
    logger = EVLogger(enable_console=True)
    
    # Test loglarÄ±
    logger.info("SYSTEM", "System initialized")
    logger.info("BATTERY", "Battery connected", {"soc": 50.0, "voltage": 350.0})
    logger.warning("BMS", "High temperature detected", {"temp": 45.0})
    logger.error("OCPP", "Communication timeout", {"retry_count": 3})
    
    # Attack log
    logger.log_attack("SOC_MANIPULATION", {
        "real_soc": 95.0,
        "fake_soc": 30.0,
        "difference": 65.0
    })
    
    # Alert log
    logger.log_alert("OVERCHARGE", "CRITICAL", "Battery overcharge detected", {
        "soc": 105.0,
        "temperature": 55.0
    })
    
    # Rapor oluÅŸtur
    print("\n\nLog Report:")
    print("-" * 50)
    report = logger.generate_report()
    for key, value in report.items():
        print(f"{key}: {value}")
    
    print(f"\n\nLog files created:")
    for name, path in logger.get_log_files().items():
        print(f"  {name}: {path}")
