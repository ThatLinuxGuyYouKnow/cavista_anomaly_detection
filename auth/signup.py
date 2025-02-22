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
# if not url or not key:
#    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

def sign_up_new_user(email: str, password: str, username: str, age: str,primary_health_care_provider_name: str, primary_health_care_contact_number: str, pimary_health_care_email:str  ):
    # Validate email, password, and username
    if len(email.split('@')) != 2 or len(password) < 6 or not username:
        return jsonify({'error': 'Invalid email, password, or username'}), 400

    try:
 

        # Attempt to sign up the user using Supabase
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
            "age" age,
            "primary_health_care_provider_name": primary_health_care_provider_name,
            "primary_health_care_contact_number": primary_health_care_contact_number
            "primary_health_care_contcat_email": primary_health_care_contact_email
            
        })

        # Check if the sign-up was successful
        if auth_response and auth_response.user:
            user_id = auth_response.user.id

            # Insert user data into the 'users' table
            insert_response = supabase.table('users').insert({
                "user_id": user_id,
                "username": username,
                "email": email
            }).execute()

            if insert_response.data:
                return jsonify({
                    'message': 'User signed up and data saved successfully',
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'user_id': user_id
                }), 201
            else:
                return jsonify({'error': 'Failed to save user data'}), 500

        else:
            return jsonify({'error': 'Failed to sign up user'}), 400

    except Exception as e:
        # Handle any errors that occur during the process
        return jsonify({'error': str(e)}), 500