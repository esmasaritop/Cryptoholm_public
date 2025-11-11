
# -*- coding: utf-8 -*-
import asyncio
import logging
import websockets
from datetime import datetime, timezone
import traceback

# ⭐ İLK ÖNCE LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    force=True
)

import can
from ocpp.routing import on
from ocpp.v201 import ChargePoint as CP
from ocpp.v201 import call_result, call

# Global bus tanımı
try:
    bus = can.interface.Bus(interface='virtual', channel='vcan0')
    logging.info("✅ CAN Bus başarıyla başlatıldı")
except Exception as e:
    logging.warning(f"⚠️ CAN Bus başlatılamadı: {e}")
    bus = None


class ChargePointSimulator(CP):

    async def _complete_transaction_tasks_async(self, can_id, payload):
        """CAN gönderme ve MeterValues simülasyonunu asenkron olarak yapar."""
        try:
            logging.info("[CP] Arka plan görevi başladı...")

            # CAN Mesajını Gönder
            data = [1, *payload]
            msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
            logging.info(f"*** KÖPRÜLEME (BRIDGE) *** OCPP -> CAN: ID 0x{can_id:X}, Data: {data}")

            if bus is not None:
                await asyncio.to_thread(bus.send, msg)
                logging.info("[CP] CAN mesajı gönderildi")

            # Charger Cevabını Simüle Et ve MeterValues Gönder
            await self.simulate_charger_response()

        except Exception as e:
            logging.error(f"[CP] _complete_transaction_tasks_async hatası: {e}")
            logging.error(traceback.format_exc())

    async def simulate_charger_response(self):
        """Charger modülünden MeterValues cevabı gelmiş gibi yapar ve CSMS'e gönderir."""
        try:
            logging.info("[CP] Charger response simüle ediliyor...")

            # Kısa bir gecikme
            await asyncio.sleep(0.5)

            meter_can_id = 0x300
            meter_data = [1, 50, 0, 0]
            meter_msg = can.Message(arbitration_id=meter_can_id, data=meter_data, is_extended_id=False)

            if bus is not None:
                await asyncio.to_thread(bus.send, meter_msg)
                logging.info(f"CAN CEVAP GÖNDERİLDİ (Simüle Edilmiş Meter): ID 0x{meter_can_id:X}")

            # CSMS'e MeterValues gönderme
            logging.info("[CP] MeterValues hazırlanıyor...")
            request = call.MeterValues(
                evse_id=1,
                meter_value=[
                    {'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
                     'sampled_value': [{'value': 500 }]}
                ]
            )

            await self.call(request)
            logging.info("✅ OCPP MeterValues CSMS'e gönderildi.")

        except Exception as e:
            logging.error(f"[CP] simulate_charger_response hatası: {e}")
            logging.error(traceback.format_exc())

    @on('RequestStartTransaction')
    async def on_request_start_transaction(self, remote_start_id, id_token, evse_id=None, **kwargs):
        """CSMS'ten RequestStartTransaction gelirse çalışır."""
        try:
            logging.info("=" * 60)
            logging.info(f"[CP] 🎯 RequestStartTransaction ALINDI!")
            logging.info(f"[CP] remote_start_id: {remote_start_id}")
            logging.info(f"[CP] id_token: {id_token}")
            logging.info(f"[CP] evse_id: {evse_id}")
            logging.info(f"[CP] kwargs: {kwargs}")
            logging.info("=" * 60)

            can_id = 0x200
            payload = [1, evse_id or 1, 1]

            logging.info(f"[CP] Arka plan görevi başlatılıyor...")
            asyncio.create_task(self._complete_transaction_tasks_async(can_id, payload))

            logging.info(f"[CP] RequestStartTransaction Accepted yanıtı döndürülüyor...")

            return call_result.RequestStartTransaction(status='Accepted')

        except Exception as e:
            logging.error(f"[CP] on_request_start_transaction hatası: {e}")
            logging.error(traceback.format_exc())
            return call_result.RequestStartTransaction(status='Rejected')

    @on('RequestStopTransaction')
    async def on_request_stop_transaction(self, transaction_id, **kwargs):
        """CSMS'ten RequestStopTransaction gelirse çalışır."""
        try:
            logging.info(f"[CP] RequestStopTransaction ALINDI!")
            logging.info(f"[CP] transaction_id: {transaction_id}")
            return call_result.RequestStopTransaction(status='Accepted')
        except Exception as e:
            logging.error(f"[CP] on_request_stop_transaction hatası: {e}")
            logging.error(traceback.format_exc())
            return call_result.RequestStopTransaction(status='Rejected')


async def main():
    print("=" * 60)
    print("🚀 CP SIMULATOR BAŞLIYOR...")
    print("=" * 60)

    logging.info("CP Simulator başlatılıyor...")

    csms_url = 'ws://127.0.0.1:9000/CP_TEST'
    cp_id = 'CP_TEST'

    try:
        logging.info(f"[CP] CSMS'e bağlanılıyor: {csms_url}")

        async with websockets.connect(csms_url, subprotocols=['ocpp2.0.1']) as ws:
            logging.info("✅ [CP] WebSocket bağlantısı kuruldu")

            cp = ChargePointSimulator(cp_id, ws)

            # ⭐ KRİTİK: Önce cp.start()'ı arka planda başlat
            start_task = asyncio.create_task(cp.start())

            # Kısa bir bekleme - cp.start() mesaj dinlemeye başlasın
            await asyncio.sleep(0.5)

            # BootNotification gönder
            logging.info("[CP] BootNotification gönderiliyor...")

            request = call.BootNotification(
                reason="PowerUp",
                charging_station={
                    "model": "SimChargePoint",
                    "vendor_name": "SimVendor"
                }
            )

            response = await cp.call(request)
            logging.info(f"✅ [CP] BootNotification cevabı: {response.status}")

            logging.info("🎧 [CP] Simülatör çalışıyor, mesaj bekleniyor...")
            logging.info("=" * 60)

            # start_task'ın bitmesini bekle
            await start_task

    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"❌ [CP] WebSocket Hatası: {e}")
    except Exception as e:
        logging.error(f"❌ [CP] Beklenmedik Hata: {e}")
        logging.error(traceback.format_exc())
    finally:
        if bus is not None:
            bus.shutdown()
            logging.info("CAN VirtualBus başarıyla kapatıldı.")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n")
        logging.info("🛑 [CP] Simülatör kullanıcı tarafından kapatıldı.")



