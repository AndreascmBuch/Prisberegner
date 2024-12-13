import sqlite3

# Opret databasen og tabellen for logning af forespørgsler

conn = sqlite3.connect("calculation_service.db")
cursor = conn.cursor()

    # Logning af beregningsforespørgsler
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
conn.close()
