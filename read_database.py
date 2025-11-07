import sqlite3
from datetime import datetime

DB_FILE = "data/traficar.db"

def show_database_stats():
    """Show basic statistics from the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Total readings
    cursor.execute("SELECT COUNT(*) FROM car_readings")
    total = cursor.fetchone()[0]
    print(f"Total readings: {total:,}")

    # Date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM car_readings")
    min_date, max_date = cursor.fetchone()
    print(f"From: {min_date}")
    print(f"To: {max_date}")

    # Unique cars
    cursor.execute("SELECT COUNT(DISTINCT car_id) FROM car_readings")
    unique_cars = cursor.fetchone()[0]
    print(f"Unique cars: {unique_cars}")

    # Latest reading sample
    print("\nLatest 5 readings:")
    cursor.execute("""
        SELECT timestamp, car_id, location, fuel, available
        FROM car_readings
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        ts, car_id, location, fuel, available = row
        status = "available" if available else "unavailable"
        print(f"  {ts} | Car {car_id} | {fuel}% fuel | {status} | {location}")

    conn.close()

def calculate_fuel_consumption():
    """Simple fuel consumption calculation"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Find cars with multiple readings
    cursor.execute("""
        SELECT car_id, COUNT(*) as cnt
        FROM car_readings
        GROUP BY car_id
        HAVING cnt > 1
    """)

    cars_with_data = cursor.fetchall()
    print(f"\n\nFuel consumption analysis:")
    print(f"Cars with multiple readings: {len(cars_with_data)}")

    consumption_events = []

    for car_id, _ in cars_with_data[:10]:  # Show first 10
        cursor.execute("""
            SELECT timestamp, fuel, available
            FROM car_readings
            WHERE car_id = ?
            ORDER BY timestamp
        """, (car_id,))

        readings = cursor.fetchall()

        for i in range(len(readings) - 1):
            prev_ts, prev_fuel, prev_available = readings[i]
            curr_ts, curr_fuel, curr_available = readings[i + 1]

            # Consumption detected
            if prev_available and curr_fuel < prev_fuel:
                consumption = prev_fuel - curr_fuel
                if consumption > 0.1:  # Significant change
                    consumption_events.append({
                        'car_id': car_id,
                        'consumption': consumption,
                        'prev_ts': prev_ts,
                        'curr_ts': curr_ts
                    })

    if consumption_events:
        print(f"\nFound {len(consumption_events)} consumption events:")
        for event in consumption_events[:5]:
            print(f"  Car {event['car_id']}: {event['consumption']:.1f}% consumed")
            print(f"    {event['prev_ts']} -> {event['curr_ts']}")
    else:
        print("\nNo consumption events detected yet (need more data)")

    conn.close()

if __name__ == "__main__":
    try:
        show_database_stats()
        calculate_fuel_consumption()
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("Run monitor_traficar.py first to create the database")
