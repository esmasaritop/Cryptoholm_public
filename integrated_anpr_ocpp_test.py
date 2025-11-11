"""
Entegre ANPR + OCPP Test Simülasyonu
ANPR anomali tespiti ile OCPP protokolü birlikte çalışır.

Hazırlayan: Yusuf Kaymaz
Öğrenci No: 230541084
Ders: Bilgi Sistemleri Güvenliği
"""

from anpr_attack_simulation import ANPRAttackSimulator
from ocpp_simulator import OCPPCentralSystem, OCPPChargePoint
import random


class IntegratedANPRandOCPP:
    """ANPR ve OCPP entegre test sistemi"""
    
    def __init__(self):
        """Entegre sistem başlatma"""
        self.anpr_simulator = ANPRAttackSimulator(num_legitimate_users=50, num_stations=5)
        self.ocpp_system = OCPPCentralSystem()
        
        # OCPP şarj istasyonları oluştur
        for station in self.anpr_simulator.stations:
            cp = OCPPChargePoint(
                charge_point_id=station['id'],
                vendor="TurkCharger",
                model="TC-50kW"
            )
            self.ocpp_system.register_charge_point(cp)
    
    def run_integrated_test(self, num_tests: int = 10):
        """Entegre test çalıştır"""
        print("\n" + "="*80)
        print("🔋 ENTEGRE ANPR + OCPP GÜVENLİK TESTİ")
        print("="*80)
        print(f"Test Sayısı: {num_tests}")
        print(f"ANPR Güven Eşiği: {self.anpr_simulator.anpr_confidence_threshold}")
        print(f"GPS Yakınlık Eşiği: {self.anpr_simulator.gps_proximity_threshold}m")
        print("="*80 + "\n")
        
        successful_attacks = 0
        blocked_attacks = 0
        normal_sessions = 0
        
        for i in range(num_tests):
            # Her testte rastgele normal veya saldırı seç
            is_attack = random.random() < 0.3  # %30 saldırı
            
            if is_attack:
                # Saldırı senaryosu
                victim = random.choice(self.anpr_simulator.legitimate_users)
                station = random.choice(self.anpr_simulator.stations)
                
                spoofed_plate, confidence = self.anpr_simulator.create_spoofed_plate(
                    victim.plate, 
                    spoof_level=random.choice(['low', 'medium', 'high'])
                )
                
                print(f"\n🎯 Test #{i+1}: SALDIRI SENARYOSU")
                print(f"   Kurban: {victim.plate} → Sahte: {spoofed_plate}")
                
                result = self.ocpp_system.simulate_attack_session(
                    charge_point_id=station['id'],
                    victim_plate=victim.plate,
                    spoofed_plate=spoofed_plate,
                    anpr_confidence=confidence
                )
                
                if result['status'] == 'blocked':
                    blocked_attacks += 1
                    print(f"   ✅ Saldırı engellendi!")
                else:
                    successful_attacks += 1
                    print(f"   ❌ Saldırı başarılı oldu!")
            
            else:
                # Normal senaryo
                user = random.choice(self.anpr_simulator.legitimate_users)
                station = random.choice(self.anpr_simulator.stations)
                
                # Normal şartlarda yüksek güven
                confidence = random.uniform(0.88, 0.98)
                
                print(f"\n✅ Test #{i+1}: NORMAL ŞARJ")
                print(f"   Kullanıcı: {user.plate}")
                
                result = self.ocpp_system.simulate_normal_charging_session(
                    charge_point_id=station['id'],
                    plate=user.plate,
                    anpr_confidence=confidence,
                    device_present=True,
                    gps_verified=True
                )
                
                if result.get('status') == 'success':
                    normal_sessions += 1
                    print(f"   ✅ Şarj tamamlandı: {result['energy_kwh']:.2f} kWh")
        
        # Sonuç özeti
        print("\n" + "="*80)
        print("📊 TEST SONUÇLARI")
        print("="*80)
        print(f"Toplam Test: {num_tests}")
        print(f"Normal Oturum: {normal_sessions}")
        print(f"Saldırı Girişimi: {successful_attacks + blocked_attacks}")
        print(f"  ├─ Engellenen: {blocked_attacks}")
        print(f"  └─ Başarılı Olan: {successful_attacks}")
        
        if (successful_attacks + blocked_attacks) > 0:
            block_rate = blocked_attacks / (successful_attacks + blocked_attacks) * 100
            print(f"\nSaldırı Engelleme Oranı: {block_rate:.1f}%")
        
        # OCPP sistem istatistikleri
        stats = self.ocpp_system.get_statistics()
        print(f"\nOCPP Sistem İstatistikleri:")
        print(f"  Aktif Şarj İstasyonu: {stats['total_charge_points']}")
        print(f"  Toplam İşlem: {stats['total_transactions']}")
        print(f"  Dolandırıcılık Girişimi: {stats['fraud_attempts']}")
        print("="*80 + "\n")


def main():
    """Ana program"""
    # Entegre test sistemi
    integrated_system = IntegratedANPRandOCPP()
    integrated_system.run_integrated_test(num_tests=15)


if __name__ == "__main__":
    main()

