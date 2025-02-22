from flask import jsonify
import supabase
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

def getAllBpm(userID):
    try:
        # Fetch all BPM data for the user
        response = supabase.table('bio_data').select('beats').eq('user_id', userID).execute()
        
        if len(response.data) > 0:
            # Extract the 'beats' field from the response
            beats = response.data[0].get('beats', [])
            return jsonify({'bpm': beats}), 200
        else:
            return jsonify({'error': "User has no BPM data"}), 400

    except Exception as e:
        # Handle any errors that occur during the process
        return jsonify({'error': str(e)}), 500

def getLast10bpm(userID):
    try:
        # Fetch all BPM data for the user
        response = supabase.table('bio_data').select('beats').eq('user_id', userID).execute()
        
        if len(response.data) > 0:
            # Extract the 'beats' field from the response
            beats = response.data[0].get('beats', [])
            
            # Return the last 10 BPM readings safely
            last_10_beats = beats[-10:] if len(beats) >= 10 else beats
            return jsonify({'bpm': last_10_beats}), 200
        else:
            return jsonify({'error': "User has no BPM data"}), 400

    except Exception as e:
        # Handle any errors that occur during the process
        return jsonify({'error': str(e)}), 500