# Calculation Service

## Introduction
The **Calculation Service** is a RESTful microservice that calculates total prices for car rentals. It integrates with external microservices to fetch data on damages and subscriptions and provides endpoints for calculations, logging, and revenue tracking.

## Features
- Fetches damage data from an external Damage Service.
- Fetches subscription data from an external Subscription Service.
- Calculates total price based on damage and subscription data.
- Logs calculation requests in a SQLite database.
- Provides endpoints to retrieve all calculations and total revenue.
- Secured with JWT-based authentication.

## Technologies Used
- **Python**: Core programming language.
- **Flask**: Web framework for building RESTful APIs.
- **SQLite**: Lightweight database for storing calculation logs.
- **Gunicorn**: WSGI server for deployment.
- **Docker**: Containerization for consistent deployments.

## API Endpoints
### Base URL
```
http://<host>:<port>/
```

### Public Endpoints
- **`GET /`**: Returns service information.

### Authenticated Endpoints (JWT Required)
1. **`POST /calculate-total-price`**
   - **Description**: Calculates the total price for a car rental.
   - **Request Body (JSON)**:
     ```json
     {
       "customer_id": <int>,
       "car_id": <int>
     }
     ```
   - **Response (201)**:
     ```json
     {
       "total_damage_cost": <float>,
       "total_subscription_cost": <float>,
       "total_price": <float>
     }
     ```

2. **`GET /get-all-calculations`**
   - **Description**: Retrieves all calculation logs.
   - **Response (200)**:
     ```json
     [
       {
         "id": <int>,
         "customer_id": <int>,
         "car_id": <int>,
         "start_date": <string>,
         "end_date": <string>,
         "total_damage_cost": <float>,
         "total_subscription_cost": <float>,
         "total_price": <float>,
         "timestamp": <string>
       }
     ]
     ```

3. **`GET /calculate-total-revenue`**
   - **Description**: Calculates the total revenue from all logged requests.
   - **Response (200)**:
     ```json
     {
       "total_revenue": <float>
     }
     ```

4. **`GET /debug`**
   - **Description**: Debug endpoint to check loaded environment variables.

## Environment Variables
Create a `.env` file with the following:
```
DB_PATH=calculation_service.db
KEY=<your_secret_key>
```

## Database Schema
The service uses a SQLite database with the following schema:
```sql
CREATE TABLE calculation_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    car_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    total_damage_cost REAL,
    total_subscription_cost REAL,
    total_price REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Prerequisites
- Python 3.10+
- Docker (for containerized deployment)

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file:
   ```bash
   echo "DB_PATH=calculation_service.db" > .env
   echo "KEY=<your_secret_key>" >> .env
   ```

## Running Locally
1. Initialize the SQLite database:
   ```bash
   python skadeberegnerdatabase.py
   ```
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. Access the API at `http://127.0.0.1:5000`.

## Deployment with Docker
1. Build the Docker image:
   ```bash
   docker build -t calculation-service .
   ```
2. Run the container:
   ```bash
   docker run -p 80:80 --env-file .env calculation-service
   ```

## External Dependencies
### Damage Service
- **Endpoint**: `GET /damage/{car_id}`
- **Example Response**:
  ```json
  {
    "car_id": 1,
    "tires": "worn out",
    "engine": "none",
    "brakes": "squealing"
  }
  ```

### Subscription Service
- **Endpoint**: `GET /abonnement/{customer_id}`
- **Example Response**:
  ```json
  {
    "customer_id": 123,
    "start_month": "2024-01-01",
    "end_month": "2024-03-01",
    "price_per_month": 200
  }
  ```

## Testing
- Use tools like Postman or Curl to test the API.
- Generate JWT tokens for authenticated endpoints.

## Known Issues
- Ensure the external Damage and Subscription services are accessible.
- JWT token expiration handling is not implemented.

## Future Improvements
- Add more detailed error handling for external service failures.
- Improve JWT token management with refresh tokens.
- Add unit tests and integration tests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
