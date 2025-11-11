"""
Anomali 2: Mahremiyet için Kalıcılık Kullanımı (Privacy vs. Immutability Anomaly)
Çözüm: Hibrit Off-Chain Storage + Zero-Knowledge Proof Blockchain Sistemi

Bu modül, blockchain'in değişmezlik özelliğini korurken,
kullanıcılara "unutulma hakkı" tanıyan hibrit bir sistem uygular.
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


@dataclass
class VehicleData:
    """Araç verisi"""
    vehicle_id: str
    location: tuple
    speed: float
    timestamp: float
    event_type: str
    
    def to_dict(self):
        return asdict(self)


class OffChainStorage:
    """
    Off-Chain Depolama Sistemi
    
    Hassas verileri blockchain dışında tutar.
    Blockchain'de sadece hash değerleri saklanır.
    Veriler silinebilir (unutulma hakkı).
    """
    
    def __init__(self):
        self.storage: Dict[str, VehicleData] = {}
        self.deleted_data: List[str] = []  # Silinen veri hash'leri
    
    def store_data(self, data: VehicleData) -> str:
        """Veriyi kaydet ve hash döndür"""
        data_json = json.dumps(data.to_dict(), sort_keys=True)
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        self.storage[data_hash] = data
        return data_hash
    
    def retrieve_data(self, data_hash: str) -> Optional[VehicleData]:
        """Hash ile veriyi getir"""
        if data_hash in self.deleted_data:
            return None  # Unutulma hakkı kullanıldı
        return self.storage.get(data_hash)
    
    def delete_data(self, data_hash: str) -> bool:
        """
        Veriyi sil (UNUTULMA HAKKI)
        
        Önemli: Blockchain'deki hash kalır ama içerik silinemez.
        Bu sayede veri bütünlüğü korunur ama mahremiyet sağlanır.
        """
        if data_hash in self.storage:
            del self.storage[data_hash]
            self.deleted_data.append(data_hash)
            return True
        return False
    
    def delete_user_data(self, vehicle_id: str) -> int:
        """Belirli bir kullanıcının tüm verilerini sil"""
        deleted_count = 0
        hashes_to_delete = []
        
        for data_hash, vehicle_data in self.storage.items():
            if vehicle_data.vehicle_id == vehicle_id:
                hashes_to_delete.append(data_hash)
        
        for data_hash in hashes_to_delete:
            if self.delete_data(data_hash):
                deleted_count += 1
        
        return deleted_count


@dataclass
class Block:
    """Blockchain bloğu"""
    index: int
    timestamp: float
    data_hash: str  # Sadece hash, gerçek veri yok!
    vehicle_id_hash: str  # Anonim kimlik
    previous_hash: str
    nonce: int = 0
    
    def calculate_hash(self) -> str:
        """Bloğun hash'ini hesapla"""
        block_string = f"{self.index}{self.timestamp}{self.data_hash}{self.vehicle_id_hash}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class ZeroKnowledgeProofSystem:
    """
    Zero-Knowledge Proof (Sıfır Bilgi İspatı) Simülasyonu
    
    Kullanıcı, verinin kendisini göstermeden veriye sahip olduğunu kanıtlar.
    Örnek: "Bu araç 80 km/h üzerinde gitti mi?" sorusuna
    "Evet" yanıtı verir ama tam hızı açıklamaz.
    """
    
    @staticmethod
    def generate_proof(data: VehicleData, condition: str) -> Dict:
        """
        Belirli bir koşul için zero-knowledge proof oluştur
        
        Gerçek uygulamada zk-SNARKs veya zk-STARKs kullanılır.
        Bu basitleştirilmiş bir simülasyondur.
        """
        proof = {
            'timestamp': data.timestamp,
            'vehicle_hash': hashlib.sha256(data.vehicle_id.encode()).hexdigest(),
            'condition': condition,
            'result': None,
            'proof_hash': None
        }
        
        # Koşul değerlendirmesi
        if condition == 'speed_over_80':
            proof['result'] = data.speed > 80
        elif condition == 'in_city_center':
            # Basitleştirilmiş konum kontrolü
            lat, lon = data.location
            proof['result'] = (37.7 < lat < 37.8) and (-122.5 < lon < -122.4)
        elif condition == 'emergency_event':
            proof['result'] = data.event_type == 'emergency'
        
        # Proof hash'i (kriptografik kanıt)
        proof_string = f"{proof['vehicle_hash']}{proof['condition']}{proof['result']}"
        proof['proof_hash'] = hashlib.sha256(proof_string.encode()).hexdigest()
        
        return proof
    
    @staticmethod
    def verify_proof(proof: Dict) -> bool:
        """Proof'u doğrula"""
        # Basitleştirilmiş doğrulama
        expected_hash = hashlib.sha256(
            f"{proof['vehicle_hash']}{proof['condition']}{proof['result']}".encode()
        ).hexdigest()
        return proof['proof_hash'] == expected_hash


class PrivacyPreservingBlockchain:
    """
    Mahremiyet Koruyan Blockchain Sistemi
    
    Çözüm yaklaşımı:
    1. Hassas veriler off-chain'de saklanır (silinebilir)
    2. Blockchain'de sadece hash'ler bulunur (değişmez)
    3. Zero-knowledge proofs ile sorgulama (mahremiyet korunur)
    4. Veri silinince blockchain geçerliliğini korur
    """
    
    def __init__(self):
        self.chain: List[Block] = []
        self.off_chain_storage = OffChainStorage()
        self.zkp_system = ZeroKnowledgeProofSystem()
        
        # Genesis bloğu
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """İlk bloğu oluştur"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data_hash="0",
            vehicle_id_hash="genesis",
            previous_hash="0"
        )
        genesis_block.nonce = 0
        self.chain.append(genesis_block)
    
    def add_vehicle_data(self, vehicle_data: VehicleData) -> Dict:
        """
        Araç verisini sisteme ekle
        
        1. Veriyi off-chain'de sakla
        2. Sadece hash'i blockchain'e ekle
        3. Kimliği anonimleştir
        """
        # 1. Off-chain storage
        data_hash = self.off_chain_storage.store_data(vehicle_data)
        
        # 2. Anonimleştir
        vehicle_id_hash = hashlib.sha256(vehicle_data.vehicle_id.encode()).hexdigest()
        
        # 3. Blockchain'e hash ekle
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data_hash=data_hash,
            vehicle_id_hash=vehicle_id_hash,
            previous_hash=previous_block.calculate_hash()
        )
        
        self.chain.append(new_block)
        
        return {
            'block_index': new_block.index,
            'data_hash': data_hash,
            'on_chain': True,
            'data_accessible': True
        }
    
    def exercise_right_to_be_forgotten(self, vehicle_id: str) -> Dict:
        """
        UNUTULMA HAKKI (Right to be Forgotten)
        
        Kritik özellik: Off-chain veriler silinir,
        blockchain hash'leri kalır (bütünlük korunur)
        """
        deleted_count = self.off_chain_storage.delete_user_data(vehicle_id)
        
        # Blockchain'deki blokları bul (sadece bilgi için)
        vehicle_hash = hashlib.sha256(vehicle_id.encode()).hexdigest()
        affected_blocks = [
            block.index for block in self.chain 
            if block.vehicle_id_hash == vehicle_hash
        ]
        
        return {
            'deleted_records': deleted_count,
            'affected_blocks': affected_blocks,
            'blockchain_integrity': self.verify_chain(),
            'data_accessible': False,
            'message': 'Veriler silindi, blockchain bütünlüğü korundu'
        }
    
    def query_with_zkp(self, data_hash: str, condition: str) -> Dict:
        """
        Zero-Knowledge Proof ile sorgulama
        
        Veriyi açığa çıkarmadan bilgi elde et
        """
        # Veriyi getir (eğer silinmediyse)
        vehicle_data = self.off_chain_storage.retrieve_data(data_hash)
        
        if vehicle_data is None:
            return {
                'success': False,
                'message': 'Veri bulunamadı veya silindi (unutulma hakkı)',
                'proof': None
            }
        
        # Zero-knowledge proof oluştur
        proof = self.zkp_system.generate_proof(vehicle_data, condition)
        is_valid = self.zkp_system.verify_proof(proof)
        
        return {
            'success': True,
            'proof_valid': is_valid,
            'condition': condition,
            'result': proof['result'],  # Sadece Evet/Hayır
            'proof_hash': proof['proof_hash'],
            'message': 'Sorgu yanıtlandı, ham veri açığa çıkmadı'
        }
    
    def verify_chain(self) -> bool:
        """Blockchain bütünlüğünü doğrula"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Önceki hash kontrolü
            if current_block.previous_hash != previous_block.calculate_hash():
                return False
        
        return True
    
    def get_chain_statistics(self) -> Dict:
        """Blockchain istatistikleri"""
        total_blocks = len(self.chain)
        total_stored = len(self.off_chain_storage.storage)
        total_deleted = len(self.off_chain_storage.deleted_data)
        
        return {
            'total_blocks': total_blocks,
            'currently_stored': total_stored,
            'deleted_by_users': total_deleted,
            'blockchain_valid': self.verify_chain(),
            'privacy_preserved': total_deleted > 0
        }


def demonstrate_anomaly_solution():
    """Anomali 2 çözümünü göster"""
    print("=" * 80)
    print("ANOMALİ 2: MAHREMİYET İÇİN KALICILIK KULLANIMI")
    print("ÇÖZÜM: Hibrit Off-Chain + Zero-Knowledge Proof Blockchain")
    print("=" * 80)
    print()
    
    # Sistem oluştur
    blockchain = PrivacyPreservingBlockchain()
    
    # Test verileri ekle
    print("📝 Araç verilerini blockchain sistemine ekleme...\n")
    
    vehicles_data = [
        VehicleData("ARAC_001", (37.7749, -122.4194), 85.0, time.time(), "normal"),
        VehicleData("ARAC_001", (37.7850, -122.4094), 120.0, time.time(), "speeding"),
        VehicleData("ARAC_002", (37.7649, -122.4294), 60.0, time.time(), "normal"),
        VehicleData("ARAC_002", (37.7749, -122.4394), 75.0, time.time(), "emergency"),
    ]
    
    data_hashes = []
    for idx, data in enumerate(vehicles_data):
        result = blockchain.add_vehicle_data(data)
        data_hashes.append(result['data_hash'])
        print(f"  Blok #{result['block_index']} | Veri Hash: {result['data_hash'][:16]}... | Eklendi ✓")
    
    print(f"\n✓ {len(vehicles_data)} veri bloğu blockchain'e eklendi")
    print(f"✓ Blockchain bütünlüğü: {blockchain.verify_chain()}")
    
    # Zero-Knowledge Proof sorgulaması
    print("\n" + "=" * 80)
    print("🔍 ZERO-KNOWLEDGE PROOF İLE SORGULAMA")
    print("=" * 80)
    print("\nSoru: ARAC_001 80 km/h üzerinde gitti mi? (Ham veri açıklanmadan)")
    
    zkp_result = blockchain.query_with_zkp(data_hashes[0], 'speed_over_80')
    print(f"\n  Cevap: {'EVET' if zkp_result['result'] else 'HAYIR'}")
    print(f"  Proof Geçerli: {zkp_result['proof_valid']}")
    print(f"  Proof Hash: {zkp_result['proof_hash'][:32]}...")
    print(f"  ℹ️  {zkp_result['message']}")
    
    # UNUTULMA HAKKI
    print("\n" + "=" * 80)
    print("🗑️  UNUTULMA HAKKI KULLANIMI (Right to be Forgotten)")
    print("=" * 80)
    print("\nKullanıcı 'ARAC_001' tüm verilerinin silinmesini talep etti...")
    
    stats_before = blockchain.get_chain_statistics()
    print(f"\nSilme Öncesi:")
    print(f"  • Blockchain Blokları: {stats_before['total_blocks']}")
    print(f"  • Erişilebilir Veri: {stats_before['currently_stored']}")
    print(f"  • Silinmiş Veri: {stats_before['deleted_by_users']}")
    
    # Veriyi sil
    forget_result = blockchain.exercise_right_to_be_forgotten("ARAC_001")
    
    print(f"\n🗑️  Silme İşlemi Tamamlandı:")
    print(f"  • Silinen Kayıt Sayısı: {forget_result['deleted_records']}")
    print(f"  • Etkilenen Bloklar: {forget_result['affected_blocks']}")
    print(f"  • Blockchain Bütünlüğü: {'✓ KORUNDU' if forget_result['blockchain_integrity'] else '✗ BOZULDU'}")
    
    stats_after = blockchain.get_chain_statistics()
    print(f"\nSilme Sonrası:")
    print(f"  • Blockchain Blokları: {stats_after['total_blocks']} (DEĞİŞMEDİ)")
    print(f"  • Erişilebilir Veri: {stats_after['currently_stored']}")
    print(f"  • Silinmiş Veri: {stats_after['deleted_by_users']}")
    
    # Silinen veriye erişim denemesi
    print("\n🔒 Silinen veriye erişim denemesi...")
    access_result = blockchain.query_with_zkp(data_hashes[0], 'speed_over_80')
    print(f"  Sonuç: {access_result['message']}")
    
    print("\n" + "=" * 80)
    print("🎯 ÇÖZÜM AÇIKLAMASI")
    print("=" * 80)
    print("""
    Paradoks Çözümü: Hibrit Mimari
    
    ❌ KLASİK BLOCKCHAIN SORUNU:
       • Tüm veriler blockchain'de → Silinemez
       • Mahremiyet yasaları (GDPR, KVKK) ihlali
       • Şifreleme kırılırsa → Tüm geçmiş açıkta
    
    ✅ HİBRİT ÇÖZÜM:
       • Hassas veriler: Off-chain (SİLİNEBİLİR)
       • Hash değerleri: On-chain (DEĞİŞMEZ)
       • Zero-knowledge proofs: Sorgu (MAHREMİYET)
    
    📋 AVANTAJLAR:
       1. Blockchain bütünlüğü korunur (hash'ler kalır)
       2. Kullanıcı unutulma hakkını kullanabilir
       3. Veri silinse de işlem kayıtları doğrulanabilir
       4. ZKP ile gizlilik korunarak sorgulama
    
    🔐 ÖRNEİK SENARYO:
       • Polis: "Bu araç 80 km/h üzerinde gitti mi?"
       • Sistem: "EVET" (ama tam hız açıklanmaz)
       • Mahremiyet korunur, kanıt sağlanır
    
    Bu sayede hem blockchain'in güvenliği hem de
    kullanıcıların mahremiyet hakları korunur!
    """)


if __name__ == "__main__":
    demonstrate_anomaly_solution()

