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
        # Validate input data types
        if not all(isinstance(x, (int, float)) for x in bpm_data_list + step_count):
            return {'error': 'Non-numeric values detected in input data'}, 400

        # Fetch existing beats
        response = supabase.table('bio_data').select('beats').eq('user_id', userID).execute()
        total_beats = response.data[0].get('beats', []) if response.data else []

        # Append new data
        total_beats.extend(bpm_data_list)

        # Update last 10 values from ACCUMULATED DATA (not just new batch)
        upsert_data = {
            "user_id": userID,
            "last_10_beats": total_beats[-10:],  # Last 10 from total
            "last_10_steps": step_count[-10:],   # Adjust if steps need accumulation
            "beats": total_beats
        }

        # Upsert to Supabase
        insert_response = supabase.table('bio_data').upsert(upsert_data).execute()
        
        return {'message': 'Data recorded'}, 200 if insert_response.data else {'error': 'Insert failed'}, 500

    except Exception as e:
        return {'error': str(e)}, 500

    except Exception as e:
        # Handle any errors that occur during the process
        return {'error': str(e)}, 500