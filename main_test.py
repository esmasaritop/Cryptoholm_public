from dlt_manager import DLTManager
from lidar_simulator import LidarSimulator
from decision_ecu import DecisionECU

# --- KARAR VERİCİ ECU'nun AÇIK Anahtarı ---
# key_generator.py çıktısındaki "KARAR VERİCİ ECU (Receiver) Keys" altındaki Public Key'dir.
ECU_RECEIVER_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEKr6YQcYCCfLQn7YbhQmelgfVhdP2Tywl
jsp4v7dT0Ua4gVDllK5ygb1UPqIIKbwdnzvl+TevEn1EEv+pEVqqDQ==
-----END PUBLIC KEY-----
"""

if __name__ == '__main__':

    # 1. Sistemi Başlat
    dlt_manager = DLTManager()

    # Karar Verici ECU'yu DLT'ye yetkili düğüm olarak kaydetme
    dlt_manager.register_node("DECISION_ECU_01", ECU_RECEIVER_PUBLIC_KEY)

    lidar_sim = LidarSimulator(dlt_manager)
    ecu = DecisionECU(dlt_manager)

    print("\n" + "=" * 50)
    print("SENARYO 1: YASAL (GÜVENLİ) MESAJ AKIŞI")
    print("=" * 50)

    # main_test.py dosyasında, SENARYO 1 kısmında, Satır 31 civarında:

    # 2. Yasal Mesaj Akışı (Yolda araç var)
    # 🛑 DÜZELTME: lidar_simulator.py'den 4 değer döndüğünü varsayarak yakalıyoruz.
    sender_id, data_str, data_hash, signature = lidar_sim.generate_and_sign_data(is_fake_data=False)

    # Mesajı Karar Verici ECU'ya gönder (DLT'de kaydı yapılmış, imzası doğru)
    success, result = ecu.process_data(sender_id, data_str, signature)  # sender_id'yi de process_data'ya gönderiyoruz

    if success:
        print(f"\n[SENARYO 1 SONUÇ]: BAŞARILI. ECU Kararı: {result}")
    else:
        print(f"\n[SENARYO 1 SONUÇ]: HATA. ECU Mesajı Reddetti: {result}")

    print("\n" + "=" * 50)
    print("SENARYO 2: ANOMALİ (SAHTE VERİ ENJEKSİYONU) TESTİ")
    print("Blokzincir bütünlüğü koruyacak mı?")
    print("=" * 50)

    # 3. Saldırı Anı: Sahte Mesaj Enjeksiyonu

    # Saldırgan, yasal mesajın içeriğini değiştirir ancak eski imzayı kullanır.
    # Bu durumda Karar Verici ECU'nun Hash Uyuşmazlığını bulması gerekir.
    fake_data_str = '{"speed": 40, "distance": 50, "object": "none"}'

    # Not: Burada signature, Senaryo 1'de üretilen YASAL imzadır.
    # Saldırgan bu imzayı ve sahte veriyi Karar Verici ECU'ya gönderir.

    # 🛑 DÜZELTME: ecu.process_data'ya gönderirken sender_id'yi ekleyin
    success, result = ecu.process_data(sender_id, fake_data_str, signature)

    if not success and "Bütünlük Hatası" in result:
        print("\n*** TEST BAŞARILI ***")
        print("Blokzincir/Hash Kontrolü, değiştirilmiş sensör verisini tespit etti ve reddetti.")
    else:
        print("\n*** TEST BAŞARISIZ ***")
        print("Sahte sensör verisi (None), Karar Birimine ulaştı veya DLT doğrulamasında başarısız oldu.")