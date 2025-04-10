from flask import Flask, render_template, request, jsonify
from chatbot import get_response, init_chat
from datetime import datetime, timedelta
import hashlib
import pandas as pd
import os

app = Flask(__name__)

# Load passport data from Excel file
passport_data = None
excel_file_path = 'indian_passport_dataset.xlsx'

def load_passport_data():
    global passport_data
    if os.path.exists(excel_file_path):
        passport_data = pd.read_excel(excel_file_path)
        # Convert passport numbers to strings to ensure compatibility
        if 'Passport Number' in passport_data.columns:
            passport_data['Passport Number'] = passport_data['Passport Number'].astype(str)
    else:
        print(f"Warning: Passport data file '{excel_file_path}' not found.")
        
# Load data at startup
load_passport_data()

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/passport-checker')
def passport_checker():
    return render_template('passport_checker.html')

@app.route('/api/validate-passport', methods=['POST'])
def validate_passport():
    passport_number = request.json.get('passport_number', '')
    travel_date_str = request.json.get('travel_date', '')
    
    if not passport_number or not travel_date_str:
        return jsonify({'error': 'Missing passport number or travel date'}), 400
    
    try:
        travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d')
        six_months_after = travel_date + timedelta(days=180)
        
        # Look up passport in the dataset
        if passport_data is not None and 'Passport Number' in passport_data.columns and 'Expiry Date' in passport_data.columns:
            # Find the passport in the dataset
            passport_info = passport_data[passport_data['Passport Number'] == passport_number]
            
            if not passport_info.empty:
                # Get expiry date from the dataset
                expiry_date_str = passport_info['Expiry Date'].iloc[0]
                if isinstance(expiry_date_str, str):
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
                else:
                    # Handle if the date is already a datetime object
                    expiry_date = expiry_date_str
                
                # Get additional passport info
                name = passport_info['Name'].iloc[0] if 'Name' in passport_info.columns else "Not Available"
                nationality = passport_info['Nationality'].iloc[0] if 'Nationality' in passport_info.columns else "Not Available"
                
                is_valid = expiry_date >= six_months_after
                
                return jsonify({
                    'is_valid': is_valid,
                    'passport_number': passport_number,
                    'name': name,
                    'nationality': nationality,
                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                    'travel_date': travel_date_str,
                    'required_validity': six_months_after.strftime('%Y-%m-%d'),
                    'found_in_database': True
                })
            
        # For passport numbers not in the database, always return invalid
        # Generate a deterministic expiry date from passport number that is not valid
        current_date = datetime.now()
        
        # Return an expiry date that is always less than 6 months after travel
        expiry_date = travel_date - timedelta(days=30)  # 1 month before travel date
        
        return jsonify({
            'is_valid': False,  # Always invalid for non-database passports
            'passport_number': passport_number,
            'name': "Not Available",
            'nationality': "Not Available",
            'expiry_date': expiry_date.strftime('%Y-%m-%d'),
            'travel_date': travel_date_str,
            'required_validity': six_months_after.strftime('%Y-%m-%d'),
            'found_in_database': False,
            'reason': "Passport number not found in the database"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('index.html')
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'response': init_chat()})
    
    response = get_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=8080) 