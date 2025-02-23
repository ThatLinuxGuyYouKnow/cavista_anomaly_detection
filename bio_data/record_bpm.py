from flask import jsonify
import supabase
from supabase import create_client, Client
import os
import json
from datetime import datetime, timedelta
import numpy as np
from collections import deque
from dotenv import load_dotenv

from alerts.create_alert import create_alert

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
if not url or not key:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

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

monitor = CorrelationMonitor()



def record_bio_data(bpm_data_list: list, step_count: list, userID: str, location):
    try:
        if isinstance(step_count, int):
            step_count = [step_count]
            
        if not all(isinstance(x, (int, float)) for x in bpm_data_list + step_count):
            return {'error': 'Non-numeric values detected in input data'}, 400

        response = supabase.table('bio_data').select('beats', 'last_10_beats').eq('user_id', userID).execute()
        
        if not response.data:
            total_beats = {"beats": []}
            last_10_beats = []
        else:
            total_beats = response.data[0].get('beats', {"beats": []})
            last_10_beats = response.data[0].get('last_10_beats', [])

        if not isinstance(total_beats, dict) or "beats" not in total_beats:
            total_beats = {"beats": []}

        current_time = datetime.utcnow()
        new_readings = []
        
        for i, bpm in enumerate(bpm_data_list):
            minutes_offset = len(bpm_data_list) - 1 - i
            entry_time = current_time - timedelta(minutes=minutes_offset)
            
            new_readings.append({
                "bpm": bpm,
                "time": entry_time.isoformat()
            })

        total_beats["beats"].extend(new_readings)
        last_10_beats.extend(new_readings)
        last_10_beats = sorted(last_10_beats[-10:], key=lambda x: x["time"])
        last_10_steps = step_count[-10:]

        # Add readings to monitor
        monitor.add_readings(bpm_data_list, step_count)

        # Check for anomalies
        is_anomalous, correlation = monitor.detect_anomaly()

        if is_anomalous:
            create_alert(
                userID,
             
            monitor.heart_rates,
            location=location
            )

        upsert_data = {
            "user_id": userID,
            "last_10_beats": last_10_beats,
            "last_10_steps": last_10_steps,
            "beats": total_beats
        }

        insert_response = supabase.table('bio_data').upsert(upsert_data).execute()

        if insert_response.data:
            return {
                'message': 'Data recorded',
                'new_entries': new_readings,
                'is_anomalous': is_anomalous,
                'correlation': float(correlation)
            }, 200
        else:
            return {'error': 'Insert failed'}, 500

    except Exception as e:
        return {'error': str(e)}, 500
