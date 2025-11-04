import requests
import csv
import os
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "https://fioletowe.live/api/v1"
DATA_FILE = "data/consumption.csv"
STATE_FILE = "data/last_state.csv"
MODELS_CACHE = "data/car_models.json"

def get_car_models():
    """Fetch and cache car model data"""
    # Try to load from cache first
    if os.path.exists(MODELS_CACHE):
        with open(MODELS_CACHE, 'r') as f:
            return json.load(f)
    
    # Fetch from API
    print("Fetching car models from API...")
    models = {}
    
    # Get both modelType 1 and 2
    for model_type in [1, 2]:
        response = requests.get(f"{BASE_URL}/car-models", params={
            "modelType": model_type,
            "electric": False
        })
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Handle different possible response structures
                if isinstance(data, dict):
                    # Try 'carModels' (capital M)
                    car_models = data.get('carModels', data.get('carmodels', data.get('models', [])))
                elif isinstance(data, list):
                    # Response is directly a list
                    car_models = data
                else:
                    print(f"Unexpected response format for modelType {model_type}: {type(data)}")
                    continue
                
                for model in car_models:
                    # CRITICAL FIX: Store with integer key for proper lookup
                    models[int(model['id'])] = {
                        'name': model['name'],
                        'type': model['type'],
                        'maxFuel': model['maxFuel']
                    }
            except Exception as e:
                print(f"Error parsing response for modelType {model_type}: {e}")
        else:
            print(f"Failed to fetch models for type {model_type}: HTTP {response.status_code}")
    
    if not models:
        raise Exception("Failed to fetch any car models from API")
    
    # Cache the models
    Path("data").mkdir(exist_ok=True)
    with open(MODELS_CACHE, 'w') as f:
        json.dump(models, f, indent=2)
    
    print(f"Cached {len(models)} car models")
    return models

def get_cars():
    """Fetch current car data"""
    response = requests.get(f"{BASE_URL}/cars", params={"zoneId": 1})
    return response.json()['cars']

def load_previous_state():
    """Load previous reading"""
    if not os.path.exists(STATE_FILE):
        return {}
    
    state = {}
    with open(STATE_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if this is old format (missing new columns)
            if 'fuel_percent' not in row or 'fuel_liters' not in row or 'model_id' not in row:
                print("Detected old state file format - will be regenerated")
                return {}  # Return empty state to regenerate
            
            state[int(row['id'])] = {
                'fuel_percent': float(row['fuel_percent']),
                'fuel_liters': float(row['fuel_liters']),
                'available': row['available'] == 'True',
                'model_id': int(row['model_id'])
            }
    return state

def save_current_state(cars, models):
    """Save current reading for next comparison"""
    Path("data").mkdir(exist_ok=True)
    with open(STATE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'fuel_percent', 'fuel_liters', 'available', 'model_id'])
        for car in cars:
            # Skip cars with unknown models or invalid types
            if car['modelId'] not in models:
                continue
            if models[car['modelId']]['type'] not in [1, 2]:
                continue
                
            max_fuel = models[car['modelId']]['maxFuel']
            fuel_liters = (car['fuel'] / 100.0) * max_fuel
            
            writer.writerow([
                car['id'],
                car['fuel'],
                f"{fuel_liters:.2f}",
                car['available'],
                car['modelId']
            ])

def calculate_consumption(previous_state, current_cars, models):
    """Calculate fuel consumption since last reading"""
    consumption_events = []
    
    for car in current_cars:
        car_id = car['id']
        model_id = car['modelId']
        
        # Skip cars with unknown models or invalid types
        if model_id not in models:
            continue
        if models[model_id]['type'] not in [1, 2]:
            continue
        
        # Check if we have previous data for this car
        if car_id not in previous_state:
            continue
        
        prev = previous_state[car_id]
        
        # Calculate current fuel in liters
        max_fuel = models[model_id]['maxFuel']
        curr_fuel_liters = (car['fuel'] / 100.0) * max_fuel
        prev_fuel_liters = prev['fuel_liters']
        
        # Only count consumption if:
        # 1. Car was available in previous reading
        # 2. Fuel decreased (not refueled)
        if prev['available'] and curr_fuel_liters < prev_fuel_liters:
            consumption = prev_fuel_liters - curr_fuel_liters
            
            # Only record significant consumption (> 0.1 liter to avoid rounding errors)
            if consumption > 0.1:
                consumption_events.append({
                    'car_id': car_id,
                    'consumption': consumption,
                    'car_name': models[model_id]['name'],
                    'model_type': models[model_id]['type'],
                    'prev_fuel': prev_fuel_liters,
                    'curr_fuel': curr_fuel_liters
                })
    
    return consumption_events

def append_consumption_log(timestamp, consumption_events):
    """Append consumption events to CSV"""
    if not consumption_events:
        return
    
    Path("data").mkdir(exist_ok=True)
    file_exists = os.path.exists(DATA_FILE)
    
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'car_id', 'car_name', 'model_type', 
                           'consumption_liters', 'prev_fuel_liters', 'curr_fuel_liters'])
        
        for event in consumption_events:
            writer.writerow([
                timestamp,
                event['car_id'],
                event['car_name'],
                event['model_type'],
                f"{event['consumption']:.2f}",
                f"{event['prev_fuel']:.2f}",
                f"{event['curr_fuel']:.2f}"
            ])

def main():
    print(f"[{datetime.now()}] Starting monitoring cycle...")
    
    # Get car models (cached after first run)
    models = get_car_models()
    
    # Get current data
    current_cars = get_cars()
    print(f"Retrieved data for {len(current_cars)} cars")
    
    # Load previous state
    previous_state = load_previous_state()
    
    # Calculate consumption (skip first run when no previous data)
    if previous_state:
        consumption_events = calculate_consumption(previous_state, current_cars, models)
        
        if consumption_events:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            append_consumption_log(timestamp, consumption_events)
            
            total_consumption = sum(e['consumption'] for e in consumption_events)
            print(f"Recorded {len(consumption_events)} consumption events")
            print(f"Total consumption: {total_consumption:.2f} liters")
            
            # Show breakdown by car model
            model_consumption = {}
            for event in consumption_events:
                name = event['car_name']
                if name not in model_consumption:
                    model_consumption[name] = {'count': 0, 'liters': 0}
                model_consumption[name]['count'] += 1
                model_consumption[name]['liters'] += event['consumption']
            
            print("\nConsumption by model:")
            for name, data in sorted(model_consumption.items()):
                print(f"  {name}: {data['liters']:.2f}L ({data['count']} events)")
        else:
            print("No consumption events detected")
    else:
        print("First run - no previous data to compare")
    
    # Save current state for next run
    save_current_state(current_cars, models)
    print("State saved successfully")

if __name__ == "__main__":
    main()
