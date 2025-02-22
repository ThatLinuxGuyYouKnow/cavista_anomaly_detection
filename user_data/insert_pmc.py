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

def insertPMC_2(userID, PMC_name, PMC_email, PMC_phone_number):
    try:
        # Insert the secondary healthcare provider information into the 'users' table
        insert_response = supabase.table('users').insert({
            "primary_health_care_2_email": PMC_email,
            "primary_health_care_2_name": PMC_name,
            "primary_health_care_2_number": PMC_phone_number
        }).eq('id', userID).execute()  # Filter by user ID
        
        # Check if the insertion was successful
        if insert_response.data:
            return {'message': 'Updated successfully'}, 200
        else:
            return {'error': 'Failed to update user data'}, 500

    except Exception as e:
        # Handle any errors that occur during the process
        return {'error': str(e)}, 500