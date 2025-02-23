from flask import jsonify
import supabase
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import datetime

from alerts.process_alert import send_emergency_alert

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

def getAlerts(userID):
    try:
        # Fetch alerts for the user
        response = supabase.table('alerts').select('*').eq('userID', userID).execute()
        
        # Check if there are any alerts
        if len(response.data) > 0:
            return jsonify({'alerts': response.data}), 200
        else:
            return jsonify({'error': 'No alerts found for this user'}), 400

    except Exception as e:
        # Handle any errors that occur during the process
        return jsonify({'error': str(e)}), 500

def create_alert(userID, bpm, location):
    try:
        # Insert a new alert into the 'alerts' table
        current_time = datetime.datetime.utcnow().isoformat()  # Get current UTC time in ISO format
        insert_response = supabase.table('alerts').insert({
            'user_id': userID,
            'bpm': bpm,
            'time': current_time,
            "location":location
        }).execute()
        
        # Check if the insertion was successful
        if insert_response.data:
            send_emergency_alert(location=location, userID=userID, bpm=bpm)
            return jsonify({'message': 'Alert created successfully'}), 200
            
        else:
            return jsonify({'error': 'Failed to create alert'}), 500

    except Exception as e:
        # Handle any errors that occur during the process
        return jsonify({'error': str(e)}), 500