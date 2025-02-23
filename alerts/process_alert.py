import os
from flask import jsonify
from twilio.rest import Client
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_healthcare_providers(userID):
    """
    Fetches primary and secondary healthcare provider details for a given user.
    """
    try:
        response = supabase.table("users").select(
            "primary_health_care_provider_name, primary_health_care_contact_number, primary_health_care_contact_email, "
            "primary_health_care_2_name, primary_health_care_2_number, primary_health_care_2_email"
        ).eq("id", userID).execute()

        if response.data:
            user_data = response.data[0]
            return {
                "primary": {
                    "name": user_data.get("primary_health_care_provider_name"),
                    "phone": user_data.get("primary_health_care_contact_number"),
                    "email": user_data.get("primary_health_care_contact_email"),
                },
                "secondary": {
                    "name": user_data.get("primary_health_care_2_name"),
                    "phone": user_data.get("primary_health_care_2_number"),
                    "email": user_data.get("primary_health_care_2_email"),
                } if user_data.get("primary_health_care_2_name") else None,
            }
        else:
            return None
    except Exception as e:
        return {"error": str(e)}


def send_emergency_alert(location, userID, bpm):
    """
    Fetches healthcare providers and sends an emergency SMS.
    """
    try:
        # Fetch user’s healthcare provider details
        providers = get_healthcare_providers(userID)
        if not providers:
            return jsonify({"error": "User healthcare details not found"}), 404

        # Format the message
        message = f"🚨 EMERGENCY ALERT 🚨\n"
        message += f"User Location: {location}\n"
        message += f"Heart Rate: {bpm} BPM\n\n"
        message += f"Primary Health Care Provider:\n"
        message += f"Name: {providers['primary']['name']}\n"
        message += f"Phone: {providers['primary']['phone']}\n"
        message += f"Email: {providers['primary']['email']}\n"

        if providers["secondary"]:
            message += f"\nSecondary Health Care Provider:\n"
            message += f"Name: {providers['secondary']['name']}\n"
            message += f"Phone: {providers['secondary']['phone']}\n"
            message += f"Email: {providers['secondary']['email']}\n"

        # Send SMS via Twilio
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_client = Client(account_sid, auth_token)

        twilio_client.messages.create(
            to= "+234907905996",#+23480002255372",  
            from_="+12764962715",   
            body=message
        )

        return jsonify({"message": "Emergency alert sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
