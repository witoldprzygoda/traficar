import pandas as pd
import os
from datetime import datetime

ALL_READINGS_FILE = "data/all_readings.csv"
CONSUMPTION_OUTPUT = "data/calculated_consumption.csv"

def load_all_readings():
    """Load all readings from CSV"""
    if not os.path.exists(ALL_READINGS_FILE):
        print(f"Error: {ALL_READINGS_FILE} not found")
        print("Please run monitor_traficar.py first to collect data")
        return None

    df = pd.read_csv(ALL_READINGS_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def calculate_consumption_from_readings(df):
    """Calculate fuel consumption by comparing consecutive readings for each car"""
    consumption_events = []

    # Group by car_id and sort by timestamp
    for car_id, car_data in df.groupby('car_id'):
        car_data = car_data.sort_values('timestamp')

        # Compare consecutive readings
        for i in range(len(car_data) - 1):
            prev_row = car_data.iloc[i]
            curr_row = car_data.iloc[i + 1]

            # Only calculate consumption if fuel decreased
            prev_fuel = float(prev_row['fuel_liters'])
            curr_fuel = float(curr_row['fuel_liters'])

            # Consumption detected when:
            # 1. Car was available in previous reading
            # 2. Fuel decreased (not refueled)
            # 3. Decrease is significant (> 0.1L to avoid rounding errors)
            if prev_row['available'] and curr_fuel < prev_fuel:
                consumption = prev_fuel - curr_fuel

                if consumption > 0.1:
                    time_diff = curr_row['timestamp'] - prev_row['timestamp']
                    time_diff_minutes = time_diff.total_seconds() / 60

                    consumption_events.append({
                        'timestamp': curr_row['timestamp'],
                        'car_id': car_id,
                        'car_name': curr_row['car_name'],
                        'model_type': curr_row['model_type'],
                        'consumption_liters': consumption,
                        'prev_fuel_liters': prev_fuel,
                        'curr_fuel_liters': curr_fuel,
                        'time_diff_minutes': time_diff_minutes,
                        'prev_timestamp': prev_row['timestamp']
                    })

    return pd.DataFrame(consumption_events)

def analyze_car_activity(df):
    """Analyze car activity patterns from all readings"""
    print("\n" + "=" * 60)
    print("CAR ACTIVITY ANALYSIS")
    print("=" * 60)

    total_readings = len(df)
    unique_cars = df['car_id'].nunique()
    time_span = df['timestamp'].max() - df['timestamp'].min()

    print(f"\nTotal readings: {total_readings:,}")
    print(f"Unique cars tracked: {unique_cars}")
    print(f"Time span: {time_span}")
    print(f"From: {df['timestamp'].min()}")
    print(f"To: {df['timestamp'].max()}")

    # Availability statistics
    total_available = df['available'].sum()
    availability_rate = (total_available / total_readings) * 100
    print(f"\nAvailability rate: {availability_rate:.1f}% ({total_available:,}/{total_readings:,})")

    # Activity by car model
    print("\n" + "=" * 60)
    print("READINGS BY CAR MODEL")
    print("=" * 60)
    model_stats = df.groupby('car_name').agg({
        'car_id': 'count',
        'available': lambda x: (x.sum() / len(x) * 100)
    }).round(1)
    model_stats.columns = ['Readings', 'Availability %']
    model_stats = model_stats.sort_values('Readings', ascending=False)
    print(model_stats.head(10).to_string())

    # Cars with most readings
    print("\n" + "=" * 60)
    print("TOP 10 MOST TRACKED CARS")
    print("=" * 60)
    car_stats = df.groupby(['car_id', 'car_name']).size().sort_values(ascending=False).head(10)
    for (car_id, car_name), count in car_stats.items():
        print(f"Car {car_id} ({car_name}): {count} readings")

def print_consumption_summary(df_consumption):
    """Print consumption summary statistics"""
    if df_consumption is None or len(df_consumption) == 0:
        print("\nNo consumption events found")
        return

    print("\n" + "=" * 60)
    print("FUEL CONSUMPTION SUMMARY")
    print("=" * 60)

    total_consumption = df_consumption['consumption_liters'].sum()
    total_events = len(df_consumption)
    avg_per_event = df_consumption['consumption_liters'].mean()

    print(f"\nTotal consumption: {total_consumption:.2f} liters")
    print(f"Total events: {total_events}")
    print(f"Average per event: {avg_per_event:.2f} liters")
    print(f"Min consumption: {df_consumption['consumption_liters'].min():.2f} liters")
    print(f"Max consumption: {df_consumption['consumption_liters'].max():.2f} liters")
    print(f"Median consumption: {df_consumption['consumption_liters'].median():.2f} liters")

    # Average time between readings
    avg_time_diff = df_consumption['time_diff_minutes'].mean()
    print(f"\nAverage time between readings: {avg_time_diff:.1f} minutes")

    # Breakdown by car model
    print("\n" + "=" * 60)
    print("CONSUMPTION BY CAR MODEL")
    print("=" * 60)
    model_stats = df_consumption.groupby('car_name').agg({
        'consumption_liters': ['sum', 'count', 'mean']
    }).round(2)
    model_stats.columns = ['Total (L)', 'Events', 'Avg (L)']
    model_stats = model_stats.sort_values('Total (L)', ascending=False)
    print(model_stats.head(10).to_string())

def main():
    print("Loading all readings...")
    df = load_all_readings()

    if df is None or len(df) == 0:
        print("No data available")
        return

    print(f"Loaded {len(df):,} readings")

    # Analyze car activity
    analyze_car_activity(df)

    # Calculate consumption
    print("\nCalculating fuel consumption...")
    df_consumption = calculate_consumption_from_readings(df)

    # Print summary
    print_consumption_summary(df_consumption)

    # Save consumption data
    if df_consumption is not None and len(df_consumption) > 0:
        df_consumption.to_csv(CONSUMPTION_OUTPUT, index=False)
        print(f"\nSaved consumption data to {CONSUMPTION_OUTPUT}")
        print(f"Columns: {', '.join(df_consumption.columns)}")
    else:
        print("\nNo consumption events to save")

if __name__ == "__main__":
    main()
