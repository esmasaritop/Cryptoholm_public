# Anomaly Detection API for OCPP Emulator

Python Flask REST API providing anomaly detection capabilities for Monta OCPP Emulator.

## Quick Start

### 1. Start API Server

```bash
cd ~/Desktop/bsgsimu/anomaly_simulation
source venv/bin/activate
python anomaly_api.py
```

Server will start on: `http://localhost:5001`

### 2. Test API

```bash
# In another terminal
python test_api.py
```

## API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Insider Threat Detection
```bash
POST /api/v1/anomaly/insider-threat
Content-Type: application/json

{
  "num_normal_users": 100,
  "num_malicious_users": 20
}
```

**Response:**
```json
{
  "test": "insider_threat",
  "status": "success",
  "results": {
    "total_users": 120,
    "anomalies_detected": 18,
    "detection_rate": "15.0%",
    "top_anomalies": [...]
  }
}
```

### False Positive Analysis
```bash
POST /api/v1/anomaly/false-positive
Content-Type: application/json

{
  "num_events": 100,
  "threat_rate": 0.2,
  "false_positive_rate": 0.15
}
```

**Response:**
```json
{
  "test": "false_positive",
  "status": "success",
  "results": {
    "confusion_matrix": {
      "true_negatives": 67,
      "false_positives": 10,
      "false_negatives": 2,
      "true_positives": 21
    },
    "metrics": {
      "accuracy": "88.00%",
      "precision": "67.74%",
      "recall": "91.30%"
    }
  }
}
```

### Sensor Attack Simulation
```bash
POST /api/v1/anomaly/sensor-attack
Content-Type: application/json

{
  "signal_type": "sine",
  "attack_type": "injection"
}
```

**Attack types:**
- `injection` - Inject fake high values
- `jamming` - Corrupt signal with noise
- `spoofing` - Replace with fake signal
- `drift` - Gradual calibration corruption

**Response:**
```json
{
  "test": "sensor_attack",
  "status": "success",
  "results": {
    "total_samples": 100,
    "anomalies_detected": 10,
    "detection_rate": "10.0%",
    "attack_description": "Fake high values injected into sensor data"
  }
}
```

### Run All Tests
```bash
POST /api/v1/anomaly/all
```

Runs all three anomaly tests and returns combined results.

## Integration with Monta OCPP Emulator

### Option 1: Direct HTTP Calls (Kotlin/Java)

```kotlin
import okhttp3.*
import kotlinx.serialization.json.*

val client = OkHttpClient()
val json = Json { prettyPrint = true }

// Test Insider Threat
val payload = """
{
  "num_normal_users": 100,
  "num_malicious_users": 20
}
""".trimIndent()

val request = Request.Builder()
    .url("http://localhost:5001/api/v1/anomaly/insider-threat")
    .post(RequestBody.create(
        MediaType.parse("application/json"),
        payload
    ))
    .build()

val response = client.newCall(request).execute()
println(response.body()?.string())
```

### Option 2: Add to OCPP Message Handlers

In your OCPP message handlers, call the API when needed:

```kotlin
// In StatusNotificationHandler.kt
fun onStatusNotification(status: String) {
    // Trigger sensor attack detection
    val sensorData = collectSensorData()
    val anomalyResult = checkForSensorAnomaly(sensorData)

    if (anomalyResult.isAnomalous) {
        log.warn("Sensor anomaly detected: ${anomalyResult.description}")
    }
}
```

### Option 3: Scheduled Background Checks

```kotlin
// Schedule periodic anomaly checks
CoroutineScope(Dispatchers.IO).launch {
    while (isActive) {
        delay(60_000) // Every minute

        // Check for insider threats
        val insiderResult = callAnomalyAPI(
            endpoint = "insider-threat",
            params = mapOf(
                "num_normal_users" to 50,
                "num_malicious_users" to 10
            )
        )

        handleAnomalyResults(insiderResult)
    }
}
```

## Example: Kotlin HTTP Client

Add to your OCPP emulator:

```kotlin
// AnomalyDetectionService.kt
package com.monta.ocpp.emulator.anomaly

import okhttp3.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*

class AnomalyDetectionService(
    private val baseUrl: String = "http://localhost:5001/api/v1"
) {
    private val client = OkHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun detectInsiderThreat(
        normalUsers: Int = 100,
        maliciousUsers: Int = 20
    ): AnomalyResult {
        val payload = json.encodeToString(mapOf(
            "num_normal_users" to normalUsers,
            "num_malicious_users" to maliciousUsers
        ))

        val request = Request.Builder()
            .url("$baseUrl/anomaly/insider-threat")
            .post(RequestBody.create(
                MediaType.parse("application/json"),
                payload
            ))
            .build()

        val response = client.newCall(request).execute()
        val body = response.body()?.string() ?: ""

        return json.decodeFromString(body)
    }

    suspend fun detectSensorAttack(
        signalType: String = "sine",
        attackType: String = "injection"
    ): AnomalyResult {
        val payload = json.encodeToString(mapOf(
            "signal_type" to signalType,
            "attack_type" to attackType
        ))

        val request = Request.Builder()
            .url("$baseUrl/anomaly/sensor-attack")
            .post(RequestBody.create(
                MediaType.parse("application/json"),
                payload
            ))
            .build()

        val response = client.newCall(request).execute()
        val body = response.body()?.string() ?: ""

        return json.decodeFromString(body)
    }
}

@Serializable
data class AnomalyResult(
    val test: String,
    val status: String,
    val results: JsonObject,
    val timestamp: String
)
```

## Testing from Command Line

```bash
# Insider Threat
curl -X POST http://localhost:5001/api/v1/anomaly/insider-threat \
  -H "Content-Type: application/json" \
  -d '{"num_normal_users":100,"num_malicious_users":20}'

# False Positive
curl -X POST http://localhost:5001/api/v1/anomaly/false-positive \
  -H "Content-Type: application/json" \
  -d '{"num_events":100,"threat_rate":0.2,"false_positive_rate":0.15}'

# Sensor Attack
curl -X POST http://localhost:5001/api/v1/anomaly/sensor-attack \
  -H "Content-Type: application/json" \
  -d '{"signal_type":"sine","attack_type":"injection"}'

# All Tests
curl -X POST http://localhost:5001/api/v1/anomaly/all
```

## Files

- `anomaly_api.py` - Flask API server
- `test_api.py` - Test suite
- `insider_threat.py` - Insider threat detection
- `false_positive.py` - False positive analysis
- `sensor_attack.py` - Sensor attack simulation
- `requirements.txt` - Python dependencies

## Dependencies

```
flask>=3.0.0
flask-cors>=4.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

## Logs

API logs are written to `api.log`

## Port Configuration

Default: `5001` (port 5000 is used by macOS ControlCenter)

To change port, edit `anomaly_api.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## Stopping the API

```bash
pkill -f "anomaly_api.py"
```

## Troubleshooting

**API won't start:**
- Check if port 5001 is available: `lsof -i :5001`
- Check logs: `tail -f api.log`

**Import errors:**
- Activate venv: `source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`

**Connection refused from Kotlin:**
- Ensure API is running: `curl http://localhost:5001/api/v1/health`
- Check firewall settings
- Try `127.0.0.1` instead of `localhost`
