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
def updatePMC_1(newPMC_1_email, newPMC_1_name, userID, newPMC_1_number):
    try:
        # Update the user's primary healthcare provider information
        update_response = supabase.table('users').update({
            "primary_health_care_provider": newPMC_1_name,
            "primary_health_care_provider_email": newPMC_1_email,"primary_health_care_provider_number":newPMC_1_number
        }).eq('id', userID).execute()  # Filter by user ID
        
        # Check if the update was successful
        if update_response.data:
            return {'message': 'Updated successfully'}, 200
        else:
            return {'error': 'Failed to update user data'}, 500

    except Exception as e:
        # Handle any errors that occur during the process
        return {'error': str(e)}, 500

def updatePMC_2(newPMC_2_email, newPMC_2_name, userID, newPMC_1_number):
    try:
        # Update the user's primary healthcare provider information
        update_response = supabase.table('users').update({
            "primary_health_care_provider": newPMC_2_name,
            "primary_health_care_provider_email": newPMC_2_email
        }).eq('id', userID).execute()  # Filter by user ID
        
        # Check if the update was successful
        if update_response.data:
            return {'message': 'Updated successfully'}, 200
        else:
            return {'error': 'Failed to update user data'}, 500

    except Exception as e:
        # Handle any errors that occur during the process
        return {'error': str(e)}, 500