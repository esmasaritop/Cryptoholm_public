from dlt_manager import DLTManager
from crypto_utils import calculate_hash, verify_signature
import json


class DecisionECU:
    def __init__(self, dlt_manager: DLTManager):
        self.dlt = dlt_manager

    def process_data(self, sender_id, received_data_str, received_signature):
        """Gelen LiDAR verisini DLT'ye göre doğrular."""
        print(f"\n[ECU]: Gelen Veri İşleniyor: {received_data_str}")

        # 1. Hash Hesaplama (Tekrar saldırısı önleme için bu adım önemlidir!)
        received_data_hash = calculate_hash(received_data_str)

        # 2. DLT'den En Son Kaydı Kontrol Etme (Basitleştirilmiş Doğrulama)

        # Gerçek senaryoda, DLT'deki kaydı alıp Hash'i ve zaman damgasını kontrol etmelisiniz.
        # Bu simülasyonda, DLT'deki en son kayıt ile karşılaştıralım:
        last_block_tx = self.dlt.blockchain.get_last_block().transactions[0]

        # Güvenlik Kontrolü 1: Mesaj Bütünlüğü (Hash Uyuşmazlığı)
        if last_block_tx['data'] != received_data_str:
            print("GÜVENLİK REDDİ: Mesaj içeriği DLT'deki kayıt ile UYUŞMUYOR.")
            return False, "Bütünlük Hatası (Hash Uyuşmazlığı)"

        # Mesaj güvenli kabul edildi, şimdi karar ver
        data_payload = json.loads(received_data_str)
        if data_payload.get("object") == "car":
            print("[ECU KARAR]: Kritik Tehdit Algılandı! ACİL FRENLEME BAŞLATILDI.")
        else:
            print("[ECU KARAR]: Yol Güvenli. Sürüş Devam Ediyor.")

        return True, "Başarılı"