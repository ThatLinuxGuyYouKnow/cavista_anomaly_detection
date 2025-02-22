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

def getStepPerMinute(userID):
    try:
        # Fetch the last 10 steps data for the user
        response = supabase.table('bio_data').select('last_10_steps').eq('user_id', userID).execute()
        
        if len(response.data) > 0:
            # Extract the 'last_10_steps' field from the response
            last_10_steps = response.data[0].get('last_10_steps', [])
            
            # Check if there are any steps recorded
            if len(last_10_steps) == 0:
                return jsonify({'error': "No step data available"}), 400
            
            # Calculate the average steps per minute
            total_steps = sum(last_10_steps)
            average_steps_per_minute = total_steps / len(last_10_steps)
            
            return jsonify({'average_steps_per_minute': average_steps_per_minute}), 200
        else:
            return jsonify({'error': "User has no step data"}), 400

    except Exception as e:
        # Handle any errors that occur during the process
        return jsonify({'error': str(e)}), 500