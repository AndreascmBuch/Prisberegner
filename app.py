import os
import sqlite3
from flask import Flask, jsonify, request, g
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Get DB_PATH from environment variable or use default
DB_PATH = os.getenv('DB_PATH', 'calculation_service.db')


# Initialize the Flask app
app = Flask(__name__)

# Function to get the database connection
def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

# Close the database connection after the request is finished
@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

# Ensure the database and table exist
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculation_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            car_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            total_damage_cost REAL,
            total_subscription_cost REAL,
            total_price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

# Home route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Calculation Service",
        "version": "1.0.0",
        "description": "A RESTful API for calculating total prices"
    })

# Function to calculate the total price
def calculate_total_price(damage_data, subscription_data):
    # Example calculation logic
    damage_cost = {
        'none': 0,
        'minor': 100,
        'major': 500,
        'puncture': 50,
        'worn out': 75,
        'bald': 100,
        'squealing': 25,
        'broken': 200,
        'dent': 150,
        'scratched': 100,
        'torn': 50,
        'stained': 75,
        'cracked': 100,
        'shattered': 250,
        'scraped': 50,
        'dented': 100,
        'broken': 150,
        'not working': 100
    }

    total_damage_cost = 0
    for field, damage in damage_data.items():
        if field != 'car_id' and damage in damage_cost:
            total_damage_cost += damage_cost[damage]

    # Example subscription calculation (assuming price is per month)
    months = subscription_data["end_month"] - subscription_data["start_month"]
    total_subscription_cost = months * subscription_data["price_per_month"]

    total_price = total_damage_cost + total_subscription_cost

    return {
        "total_damage_cost": total_damage_cost,
        "total_subscription_cost": total_subscription_cost,
        "total_price": total_price
    }

@app.route('/calculate-total-price', methods=['POST'])
def calculate_total_price_endpoint():
    data = request.json
    customer_id = data.get("customer_id")
    car_id = data.get("car_id")

    if not customer_id or not car_id:
        return jsonify({"error": "customer_id and car_id are required"}), 400

    try:
        # Fetch damage data from damage service
        damage_response = requests.get(f"https://skade-demo-b2awcyb4gedxdnhj.northeurope-01.azurewebsites.net/damage/{car_id}")
        damage_response.raise_for_status()
        damage_data = damage_response.json()[0] if damage_response.json() else {}

        # Fetch subscription data from subscription service
        subscription_response = requests.get(f"https://abonnement-beczhgfth9axdzd9.northeurope-01.azurewebsites.net/abonnement/{customer_id}")
        subscription_response.raise_for_status()
        subscription_data = subscription_response.json()

        # Calculate total price
        result = calculate_total_price(damage_data, subscription_data)

        # Log calculation in the database
        conn = sqlite3.connect("calculation_requests.db")
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO calculation_requests (
                customer_id, car_id, start_date, end_date,
                total_damage_cost, total_subscription_cost, total_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id, car_id, subscription_data["start_month"], subscription_data["end_month"],
            result["total_damage_cost"], result["total_subscription_cost"], result["total_price"]
        ))
        conn.commit()

        return jsonify(result), 201

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching data from external services: {str(e)}"}), 500

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# Route to calculate total revenue
@app.route('/calculate-total-revenue', methods=['GET'])
def calculate_total_revenue():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(total_price) AS total_revenue FROM calculation_requests')
        result = cursor.fetchone()
        total_revenue = result["total_revenue"] if result["total_revenue"] is not None else 0
        return jsonify({"total_revenue": total_revenue})

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

