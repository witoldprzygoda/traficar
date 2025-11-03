import requests
import csv
import os
from datetime import datetime
from pathlib import Path

BASE_URL = "https://fioletowe.live/api/v1/cars"
DATA_FILE = "data/consumption.csv"
STATE_FILE = "data/last_state.csv"

def get_cars():
    """Fetch current car data"""
    response = requests.get(BASE_URL, params={"zoneId": 1})
    return response.json()['cars']

def load_previous_state():
    """Load previous reading"""
    if not os.path.exists(STATE_FILE):
        return {}
    
    state = {}
    with open(STATE_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state[int(row['id'])] = {
                'fuel': float(row['fuel']),
                'available': row['available'] == 'True'
            }
    return state

def save_current_state(cars):
    """Save current reading for next comparison"""
    Path("data").mkdir(exist_ok=True)
    with open(STATE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'fuel', 'available'])
        for car in cars:
            writer.writerow([car['id'], car['fuel'], car['available']])

def calculate_consumption(previous_state, current_cars):
    """Calculate fuel consumption since last reading"""
    total_consumption = 0
    consumption_events = 0
    
    for car in current_cars:
        car_id = car['id']
        
        # Check if we have previous data for this car
        if car_id not in previous_state:
            continue
        
        prev = previous_state[car_id]
        curr_fuel = car['fuel']
        prev_fuel = prev['fuel']
        
        # Car was available and fuel decreased = consumption event
        if prev['available'] and curr_fuel < prev_fuel:
            consumption = prev_fuel - curr_fuel
            total_consumption += consumption
            consumption_events += 1
    
    return total_consumption, consumption_events

def append_consumption_log(timestamp, consumption, events):
    """Append consumption to CSV"""
    Path("data").mkdir(exist_ok=True)
    file_exists = os.path.exists(DATA_FILE)
    
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'consumption_percentage', 'events_count'])
        writer.writerow([timestamp, f"{consumption:.2f}", events])

def main():
    print(f"[{datetime.now()}] Starting monitoring cycle...")
    
    # Get current data
    current_cars = get_cars()
    print(f"Retrieved data for {len(current_cars)} cars")
    
    # Load previous state
    previous_state = load_previous_state()
    
    # Calculate consumption (skip first run when no previous data)
    if previous_state:
        consumption, events = calculate_consumption(previous_state, current_cars)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        append_consumption_log(timestamp, consumption, events)
        print(f"Consumption: {consumption:.2f}% across {events} events")
    else:
        print("First run - no previous data to compare")
    
    # Save current state for next run
    save_current_state(current_cars)
    print("State saved successfully")

if __name__ == "__main__":
    main()
