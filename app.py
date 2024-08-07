from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
import json
import requests

app = Flask(__name__)

# Load trained model
with open('linear_regression_model.pkl', 'rb') as f:
    loaded_lr_model = pickle.load(f)

# Google reCAPTCHA secret key
RECAPTCHA_SECRET_KEY = '6LdI6h8qAAAAAGsDskoZ3-Kc3jps3HHw6Z-ck2zp'

def verify_recaptcha(response):
    payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': response}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    return r.json().get('success')

def map_day_of_week(day):
    days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
    return days.get(day, 0)

def map_time(time):
    time_map = {
        '08:00': 8,
        '10:00': 10,
        '12:00': 12,
        '14:00': 14,
        '16:00': 16
    }
    return time_map.get(time, 0)

def map_department(department):
    departments = {
        'ICT 400lvl': 1,
        'EEE 500lvl': 2,
        'CPE 500lvl': 3,
        'EEE 400lvl': 4,
        'CPE 400lvl': 5
    }
    return departments.get(department, 0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_attendance_rate():
    data = request.get_json()
    
    recaptcha_response = data.get('recaptchaResponse')
    if not verify_recaptcha(recaptcha_response):
        return jsonify({'error': 'Invalid reCAPTCHA. Please try again.'}), 400

    # Map data to numerical values
    day_of_week = map_day_of_week(data['dayOfWeek'])
    time = map_time(data['time'])
    department = map_department(data['department'])

    # Convert mapped data to DataFrame
    df = pd.DataFrame([{
        'Day of the Week': day_of_week,
        'Time': time,
        'department': department
    }])

    # Make predictions
    predictions = loaded_lr_model.predict(df)
    
    # Convert predictions to JSON format
    predictions_json = predictions.tolist()
 
    # Return predictions
    return jsonify({'predictions': predictions_json})

if __name__ == '__main__':
    app.run(debug=True)
