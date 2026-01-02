//Kurban ECU

import can
import time

def legitimate_ecu():
    # Sanal veriyoluna bağlan (udp_multicast)
    bus = can.interface.Bus(interface='udp_multicast', channel='default')
    
    print(" MEŞRU ECU: Çalışıyor... (ID: 0x100 - Fren Durumu: SERBEST)")

    try:
        while True:
            # 1. Normal Durum Mesajı Gönder (Frenler SERBEST)
            msg = can.Message(arbitration_id=0x100, data=[0x00], is_extended_id=False)
            bus.send(msg)
            
            # 2. Gelen "Susturma" komutu var mı diye dinle (Non-blocking)
            rx_msg = bus.recv(timeout=0.1) # 0.1 saniye bekle ve dinle
            
            if rx_msg and rx_msg.arbitration_id == 0x7E0:
                # Saldırganın gönderdiği "Diagnostic Session Control" paketi mi?
                # Pundir ve Koscher makalelerinde belirtilen "Susturma" aşaması.
                if rx_msg.data[0] == 0x10 and rx_msg.data[1] == 0x03:
                    print("\n⚠️  KRİTİK HATA: Tanılama komutu alındı! ECU Susturuluyor...")
                    print(" MEŞRU ECU: Çevrimdışı moda geçti.")
                    break # Döngüden çık, yani sus.

    except KeyboardInterrupt:
        print("ECU kapatıldı.")

if __name__ == "__main__":
    legitimate_ecu()