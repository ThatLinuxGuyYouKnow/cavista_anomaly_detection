from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import numpy as np
from collections import deque
from alerts.create_alert import getAlerts
from auth.signin import signin
from auth.signup import sign_up_new_user
from bio_data.get_bpm import getAllBpm, getLast10bpm
from user_data.update_pmc import updatePMC_1, updatePMC_2
from bio_data.record_bpm import record_bio_data
from bio_data.get_step_data import getStepPerMinute


app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow all methods
        "allow_headers": ["Content-Type", "Authorization"]  # Allow these headers
    }
})




@app.route("/signup", methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'name' not in data or 'email' not in data or 'password' not in data or 'pmc_name' not in data or 'pmc_number' not in data or 'pmc_email' not in data:
            return jsonify({'error': 'Missing required data. Please provide name, email, password, pmc_name, pmc_number, and pmc_email'}), 400
        
        user_name = data['name']
        user_email = data['email']
        age = data['age']
        password = data['password']
        primary_health_care_provider_name = data['pmc_name']
        primary_health_care_provider_number = data['pmc_number']  
        primary_health_care_provider_email = data['pmc_email']
        
        # Call the sign_up_new_user function
        response = sign_up_new_user(
            password=password,
            age=age,
            username=user_name,
            email=user_email,
            primary_health_care_contact_email=primary_health_care_provider_email,
            primary_health_care_provider_name=primary_health_care_provider_name,
            primary_health_care_contact_number=primary_health_care_provider_number
        )
        
        # Return the response from sign_up_new_user
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/signin", methods=['POST'])
def sign_in():
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required data. Please provide email and password'}), 400
        
        email = data['email']
        password = data['password']
        
        # Call the signin function
        response = signin(password=password, email=email)
        
        # Return the response from signin
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Data Routes
@app.route("/update_pmc_1", methods=['POST'])
def update_pmc_1():
    try:
        data = request.get_json()
        pmc_name = data['pmc_name']
        pmc_email = data['pmc_email']
        pmc_number = data['pmc_number']
        userID = data['userID']
        response = updatePMC_1(newPMC_1_name=pmc_name, newPMC_1_email=pmc_email, userID=userID,newPMC_1_number=pmc_number)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/update_pmc_2", methods=['POST'])
def update_pmc_2():
    try:
        data = request.get_json()
        pmc_name = data['pmc_name']
        pmc_email = data['pmc_email']
        pmc_number = data['pmc_number']
        userID = data['userID']
        response = updatePMC_2(newPMC_2_name=pmc_name, newPMC_2_email=pmc_email, userID=userID,newPMC_1_number=pmc_number)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/insert_pmc_2", methods=['POST'])
def insert_pmc_2():
    try:
        data = request.get_json()
        pmc_name = data['pmc_name']
        pmc_email = data['pmc_email']
        pmc_number = data['pmc_number']
        userID = data['userID']
        response = updatePMC_2(newPMC_2_name=pmc_name, newPMC_2_email=pmc_email, userID=userID,newPMC_1_number=pmc_number)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Get and Push Bio Data
@app.route("/get_step_data", methods=['GET'])
def getSteps():
    try:
        data = request.get_json()
        userID = data['userID']
        response = getStepPerMinute(userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/record_bio_data", methods=['POST'])
def record_data():
    try:
        data = request.get_json()
        bpm_list = data['bpm_list']
        step_list = data['step_list']
        userID = data['userID']
        location = data['location']
        response = record_bio_data(bpm_data_list=bpm_list, step_count=step_list, userID=userID, location=location)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/get_all_bpm", methods=['GET'])
def get_all_bpm():
    try:
        data = request.get_json()
        userID = data['userID']
        response = getAllBpm(userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/get_beats_10", methods=['GET'])
def get_last_10():
    try:
        data = request.get_json()
        userID = data['userID']
        response = getLast10bpm(userID=userID)
        return response
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
app.route("/get_alerts", methods = ['POST'])
def get_user_Alerts():
    userID = request.get_data['userID']
    getAlerts(userID=userID)
if __name__ == "__main__":
    app.run(debug=True)