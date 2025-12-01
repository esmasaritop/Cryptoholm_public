import asyncio
import websockets
import json

async def csms_handler(websocket):
    print("[CSMS] CP bağlandı.")

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("action") == "MeterValues":
                try:
                    value = data["payload"]["meterValue"][0]["sampledValue"][0]["value"]
                    print(f"[CSMS] Gelen MeterValues Değeri: {value} Wh")
                except Exception as e:
                    print("[CSMS] MeterValues parse edilirken hata:", e)
            else:
                print("[CSMS] Diğer mesaj:", data)

    except websockets.exceptions.ConnectionClosed:
        print("[CSMS] CP bağlantısı kapandı.")

async def main():
    async with websockets.serve(csms_handler, "localhost", 9000):
        print("[CSMS] Sunucu başlatıldı → ws://localhost:9000")
        await asyncio.Future()

asyncio.run(main())

