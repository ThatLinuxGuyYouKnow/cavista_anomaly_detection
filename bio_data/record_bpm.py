from flask import jsonify
import supabase
from supabase import create_client, Client
import os
from dotenv import load_dotenv
"This route for the which app to push its data to the db"
# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

def record_bio_data(bpm_data_list: list, step_count: list, userID: str):
    try:
        # Fetch the current 'beats' data for the user
        response = supabase.table('bio_data').select('beats').eq('user_id', userID).execute()
        
        # Check if there is existing data for the user
        total_beats = []
        if response.data and len(response.data) > 0:
            # If there's existing data, retrieve the 'beats' field
            total_beats = response.data[0].get('beats', [])
        
        # Append the new bpm_data_list to the existing beats
        total_beats.extend(bpm_data_list)
        
        # Insert or update biometric data into the 'bio_data' table
        insert_response = supabase.table('bio_data').upsert({
            "user_id": userID,
            "last_10_beats": bpm_data_list[-10:],  # Store only the last 10 readings
            "last_10_steps": step_count[-10:],     # Store only the last 10 steps
            "beats": total_beats                  # Store all historical beats
        }).execute()
        
        # Check if the insertion was successful
        if insert_response.data:
            return {'message': 'Biometric data recorded successfully'}, 200
        else:
            return {'error': 'Failed to record biometric data'}, 500

    except Exception as e:
        # Handle any errors that occur during the process
        return {'error': str(e)}, 500