//Gösterge Paneli

import can

def dashboard():
    bus = can.interface.Bus(interface='udp_multicast', channel='default')
    print("GÖSTERGE PANELİ: Veriyolu dinleniyor...")

    try:
        while True:
            msg = bus.recv() # Mesaj gelene kadar bekle
            
            if msg.arbitration_id == 0x100:
                brake_status = msg.data[0]
                
                if brake_status == 0x00:
                    print(f"GÜVENLİ: Frenler Serbest (Gelen Veri: {msg.data.hex()})")
                elif brake_status == 0xFF:
                    print(f"TEHLİKE: FRENLER KİLİTLENDİ! (Gelen Veri: {msg.data.hex()})")
                else:
                    print(f"Bilinmeyen Durum: {msg.data.hex()}")

    except KeyboardInterrupt:
        print("Panel kapatıldı.")

if __name__ == "__main__":
    dashboard()