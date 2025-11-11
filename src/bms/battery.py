"""
Battery Simulation Module
Batarya simÃ¼lasyonu - Fiziksel parametreleri ve durumu yÃ¶netir
"""

import time
import numpy as np
from datetime import datetime
from typing import Dict, Optional


class Battery:
    """
    Elektrikli araÃ§ bataryasÄ± simÃ¼lasyonu
    GerÃ§ekÃ§i fiziksel parametrelerle Ã§alÄ±ÅŸÄ±r
    """
    
    def __init__(
        self,
        capacity_kwh: float = 75.0,  # kWh cinsinden kapasite
        initial_soc: float = 30.0,    # BaÅŸlangÄ±Ã§ SOC %
        max_voltage: float = 400.0,   # Maksimum voltaj
        min_voltage: float = 300.0,   # Minimum voltaj
        nominal_temp: float = 25.0,   # Nominal sÄ±caklÄ±k (Â°C)
        max_safe_temp: float = 45.0,  # Maksimum gÃ¼venli sÄ±caklÄ±k
        critical_temp: float = 60.0,  # Kritik sÄ±caklÄ±k eÅŸiÄŸi
    ):
        self.capacity_kwh = capacity_kwh
        self.soc = initial_soc  # State of Charge (%)
        self.max_voltage = max_voltage
        self.min_voltage = min_voltage
        self.temperature = nominal_temp
        self.nominal_temp = nominal_temp
        self.max_safe_temp = max_safe_temp
        self.critical_temp = critical_temp
        
        # Åarj parametreleri
        self.current = 0.0  # Ampere
        self.voltage = self._calculate_voltage()
        self.power = 0.0    # kW
        
        # Durum bayraklarÄ±
        self.is_charging = False
        self.overcharge_detected = False
        self.overheat_detected = False
        self.health_percentage = 100.0
        
        # Ä°statistikler
        self.charge_cycles = 0
        self.total_energy_charged = 0.0
        
    def _calculate_voltage(self) -> float:
        """SOC'a gÃ¶re voltaj hesapla"""
        voltage_range = self.max_voltage - self.min_voltage
        return self.min_voltage + (self.soc / 100.0) * voltage_range
    
    def _calculate_temperature_rise(self, charging_power: float, duration: float) -> float:
        """
        Åarj gÃ¼cÃ¼ne gÃ¶re sÄ±caklÄ±k artÄ±ÅŸÄ±nÄ± hesapla
        AÅŸÄ±rÄ± ÅŸarjda sÄ±caklÄ±k artÄ±ÅŸÄ± daha fazla olur
        """
        # Temel Ä±sÄ±nma
        base_heating = (charging_power / 50.0) * duration
        
        # SOC > 90% ise Ä±sÄ±nma artar
        if self.soc > 90:
            overcharge_factor = 1.0 + ((self.soc - 90) / 10.0) * 2.0
            base_heating *= overcharge_factor
        
        # SOC > 100% ise aÅŸÄ±rÄ± Ä±sÄ±nma (kritik durum)
        if self.soc > 100:
            critical_heating = ((self.soc - 100) / 10.0) * 5.0
            base_heating += critical_heating
        
        # Ortam sÄ±caklÄ±ÄŸÄ±na yakÄ±nsama (soÄŸuma)
        cooling = (self.temperature - self.nominal_temp) * 0.05 * duration
        
        return base_heating - cooling
    
    def charge(self, power_kw: float, duration_seconds: float = 1.0) -> Dict:
        """
        BataryayÄ± belirtilen gÃ¼Ã§le ÅŸarj et
        
        Args:
            power_kw: Åarj gÃ¼cÃ¼ (kW)
            duration_seconds: Åarj sÃ¼resi (saniye)
            
        Returns:
            Batarya durumu bilgileri
        """
        self.is_charging = True
        self.power = power_kw
        
        # Enerji artÄ±ÅŸÄ± (kWh)
        energy_added = (power_kw * duration_seconds) / 3600.0
        
        # SOC artÄ±ÅŸÄ±
        soc_increase = (energy_added / self.capacity_kwh) * 100.0
        self.soc += soc_increase
        
        # Ä°statistikleri gÃ¼ncelle
        self.total_energy_charged += energy_added
        
        # AkÄ±m hesapla (P = V * I)
        self.voltage = self._calculate_voltage()
        self.current = (power_kw * 1000) / self.voltage if self.voltage > 0 else 0
        
        # SÄ±caklÄ±k artÄ±ÅŸÄ±
        temp_rise = self._calculate_temperature_rise(power_kw, duration_seconds)
        self.temperature += temp_rise
        
        # AÅŸÄ±rÄ± ÅŸarj kontrolÃ¼
        if self.soc > 100.0:
            self.overcharge_detected = True
            
        # AÅŸÄ±rÄ± Ä±sÄ±nma kontrolÃ¼
        if self.temperature > self.critical_temp:
            self.overheat_detected = True
        
        # SaÄŸlÄ±k dÃ¼ÅŸÃ¼ÅŸÃ¼ (aÅŸÄ±rÄ± ÅŸarj ve Ä±sÄ±nma zararlÄ±)
        if self.soc > 100:
            self.health_percentage -= 0.01 * (self.soc - 100)
        if self.temperature > self.max_safe_temp:
            self.health_percentage -= 0.005 * (self.temperature - self.max_safe_temp)
        
        self.health_percentage = max(0, self.health_percentage)
        
        return self.get_status()
    
    def stop_charging(self):
        """ÅarjÄ± durdur"""
        self.is_charging = False
        self.current = 0.0
        self.power = 0.0
    
    def get_status(self) -> Dict:
        """Batarya durumunu dÃ¶ndÃ¼r"""
        return {
            "timestamp": datetime.now().isoformat(),
            "soc": round(self.soc, 2),
            "voltage": round(self.voltage, 2),
            "current": round(self.current, 2),
            "temperature": round(self.temperature, 2),
            "power": round(self.power, 2),
            "capacity_kwh": self.capacity_kwh,
            "health_percentage": round(self.health_percentage, 2),
            "is_charging": self.is_charging,
            "overcharge_detected": self.overcharge_detected,
            "overheat_detected": self.overheat_detected,
            "charge_cycles": self.charge_cycles,
            "total_energy_charged": round(self.total_energy_charged, 2),
            # GÃ¼venlik durumu
            "safety_status": self._get_safety_status()
        }
    
    def _get_safety_status(self) -> str:
        """GÃ¼venlik durumunu deÄŸerlendir"""
        if self.overcharge_detected or self.overheat_detected:
            return "CRITICAL"
        elif self.soc > 95 or self.temperature > self.max_safe_temp:
            return "WARNING"
        elif self.soc > 90:
            return "CAUTION"
        else:
            return "NORMAL"
    
    def reset_anomalies(self):
        """Anomali bayraklarÄ±nÄ± sÄ±fÄ±rla (test amaÃ§lÄ±)"""
        self.overcharge_detected = False
        self.overheat_detected = False


if __name__ == "__main__":
    # Test senaryosu
    print("=== Batarya SimÃ¼lasyon Testi ===\n")
    
    battery = Battery(initial_soc=30.0)
    
    print("BaÅŸlangÄ±Ã§ Durumu:")
    print(f"SOC: {battery.soc}%")
    print(f"SÄ±caklÄ±k: {battery.temperature}Â°C")
    print(f"Voltaj: {battery.voltage}V\n")
    
    print("Normal ÅŸarj simÃ¼lasyonu (50 kW, 10 saniye):")
    for i in range(10):
        status = battery.charge(power_kw=50.0, duration_seconds=1.0)
        print(f"  t={i+1}s: SOC={status['soc']}%, Temp={status['temperature']}Â°C, Status={status['safety_status']}")
    
    print(f"\nFinal Durum:")
    final_status = battery.get_status()
    for key, value in final_status.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")
