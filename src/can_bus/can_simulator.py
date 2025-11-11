"""
CAN Bus Simulator
AraÃ§ iÃ§i CAN bus iletiÅŸim simÃ¼lasyonu
"""

import random
import time
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CANMessage:
    """CAN Bus mesaj yapÄ±sÄ±"""
    can_id: int  # CAN ID (11-bit veya 29-bit)
    data: bytes  # Veri (max 8 byte)
    timestamp: float
    
    def __str__(self):
        return f"[{self.can_id:03X}] {self.data.hex().upper()} @ {self.timestamp:.3f}"


class CANBusSimulator:
    """
    CAN Bus SimÃ¼latÃ¶rÃ¼
    Elektrikli araÃ§ CAN bus iletiÅŸimini simÃ¼le eder
    """
    
    # Standart CAN ID'leri (Ã¶rnek)
    CAN_IDS = {
        "BMS_SOC": 0x1A0,  # Batarya SOC
        "BMS_VOLTAGE": 0x1A1,  # Batarya voltajÄ±
        "BMS_CURRENT": 0x1A2,  # Batarya akÄ±mÄ±
        "BMS_TEMP": 0x1A3,  # Batarya sÄ±caklÄ±ÄŸÄ±
        "BMS_STATUS": 0x1A4,  # BMS durumu
        "CHARGER_STATUS": 0x2A0,  # Åarj durumu
        "CHARGER_POWER": 0x2A1,  # Åarj gÃ¼cÃ¼
    }
    
    def __init__(self, battery):
        """
        Args:
            battery: Battery instance
        """
        self.battery = battery
        self.messages = []
        self.start_time = time.time()
        
        # Anomali tespiti iÃ§in
        self.anomaly_detector = CANAnomalyDetector()
        
    def _get_timestamp(self) -> float:
        """Zaman damgasÄ± al"""
        return time.time() - self.start_time
    
    def _float_to_bytes(self, value: float, scale: int = 100) -> bytes:
        """Float deÄŸeri CAN mesajÄ± iÃ§in byte'lara Ã§evir"""
        int_value = int(value * scale)
        return int_value.to_bytes(2, byteorder='big', signed=True)
    
    def _bytes_to_float(self, data: bytes, scale: int = 100) -> float:
        """Byte'larÄ± float'a Ã§evir"""
        int_value = int.from_bytes(data, byteorder='big', signed=True)
        return int_value / scale
    
    def create_soc_message(self, soc: Optional[float] = None) -> CANMessage:
        """SOC CAN mesajÄ± oluÅŸtur"""
        if soc is None:
            soc = self.battery.soc
        
        # SOC'u 2 byte'a sÄ±ÄŸdÄ±r (0-100 * 100 = 0-10000)
        data = self._float_to_bytes(soc, scale=100)
        data += b'\x00' * 6  # Padding
        
        return CANMessage(
            can_id=self.CAN_IDS["BMS_SOC"],
            data=data,
            timestamp=self._get_timestamp()
        )
    
    def create_voltage_message(self, voltage: Optional[float] = None) -> CANMessage:
        """Voltaj CAN mesajÄ± oluÅŸtur"""
        if voltage is None:
            voltage = self.battery.voltage
        
        data = self._float_to_bytes(voltage, scale=10)
        data += b'\x00' * 6
        
        return CANMessage(
            can_id=self.CAN_IDS["BMS_VOLTAGE"],
            data=data,
            timestamp=self._get_timestamp()
        )
    
    def create_current_message(self, current: Optional[float] = None) -> CANMessage:
        """AkÄ±m CAN mesajÄ± oluÅŸtur"""
        if current is None:
            current = self.battery.current
        
        data = self._float_to_bytes(current, scale=10)
        data += b'\x00' * 6
        
        return CANMessage(
            can_id=self.CAN_IDS["BMS_CURRENT"],
            data=data,
            timestamp=self._get_timestamp()
        )
    
    def create_temperature_message(self, temperature: Optional[float] = None) -> CANMessage:
        """SÄ±caklÄ±k CAN mesajÄ± oluÅŸtur"""
        if temperature is None:
            temperature = self.battery.temperature
        
        data = self._float_to_bytes(temperature, scale=10)
        data += b'\x00' * 6
        
        return CANMessage(
            can_id=self.CAN_IDS["BMS_TEMP"],
            data=data,
            timestamp=self._get_timestamp()
        )
    
    def create_status_message(self) -> CANMessage:
        """BMS durum mesajÄ± oluÅŸtur"""
        status_byte = 0x00
        
        if self.battery.is_charging:
            status_byte |= 0x01
        if self.battery.overcharge_detected:
            status_byte |= 0x02
        if self.battery.overheat_detected:
            status_byte |= 0x04
        
        data = bytes([status_byte]) + b'\x00' * 7
        
        return CANMessage(
            can_id=self.CAN_IDS["BMS_STATUS"],
            data=data,
            timestamp=self._get_timestamp()
        )
    
    def send_battery_status(self) -> List[CANMessage]:
        """Batarya durumunu CAN bus'a gÃ¶nder"""
        messages = [
            self.create_soc_message(),
            self.create_voltage_message(),
            self.create_current_message(),
            self.create_temperature_message(),
            self.create_status_message()
        ]
        
        # MesajlarÄ± kaydet
        self.messages.extend(messages)
        
        # Anomali tespiti
        for msg in messages:
            self.anomaly_detector.analyze_message(msg)
        
        return messages
    
    def inject_malicious_message(self, can_id: int, data: bytes) -> CANMessage:
        """
        KÃ¶tÃ¼ niyetli CAN mesajÄ± enjekte et (saldÄ±rÄ± simÃ¼lasyonu)
        
        Args:
            can_id: CAN ID
            data: Veri
            
        Returns:
            Enjekte edilen mesaj
        """
        malicious_msg = CANMessage(
            can_id=can_id,
            data=data,
            timestamp=self._get_timestamp()
        )
        
        self.messages.append(malicious_msg)
        print(f"ğŸ”´ MALICIOUS CAN MESSAGE INJECTED: {malicious_msg}")
        
        return malicious_msg
    
    def inject_fake_soc(self, fake_soc: float) -> CANMessage:
        """Sahte SOC mesajÄ± enjekte et"""
        print(f"\nâš ï¸  ATTACK: Injecting fake SOC: {fake_soc}% (Real: {self.battery.soc}%)")
        return self.inject_malicious_message(
            can_id=self.CAN_IDS["BMS_SOC"],
            data=self._float_to_bytes(fake_soc, scale=100) + b'\x00' * 6
        )
    
    def get_messages(self, limit: int = 10) -> List[CANMessage]:
        """CAN mesajlarÄ±nÄ± dÃ¶ndÃ¼r"""
        return self.messages[-limit:]
    
    def clear_messages(self):
        """Mesaj geÃ§miÅŸini temizle"""
        self.messages.clear()
        self.start_time = time.time()


class CANAnomalyDetector:
    """
    CAN Bus Anomali Tespit Sistemi
    """
    
    def __init__(self):
        """Initialize anomaly detector"""
        self.message_history = {}
        self.anomalies = []
        
        # Her CAN ID iÃ§in beklenen mesaj frekansÄ± (saniye)
        self.expected_intervals = {
            0x1A0: 0.1,  # BMS_SOC: her 100ms
            0x1A1: 0.1,  # BMS_VOLTAGE
            0x1A2: 0.1,  # BMS_CURRENT
            0x1A3: 0.5,  # BMS_TEMP: her 500ms
        }
        
        # Tolerans
        self.interval_tolerance = 0.5  # 50%
    
    def analyze_message(self, message: CANMessage):
        """CAN mesajÄ±nÄ± analiz et ve anomali tespit et"""
        can_id = message.can_id
        timestamp = message.timestamp
        
        # Ä°lk mesaj ise kaydet
        if can_id not in self.message_history:
            self.message_history[can_id] = {
                "last_timestamp": timestamp,
                "last_data": message.data,
                "count": 1
            }
            return
        
        history = self.message_history[can_id]
        
        # Frekans kontrolÃ¼
        if can_id in self.expected_intervals:
            expected_interval = self.expected_intervals[can_id]
            actual_interval = timestamp - history["last_timestamp"]
            
            # Ã‡ok hÄ±zlÄ± mesaj (flooding attack)
            if actual_interval < expected_interval * (1 - self.interval_tolerance):
                self._report_anomaly({
                    "type": "FLOODING",
                    "can_id": f"0x{can_id:03X}",
                    "expected_interval": expected_interval,
                    "actual_interval": actual_interval,
                    "message": "Too frequent CAN messages"
                })
            
            # Ã‡ok yavaÅŸ mesaj (denial of service)
            elif actual_interval > expected_interval * (1 + self.interval_tolerance) * 3:
                self._report_anomaly({
                    "type": "TIMEOUT",
                    "can_id": f"0x{can_id:03X}",
                    "expected_interval": expected_interval,
                    "actual_interval": actual_interval,
                    "message": "CAN message timeout"
                })
        
        # AynÄ± veri tekrarÄ± kontrolÃ¼ (replay attack)
        if message.data == history["last_data"]:
            history["count"] += 1
            if history["count"] > 10:  # 10 kez aynÄ± veri
                self._report_anomaly({
                    "type": "REPLAY_SUSPECTED",
                    "can_id": f"0x{can_id:03X}",
                    "repeat_count": history["count"],
                    "message": "Same data repeated multiple times"
                })
        else:
            history["count"] = 1
        
        # GeÃ§miÅŸi gÃ¼ncelle
        history["last_timestamp"] = timestamp
        history["last_data"] = message.data
    
    def _report_anomaly(self, anomaly: Dict):
        """Anomali raporla"""
        anomaly["timestamp"] = datetime.now().isoformat()
        self.anomalies.append(anomaly)
        
        print(f"ğŸš¨ CAN ANOMALY DETECTED: {anomaly['type']} - {anomaly['message']}")
    
    def get_anomalies(self, limit: int = 10) -> List[Dict]:
        """Anomalileri dÃ¶ndÃ¼r"""
        return self.anomalies[-limit:]
    
    def clear_anomalies(self):
        """Anomali geÃ§miÅŸini temizle"""
        self.anomalies.clear()


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from bms.battery import Battery
    
    print("=== CAN Bus Simulator Test ===\n")
    
    # Batarya ve CAN bus oluÅŸtur
    battery = Battery(initial_soc=50.0)
    can_bus = CANBusSimulator(battery)
    
    print("1. Normal CAN messages:")
    print("-" * 50)
    messages = can_bus.send_battery_status()
    for msg in messages:
        print(f"   {msg}")
    
    print("\n2. Simulating charging...")
    print("-" * 50)
    for i in range(3):
        battery.charge(power_kw=50.0, duration_seconds=1.0)
        time.sleep(0.1)
        messages = can_bus.send_battery_status()
        soc_msg = messages[0]
        print(f"   Cycle {i+1}: {soc_msg}")
    
    print("\n3. ATTACK: Injecting fake SOC...")
    print("-" * 50)
    battery.soc = 95.0  # GerÃ§ek SOC %95
    can_bus.inject_fake_soc(fake_soc=30.0)  # Sahte SOC %30
    
    print("\n4. Anomaly detection results:")
    print("-" * 50)
    anomalies = can_bus.anomaly_detector.get_anomalies()
    if anomalies:
        for anomaly in anomalies:
            print(f"   - {anomaly['type']}: {anomaly['message']}")
    else:
        print("   No anomalies detected")
