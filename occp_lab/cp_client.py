import asyncio
import websockets
import json
import can

async def send_meter_values(ws):

    # Virtual CAN bus
    bus = can.interface.Bus(bustype='virtual')

    while True:
        real_energy = 4500  # Gerçek değer (4.5 kWh)

        # CAN Frame → virtual bus'a gönder
        msg = can.Message(
            arbitration_id=0x300,
            data=[(real_energy >> 8) & 0xFF, real_energy & 0xFF],
            is_extended_id=False
        )

        bus.send(msg)
        print(f"[CP] CAN → ID:0x300 DATA:{list(msg.data)}")

        # OCPP MeterValues payload
        payload = {
            "messageTypeId": 2,
            "messageId": "1234",
            "action": "MeterValues",
            "payload": {
                "meterValue": [{
                    "sampledValue": [{
                        "measurand": "Energy.Active.Import.Register",
                        "value": str(real_energy)
                    }]
                }]
            }
        }

        await ws.send(json.dumps(payload))
        print(f"[CP] Gönderilen NORMAL MeterValues: {real_energy} Wh")

        await asyncio.sleep(5)

async def main():
    uri = "ws://localhost:8000"  # MITM proxy adresi
    async with websockets.connect(uri) as ws:
        print("[CP] MITM proxy'e bağlandı.")
        await send_meter_values(ws)

asyncio.run(main())

