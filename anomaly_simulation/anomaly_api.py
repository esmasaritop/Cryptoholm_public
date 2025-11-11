#!/usr/bin/env python3
"""
Anomaly Detection API Server
Flask REST API for OCPP Emulator integration
"""

import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend BEFORE importing pyplot

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import base64
from datetime import datetime

# Import anomaly modules
from false_positive import run_false_positive_simulation, generate_detection_scenario, analyze_false_positives, visualize_confusion_matrix

app = Flask(__name__)
CORS(app)  # Enable CORS for Kotlin/Java client

# API Configuration
API_VERSION = "v1"
BASE_PATH = f"/api/{API_VERSION}"


@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'name': 'Anomaly Detection API',
        'version': API_VERSION,
        'status': 'running',
        'endpoints': {
            'false_positive': f'{BASE_PATH}/anomaly/false-positive',
            'health': f'{BASE_PATH}/health'
        }
    })


@app.route(f'{BASE_PATH}/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route(f'{BASE_PATH}/anomaly/insider-threat', methods=['POST'])
def insider_threat_test():
    """
    Run insider threat detection test

    Body:
    {
        "num_normal_users": 100,
        "num_malicious_users": 20
    }
    """
    try:
        data = request.get_json() or {}
        num_normal = data.get('num_normal_users', 100)
        num_malicious = data.get('num_malicious_users', 20)

        # Generate logs
        log_file = 'user_logs.csv'
        generate_user_logs(log_file, num_normal, num_malicious)

        # Detect anomalies
        results = detect_insider_threat(log_file)

        # Calculate statistics
        anomalies = results[results['anomaly'] == -1]

        response = {
            'test': 'insider_threat',
            'status': 'success',
            'parameters': {
                'num_normal_users': num_normal,
                'num_malicious_users': num_malicious
            },
            'results': {
                'total_users': len(results),
                'anomalies_detected': len(anomalies),
                'detection_rate': f"{len(anomalies)/len(results)*100:.1f}%",
                'top_anomalies': anomalies.sort_values('anomaly_score').head(5)[
                    ['user_id', 'login_hour', 'files_accessed', 'data_volume', 'anomaly_score']
                ].to_dict('records')
            },
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'test': 'insider_threat',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route(f'{BASE_PATH}/anomaly/false-positive', methods=['POST'])
def false_positive_test():
    """
    Run false positive analysis

    Body:
    {
        "num_events": 100,
        "threat_rate": 0.2,
        "false_positive_rate": 0.15
    }
    """
    try:
        data = request.get_json() or {}
        num_events = data.get('num_events', 100)
        threat_rate = data.get('threat_rate', 0.2)
        fp_rate = data.get('false_positive_rate', 0.15)

        # Generate scenario
        y_true, y_pred = generate_detection_scenario(num_events, threat_rate, fp_rate)

        # Analyze
        from sklearn.metrics import confusion_matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        # Calculate metrics
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn)

        # Generate visualization
        visualize_confusion_matrix(y_true, y_pred)

        response = {
            'test': 'false_positive',
            'status': 'success',
            'parameters': {
                'num_events': num_events,
                'threat_rate': threat_rate,
                'false_positive_rate': fp_rate
            },
            'results': {
                'confusion_matrix': {
                    'true_negatives': int(tn),
                    'false_positives': int(fp),
                    'false_negatives': int(fn),
                    'true_positives': int(tp)
                },
                'metrics': {
                    'false_positive_rate': f"{fpr:.2%}",
                    'false_negative_rate': f"{fnr:.2%}",
                    'precision': f"{precision:.2%}",
                    'recall': f"{recall:.2%}",
                    'accuracy': f"{accuracy:.2%}"
                }
            },
            'visualization': 'confusion_matrix.png',
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'test': 'false_positive',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route(f'{BASE_PATH}/anomaly/sensor-attack', methods=['POST'])
def sensor_attack_test():
    """
    Run sensor attack simulation

    Body:
    {
        "signal_type": "sine",
        "attack_type": "injection"
    }
    """
    try:
        data = request.get_json() or {}
        signal_type = data.get('signal_type', 'sine')
        attack_type = data.get('attack_type', 'injection')

        # Generate normal signal
        time, normal_signal = generate_normal_sensor_data(signal_type=signal_type)

        # Apply attack
        attacked_signal = apply_sensor_attack(normal_signal, attack_type=attack_type)

        # Detect anomalies
        anomalies = detect_sensor_anomaly(normal_signal, attacked_signal)
        num_anomalies = sum(anomalies)

        response = {
            'test': 'sensor_attack',
            'status': 'success',
            'parameters': {
                'signal_type': signal_type,
                'attack_type': attack_type
            },
            'results': {
                'total_samples': len(anomalies),
                'anomalies_detected': int(num_anomalies),
                'detection_rate': f"{num_anomalies/len(anomalies)*100:.1f}%",
                'attack_description': {
                    'injection': 'Fake high values injected into sensor data',
                    'jamming': 'Signal corrupted with excessive noise',
                    'spoofing': 'Sensor replaced with completely fake signal',
                    'drift': 'Gradual calibration corruption over time'
                }.get(attack_type, 'Unknown attack type')
            },
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'test': 'sensor_attack',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route(f'{BASE_PATH}/anomaly/all', methods=['POST'])
def run_all_tests():
    """Run all anomaly tests"""
    try:
        results = {}

        # Insider Threat
        try:
            generate_user_logs('user_logs.csv', 100, 20)
            it_results = detect_insider_threat('user_logs.csv')
            it_anomalies = it_results[it_results['anomaly'] == -1]
            results['insider_threat'] = {
                'status': 'success',
                'anomalies_detected': len(it_anomalies),
                'total_users': len(it_results)
            }
        except Exception as e:
            results['insider_threat'] = {'status': 'error', 'error': str(e)}

        # False Positive
        try:
            y_true, y_pred = generate_detection_scenario(100, 0.2, 0.15)
            from sklearn.metrics import confusion_matrix
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            results['false_positive'] = {
                'status': 'success',
                'false_positives': int(fp),
                'false_negatives': int(fn)
            }
        except Exception as e:
            results['false_positive'] = {'status': 'error', 'error': str(e)}

        # Sensor Attack
        try:
            time, normal = generate_normal_sensor_data()
            attacked = apply_sensor_attack(normal, 'injection')
            anomalies = detect_sensor_anomaly(normal, attacked)
            results['sensor_attack'] = {
                'status': 'success',
                'anomalies_detected': int(sum(anomalies)),
                'total_samples': len(anomalies)
            }
        except Exception as e:
            results['sensor_attack'] = {'status': 'error', 'error': str(e)}

        return jsonify({
            'test': 'all_tests',
            'status': 'success',
            'results': results,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'test': 'all_tests',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route(f'{BASE_PATH}/visualization/<filename>', methods=['GET'])
def get_visualization(filename):
    """Get generated visualization images"""
    try:
        if os.path.exists(filename):
            return send_file(filename, mimetype='image/png')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("    ANOMALY DETECTION API SERVER")
    print("    For OCPP Emulator Integration")
    print("="*70)
    print(f"\nAPI Version: {API_VERSION}")
    print(f"Server: http://localhost:5001")
    print(f"Endpoints:")
    print(f"  - POST {BASE_PATH}/anomaly/insider-threat")
    print(f"  - POST {BASE_PATH}/anomaly/false-positive")
    print(f"  - POST {BASE_PATH}/anomaly/sensor-attack")
    print(f"  - POST {BASE_PATH}/anomaly/all")
    print(f"  - GET  {BASE_PATH}/health")
    print("="*70)
    print("\nStarting server...\n")

    app.run(host='0.0.0.0', port=5001, debug=True)
