import requests
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_URL = "https://fioletowe.live/api/v1"
DB_FILE = "data/traficar.db"

def init_database():
    """Initialize SQLite database with simple schema"""
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Simple table - just store all car data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            car_id INTEGER NOT NULL,
            lat TEXT,
            lng TEXT,
            location TEXT,
            zone_id INTEGER,
            model_id INTEGER,
            reg_plate TEXT,
            side_number INTEGER,
            fuel REAL,
            range INTEGER,
            available INTEGER,
            last_update TEXT
        )
    """)

    # Index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_car_timestamp
        ON car_readings(car_id, timestamp)
    """)

    conn.commit()
    conn.close()

def get_cars():
    """Fetch current car data from API"""
    response = requests.get(f"{BASE_URL}/cars", params={"zoneId": 1})
    response.raise_for_status()
    return response.json()['cars']

def store_car_data(cars):
    """Store all car data to SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    for car in cars:
        cursor.execute("""
            INSERT INTO car_readings (
                timestamp, car_id, lat, lng, location, zone_id, model_id,
                reg_plate, side_number, fuel, range, available, last_update
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            car['id'],
            car.get('lat'),
            car.get('lng'),
            car.get('location'),
            car.get('zoneId'),
            car.get('modelId'),
            car.get('regPlate'),
            car.get('sideNumber'),
            car.get('fuel'),
            car.get('range'),
            1 if car.get('available') else 0,
            car.get('lastUpdate')
        ))

    conn.commit()
    conn.close()

def main():
    print(f"[{datetime.now()}] Starting monitoring...")

    # Initialize database
    init_database()

    # Get car data
    cars = get_cars()
    print(f"Retrieved {len(cars)} cars from API")

    # Store all data
    store_car_data(cars)
    print(f"Stored {len(cars)} car readings to database")
    print(f"Database: {DB_FILE}")

if __name__ == "__main__":
    main()
