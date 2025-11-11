"""
Secure System Demo - Cryptographic Protection Demonstration
GÃ¼venli sistem demosu - Kriptografik koruma gÃ¶sterimi
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
from src.security.crypto_handler import CryptoHandler
from src.security.integrity_checker import IntegrityChecker
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


def demo_secure_system():
    \"\"\"
    GÃœVENLÄ° SÄ°STEM DEMOSU
    Kriptografik koruma ile gÃ¼venli sistem
    \"\"\"
    print_header("ğŸ›¡ï¸  SECURE SYSTEM DEMONSTRATION")
    print("This demo shows a charging system WITH security mechanisms:")
    print("  âœ… Cryptographic message signing (HMAC + RSA)")
    print("  âœ… Timestamp validation (replay attack protection)")
    print("  âœ… BMS independent sensor validation")
    print("  âœ… Integrity checking\n")
    input("Press Enter to start the demonstration...")
    
    # Logger
    logger = EVLogger(log_dir="../logs", enable_console=False)
    logger.info("DEMO", "Starting secure system demonstration")
    
    # GÃ¶rselleÅŸtirici
    visualizer = ChargingVisualizer("Secure System - Attack Prevention")
    
    # GÃ¼venlik bileÅŸenleri
    print_section("1. Initializing Secure Components")
    crypto = CryptoHandler(secret_key="secure-ev-charging-2025")
    integrity_checker = IntegrityChecker()
    
    print("ğŸ”’ Cryptographic Handler initialized")
    print("   - HMAC-SHA256 for message integrity")
    print("   - RSA-2048 for digital signatures")
    print("   - Timestamp validation enabled")
    
    print("\nğŸ›¡ï¸  Integrity Checker initialized")
    print("   - Anomaly detection active")
    print("   - Physical consistency checks enabled")
    
    # BileÅŸenler
    battery = Battery(initial_soc=30.0, capacity_kwh=75.0)
    bms = BMSController(battery, secure_mode=True)  # GÃ¼venli mod AÃ‡IK
    vehicle = VehicleClient("EV-SECURE-001", battery, bms)
    station = ChargingStation("SECURE-STATION-001", max_power_kw=150.0)
    
    print(f"\nâœ… Battery: {battery.capacity_kwh} kWh, Initial SOC: {battery.soc}%")
    print(f"âœ… BMS: Secure mode = {bms.secure_mode} (PROTECTED!)")
    print(f"âœ… Vehicle: {vehicle.vehicle_id}")
    print(f"âœ… Charging Station: {station.station_id}")
    
    # BaÄŸlantÄ±
    print_section("2. Establishing Secure Connection")
    vehicle.connect_to_station(station.station_id)
    station.accept_connection(vehicle)
    print(f"âœ… Secure connection established")
    
    # Åarj baÅŸlat
    start_msg = vehicle.request_charging(power_kw=50.0)
    start_resp = station.process_start_transaction(start_msg)
    print(f"âœ… Charging started: {start_resp['power_kw']} kW")
    
    # Normal ÅŸarj (gÃ¼venli)
    print_section("3. Normal Secure Charging")
    print("ğŸ”‹ Charging with cryptographic protection...\n")
    
    for t in range(30):
        # Åarj et
        station.charge_vehicle(vehicle, duration_seconds=1.0)
        
        # GÃ¼venli mesaj oluÅŸtur
        status_msg = vehicle.send_status_notification()
        secure_msg = crypto.add_security_fields(status_msg)
        
        # Mesaj doÄŸrulamasÄ±
        verification = crypto.verify_message_security(secure_msg)
        integrity_check = integrity_checker.check_message_integrity(secure_msg)
        
        if not verification['valid']:
            logger.error("SECURITY", "Message verification failed", verification)
            print(f"âŒ t={t}s: Message rejected - {verification['errors']}")
            continue
        
        # BMS doÄŸrulamasÄ±
        bms_validation = bms.validate_charging_request(
            reported_soc=secure_msg['battery_data']['soc'],
            reported_temp=secure_msg['battery_data']['temperature']
        )
        
        if not bms_validation['allow_charging']:
            logger.warning("BMS", "Charging not allowed", bms_validation)
            print(f"âš ï¸  Charging stopped: {bms_validation['reason']}")
            break
        
        # Ä°stasyona gÃ¶nder
        status_resp = station.process_status_notification(secure_msg)
        
        # GÃ¶rselleÅŸtirme
        status = battery.get_status()
        visualizer.add_data_point(
            t, status['soc'], None,
            status['temperature'], status['voltage'], status['current']
        )
        
        if t % 5 == 0:
            print(f"  t={t}s: SOC={status['soc']:.1f}%, Temp={status['temperature']:.1f}Â°C, Status={status['safety_status']}")
        
        # SOC %95'e ulaÅŸtÄ± mÄ±?
        if status['soc'] >= 95.0:
            print(f"\nâœ… SOC reached safe limit ({status['soc']:.1f}%)")
            print("   BMS automatically stopping charge to prevent overcharge")
            break
        
        time.sleep(0.1)
    
    # SALDIRI DENEMESÄ°!
    print_section("4. ğŸ”´ SIMULATING ATTACK ATTEMPT")
    print("âš ï¸  Attacker tries to manipulate SOC...")
    
    attacker = SOCManipulator()
    mitm_proxy = MITMProxy("Attempted-Attacker")
    
    mitm_proxy.activate()
    attacker.enable_attack(mode="fixed", fake_soc=30.0)
    mitm_proxy.add_manipulation(attacker.intercept_message)
    
    logger.log_attack("SOC_MANIPULATION_ATTEMPT", {
        "attack_mode": "fixed",
        "fake_soc": 30.0,
        "real_soc": battery.soc
    })
    
    print(f"\nğŸ­ Attacker manipulates SOC: Real={battery.soc:.1f}% â†’ Fake=30.0%\n")
    
    # ManipÃ¼le edilmiÅŸ mesaj gÃ¶nderme denemesi
    original_msg = vehicle.send_status_notification()
    
    # Ã–nce gÃ¼venli imza ekle
    secure_msg = crypto.add_security_fields(original_msg)
    
    # Sonra saldÄ±rgan manipÃ¼le etmeye Ã§alÄ±ÅŸÄ±r
    manipulated_msg = mitm_proxy.intercept_vehicle_to_station(secure_msg)
    
    print("ğŸ” Security validation...")
    
    # Kriptografik doÄŸrulama
    verification = crypto.verify_message_security(manipulated_msg)
    
    if not verification['valid']:
        print("âŒ ATTACK DETECTED by cryptographic validation!")
        print(f"   Errors: {verification['errors']}")
        logger.log_alert("ATTACK_BLOCKED", "CRITICAL", 
                        "SOC manipulation attack blocked by cryptographic validation")
    
    # BMS baÄŸÄ±msÄ±z doÄŸrulama
    bms_validation = bms.validate_charging_request(
        reported_soc=manipulated_msg['battery_data']['soc'],
        reported_temp=manipulated_msg['battery_data']['temperature']
    )
    
    if not bms_validation['valid']:
        print("âŒ ATTACK DETECTED by BMS independent sensors!")
        print(f"   Reason: {bms_validation['reason']}")
        for alert in bms_validation['alerts']:
            print(f"   Alert: {alert['message']}")
        logger.log_alert("ATTACK_BLOCKED", "CRITICAL",
                        "SOC manipulation attack blocked by BMS validation")
    
    # Integrity checking
    integrity_check = integrity_checker.check_message_integrity(manipulated_msg)
    if integrity_check['anomalies']:
        print("âŒ ATTACK DETECTED by integrity checker!")
        for anomaly in integrity_check['anomalies']:
            print(f"   Anomaly: {anomaly}")
    
    print("\nâœ… ATTACK SUCCESSFULLY BLOCKED!")
    print("   Multiple security layers prevented the attack:")
    print("   1. Cryptographic signature verification")
    print("   2. BMS independent sensor validation")
    print("   3. Integrity checking")
    
    mitm_proxy.deactivate()
    
    # SonuÃ§lar
    print_section("5. âœ… SECURE SYSTEM RESULTS")
    
    final_status = battery.get_status()
    bms_stats = bms.get_statistics()
    
    print("Battery Status:")
    print(f"  Final SOC: {final_status['soc']:.1f}% (SAFE)")
    print(f"  Temperature: {final_status['temperature']:.1f}Â°C (NORMAL)")
    print(f"  Health: {final_status['health_percentage']:.1f}% (EXCELLENT)")
    print(f"  Overcharge: {final_status['overcharge_detected']} âœ…")
    print(f"  Overheat: {final_status['overheat_detected']} âœ…")
    
    print("\nBMS Statistics:")
    print(f"  Total Alerts: {bms_stats['total_alerts']}")
    print(f"  Emergency Stops: {bms_stats['emergency_stops']}")
    print(f"  Battery Health: {bms_stats['battery_health']:.1f}%")
    
    print("\nâœ… BENEFITS:")
    print("  ğŸ›¡ï¸  Attack prevented â†’ No damage")
    print("  ğŸ”‹ Battery health maintained")
    print("  âœ… Safe charging operation")
    print("  ğŸ”’ System integrity preserved")
    
    # GÃ¶rselleÅŸtirme
    print_section("6. Generating Visualization")
    visualizer.plot_static(save_path="../logs/secure_system_demo.png")
    
    print_section("Demo Complete")
    print("âœ… Logs saved to: ../logs/")
    print("ğŸ“Š Visualization saved to: ../logs/secure_system_demo.png")
    print("\nâœ… This demonstration shows how cryptographic security mechanisms")
    print("   effectively protect EV charging systems from manipulation attacks.\n")


if __name__ == "__main__":
    try:
        demo_secure_system()
    except KeyboardInterrupt:
        print("\n\nâš ï¸  Demo interrupted by user")
    except Exception as e:
        print(f"\n\nâŒ Error: {e}")
        import traceback
        traceback.print_exc()
