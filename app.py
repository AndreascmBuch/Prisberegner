from flask import Flask, request, jsonify
import requests
from datetime import datetime
import sqlite3

app = Flask(__name__)


def connect_db():
    conn = sqlite3.connect('calculation_service.db')
    conn.row_factory = sqlite3.Row  
    return conn 

# Funktion til beregning
def calculate_total_price(damage_data, subscription_data):
    damage_prices = {
        "engine_damage": 5000,
        "tire_damage": 1000,
        "brake_damage": 1500,
        "bodywork_damage": 4000,
        "interior_damage": 2000,
        "electronic_damage": 3000,
        "glass_damage": 1200,
        "undercarriage_damage": 2500,
        "light_damage": 800,
    }

    total_damage_cost = sum(
        damage_prices[damage] for damage, status in damage_data.items() if status != "none"
    )

    start_date = datetime.strptime(subscription_data["start_month"], "%Y-%m-%d")
    end_date = datetime.strptime(subscription_data["end_month"], "%Y-%m-%d")
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    total_subscription_cost = months * subscription_data["price_per_month"]

    total_price = total_damage_cost + total_subscription_cost
    return {
        "total_damage_cost": total_damage_cost,
        "total_subscription_cost": total_subscription_cost,
        "total_price": total_price,
    }

# Endpoint til beregning
@app.route('/calculate-total-price', methods=['POST'])
def calculate_total_price_endpoint():
    data = request.json
    customer_id = data["kunde_id"]
    car_id = data["car_id"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    # Hent skadesdata fra skade-mikroservicen
    damage_response = requests.get(f"https://skade-demo-b2awcyb4gedxdnhj.northeurope-01.azurewebsites.net/damage/{car_id}")
    damage_data = damage_response.json()

    # Hent abonnementsdata fra abonnements-mikroservicen
    subscription_response = requests.get(f"https://abonnement-beczhgfth9axdzd9.northeurope-01.azurewebsites.net/abonnement/{customer_id}")
    subscription_data = subscription_response.json()

    # Beregn samlet pris
    result = calculate_total_price(damage_data, subscription_data)

    # Log beregningen i databasen
    connection = sqlite3.connect("calculation_service.db")
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO calculation_requests (
            customer_id, car_id, start_date, end_date,
            total_damage_cost, total_subscription_cost, total_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        customer_id, car_id, start_date, end_date,
        result["total_damage_cost"], result["total_subscription_cost"], result["total_price"]
    ))
    connection.commit()
    connection.close()

    return jsonify(result)

@app.route('/calculate-total-revenue', methods=['GET'])
def calculate_total_revenue():
    # Forbind til databasen
    connection = sqlite3.connect("calculation_service.db")
    cursor = connection.cursor()

    # Beregn samlet omsætning
    cursor.execute('''
        SELECT SUM(total_price) AS total_revenue FROM calculation_requests
    ''')
    result = cursor.fetchone()
    connection.close()

    # Returner resultatet
    total_revenue = result[0] if result[0] is not None else 0
    return jsonify({"total_revenue": total_revenue})


# test route så vi ikke får 404
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Payment Service",
        "version": "1.0.0",
        "description": "A RESTful API for managing payments"
    })



if __name__ == '__main__':
    app.run(debug=True)



