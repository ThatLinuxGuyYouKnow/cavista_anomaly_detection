from flask import jsonify
import supabase
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import datetime
# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(supabase_url=url, supabase_key=key)

def getAlerts(userID):
    get_data = supabase.table('alerts').select().eq('userID',userID)
    if len(get_data) > 0 :
     return get_data,200
    else:
       return ({"error":"no alerts"}),400