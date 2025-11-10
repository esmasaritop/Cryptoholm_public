from crypto_utils import calculate_hash, sign_message
from dlt_manager import DLTManager  # DLTManager'ı buradan aktaracağız
import json

# lidar_simulator.py dosyasında

# --- LiDAR SIMULATOR Keys ---
LIDAR_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIGEAgEAMBAGByqGSM49AgEGBSuBBAAKBG0wawIBAQQghI+yBtSXG8Sia++wHCKW
EEb7fqxhB1RZ2vW7yIFRToahRANCAARe5bx0/hew4XUwFBj4sc7V5YoXy9lFA8CE
SbuGCeN+uClTCvS+ZfX4O76mjFRl/+gEvG3fGRUmnwTiBqXvSPkb
-----END PRIVATE KEY-----
"""

LIDAR_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEXuW8dP4XsOF1MBQY+LHO1eWKF8vZRQPA
hEm7hgnjfrgpUwr0vmX1+Du+poxUZf/oBLxt3xkVJp8E4gal70j5Gw==
-----END PUBLIC KEY-----
"""
# ... (kodun geri kalanı)

class LidarSimulator:
    def __init__(self, dlt_manager: DLTManager):
        self.id = "LIDAR_SIM_01"
        self.dlt = dlt_manager
        # Simülatörü DLT'ye kaydet
        self.dlt.register_node(self.id, LIDAR_PUBLIC_KEY)

    def generate_and_sign_data(self, is_fake_data=False):
        """LiDAR verisi üretir, imzalar ve DLT'ye kaydeder."""

        # 1. Gerçek/Sahte Veriyi Oluştur
        if is_fake_data:
            # ANOMALİ: Sahte Mesaj (Yoldaki aracı 'yok' olarak gösterir)
            data_payload = {"speed": 40, "distance": 50, "object": "none"}
            print("\n[SALDIRI]: SAHTE MESAJ ENJEKTE EDİLİYOR: 'Yol Boş'")
        else:
            # Yasal Veri (Yolda 10 metrede bir araç var)
            data_payload = {"speed": 40, "distance": 10, "object": "car"}
            print("\n[YASAL]: Yasal Mesaj Gönderiliyor: '10m'de Araç Var'")

        data_str = json.dumps(data_payload, sort_keys=True)

        # 2. Hash Hesaplama (Zaman damgası eklenmiş hash)
        data_hash = calculate_hash(data_str)

        # 3. Dijital İmza Oluşturma
        signature = sign_message(LIDAR_PRIVATE_KEY, data_hash)

        # 4. Veri Gönderimi ve DLT Kaydı
        # Gerçek bir senaryoda bu veri CAN bus üzerinden gönderilir ve DLT'ye kaydedilir.
        is_logged = self.dlt.log_and_verify_message(self.id, data_hash, signature, data_str)

        return is_logged, data_str, data_hash, signature