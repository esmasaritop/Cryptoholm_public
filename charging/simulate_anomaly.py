import asyncio
import websockets
import json
from datetime import datetime, timezone

URI = "ws://127.0.0.1:9004/CP-TEST"   # OCPP 2.0.1 SP0 portu
CP_ID = "CP-TEST"

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

async def send(ws, msg):
    await ws.send(json.dumps(msg))

async def recv(ws):
    resp = await ws.recv()
    print("[Server]:", resp)
    return json.loads(resp)

async def simulate_sensor_anomaly():
    async with websockets.connect(URI, subprotocols=["ocpp2.0.1"]) as ws:
        print("[+] Bağlandı, BootNotification gönderiliyor...")

        # 1) BootNotification
        boot = [
            2, "UID-BOOT-1", "BootNotification",
            {
                "chargingStation": {
                    "model": "E2507",
                    "vendorName": "EmuOCPPCharge",
                    "serialNumber": CP_ID
                },
                "reason": "PowerUp"
            }
        ]
        await send(ws, boot)
        boot_res = await recv(ws)
        # boot_res = [3, "UID-BOOT-1", {...payload...}]
        status = boot_res[2].get("status", "Rejected")
        if status != "Accepted":
            print("[x] Boot REJECTED:", status)
            return
        print("[✓] Boot ACCEPTED, interval:", boot_res[2].get("interval"))

        # 2) Basit StatusNotification
        status_msg = [
            2, "UID-STATUS-1", "StatusNotification",
            {
                "timestamp": now(),
                "connectorStatus": "Available",
                "evseId": 0,
                "connectorId": 0
            }
        ]
        await send(ws, status_msg)
        await recv(ws)

        # 3) Normal akış + ANOMALİ
        tx_id = "TEST-ANOMALY"
        seq = 1

        # Authorized
        authorized = [
            2, "UID-TXN-1", "TransactionEvent",
            {
                "eventType": "Started",
                "timestamp": now(),
                "triggerReason": "Authorized",
                "seqNo": seq,
                "transactionInfo": {"transactionId": tx_id},
                "idToken": {"type": "Central", "idToken": "DEADBEEF"}
            }
        ]
        await send(ws, authorized); await recv(ws); seq += 1

        # CablePluggedIn
        cable = [
            2, "UID-TXN-2", "TransactionEvent",
            {
                "eventType": "Updated",
                "timestamp": now(),
                "triggerReason": "CablePluggedIn",
                "seqNo": seq,
                "transactionInfo": {"transactionId": tx_id}
            }
        ]
        await send(ws, cable); await recv(ws); seq += 1

        # ChargingStateChanged -> Charging (normal)
        charging = [
            2, "UID-TXN-3", "TransactionEvent",
            {
                "eventType": "Updated",
                "timestamp": now(),
                "triggerReason": "ChargingStateChanged",
                "seqNo": seq,
                "transactionInfo": {"transactionId": tx_id, "chargingState": "Charging"}
            }
        ]
        await send(ws, charging); await recv(ws); seq += 1

        # 4) ANOMALİ: sensör verisi işlenemiyor (bozuk meterValue)
        # -- OCPP 2.0.1: sampledValue içindeki "value" **string** beklenir.
        #    Burada "NaN" veya boş liste ile kasıtlı biçim hatası yaratıyoruz.
        anomaly_meter_value = [
            {
                "timestamp": now(),
                "sampledValue": [
                    {"measurand": "Energy.Active.Import.Register", "value": "NaN"}  # bilinçli kirli veri
                ]
            }
        ]
        anomaly = [
            2, "UID-TXN-4", "TransactionEvent",
            {
                "eventType": "Updated",
                "timestamp": now(),
                "triggerReason": "ChargingStateChanged",
                "seqNo": seq,
                "transactionInfo": {"transactionId": tx_id, "chargingState": "Charging"},
                "meterValue": anomaly_meter_value
            }
        ]
        print("[!] ANOMALY gönderiliyor (meterValue -> NaN)...")
        await send(ws, anomaly)
        await recv(ws)

        print("[✓] Anomali testi bitti.")

if __name__ == "__main__":
    asyncio.run(simulate_sensor_anomaly())
