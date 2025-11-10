import time
import json
from crypto_utils import calculate_hash  # Adım 2.1'deki fonksiyonu içe aktarıyoruz


class Block:
    """Blokzincirdeki temel veri yapısı."""

    def __init__(self, index, timestamp, transactions, previous_hash=''):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions  # CAN/OCPP mesajının güvenlik verileri
        self.previous_hash = previous_hash
        self.hash = self.calculate_own_hash()

    def calculate_own_hash(self):
        """Blok içeriğinin hash'ini hesaplar."""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        # Basitleştirilmiş bir hashleme yöntemi kullanıyoruz
        return calculate_hash(block_string)


class LightBlockchain:
    """Hafif Dağıtık Defter Yapısı."""

    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []  # Bloklara eklenecek beklemedeki işlemler (mesajlar)
        # Simülasyon için DLT'deki tüm düğümlerin listesini burada tutabiliriz.

    def create_genesis_block(self):
        """Zincirin ilk bloğunu (Genesis Blok) oluşturur."""
        return Block(0, time.time(), "Genesis Block", "0")

    def get_last_block(self):
        """Zincirin son bloğunu döndürür."""
        return self.chain[-1]

    def add_transaction(self, sender_public_key: str, message_data: str, signature: str):
        """Blokzincire bir CAN/OCPP mesajı (işlem) ekler."""

        # İşleminizin yapması gereken temel güvenlik kontrolleri:
        # 1. İmza Doğrulaması (Kimlik Doğrulama) -> crypto_utils'de
        # 2. Zaman Damgası Kontrolü (Tekrar Saldırısı Önleme) -> Hash hesaplama içinde

        transaction = {
            'sender': sender_public_key,
            'data': message_data,
            'signature': signature,
            'timestamp': int(time.time())  # Yeni zaman damgası
        }
        self.pending_transactions.append(transaction)
        print(f"DLT: Yeni işlem eklendi. (Beklemede)")
        return len(self.get_last_block().transactions) + 1

    def mine_pending_transactions(self):
        """Bekleyen işlemleri alır ve yeni bir blok oluşturarak zincire ekler."""
        if not self.pending_transactions:
            print("DLT: Oluşturulacak bekleyen işlem yok.")
            return False

        # Basitleştirilmiş madencilik (Proof-of-Work yok, sadece blok oluşturma)
        new_block = Block(
            len(self.chain),
            time.time(),
            self.pending_transactions,
            self.get_last_block().hash
        )

        self.chain.append(new_block)
        self.pending_transactions = []
        print(f"DLT: Yeni blok ({new_block.index}) zincire eklendi. Hash: {new_block.hash[:10]}...")
        return new_block.index