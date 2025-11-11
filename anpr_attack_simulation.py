"""
ANPR (Automatic Number Plate Recognition) Yanıltma Saldırısı Simülasyonu
Plaka tanıma sistemindeki güvenlik açıklarını test eder ve anomali tespiti yapar.

Hazırlayan: Yusuf Kaymaz
Öğrenci No: 230541084
Ders: Bilgi Sistemleri Güvenliği
"""

import random
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Dict
import json


@dataclass
class Vehicle:
    """Araç bilgilerini tutan sınıf"""
    plate: str
    owner_id: str
    balance: float
    gps_location: Tuple[float, float]
    device_uuid: str
    
    
@dataclass
class ChargingSession:
    """Şarj oturumu bilgilerini tutan sınıf"""
    session_id: str
    detected_plate: str
    actual_plate: str
    anpr_confidence: float
    timestamp: datetime
    station_id: str
    station_location: Tuple[float, float]
    authorized_user_id: str
    actual_user_id: str
    charge_amount_kwh: float
    cost: float
    is_fraudulent: bool
    detection_method: str = None
    gps_match: bool = False
    device_present: bool = False
    weather_condition: str = "normal"
    

class ANPRAttackSimulator:
    """ANPR saldırı simülasyonu ana sınıfı"""
    
    # Plaka karakter benzerlik haritası (yanıltma için kullanılır)
    SIMILAR_CHARS = {
        'O': ['0', 'Q', 'D'],
        '0': ['O', 'Q'],
        'B': ['8', '3'],
        '8': ['B', '3'],
        'S': ['5'],
        '5': ['S'],
        'Z': ['2'],
        '2': ['Z'],
        'I': ['1', 'l'],
        '1': ['I', 'l'],
        'A': ['4'],
        '4': ['A']
    }
    
    WEATHER_CONDITIONS = ['normal', 'rain', 'night', 'fog', 'dirty_plate']
    
    def __init__(self, num_legitimate_users: int = 100, num_stations: int = 10):
        """
        Simülatör başlatma
        
        Args:
            num_legitimate_users: Meşru kullanıcı sayısı
            num_stations: Şarj istasyonu sayısı
        """
        self.legitimate_users = self._generate_users(num_legitimate_users)
        self.stations = self._generate_stations(num_stations)
        self.sessions: List[ChargingSession] = []
        
        # Güvenlik parametreleri
        self.anpr_confidence_threshold = 0.85
        self.gps_proximity_threshold = 100  # metre
        self.max_sessions_per_hour = 3
        
    def _generate_users(self, count: int) -> List[Vehicle]:
        """Rastgele meşru kullanıcı oluştur"""
        users = []
        cities = ['06', '34', '35', '16', '42', '07']
        
        for i in range(count):
            city = random.choice(cities)
            letters = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVYZ', k=random.choice([1, 2, 3])))
            numbers = ''.join(random.choices('0123456789', k=random.randint(2, 4)))
            plate = f"{city} {letters} {numbers}"
            
            users.append(Vehicle(
                plate=plate,
                owner_id=f"USER_{i:04d}",
                balance=random.uniform(100, 1000),
                gps_location=(random.uniform(38.0, 42.0), random.uniform(26.0, 45.0)),
                device_uuid=f"DEVICE_{i:04d}"
            ))
        return users
    
    def _generate_stations(self, count: int) -> List[Dict]:
        """Rastgele şarj istasyonu oluştur"""
        stations = []
        for i in range(count):
            stations.append({
                'id': f"STATION_{i:03d}",
                'name': f"AVM/Site Şarj İstasyonu {i+1}",
                'location': (random.uniform(38.0, 42.0), random.uniform(26.0, 45.0))
            })
        return stations
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """İki konum arasındaki mesafeyi hesapla (km cinsinden yaklaşık)"""
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        # Basitleştirilmiş mesafe hesabı
        return np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # km
    
    def create_spoofed_plate(self, original_plate: str, spoof_level: str = 'medium') -> Tuple[str, float]:
        """
        Sahte/yanıltıcı plaka oluştur
        
        Args:
            original_plate: Orijinal plaka
            spoof_level: Yanıltma seviyesi ('low', 'medium', 'high')
            
        Returns:
            (sahte_plaka, anpr_confidence_score)
        """
        plate_chars = list(original_plate.replace(' ', ''))
        
        if spoof_level == 'high':
            # Yüksek seviye: Çok benzer karakterler, yüksek başarı şansı
            num_changes = random.randint(1, 2)
            confidence = random.uniform(0.75, 0.95)
        elif spoof_level == 'medium':
            # Orta seviye: Bazı karakterler değiştirilir
            num_changes = random.randint(2, 3)
            confidence = random.uniform(0.65, 0.85)
        else:  # low
            # Düşük seviye: Birçok karakter değiştirilir, düşük başarı şansı
            num_changes = random.randint(3, 5)
            confidence = random.uniform(0.45, 0.75)
        
        # Rastgele pozisyonlarda karakter değiştir
        for _ in range(min(num_changes, len(plate_chars))):
            pos = random.randint(0, len(plate_chars) - 1)
            original_char = plate_chars[pos]
            
            if original_char in self.SIMILAR_CHARS:
                plate_chars[pos] = random.choice(self.SIMILAR_CHARS[original_char])
        
        spoofed = ''.join(plate_chars)
        # Orijinal formatı koru (boşluklar)
        if len(original_plate.split()) == 3:
            parts = [spoofed[:2], spoofed[2:-4], spoofed[-4:]]
            spoofed = ' '.join([p for p in parts if p])
        
        return spoofed, confidence
    
    def simulate_normal_session(self) -> ChargingSession:
        """Normal (meşru) şarj oturumu simüle et"""
        user = random.choice(self.legitimate_users)
        station = random.choice(self.stations)
        
        # Normal şartlarda yüksek ANPR güven skoru
        weather = random.choice(self.WEATHER_CONDITIONS)
        if weather == 'normal':
            confidence = random.uniform(0.90, 0.99)
        elif weather in ['rain', 'night']:
            confidence = random.uniform(0.80, 0.92)
        else:  # fog, dirty_plate
            confidence = random.uniform(0.70, 0.85)
        
        # Kullanıcı istasyona yakın (GPS eşleşmesi)
        distance = random.uniform(0, 50)  # 0-50 metre
        gps_match = distance < self.gps_proximity_threshold
        
        charge_kwh = random.uniform(10, 60)
        cost = charge_kwh * random.uniform(3.5, 5.0)  # TL/kWh
        
        session = ChargingSession(
            session_id=f"SESSION_{len(self.sessions):06d}",
            detected_plate=user.plate,
            actual_plate=user.plate,
            anpr_confidence=confidence,
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30)),
            station_id=station['id'],
            station_location=station['location'],
            authorized_user_id=user.owner_id,
            actual_user_id=user.owner_id,
            charge_amount_kwh=charge_kwh,
            cost=cost,
            is_fraudulent=False,
            gps_match=gps_match,
            device_present=True,
            weather_condition=weather
        )
        
        return session
    
    def simulate_attack_session(self, spoof_level: str = 'medium') -> ChargingSession:
        """Saldırı senaryosu: Plaka yanıltma saldırısı simüle et"""
        victim = random.choice(self.legitimate_users)
        attacker_id = f"ATTACKER_{random.randint(1000, 9999)}"
        station = random.choice(self.stations)
        
        # Saldırgan kurbanın plakasını taklit eder
        spoofed_plate, confidence = self.create_spoofed_plate(victim.plate, spoof_level)
        
        # Hava koşulları saldırı başarı şansını etkiler
        weather = random.choice(self.WEATHER_CONDITIONS)
        if weather in ['rain', 'night', 'fog', 'dirty_plate']:
            # Kötü hava koşulları ANPR hatasını artırır
            confidence *= random.uniform(0.85, 0.95)
        
        # Saldırgan kurbanın GPS lokasyonunda değil
        attacker_location = (
            victim.gps_location[0] + random.uniform(-1, 1),
            victim.gps_location[1] + random.uniform(-1, 1)
        )
        distance = self._calculate_distance(attacker_location, station['location'])
        gps_match = distance < self.gps_proximity_threshold * 10  # Saldırgan uzakta
        
        charge_kwh = random.uniform(15, 80)
        cost = charge_kwh * random.uniform(3.5, 5.0)
        
        session = ChargingSession(
            session_id=f"SESSION_{len(self.sessions):06d}",
            detected_plate=spoofed_plate,
            actual_plate=victim.plate,  # Sistem bunu kurbanın plakası olarak algılar
            anpr_confidence=confidence,
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30)),
            station_id=station['id'],
            station_location=station['location'],
            authorized_user_id=victim.owner_id,  # Kurban hesabına yetkilendirme
            actual_user_id=attacker_id,  # Gerçekte saldırgan
            charge_amount_kwh=charge_kwh,
            cost=cost,
            is_fraudulent=True,
            gps_match=False,  # GPS uyuşmazlığı
            device_present=False,  # Kurbanın cihazı mevcut değil
            weather_condition=weather
        )
        
        return session
    
    def detect_anomalies(self, session: ChargingSession) -> Dict[str, any]:
        """
        Anomali tespiti algoritması
        
        Returns:
            Tespit sonuçları ve risk skoru
        """
        anomalies = []
        risk_score = 0.0
        
        # 1. ANPR güven skoru kontrolü
        if session.anpr_confidence < self.anpr_confidence_threshold:
            anomalies.append("LOW_ANPR_CONFIDENCE")
            risk_score += 30
        
        # 2. GPS lokasyon uyuşmazlığı
        if not session.gps_match:
            anomalies.append("GPS_MISMATCH")
            risk_score += 40
        
        # 3. Cihaz varlığı kontrolü (BLE/NFC)
        if not session.device_present:
            anomalies.append("DEVICE_NOT_PRESENT")
            risk_score += 25
        
        # 4. Kötü hava koşulları + düşük güven skoru
        if session.weather_condition in ['rain', 'fog', 'dirty_plate'] and \
           session.anpr_confidence < 0.80:
            anomalies.append("WEATHER_LOW_CONFIDENCE")
            risk_score += 15
        
        # 5. Plakada benzer karakter tespiti
        has_ambiguous_chars = any(char in session.detected_plate 
                                  for char in ['O', '0', 'B', '8', 'S', '5', 'Z', '2'])
        if has_ambiguous_chars and session.anpr_confidence < 0.90:
            anomalies.append("AMBIGUOUS_CHARACTERS")
            risk_score += 20
        
        # Risk skoru normalizasyonu (0-100)
        risk_score = min(100, risk_score)
        
        detection_result = {
            'session_id': session.session_id,
            'is_fraudulent': session.is_fraudulent,
            'anomalies': anomalies,
            'risk_score': risk_score,
            'should_block': risk_score > 60,
            'requires_manual_verification': 40 < risk_score <= 60,
            'anpr_confidence': session.anpr_confidence
        }
        
        return detection_result
    
    def run_simulation(self, 
                      num_normal: int = 800, 
                      num_attacks: int = 200,
                      attack_distribution: Dict[str, int] = None) -> List[Dict]:
        """
        Tam simülasyon çalıştır
        
        Args:
            num_normal: Normal oturum sayısı
            num_attacks: Saldırı oturumu sayısı
            attack_distribution: Saldırı seviyesi dağılımı {'low': 50, 'medium': 100, 'high': 50}
        
        Returns:
            Tespit sonuçları listesi
        """
        if attack_distribution is None:
            attack_distribution = {
                'low': num_attacks // 4,
                'medium': num_attacks // 2,
                'high': num_attacks // 4
            }
        
        print(f"🚗 ANPR Saldırı Simülasyonu Başlatılıyor...")
        print(f"📊 {num_normal} normal oturum + {num_attacks} saldırı oturumu")
        print("-" * 60)
        
        results = []
        
        # Normal oturumlar
        for i in range(num_normal):
            session = self.simulate_normal_session()
            self.sessions.append(session)
            detection = self.detect_anomalies(session)
            results.append(detection)
            
            if (i + 1) % 200 == 0:
                print(f"✅ {i + 1} normal oturum simüle edildi...")
        
        # Saldırı oturumları
        attack_count = 0
        for level, count in attack_distribution.items():
            for i in range(count):
                session = self.simulate_attack_session(spoof_level=level)
                self.sessions.append(session)
                detection = self.detect_anomalies(session)
                results.append(detection)
                attack_count += 1
                
                if attack_count % 50 == 0:
                    print(f"🎯 {attack_count} saldırı oturumu simüle edildi...")
        
        print("-" * 60)
        print("✅ Simülasyon tamamlandı!")
        
        return results
    
    def calculate_metrics(self, results: List[Dict]) -> Dict:
        """
        Performans metriklerini hesapla
        """
        true_positives = sum(1 for r in results if r['is_fraudulent'] and r['should_block'])
        false_positives = sum(1 for r in results if not r['is_fraudulent'] and r['should_block'])
        true_negatives = sum(1 for r in results if not r['is_fraudulent'] and not r['should_block'])
        false_negatives = sum(1 for r in results if r['is_fraudulent'] and not r['should_block'])
        
        total = len(results)
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Finansal etki hesaplama
        total_fraud_cost = sum(s.cost for s in self.sessions if s.is_fraudulent)
        prevented_fraud_cost = sum(s.cost for s, r in zip(self.sessions, results) 
                                   if s.is_fraudulent and r['should_block'])
        undetected_fraud_cost = total_fraud_cost - prevented_fraud_cost
        
        metrics = {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'true_negatives': true_negatives,
            'false_negatives': false_negatives,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'total_sessions': total,
            'fraudulent_sessions': sum(1 for r in results if r['is_fraudulent']),
            'blocked_sessions': sum(1 for r in results if r['should_block']),
            'total_fraud_cost_tl': total_fraud_cost,
            'prevented_fraud_cost_tl': prevented_fraud_cost,
            'undetected_fraud_cost_tl': undetected_fraud_cost,
            'fraud_prevention_rate': (prevented_fraud_cost / total_fraud_cost * 100) if total_fraud_cost > 0 else 0
        }
        
        return metrics
    
    def save_results(self, results: List[Dict], metrics: Dict, filename: str = 'simulation_results.json'):
        """Sonuçları JSON dosyasına kaydet"""
        data = {
            'simulation_date': datetime.now().isoformat(),
            'metrics': metrics,
            'detection_results': results[:100],  # İlk 100 sonucu kaydet
            'sessions_summary': {
                'total_sessions': len(self.sessions),
                'normal_sessions': sum(1 for s in self.sessions if not s.is_fraudulent),
                'attack_sessions': sum(1 for s in self.sessions if s.is_fraudulent)
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Sonuçlar '{filename}' dosyasına kaydedildi.")


def main():
    """Ana test fonksiyonu"""
    # Simülatör oluştur
    simulator = ANPRAttackSimulator(num_legitimate_users=100, num_stations=10)
    
    # Simülasyonu çalıştır
    results = simulator.run_simulation(
        num_normal=800,
        num_attacks=200,
        attack_distribution={'low': 50, 'medium': 100, 'high': 50}
    )
    
    # Metrikleri hesapla
    metrics = simulator.calculate_metrics(results)
    
    # Sonuçları yazdır
    print("\n" + "=" * 60)
    print("📈 PERFORMANS METRİKLERİ")
    print("=" * 60)
    print(f"Toplam Oturum: {metrics['total_sessions']}")
    print(f"Sahte Oturum: {metrics['fraudulent_sessions']}")
    print(f"Engellenen Oturum: {metrics['blocked_sessions']}")
    print(f"\nDoğru Pozitif (TP): {metrics['true_positives']}")
    print(f"Yanlış Pozitif (FP): {metrics['false_positives']}")
    print(f"Doğru Negatif (TN): {metrics['true_negatives']}")
    print(f"Yanlış Negatif (FN): {metrics['false_negatives']}")
    print(f"\nDoğruluk (Accuracy): {metrics['accuracy']*100:.2f}%")
    print(f"Kesinlik (Precision): {metrics['precision']*100:.2f}%")
    print(f"Duyarlılık (Recall): {metrics['recall']*100:.2f}%")
    print(f"F1 Skoru: {metrics['f1_score']*100:.2f}%")
    print(f"\n💰 FİNANSAL ETKİ")
    print(f"Toplam Dolandırıcılık Maliyeti: {metrics['total_fraud_cost_tl']:.2f} TL")
    print(f"Önlenen Dolandırıcılık: {metrics['prevented_fraud_cost_tl']:.2f} TL")
    print(f"Tespit Edilemeyen Kayıp: {metrics['undetected_fraud_cost_tl']:.2f} TL")
    print(f"Dolandırıcılık Önleme Oranı: {metrics['fraud_prevention_rate']:.2f}%")
    print("=" * 60)
    
    # Sonuçları kaydet
    simulator.save_results(results, metrics)
    
    return simulator, results, metrics


if __name__ == "__main__":
    simulator, results, metrics = main()

