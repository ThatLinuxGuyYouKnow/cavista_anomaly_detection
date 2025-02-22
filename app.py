from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np
from collections import deque

class CorrelationMonitor:
    def __init__(self, window_size=10, correlation_threshold=0.5):
        self.window_size = window_size
        self.correlation_threshold = correlation_threshold
        self.heart_rates = deque(maxlen=window_size)
        self.step_counts = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
    
    def normalize_deltas(self, data):
        deltas = np.diff(data)
        if len(deltas) == 0 or np.all(deltas == 0):
            return np.zeros(len(data) - 1)
        return (deltas - np.min(deltas)) / (np.max(deltas) - np.min(deltas) + 1e-10)
    
    def add_readings(self, heart_rates, step_counts):
        """Add multiple readings at once"""
        for hr, steps in zip(heart_rates, step_counts):
            self.heart_rates.append(hr)
            self.step_counts.append(steps)
            self.timestamps.append(datetime.now())
    
    def detect_anomaly(self):
        if len(self.heart_rates) < 3:
            return False, 0
            
        norm_hr_deltas = self.normalize_deltas(list(self.heart_rates))
        norm_step_deltas = self.normalize_deltas(list(self.step_counts))
        
        correlation = np.corrcoef(norm_hr_deltas, norm_step_deltas)[0,1]
        is_anomalous = abs(correlation) < self.correlation_threshold
        
        return is_anomalous, correlation

app = Flask(__name__)
monitor = CorrelationMonitor()

@app.route("/monitor", methods=['POST'])
def monitor_vitals():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'bpm' not in data or 'steps' not in data:
            return jsonify({
                'error': 'Missing required data. Please provide both bpm and steps lists'
            }), 400
            
        bpm_list = data['bpm']
        steps_list = data['steps']
        
        # Validate data format
        if not isinstance(bpm_list, list) or not isinstance(steps_list, list):
            return jsonify({
                'error': 'BPM and steps must be lists'
            }), 400
            
        if len(bpm_list) != len(steps_list):
            return jsonify({
                'error': 'BPM and steps lists must have the same length'
            }), 400
            
        # Add new readings
        monitor.add_readings(bpm_list, steps_list)
        
        # Check for anomalies
        is_anomalous, correlation = monitor.detect_anomaly()
        is_data_anomalous: str
        if is_anomalous:
            is_data_anomalous = 'true'
        else:
            is_data_anomalous="false" 
        # Prepare response
        response = {
            'timestamp': datetime.now().isoformat(),
            'is_anomalous':  is_data_anomalous,
            'correlation': float(correlation),
            'current_readings': {
                'heart_rate': list(monitor.heart_rates)[-1] if monitor.heart_rates else None,
                'steps': list(monitor.step_counts)[-1] if monitor.step_counts else None
            },
            'window_size': len(monitor.heart_rates)
        }
        
        if is_anomalous:
            response['alert'] = {
                'message': 'Anomaly detected - heart rate changes not correlated with activity',
                'heart_rate_window': list(monitor.heart_rates),
                'steps_window': list(monitor.step_counts)
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

if __name__ == "__main__":
    app.run(debug=True)