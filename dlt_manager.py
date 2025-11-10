from light_blockchain import LightBlockchain
from crypto_utils import verify_signature


class DLTManager:
    """Dağıtık Defter Teknolojisi (Blokzincir) Yöneticisi"""

    def __init__(self):
        self.blockchain = LightBlockchain()
        # Ağdaki yetkili düğümlerin (ECU'lar) açık anahtarları
        self.registered_nodes = {}

    def register_node(self, node_id, public_key):
        """ECU'ları sisteme kaydeder."""
        self.registered_nodes[node_id] = public_key
        print(f"DLT: {node_id} başarıyla kaydedildi.")

    def log_and_verify_message(self, node_id, data_hash, signature, raw_data):
        """Gelen mesajı (işlemi) doğrular ve DLT'ye kaydeder."""
        if node_id not in self.registered_nodes:
            print(f"HATA: {node_id} yetkili bir düğüm değil.")
            return False

        public_key = self.registered_nodes[node_id]

        # 1. İmza Doğrulama (Kimlik Kontrolü)
        is_valid_signature = verify_signature(public_key, data_hash, signature)
        if not is_valid_signature:
            print("GÜVENLİK İHLALİ: İmza doğrulanamadı. Mesaj kaynağı sahte olabilir!")
            return False

        # 2. Hash Kontrolü (Tekrar Saldırısı/Zaman Kontrolü)
        # Basitleştirilmiş senaryoda, DLT'ye her yeni işlem eklendiğinde Hash'in benzersizliğini ve zamanını kabul ediyoruz.
        # Gerçek bir çözümde DLT'deki zaman damgası kontrol edilmeliydi.

        # 3. İşlemi DLT'ye ekle
        self.blockchain.add_transaction(node_id, raw_data, signature)
        self.blockchain.mine_pending_transactions()

        return True