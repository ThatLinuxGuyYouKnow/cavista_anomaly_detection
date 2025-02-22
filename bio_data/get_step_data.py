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
        response = supabase.table('bio_data').select('last_10_steps').eq('user_id', userID).execute()
        
        if response.data:
            # Extract JSONB array directly as Python list
            last_10_steps = response.data[0].get('last_10_steps', [])
            
            if not last_10_steps:  # Check for empty array
                return jsonify({'error': "No step data available"}), 400

            # Calculate average (no conversion needed if stored as numbers)
            total_steps = sum(last_10_steps)
            average = total_steps / len(last_10_steps)
            return jsonify({'average_steps_per_minute': average}), 200
            
        return jsonify({'error': "User not found"}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        # Handle any other errors
        return jsonify({'error': str(e)}), 500