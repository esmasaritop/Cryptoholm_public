"""
CypherCar: Otonom Araç Güvenlik Anomalilerinin Python Çözümleri
Ana Demonstrasyon Programı

Bu program, bağlantılı ve otonom araçlarda (CAV) tespit edilen
üç kritik güvenlik anomalisinin çözümlerini gösterir.

Anomaliler:
1. Güvenlik ve Gecikme Paradoksu (Security vs. Latency Paradox)
2. Mahremiyet için Kalıcılık Kullanımı (Privacy vs. Immutability)
3. Kanıtın Kendi Kendini Yok Etmesi (Self-Destructing Evidence)

Yazar: CypherCar Security Research Team
Tarih: 2025
"""

import sys
import time
from colorama import init, Fore, Style, Back

# Colorama başlat (Windows/Linux uyumluluğu için)
init(autoreset=True)

# Anomali modüllerini import et
try:
    from anomaly1_security_latency import demonstrate_anomaly_solution as demo1
    from anomaly2_privacy_blockchain import demonstrate_anomaly_solution as demo2
    from anomaly3_forensic_evidence import demonstrate_anomaly_solution as demo3
except ImportError as e:
    print(f"HATA: Modüller yüklenemedi: {e}")
    print("Lütfen tüm anomali modüllerinin aynı dizinde olduğundan emin olun.")
    sys.exit(1)


def print_banner():
    """Hoş geldin banner'ı göster"""
    banner = f"""
{Fore.CYAN}{'=' * 80}
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║{Fore.YELLOW}                            🚗 CYPHERCAR 🔐                                   {Fore.CYAN}║
{Fore.CYAN}║{Fore.WHITE}        Otonom Araç Güvenlik Anomalilerinin Python Çözümleri                 {Fore.CYAN}║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝
{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}
    """
    print(banner)


def print_menu():
    """Ana menüyü göster"""
    menu = f"""
{Fore.GREEN}╔════════════════════════════════════════════════════════════════════════╗
{Fore.GREEN}║                          ANA MENÜ                                      ║
{Fore.GREEN}╠════════════════════════════════════════════════════════════════════════╣
{Fore.GREEN}║                                                                        ║
{Fore.YELLOW}║  1. {Fore.WHITE}Anomali 1: Güvenlik ve Gecikme Paradoksu                       {Fore.GREEN}║
{Fore.WHITE}║     {Fore.CYAN}→ Adaptif Risk Tabanlı Güvenlik Sistemi                        {Fore.GREEN}║
{Fore.WHITE}║     {Fore.MAGENTA}(Han, J., et al. 2023 - Secure Operations)                     {Fore.GREEN}║
{Fore.GREEN}║                                                                        ║
{Fore.YELLOW}║  2. {Fore.WHITE}Anomali 2: Mahremiyet için Kalıcılık Kullanımı                 {Fore.GREEN}║
{Fore.WHITE}║     {Fore.CYAN}→ Hibrit Off-Chain + Zero-Knowledge Proof Blockchain           {Fore.GREEN}║
{Fore.WHITE}║     {Fore.MAGENTA}(Xu, C., et al. 2022 - Blockchain & Privacy)                   {Fore.GREEN}║
{Fore.GREEN}║                                                                        ║
{Fore.YELLOW}║  3. {Fore.WHITE}Anomali 3: Kanıtın Kendi Kendini Yok Etmesi                    {Fore.GREEN}║
{Fore.WHITE}║     {Fore.CYAN}→ Çok Katmanlı Dayanıklı Veri Saklama Sistemi                  {Fore.GREEN}║
{Fore.WHITE}║     {Fore.MAGENTA}(Strandberg, K., et al. 2022 - Automotive Forensics)           {Fore.GREEN}║
{Fore.GREEN}║                                                                        ║
{Fore.YELLOW}║  4. {Fore.WHITE}Tüm Anomalileri Sırayla Göster                                 {Fore.GREEN}║
{Fore.YELLOW}║  5. {Fore.WHITE}Hakkında                                                       {Fore.GREEN}║
{Fore.YELLOW}║  0. {Fore.RED}Çıkış                                                          {Fore.GREEN}║
{Fore.GREEN}║                                                                        ║
{Fore.GREEN}╚════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(menu)


def print_about():
    """Hakkında bilgisi"""
    about = f"""
{Fore.CYAN}{'=' * 80}
{Fore.YELLOW}HAKKINDA
{Fore.CYAN}{'=' * 80}

{Fore.WHITE}Bu proje, bağlantılı ve otonom araç (CAV) güvenliği alanındaki üç kritik
anomalinin Python tabanlı çözümlerini sunar.

{Fore.GREEN}📚 Kaynak Makaleler:{Fore.WHITE}

1. Han, J., et al. (2023): "Secure Operations in Connected and Autonomous Vehicles"
   {Fore.CYAN}→ Güvenlik ve Gecikme Paradoksu{Fore.WHITE}
   {Fore.MAGENTA}Problem:{Fore.WHITE} Siber güvenlik kontrolleri gecikme yaratır, fiziksel kaza riski artar.
   {Fore.GREEN}Çözüm:{Fore.WHITE} Adaptif risk tabanlı güvenlik seviyesi seçimi.

2. Xu, C., et al. (2022): "Blockchain and Privacy in Internet of Vehicles"
   {Fore.CYAN}→ Mahremiyet için Kalıcılık Kullanımı{Fore.WHITE}
   {Fore.MAGENTA}Problem:{Fore.WHITE} Blockchain'in değişmezliği, unutulma hakkıyla çelişir.
   {Fore.GREEN}Çözüm:{Fore.WHITE} Hibrit off-chain storage + zero-knowledge proofs.

3. Strandberg, K., et al. (2022): "Automotive Digital Forensics"
   {Fore.CYAN}→ Kanıtın Kendi Kendini Yok Etmesi{Fore.WHITE}
   {Fore.MAGENTA}Problem:{Fore.WHITE} Kaza anında dijital kanıtlar fiziksel hasarla yok olur.
   {Fore.GREEN}Çözüm:{Fore.WHITE} Redundant storage + gerçek zamanlı bulut senkronizasyonu.

{Fore.GREEN}🔧 Teknolojiler:{Fore.WHITE}
   • Python 3.8+
   • Cryptography (AES, SHA, RSA)
   • Simüle edilmiş Blockchain
   • Zero-Knowledge Proofs (basitleştirilmiş)
   • Redundant Storage Architecture

{Fore.GREEN}📧 İletişim:{Fore.WHITE}
   • GitHub: github.com/cyphercar
   • E-posta: info@cyphercar.com

{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}
    """
    print(about)


def run_anomaly(anomaly_num: int):
    """Belirtilen anomali demonstrasyonunu çalıştır"""
    print(f"\n{Fore.YELLOW}Demonstrasyon başlatılıyor...{Style.RESET_ALL}\n")
    time.sleep(1)
    
    try:
        if anomaly_num == 1:
            demo1()
        elif anomaly_num == 2:
            demo2()
        elif anomaly_num == 3:
            demo3()
        else:
            print(f"{Fore.RED}Geçersiz anomali numarası!{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}✓ Demonstrasyon tamamlandı!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}HATA: Demonstrasyon sırasında bir hata oluştu:{Style.RESET_ALL}")
        print(f"{Fore.RED}{str(e)}{Style.RESET_ALL}")


def run_all_anomalies():
    """Tüm anomalileri sırayla çalıştır"""
    anomalies = [
        ("Anomali 1: Güvenlik ve Gecikme Paradoksu", demo1),
        ("Anomali 2: Mahremiyet için Kalıcılık Kullanımı", demo2),
        ("Anomali 3: Kanıtın Kendi Kendini Yok Etmesi", demo3)
    ]
    
    for idx, (name, demo_func) in enumerate(anomalies, 1):
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.YELLOW}[{idx}/3] {name}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
        
        time.sleep(1)
        
        try:
            demo_func()
            print(f"\n{Fore.GREEN}✓ Demonstrasyon {idx} tamamlandı!{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}HATA: Demonstrasyon {idx} sırasında bir hata oluştu:{Style.RESET_ALL}")
            print(f"{Fore.RED}{str(e)}{Style.RESET_ALL}")
        
        if idx < len(anomalies):
            print(f"\n{Fore.YELLOW}Sonraki anomaliye geçiliyor...{Style.RESET_ALL}")
            time.sleep(2)
    
    print(f"\n{Fore.GREEN}{'=' * 80}")
    print(f"{Fore.GREEN}✓ TÜM ANOMALİLER TAMAMLANDI!")
    print(f"{Fore.GREEN}{'=' * 80}{Style.RESET_ALL}\n")


def main():
    """Ana program döngüsü"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input(f"{Fore.YELLOW}Seçiminiz (0-5): {Style.RESET_ALL}").strip()
            
            if choice == '0':
                print(f"\n{Fore.CYAN}CypherCar'dan ayrılıyorsunuz. Güvenli sürüşler! 🚗{Style.RESET_ALL}\n")
                sys.exit(0)
            
            elif choice == '1':
                run_anomaly(1)
            
            elif choice == '2':
                run_anomaly(2)
            
            elif choice == '3':
                run_anomaly(3)
            
            elif choice == '4':
                confirm = input(f"\n{Fore.YELLOW}Tüm demonstrasyonlar sırayla çalıştırılacak. Devam etmek istiyor musunuz? (e/h): {Style.RESET_ALL}").strip().lower()
                if confirm == 'e' or confirm == 'evet':
                    run_all_anomalies()
                else:
                    print(f"{Fore.CYAN}İptal edildi.{Style.RESET_ALL}")
            
            elif choice == '5':
                print_about()
            
            else:
                print(f"{Fore.RED}Geçersiz seçim! Lütfen 0-5 arasında bir sayı girin.{Style.RESET_ALL}")
            
            # Devam için bekle
            if choice != '0':
                input(f"\n{Fore.CYAN}Ana menüye dönmek için Enter tuşuna basın...{Style.RESET_ALL}")
                print("\n" * 2)
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Program kullanıcı tarafından sonlandırıldı.{Style.RESET_ALL}\n")
            sys.exit(0)
        
        except Exception as e:
            print(f"\n{Fore.RED}Beklenmeyen bir hata oluştu: {str(e)}{Style.RESET_ALL}\n")
            input(f"{Fore.CYAN}Devam etmek için Enter tuşuna basın...{Style.RESET_ALL}")


if __name__ == "__main__":
    print(f"\n{Fore.GREEN}CypherCar başlatılıyor...{Style.RESET_ALL}\n")
    time.sleep(0.5)
    
    try:
        main()
    except Exception as e:
        print(f"\n{Fore.RED}Kritik hata: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)
