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

def signin(email: str, password: str):
    try:
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Sign in the user
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Get the user_id from the auth response
        user_id = response.user.id

        # Fetch all user details from the users table
        try:
            user_response = supabase.table("users").select(
                "username, age, primary_health_care_provider_name, "
                "primary_health_care_contact_number, primary_health_care_contact_email"
            ).eq("user_id", user_id).execute()

            if not user_response.data:
                return jsonify({'error': 'User not found in database'}), 404

            # Extract user data from response
            user_info = user_response.data[0]

        except Exception as e:
            return jsonify({'error': f'Error fetching user details: {str(e)}'}), 500

        # Prepare session and user data
        session_data = {
            'access_token': response.session.access_token,
            'refresh_token': response.session.refresh_token,
            'expires_in': response.session.expires_in,
            'expires_at': response.session.expires_at,
            'user_id': user_id  # Use the correct user ID
        }
        user_data = {
            'id': user_id,
            'email': response.user.email,
            'email_verified': response.user.email_confirmed_at is not None,
            'username': user_info["username"],
            'data': {
                'username': user_info["username"],
                'age': user_info["age"],
                'primary_health_care_provider_name': user_info["primary_health_care_provider_name"],
                'primary_health_care_contact_number': user_info["primary_health_care_contact_number"],
                'primary_health_care_contact_email': user_info["primary_health_care_contact_email"]
            }
        }

        # Return success response
        return jsonify({
            'message': 'Successfully signed in',
            'session': session_data,
            'user': user_data
        }), 200

    except Exception as e:
        # Handle authentication errors
        return jsonify({'error': str(e)}), 401
