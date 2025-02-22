from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np
from collections import deque
from auth.signin import signin
from auth.signup import sign_up_new_user
from bio_data.get_bpm import getAllBpm, getLast10bpm
from user_data.update_pmc import updatePMC_1, updatePMC_2
from bio_data.record_bpm import record_bio_data
from bio_data.get_step_data import getStepPerMinute

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

## Mobile route, disregard for front end
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
        is_data_anomalous = 'true' if is_anomalous else 'false'
        
        # Prepare response
        response = {
            'timestamp': datetime.now().isoformat(),
            'is_anomalous': is_data_anomalous,
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
    
@app.route("/signup", methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'name' not in data or 'email' not in data or 'password' not in data or 'pmc_name' not in data or 'pmc_number' not in data or 'pmc_email' not in data:
            return jsonify({'error': 'Missing required data. Please provide name, email, password, pmc_name, pmc_number, and pmc_email'}), 400
        
        user_name = data['name']
        user_email = data['email']
        password = data['password']
        primary_health_care_provider_name = data['pmc_name']
        primary_health_care_provider_number = data['pmc_number']  
        primary_health_care_provider_email = data['pmc_email']
        
        # Call the sign_up_new_user function
        response = sign_up_new_user(
            password=password,
            username=user_name,
            email=user_email,
            primary_health_care_contact_email=primary_health_care_provider_email,
            primary_health_care_provider_name=primary_health_care_provider_name,
            primary_health_care_contact_number=primary_health_care_provider_number
        )
        
        # Return the response from sign_up_new_user
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/signin", methods=['POST'])
def sign_in():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required data. Please provide email and password'}), 400
        
        email = data['email']
        password = data['password']
        
        # Call the signin function
        response = signin(password=password, email=email)
        
        # Return the response from signin
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Data Routes
@app.route("/update_pmc_1", methods=['POST'])
def update_pmc_1():
    try:
        data = request.get_json()
        pmc_name = data['pmc_name']
        pmc_email = data['pmc_email']
        pmc_number = data['pmc_number']
        userID = data['userID']
        response = updatePMC_1(newPMC_1_name=pmc_name, newPMC_1_email=pmc_email, userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/update_pmc_2", methods=['POST'])
def update_pmc_2():
    try:
        data = request.get_json()
        pmc_name = data['pmc_name']
        pmc_email = data['pmc_email']
        pmc_number = data['pmc_number']
        userID = data['userID']
        response = updatePMC_2(newPMC_2_name=pmc_name, newPMC_2_email=pmc_email, userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/insert_pmc_2", methods=['POST'])
def insert_pmc_2():
    try:
        data = request.get_json()
        pmc_name = data['pmc_name']
        pmc_email = data['pmc_email']
        pmc_number = data['pmc_number']
        userID = data['userID']
        response = updatePMC_2(newPMC_2_name=pmc_name, newPMC_2_email=pmc_email, userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Get and Push Bio Data
@app.route("/get_step_data", methods=['POST'])
def getSteps():
    try:
        data = request.get_json()
        userID = data['userID']
        response = getStepPerMinute(userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/record_bio_data", methods=['POST'])
def record_data():
    try:
        data = request.get_json()
        bpm_list = data['bpm_list']
        step_list = data['step_list']
        userID = data['userID']
        response = record_bio_data(bpm_data_list=bpm_list, step_count=step_list, userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/get_all_bpm", methods=['POST'])
def get_all_bpm():
    try:
        data = request.get_json()
        userID = data['userID']
        response = getAllBpm(userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/get_beats_10", methods=['POST'])
def get_last_10():
    try:
        data = request.get_json()
        userID = data['userID']
        response = getLast10bpm(userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)