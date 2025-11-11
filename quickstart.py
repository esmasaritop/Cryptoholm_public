"""
Quick Start Script
HÄ±zlÄ± baÅŸlangÄ±Ã§ iÃ§in kullanÄ±ÅŸlÄ± script
"""

import sys
import os


def print_banner():
    banner = \"\"\"
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                                                                       â•‘
â•‘   âš¡ EV Charging SOC Manipulation Attack Simulation âš¡               â•‘
â•‘                                                                       â•‘
â•‘   Elektrikli AraÃ§ Åarj Ä°stasyonu                                     â•‘
â•‘   SOC ManipÃ¼lasyonu SaldÄ±rÄ± SimÃ¼lasyonu                              â•‘
â•‘                                                                       â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    \"\"\"
    print(banner)


def print_menu():
    menu = \"\"\"
MenÃ¼:
  1. ğŸ”´ Zafiyet Demosu (Attack Demo)
     - SOC manipÃ¼lasyon saldÄ±rÄ±sÄ±
     - AÅŸÄ±rÄ± ÅŸarj tehlikesi
     - MITM proxy saldÄ±rÄ±sÄ±
     
  2. ğŸ›¡ï¸  GÃ¼venli Sistem Demosu (Secure Demo)
     - Kriptografik koruma
     - SaldÄ±rÄ± engelleme
     - BaÄŸÄ±msÄ±z doÄŸrulama
     
  3. ğŸ§ª Testleri Ã‡alÄ±ÅŸtÄ±r (Run Tests)
     - Zafiyet testleri
     - GÃ¼venlik testleri
     
  4. ğŸ“Š ModÃ¼l Testleri (Module Tests)
     - BMS testi
     - OCPP testi
     - CAN bus testi
     - GÃ¼venlik testleri
     
  5. â„¹ï¸  Proje HakkÄ±nda (About)
  
  0. ğŸšª Ã‡Ä±kÄ±ÅŸ (Exit)
    \"\"\"
    print(menu)


def run_attack_demo():
    \"\"\"SaldÄ±rÄ± demosunu Ã§alÄ±ÅŸtÄ±r\"\"\"
    print("\nğŸ”´ Starting Attack Demo...\n")
    os.system("python demos/demo_attack.py")


def run_secure_demo():
    \"\"\"GÃ¼venli sistem demosunu Ã§alÄ±ÅŸtÄ±r\"\"\"
    print("\nğŸ›¡ï¸  Starting Secure System Demo...\n")
    os.system("python demos/demo_secure.py")


def run_tests():
    \"\"\"Testleri Ã§alÄ±ÅŸtÄ±r\"\"\"
    print("\nğŸ§ª Running Tests...\n")
    print("Running vulnerable system tests...")
    os.system("pytest tests/test_vulnerable.py -v")
    print("\nRunning secure system tests...")
    os.system("pytest tests/test_secure.py -v")


def run_module_tests():
    \"\"\"ModÃ¼l testlerini Ã§alÄ±ÅŸtÄ±r\"\"\"
    print("\nğŸ“Š Module Tests\n")
    print("1. BMS Test")
    print("2. OCPP Test")
    print("3. CAN Bus Test")
    print("4. Security Test")
    print("5. All Module Tests")
    print("0. Back to Main Menu")
    
    choice = input("\nSelect module: ")
    
    if choice == "1":
        print("\nğŸ”‹ Testing BMS...")
        os.system("python src/bms/battery.py")
        os.system("python src/bms/bms_controller.py")
    elif choice == "2":
        print("\nğŸ“¡ Testing OCPP...")
        os.system("python src/ocpp/vehicle_client.py")
        os.system("python src/ocpp/charging_station.py")
    elif choice == "3":
        print("\nğŸš— Testing CAN Bus...")
        os.system("python src/can_bus/can_simulator.py")
    elif choice == "4":
        print("\nğŸ”’ Testing Security...")
        os.system("python src/security/crypto_handler.py")
        os.system("python src/security/integrity_checker.py")
    elif choice == "5":
        print("\nğŸ“Š Testing All Modules...")
        os.system("python src/bms/battery.py")
        os.system("python src/bms/bms_controller.py")
        os.system("python src/ocpp/vehicle_client.py")
        os.system("python src/ocpp/charging_station.py")
        os.system("python src/can_bus/can_simulator.py")
        os.system("python src/security/crypto_handler.py")
        os.system("python src/security/integrity_checker.py")


def show_about():
    \"\"\"Proje hakkÄ±nda bilgi gÃ¶ster\"\"\"
    about = \"\"\"
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘                         PROJE HAKKINDA                                â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

ğŸ“‹ Senaryo:
SaldÄ±rgan, araÃ§ ile ÅŸarj istasyonu arasÄ±ndaki OCPP iletiÅŸim hattÄ±nÄ± 
manipÃ¼le ederek, bataryanÄ±n doluluk oranÄ± (SOC) hakkÄ±nda hatalÄ± veri 
iletir. Kimlik doÄŸrulamasÄ± ve veri bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ kontrolÃ¼ eksik olan 
sistemde, araÃ§ bataryasÄ± zaten dolu olmasÄ±na raÄŸmen ÅŸarj devam eder.

âš ï¸  Tespit Edilen Zafiyetler:
  â€¢ SOC verilerinde kriptografik bÃ¼tÃ¼nlÃ¼k korumasÄ± eksikliÄŸi
  â€¢ Dijital imza ve zaman damgasÄ± mekanizmasÄ± bulunmamasÄ±
  â€¢ BMS'in OCPP mesajlarÄ±na karÅŸÄ± baÄŸÄ±msÄ±z doÄŸrulama yapamamasÄ±
  â€¢ Man-in-the-Middle (MITM) saldÄ±rÄ±larÄ±na karÅŸÄ± yetersiz koruma

ğŸ’¥ OlasÄ± SonuÃ§lar:
  â€¢ Batarya hÃ¼crelerinde yangÄ±n ve patlama riski
  â€¢ Kritik sÄ±caklÄ±k seviyelerine ulaÅŸma
  â€¢ Batarya Ã¶mrÃ¼nÃ¼n ciddi ÅŸekilde kÄ±salmasÄ±
  â€¢ Åarj istasyonu ekipmanlarÄ±nda hasar

ğŸ›¡ï¸  GÃ¼venlik Ã‡Ã¶zÃ¼mleri:
  â€¢ HMAC-SHA256 ile mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼
  â€¢ RSA dijital imzalama
  â€¢ Zaman damgasÄ± kontrolÃ¼ (replay attack korumasÄ±)
  â€¢ BMS baÄŸÄ±msÄ±z sensÃ¶r doÄŸrulamasÄ±
  â€¢ Anomali tespiti

ğŸ“š Proje YapÄ±sÄ±:
  â€¢ src/bms/          - Battery Management System
  â€¢ src/ocpp/         - OCPP Protocol Implementation
  â€¢ src/attack/       - Attack Simulation Modules
  â€¢ src/security/     - Security Mechanisms
  â€¢ src/can_bus/      - CAN Bus Simulation
  â€¢ src/utils/        - Utilities (Logger, Visualizer)
  â€¢ demos/            - Demo Scripts
  â€¢ tests/            - Test Suites

âš–ï¸  Yasal UyarÄ±:
Bu proje sadece eÄŸitim ve araÅŸtÄ±rma amaÃ§lÄ±dÄ±r. GerÃ§ek sistemlerde 
izinsiz test yapmak yasa dÄ±ÅŸÄ±dÄ±r.

    \"\"\"
    print(about)
    input("\nPress Enter to continue...")


def main():
    \"\"\"Ana fonksiyon\"\"\"
    while True:
        print_banner()
        print_menu()
        
        choice = input("SeÃ§iminiz (0-5): ").strip()
        
        if choice == "1":
            run_attack_demo()
        elif choice == "2":
            run_secure_demo()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            run_module_tests()
        elif choice == "5":
            show_about()
        elif choice == "0":
            print("\nğŸ‘‹ Ã‡Ä±kÄ±ÅŸ yapÄ±lÄ±yor...\n")
            sys.exit(0)
        else:
            print("\nâŒ GeÃ§ersiz seÃ§im! LÃ¼tfen 0-5 arasÄ±nda bir deÄŸer girin.\n")
        
        input("\nPress Enter to continue...")
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nğŸ‘‹ Program sonlandÄ±rÄ±ldÄ±.\n")
        sys.exit(0)
