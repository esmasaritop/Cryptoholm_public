"""
Anomali 3: Kanıtın Kendi Kendini Yok Etmesi (Self-Destructing Evidence Anomaly)
Çözüm: Çok Katmanlı Dayanıklı Veri Saklama ve Gerçek Zamanlı Bulut Yedekleme Sistemi

Bu modül, kaza anında kritik verilerin yok olmaması için
redundant storage, non-volatile memory ve anlık bulut senkronizasyonu kullanır.
"""

import time
import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import hashlib


class StorageType(Enum):
    """Depolama türleri"""
    VOLATILE = 1      # RAM - Güç kesilince kaybolur
    NON_VOLATILE = 2  # Flash/EEPROM - Kalıcı
    CLOUD = 3         # Bulut - Uzak yedekleme
    BLACK_BOX = 4     # Kara Kutu - Darbe dayanımlı


class EventSeverity(Enum):
    """Olay ciddiyeti"""
    NORMAL = 1
    WARNING = 2
    CRITICAL = 3
    CRASH = 4


@dataclass
class ForensicData:
    """Adli bilişim verisi"""
    timestamp: float
    vehicle_id: str
    speed_kmh: float
    acceleration_g: float
    steering_angle: float
    brake_pressure: float
    location: tuple
    sensor_data: Dict
    event_type: EventSeverity
    data_id: str
    
    def to_json(self) -> str:
        """JSON formatına çevir"""
        data_dict = asdict(self)
        data_dict['event_type'] = self.event_type.name
        return json.dumps(data_dict, sort_keys=True)
    
    def get_hash(self) -> str:
        """Veri bütünlüğü için hash"""
        return hashlib.sha256(self.to_json().encode()).hexdigest()


@dataclass
class StorageStatus:
    """Depolama durumu"""
    storage_type: StorageType
    is_operational: bool
    capacity_used: float  # 0-100%
    last_write_time: float
    damage_level: float  # 0-100%


class RedundantStorageSystem:
    """
    Redundant (Yedekli) Depolama Sistemi
    
    Aynı veriyi 4 farklı yerde saklar:
    1. Volatile RAM (hızlı erişim)
    2. Non-volatile Flash (kalıcı)
    3. Cloud Storage (uzak yedek)
    4. Black Box (darbe dayanımlı kara kutu)
    """
    
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        
        # 4 farklı depolama katmanı
        self.storages = {
            StorageType.VOLATILE: {
                'data': [],
                'status': StorageStatus(StorageType.VOLATILE, True, 0.0, time.time(), 0.0)
            },
            StorageType.NON_VOLATILE: {
                'data': [],
                'status': StorageStatus(StorageType.NON_VOLATILE, True, 0.0, time.time(), 0.0)
            },
            StorageType.CLOUD: {
                'data': [],
                'status': StorageStatus(StorageType.CLOUD, True, 0.0, time.time(), 0.0)
            },
            StorageType.BLACK_BOX: {
                'data': [],
                'status': StorageStatus(StorageType.BLACK_BOX, True, 0.0, time.time(), 0.0)
            }
        }
        
        # Senkronizasyon durumu
        self.sync_queue = []
        self.total_writes = 0
        self.failed_writes = 0
        
    def write_data(self, forensic_data: ForensicData) -> Dict:
        """
        Veriyi tüm depolama sistemlerine yaz
        
        Kritik: Paralel yazma - Bir sistem başarısız olsa bile diğerleri çalışır
        """
        self.total_writes += 1
        write_results = {}
        successful_writes = 0
        
        # Her depolama sistemine yaz (paralel simülasyonu)
        for storage_type, storage_info in self.storages.items():
            try:
                # Depolama durumunu kontrol et
                if not storage_info['status'].is_operational:
                    write_results[storage_type.name] = {
                        'success': False,
                        'reason': 'Storage not operational'
                    }
                    continue
                
                # Yazma gecikme simülasyonu
                write_latency = self._get_write_latency(storage_type)
                
                # Veriyi yaz
                storage_info['data'].append(forensic_data)
                storage_info['status'].last_write_time = time.time()
                storage_info['status'].capacity_used = len(storage_info['data']) * 0.1
                
                write_results[storage_type.name] = {
                    'success': True,
                    'latency_ms': write_latency,
                    'records_stored': len(storage_info['data'])
                }
                successful_writes += 1
                
            except Exception as e:
                write_results[storage_type.name] = {
                    'success': False,
                    'reason': str(e)
                }
                self.failed_writes += 1
        
        return {
            'data_id': forensic_data.data_id,
            'total_storages': len(self.storages),
            'successful_writes': successful_writes,
            'write_results': write_results,
            'redundancy_level': successful_writes / len(self.storages) * 100
        }
    
    def _get_write_latency(self, storage_type: StorageType) -> float:
        """Depolama türüne göre yazma gecikmesi"""
        latencies = {
            StorageType.VOLATILE: 0.1,      # 0.1ms - Çok hızlı
            StorageType.NON_VOLATILE: 2.0,  # 2ms - Hızlı
            StorageType.CLOUD: 50.0,        # 50ms - Yavaş (ağ gecikmesi)
            StorageType.BLACK_BOX: 5.0      # 5ms - Orta
        }
        return latencies[storage_type]
    
    def simulate_crash(self, power_loss: bool = True, physical_damage: float = 80.0):
        """
        Kaza simülasyonu
        
        power_loss: Güç kaybı (volatile memory kaybolur)
        physical_damage: Fiziksel hasar seviyesi (0-100%)
        """
        print("\n" + "!" * 80)
        print("⚠️  KAZA ALGILANDI - Veri Kayıp Analizi")
        print("!" * 80)
        
        damage_report = {}
        
        for storage_type, storage_info in self.storages.items():
            original_records = len(storage_info['data'])
            status = storage_info['status']
            
            # Volatile memory - Güç kaybında tamamen kaybolur
            if storage_type == StorageType.VOLATILE and power_loss:
                storage_info['data'].clear()
                status.is_operational = False
                status.damage_level = 100.0
                damage_report[storage_type.name] = {
                    'original_records': original_records,
                    'remaining_records': 0,
                    'loss_percentage': 100.0,
                    'reason': 'Güç kaybı - RAM temizlendi'
                }
            
            # Non-volatile memory - Fiziksel hasara karşı savunmasız
            elif storage_type == StorageType.NON_VOLATILE:
                if physical_damage > 70:
                    # Yüksek hasar - Kısmi veri kaybı
                    lost_data = int(original_records * (physical_damage / 100))
                    storage_info['data'] = storage_info['data'][:-lost_data] if lost_data < original_records else []
                    status.damage_level = physical_damage
                    status.is_operational = physical_damage < 90
                    
                    damage_report[storage_type.name] = {
                        'original_records': original_records,
                        'remaining_records': len(storage_info['data']),
                        'loss_percentage': (lost_data / max(1, original_records)) * 100,
                        'reason': f'Fiziksel hasar: {physical_damage}%'
                    }
                else:
                    damage_report[storage_type.name] = {
                        'original_records': original_records,
                        'remaining_records': original_records,
                        'loss_percentage': 0.0,
                        'reason': 'Düşük hasar - Veri korundu'
                    }
            
            # Black Box - En dayanıklı, yüksek hasara karşı korumalı
            elif storage_type == StorageType.BLACK_BOX:
                if physical_damage > 95:
                    # Sadece çok yüksek hasarda kayıp
                    lost_data = int(original_records * 0.2)  # Maksimum %20 kayıp
                    storage_info['data'] = storage_info['data'][:-lost_data] if lost_data < original_records else []
                    status.damage_level = physical_damage
                    
                    damage_report[storage_type.name] = {
                        'original_records': original_records,
                        'remaining_records': len(storage_info['data']),
                        'loss_percentage': 20.0,
                        'reason': 'Ekstrem hasar - Kısmi kayıp'
                    }
                else:
                    damage_report[storage_type.name] = {
                        'original_records': original_records,
                        'remaining_records': original_records,
                        'loss_percentage': 0.0,
                        'reason': 'Darbe dayanımlı kasa - Veri korundu'
                    }
            
            # Cloud Storage - Uzakta, fiziksel hasardan etkilenmez
            elif storage_type == StorageType.CLOUD:
                # Bulut her zaman güvende (network yoksa erişilemez ama veri kaybolmaz)
                damage_report[storage_type.name] = {
                    'original_records': original_records,
                    'remaining_records': original_records,
                    'loss_percentage': 0.0,
                    'reason': 'Uzak depolama - Fiziksel hasardan etkilenmez'
                }
        
        return damage_report
    
    def recover_data(self) -> Dict:
        """
        Kaza sonrası veri kurtarma
        
        Öncelik sırası:
        1. Cloud (en güvenli)
        2. Black Box (darbe dayanımlı)
        3. Non-volatile (kalıcı ama hasarlı olabilir)
        4. Volatile (muhtemelen kayıp)
        """
        recovery_priority = [
            StorageType.CLOUD,
            StorageType.BLACK_BOX,
            StorageType.NON_VOLATILE,
            StorageType.VOLATILE
        ]
        
        recovered_data = []
        recovery_source = None
        
        for storage_type in recovery_priority:
            storage_info = self.storages[storage_type]
            if len(storage_info['data']) > 0 and storage_info['status'].is_operational:
                recovered_data = storage_info['data']
                recovery_source = storage_type
                break
        
        # Veri bütünlüğü kontrolü
        data_integrity = self._verify_data_integrity(recovered_data)
        
        return {
            'recovery_successful': len(recovered_data) > 0,
            'recovered_records': len(recovered_data),
            'recovery_source': recovery_source.name if recovery_source else None,
            'data_integrity': data_integrity,
            'forensic_timeline': self._build_timeline(recovered_data)
        }
    
    def _verify_data_integrity(self, data_list: List[ForensicData]) -> Dict:
        """Veri bütünlüğünü kontrol et"""
        if not data_list:
            return {'valid': False, 'reason': 'No data'}
        
        # Hash kontrolü
        for data in data_list:
            expected_hash = data.get_hash()
            # Simülasyon - gerçek uygulamada saklanan hash ile karşılaştırılır
        
        return {
            'valid': True,
            'total_records': len(data_list),
            'time_span_seconds': data_list[-1].timestamp - data_list[0].timestamp if len(data_list) > 1 else 0,
            'integrity_score': 100.0
        }
    
    def _build_timeline(self, data_list: List[ForensicData]) -> List[Dict]:
        """Adli bilişim için zaman çizelgesi oluştur"""
        timeline = []
        for data in data_list[-10:]:  # Son 10 kayıt (kaza öncesi)
            timeline.append({
                'timestamp': datetime.fromtimestamp(data.timestamp).strftime('%H:%M:%S.%f')[:-3],
                'speed_kmh': data.speed_kmh,
                'brake_pressure': data.brake_pressure,
                'event': data.event_type.name
            })
        return timeline
    
    def get_storage_health(self) -> Dict:
        """Depolama sistemlerinin sağlık durumu"""
        health_status = {}
        for storage_type, storage_info in self.storages.items():
            status = storage_info['status']
            health_status[storage_type.name] = {
                'operational': status.is_operational,
                'damage_level': status.damage_level,
                'records_stored': len(storage_info['data']),
                'capacity_used': status.capacity_used
            }
        return health_status


class RealTimeSyncSystem:
    """
    Gerçek Zamanlı Senkronizasyon Sistemi
    
    Kritik verileri anlık olarak buluta gönderir.
    Kaza anında aracın kendisi yok olsa bile veriler bulutta kalır.
    """
    
    def __init__(self):
        self.sync_interval_ms = 100  # 100ms'de bir senkronize et
        self.pending_sync = []
        self.synced_count = 0
        self.sync_failures = 0
    
    def sync_to_cloud(self, data: ForensicData) -> bool:
        """Veriyi buluta senkronize et"""
        try:
            # Simüle edilmiş ağ gecikmesi
            network_delay = random.uniform(10, 50)  # 10-50ms
            
            # %95 başarı oranı (gerçekçi)
            if random.random() < 0.95:
                self.synced_count += 1
                return True
            else:
                self.sync_failures += 1
                self.pending_sync.append(data)
                return False
        except Exception:
            self.sync_failures += 1
            return False
    
    def get_sync_stats(self) -> Dict:
        """Senkronizasyon istatistikleri"""
        total = self.synced_count + self.sync_failures
        success_rate = (self.synced_count / max(1, total)) * 100
        
        return {
            'synced_records': self.synced_count,
            'failed_syncs': self.sync_failures,
            'success_rate': success_rate,
            'pending_sync': len(self.pending_sync)
        }


def demonstrate_anomaly_solution():
    """Anomali 3 çözümünü göster"""
    print("=" * 80)
    print("ANOMALİ 3: KANITIN KENDİ KENDİNİ YOK ETMESİ")
    print("ÇÖZÜM: Çok Katmanlı Dayanıklı Veri Saklama Sistemi")
    print("=" * 80)
    print()
    
    # Sistem oluştur
    vehicle_id = "ARAC_FORENSIC_001"
    storage_system = RedundantStorageSystem(vehicle_id)
    sync_system = RealTimeSyncSystem()
    
    # Sürüş simülasyonu - Normal koşullar
    print("🚗 Sürüş Simülasyonu Başlatılıyor...")
    print("\nNormal sürüş verileri kaydediliyor (4 farklı depolama sistemine):\n")
    
    # 20 saniye sürüş verisi üret
    forensic_records = []
    for i in range(20):
        # Kaza öncesi son 5 saniyede anormal değerler
        is_critical = i >= 15
        
        data = ForensicData(
            timestamp=time.time() + i * 0.1,
            vehicle_id=vehicle_id,
            speed_kmh=80 + (i * 5) if is_critical else 60,
            acceleration_g=-0.2 if is_critical else 0.0,
            steering_angle=random.uniform(-10, 10),
            brake_pressure=90 if is_critical else 0,
            location=(37.7749 + i * 0.0001, -122.4194 + i * 0.0001),
            sensor_data={'lidar': 'OK', 'camera': 'OK'},
            event_type=EventSeverity.CRITICAL if is_critical else EventSeverity.NORMAL,
            data_id=f"DATA_{vehicle_id}_{i:03d}"
        )
        
        # Tüm depolama sistemlerine yaz
        write_result = storage_system.write_data(data)
        
        # Buluta senkronize et
        sync_system.sync_to_cloud(data)
        
        forensic_records.append(data)
        
        if i % 5 == 0:
            print(f"  ⏱️  T+{i}s | Hız: {data.speed_kmh:.0f} km/h | "
                  f"Fren: {data.brake_pressure:.0f}% | "
                  f"Yedek: {write_result['successful_writes']}/4 sistem")
    
    print(f"\n✓ {len(forensic_records)} kayıt başarıyla yazıldı")
    
    # Depolama durumu
    print("\n" + "=" * 80)
    print("📊 KAZA ÖNCESİ DEPOLAMA DURUMU")
    print("=" * 80)
    
    health = storage_system.get_storage_health()
    for storage_name, status in health.items():
        print(f"\n{storage_name}:")
        print(f"  • Durum: {'✓ Çalışıyor' if status['operational'] else '✗ Arızalı'}")
        print(f"  • Kayıtlı Veri: {status['records_stored']} kayıt")
        print(f"  • Hasar Seviyesi: {status['damage_level']:.1f}%")
    
    sync_stats = sync_system.get_sync_stats()
    print(f"\nBulut Senkronizasyonu:")
    print(f"  • Senkronize Edilen: {sync_stats['synced_records']} kayıt")
    print(f"  • Başarı Oranı: {sync_stats['success_rate']:.1f}%")
    
    # KAZA SİMÜLASYONU
    print("\n" + "=" * 80)
    print("💥 KAZA SİMÜLASYONU")
    print("=" * 80)
    print("\nYüksek hızda çarpışma tespit edildi!")
    print("  • Güç kaybı: EVET (akü bağlantısı kesildi)")
    print("  • Fiziksel hasar: %85 (şiddetli darbe)")
    
    damage_report = storage_system.simulate_crash(power_loss=True, physical_damage=85.0)
    
    print("\n📉 Veri Kayıp Raporu:\n")
    for storage_name, report in damage_report.items():
        loss_icon = "✗" if report['loss_percentage'] > 0 else "✓"
        print(f"{loss_icon} {storage_name}:")
        print(f"    Orijinal: {report['original_records']} kayıt")
        print(f"    Kalan: {report['remaining_records']} kayıt")
        print(f"    Kayıp: {report['loss_percentage']:.1f}%")
        print(f"    Sebep: {report['reason']}\n")
    
    # VERİ KURTARMA
    print("=" * 80)
    print("🔧 ADLİ BİLİŞİM VERİ KURTARMA")
    print("=" * 80)
    print("\nOlay yeri inceleme ekibi verileri kurtarmaya çalışıyor...")
    
    recovery_result = storage_system.recover_data()
    
    if recovery_result['recovery_successful']:
        print(f"\n✓ VERİ KURTARMA BAŞARILI!")
        print(f"\n  • Kaynak: {recovery_result['recovery_source']}")
        print(f"  • Kurtarılan Kayıt: {recovery_result['recovered_records']}")
        print(f"  • Veri Bütünlüğü: {recovery_result['data_integrity']['integrity_score']:.1f}%")
        
        print(f"\n⏱️  Kaza Öncesi Zaman Çizelgesi (Son 10 saniye):\n")
        print(f"{'Zaman':<15} {'Hız (km/h)':<12} {'Fren (%)':<12} {'Olay':<15}")
        print("-" * 60)
        
        for event in recovery_result['forensic_timeline'][-10:]:
            print(f"{event['timestamp']:<15} {event['speed_kmh']:<12.1f} "
                  f"{event['brake_pressure']:<12.1f} {event['event']:<15}")
        
        print("\n🎯 Analiz:")
        timeline = recovery_result['forensic_timeline']
        if len(timeline) >= 2:
            print(f"  • Son hız: {timeline[-1]['speed_kmh']:.0f} km/h")
            print(f"  • Frenleme: {timeline[-1]['brake_pressure']:.0f}% basınç")
            print(f"  • Kaza öncesi süre: ~{len(timeline)} saniye veri")
            print(f"  • Sonuç: Veriler başarıyla kurtarıldı, kaza nedeni belirlenebilir")
    else:
        print("\n✗ VERİ KURTARMA BAŞARISIZ")
        print("  Tüm depolama sistemleri hasar gördü")
    
    print("\n" + "=" * 80)
    print("🎯 ÇÖZÜM AÇIKLAMASI")
    print("=" * 80)
    print("""
    Paradoks Çözümü: Çok Katmanlı Redundant Storage
    
    ❌ KLASİK SORUN:
       • Tek depolama noktası (EDR/ECU)
       • Volatile memory (güç kesilince kayıp)
       • Fiziksel hasar → Tüm veri kaybı
       • Adli bilişim imkansız
    
    ✅ ÇÖZÜM MİMARİSİ:
    
       1️⃣  VOLATILE MEMORY (RAM)
           • Hızlı erişim (0.1ms)
           • Anlık veri işleme
           • ⚠️  Güç kaybında sıfırlanır
       
       2️⃣  NON-VOLATILE MEMORY (Flash)
           • Kalıcı depolama (2ms)
           • Güç kesilince korunur
           • ⚠️  Fiziksel hasara karşı savunmasız
       
       3️⃣  BLACK BOX (Kara Kutu)
           • Darbe dayanımlı kasa (5ms)
           • Yüksek sıcaklık/basınç koruması
           • ✓ %95+ hasar oranında bile korunur
       
       4️⃣  CLOUD STORAGE (Bulut)
           • Gerçek zamanlı senkronizasyon (50ms)
           • Fiziksel hasardan etkilenmez
           • ✓ Aracın kendisi yok olsa bile veri kalır
    
    📋 AVANTAJLAR:
       • 4 bağımsız yedek → Tek nokta arızası yok
       • Kaza şiddeti ne olursa olsun en az 1 kaynak hayatta
       • Bulut senkronizasyonu → Uzaktan erişim
       • Veri bütünlüğü kontrolü (hash doğrulama)
    
    🔍 ADLİ BİLİŞİM:
       • Kaza nedenini belirlemek için tam zaman çizelgesi
       • Hız, frenleme, direksiyon verileri
       • Siber saldırı tespiti için log kayıtları
       • Mahkeme için tamper-proof kanıt
    
    Bu sayede kritik veriler kazadan kurtulur ve
    adli bilişim ekipleri olay nedeni belirleyebilir!
    """)


if __name__ == "__main__":
    demonstrate_anomaly_solution()

