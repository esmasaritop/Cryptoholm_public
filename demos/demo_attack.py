"""
Attack Demo - SOC Manipulation Attack Demonstration
Zafiyet demosu - SOC manipÃ¼lasyonu saldÄ±rÄ±sÄ± gÃ¶sterimi
"""

import sys
import time
sys.path.append('..')

from src.bms.battery import Battery
from src.bms.bms_controller import BMSController
from src.ocpp.vehicle_client import VehicleClient
from src.ocpp.charging_station import ChargingStation
from src.attack.soc_manipulator import SOCManipulator
from src.attack.mitm_proxy import MITMProxy
from src.utils.logger import EVLogger
from src.utils.visualizer import ChargingVisualizer


def print_header(title: str):
    \"\"\"BaÅŸlÄ±k yazdÄ±r\"\"\"
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_section(title: str):
    \"\"\"BÃ¶lÃ¼m baÅŸlÄ±ÄŸÄ± yazdÄ±r\"\"\"
    print(f"\n{'-'*80}")
    print(f"  {title}")
    print(f"{'-'*80}\n")


def demo_vulnerable_system():
    \"\"\"
    ZAFÄ°YETLÄ° SÄ°STEM DEMOSU
    Kriptografik koruma olmadan, saldÄ±rÄ±ya aÃ§Ä±k sistem
    \"\"\"
    print_header("ğŸ”´ VULNERABLE SYSTEM DEMONSTRATION")
    print("This demo shows a charging system WITHOUT security mechanisms.")
    print("The system is vulnerable to SOC manipulation attacks.\n")
    input("Press Enter to start the demonstration...")
    
    # Logger
    logger = EVLogger(log_dir="../logs", enable_console=False)
    logger.info("DEMO", "Starting vulnerable system demonstration")
    
    # GÃ¶rselleÅŸtirici
    visualizer = ChargingVisualizer("Vulnerable System - SOC Manipulation Attack")
    
    # BileÅŸenler
    print_section("1. Initializing Components")
    battery = Battery(initial_soc=30.0, capacity_kwh=75.0)
    bms = BMSController(battery, secure_mode=False)  # GÃ¼venli mod KAPALI
    vehicle = VehicleClient("EV-VICTIM-001", battery, bms)
    station = ChargingStation("STATION-001", max_power_kw=150.0)
    
    print(f"âœ… Battery: {battery.capacity_kwh} kWh, Initial SOC: {battery.soc}%")
    print(f"âœ… BMS: Secure mode = {bms.secure_mode} (VULNERABLE!)")
    print(f"âœ… Vehicle: {vehicle.vehicle_id}")
    print(f"âœ… Charging Station: {station.station_id}")
    
    # SaldÄ±rgan bileÅŸenleri
    print_section("2. Attacker Setup")
    attacker = SOCManipulator(attack_enabled=False)
    mitm_proxy = MITMProxy("Malicious-Attacker")
    
    print("ğŸ•µï¸  MITM Proxy created")
    print("ğŸ­ SOC Manipulator ready")
    
    # Normal baÄŸlantÄ±
    print_section("3. Normal Charging Session")
    vehicle.connect_to_station(station.station_id)
    station.accept_connection(vehicle)
    print(f"âœ… Vehicle connected to {station.station_id}")
    
    # Åarj baÅŸlat
    start_msg = vehicle.request_charging(power_kw=50.0)
    start_resp = station.process_start_transaction(start_msg)
    print(f"âœ… Charging started: {start_resp['power_kw']} kW")
    
    # Normal ÅŸarj (ilk 10 saniye)
    print("\nğŸ”‹ Normal charging (0-10s)...")
    for t in range(10):
        # Åarj et
        station.charge_vehicle(vehicle, duration_seconds=1.0)
        
        # Durum bildir (normal, manipÃ¼lasyon yok)
        status_msg = vehicle.send_status_notification()
        status_resp = station.process_status_notification(status_msg)
        
        # GÃ¶rselleÅŸtirme verisi
        status = battery.get_status()
        visualizer.add_data_point(
            t, status['soc'], status['soc'],
            status['temperature'], status['voltage'], status['current']
        )
        
        if t % 2 == 0:
            print(f"  t={t}s: SOC={status['soc']:.1f}%, Temp={status['temperature']:.1f}Â°C")
        
        time.sleep(0.1)
    
    # SALDIRI BAÅLIYOR!
    print_section("4. ğŸ”´ ATTACK INITIATED!")
    print("âš ï¸  Attacker activates MITM proxy and SOC manipulator...")
    
    mitm_proxy.activate()
    attacker.enable_attack(mode="fixed", fake_soc=30.0)
    mitm_proxy.add_manipulation(attacker.intercept_message)
    
    logger.log_attack("SOC_MANIPULATION", {
        "attack_mode": "fixed",
        "fake_soc": 30.0,
        "real_soc": battery.soc
    })
    
    print("\nğŸ­ SOC Manipulation active:")
    print(f"   Real SOC: {battery.soc:.1f}%")
    print(f"   Fake SOC: 30.0% (will be reported to station)")
    print("\nâš¡ Continuing charging with manipulated data...\n")
    
    # ManipÃ¼le edilmiÅŸ ÅŸarj (40 saniye daha)
    for t in range(10, 50):
        # Åarj et
        station.charge_vehicle(vehicle, duration_seconds=1.0)
        
        # Durum bildir (PROXY ÃœZERÄ°NDEN - manipÃ¼le edilmiÅŸ)
        original_msg = vehicle.send_status_notification()
        manipulated_msg = mitm_proxy.intercept_vehicle_to_station(original_msg)
        status_resp = station.process_status_notification(manipulated_msg)
        
        # GÃ¶rselleÅŸtirme verisi
        status = battery.get_status()
        visualizer.add_data_point(
            t,
            status['soc'],  # GerÃ§ek SOC
            manipulated_msg['battery_data']['soc'],  # Sahte SOC
            status['temperature'],
            status['voltage'],
            status['current']
        )
        
        # BMS monitoring
        bms_status = bms.monitor_charging()
        
        # Her 5 saniyede rapor
        if t % 5 == 0:
            print(f"  t={t}s:")
            print(f"    Real SOC: {status['soc']:.1f}%")
            print(f"    Reported SOC: {manipulated_msg['battery_data']['soc']:.1f}%")
            print(f"    Temperature: {status['temperature']:.1f}Â°C")
            print(f"    Safety: {status['safety_status']}")
        
        # AÅŸÄ±rÄ± ÅŸarj tespit edildi mi?
        if status['overcharge_detected']:
            logger.log_alert("OVERCHARGE", "CRITICAL", 
                           "Battery overcharge detected due to SOC manipulation")
            break
        
        # AÅŸÄ±rÄ± Ä±sÄ±nma tespit edildi mi?
        if status['overheat_detected']:
            logger.log_alert("OVERHEAT", "CRITICAL",
                           "Battery overheat detected")
            break
        
        time.sleep(0.1)
    
    # SonuÃ§lar
    print_section("5. ğŸ’¥ ATTACK RESULTS")
    
    final_status = battery.get_status()
    attack_stats = attacker.get_statistics()
    proxy_stats = mitm_proxy.get_statistics()
    
    print("Battery Status:")
    print(f"  Final SOC: {final_status['soc']:.1f}% {'(OVERCHARGED!)' if final_status['soc'] > 100 else ''}")
    print(f"  Temperature: {final_status['temperature']:.1f}Â°C {'(CRITICAL!)' if final_status['temperature'] > 60 else ''}")
    print(f"  Health: {final_status['health_percentage']:.1f}%")
    print(f"  Overcharge Detected: {final_status['overcharge_detected']}")
    print(f"  Overheat Detected: {final_status['overheat_detected']}")
    
    print("\nAttack Statistics:")
    print(f"  Messages Intercepted: {proxy_stats['total_intercepted']}")
    print(f"  Messages Manipulated: {proxy_stats['total_manipulated']}")
    print(f"  Manipulation Rate: {proxy_stats['manipulation_rate']:.1f}%")
    
    print("\nâš ï¸  CONSEQUENCES:")
    print("  ğŸ”¥ Battery overcharge â†’ Fire/explosion risk")
    print("  ğŸŒ¡ï¸  Critical temperature â†’ Thermal runaway risk")
    print("  ğŸ”‹ Reduced battery life")
    print("  âš¡ Potential equipment damage")
    
    # GÃ¶rselleÅŸtirme
    print_section("6. Generating Visualization")
    logger.info("DEMO", "Generating visualization")
    visualizer.plot_static(save_path="../logs/vulnerable_attack_demo.png")
    
    # Rapor
    mitm_proxy.print_attack_report()
    
    print_section("Demo Complete")
    print("âœ… Logs saved to: ../logs/")
    print("ğŸ“Š Visualization saved to: ../logs/vulnerable_attack_demo.png")
    print("\nâš ï¸  This demonstration shows the critical importance of security mechanisms")
    print("    in EV charging systems. Without cryptographic validation, attackers can")
    print("    manipulate charging parameters and cause severe damage.\n")


if __name__ == "__main__":
    try:
        demo_vulnerable_system()
    except KeyboardInterrupt:
        print("\n\nâš ï¸  Demo interrupted by user")
    except Exception as e:
        print(f"\n\nâŒ Error: {e}")
        import traceback
        traceback.print_exc()
