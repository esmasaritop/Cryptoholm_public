from crypto_utils import generate_key_pair

# 1. LiDAR Simülatörü için Anahtarlar
lidar_priv_key, lidar_pub_key = generate_key_pair()
print("--- LiDAR SIMULATOR (Sender) Keys ---")
print("Private Key (SIGN): \n", lidar_priv_key)
print("Public Key (VERIFY): \n", lidar_pub_key)

# 2. Karar Verici ECU için Anahtarlar (Sadece Açık Anahtarı kullanacağız)
ecu_priv_key, ecu_pub_key = generate_key_pair()
print("\n--- KARAR VERİCİ ECU (Receiver) Keys ---")
print("Private Key (NOT USED YET): \n", ecu_priv_key)
print("Public Key: \n", ecu_pub_key)