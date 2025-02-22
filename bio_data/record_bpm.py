from flask import jsonify
import supabase
from supabase import create_client, Client
import os
import json
from datetime import datetime, timedelta  # Added timedelta import
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
if not url or not key:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

def record_bio_data(bpm_data_list: list, step_count: list, userID: str):
    try:
        # Ensure step_count is a list
        if isinstance(step_count, int):
            step_count = [step_count]
            
        # Validate input data types
        if not all(isinstance(x, (int, float)) for x in bpm_data_list + step_count):
            return {'error': 'Non-numeric values detected in input data'}, 400

        # Fetch existing beats
        response = supabase.table('bio_data').select('beats', 'last_10_beats').eq('user_id', userID).execute()
        
        # If no data exists, initialize an empty structure
        if not response.data:
            total_beats = {"beats": []}
            last_10_beats = []
        else:
            total_beats = response.data[0].get('beats', {"beats": []})
            last_10_beats = response.data[0].get('last_10_beats', [])

        # Ensure proper dictionary structure
        if not isinstance(total_beats, dict) or "beats" not in total_beats:
            total_beats = {"beats": []}

        # Generate timestamps with progressive offsets
        current_time = datetime.utcnow()
        new_readings = []
        
        for i, bpm in enumerate(bpm_data_list):
            # Calculate minutes offset: latest entry (last in list) gets current time,
            # previous entries get progressively older timestamps
            minutes_offset = len(bpm_data_list) - 1 - i
            entry_time = current_time - timedelta(minutes=minutes_offset)
            
            new_readings.append({
                "bpm": bpm,
                "time": entry_time.isoformat()
            })

        # Append new readings to history
        total_beats["beats"].extend(new_readings)

        # Update last 10 beats (maintain chronological order)
        last_10_beats.extend(new_readings)
        last_10_beats = sorted(last_10_beats[-10:], key=lambda x: x["time"])

        # Update last 10 steps
        last_10_steps = step_count[-10:]

        # Prepare data for upserting
        upsert_data = {
            "user_id": userID,
            "last_10_beats": last_10_beats,
            "last_10_steps": last_10_steps,
            "beats": total_beats
        }

        # Upsert into Supabase
        insert_response = supabase.table('bio_data').upsert(upsert_data).execute()

        if insert_response.data:
            return {'message': 'Data recorded', 'new_entries': new_readings}, 200
        else:
            return {'error': 'Insert failed'}, 500

    except Exception as e:
        return {'error': str(e)}, 500