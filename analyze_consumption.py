import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

DATA_FILE = "data/consumption.csv"

def load_consumption_data():
    """Load and parse consumption data"""
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found")
        return None
    
    df = pd.read_csv(DATA_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def print_summary_statistics(df):
    """Print overall statistics"""
    print("=" * 60)
    print("CONSUMPTION SUMMARY")
    print("=" * 60)
    
    total_consumption = df['consumption_liters'].sum()
    total_events = len(df)
    avg_per_event = df['consumption_liters'].mean()
    
    print(f"\nOverall Statistics:")
    print(f"  Total consumption: {total_consumption:.2f} liters")
    print(f"  Total events: {total_events}")
    print(f"  Average per event: {avg_per_event:.2f} liters")
    print(f"  Min consumption: {df['consumption_liters'].min():.2f} liters")
    print(f"  Max consumption: {df['consumption_liters'].max():.2f} liters")
    print(f"  Median consumption: {df['consumption_liters'].median():.2f} liters")
    
    # Time range
    start_date = df['timestamp'].min()
    end_date = df['timestamp'].max()
    duration = end_date - start_date
    
    print(f"\nTime Range:")
    print(f"  From: {start_date}")
    print(f"  To: {end_date}")
    print(f"  Duration: {duration}")
    
    if duration.total_seconds() > 0:
        hours = duration.total_seconds() / 3600
        liters_per_hour = total_consumption / hours
        print(f"  Average consumption rate: {liters_per_hour:.2f} liters/hour")

def print_model_breakdown(df):
    """Print statistics by car model"""
    print("\n" + "=" * 60)
    print("CONSUMPTION BY CAR MODEL")
    print("=" * 60)
    
    model_stats = df.groupby('car_name').agg({
        'consumption_liters': ['sum', 'count', 'mean', 'median'],
        'model_type': 'first'
    }).round(2)
    
    model_stats.columns = ['Total (L)', 'Events', 'Avg (L)', 'Median (L)', 'Type']
    model_stats = model_stats.sort_values('Total (L)', ascending=False)
    
    print(model_stats.to_string())
    
    print("\n" + "=" * 60)
    print("MODEL TYPE BREAKDOWN")
    print("=" * 60)
    
    type_stats = df.groupby('model_type').agg({
        'consumption_liters': ['sum', 'count', 'mean']
    }).round(2)
    
    type_stats.columns = ['Total (L)', 'Events', 'Avg (L)']
    print(type_stats.to_string())

def plot_consumption_over_time(df):
    """Plot consumption trends over time"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Hourly consumption
    df_hourly = df.set_index('timestamp').resample('H')['consumption_liters'].sum()
    axes[0].plot(df_hourly.index, df_hourly.values, marker='o', linestyle='-', linewidth=1)
    axes[0].set_title('Hourly Fuel Consumption', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Consumption (liters)')
    axes[0].grid(True, alpha=0.3)
    
    # Cumulative consumption
    df_sorted = df.sort_values('timestamp')
    cumulative = df_sorted['consumption_liters'].cumsum()
    axes[1].plot(df_sorted['timestamp'], cumulative, linewidth=2)
    axes[1].set_title('Cumulative Fuel Consumption', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('Total Consumption (liters)')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/consumption_over_time.png', dpi=300, bbox_inches='tight')
    print("\nSaved: data/consumption_over_time.png")

def plot_model_comparison(df):
    """Plot comparison between car models"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Total consumption by model
    model_totals = df.groupby('car_name')['consumption_liters'].sum().sort_values(ascending=False)
    top_10 = model_totals.head(10)
    
    axes[0].barh(range(len(top_10)), top_10.values)
    axes[0].set_yticks(range(len(top_10)))
    axes[0].set_yticklabels(top_10.index)
    axes[0].set_xlabel('Total Consumption (liters)')
    axes[0].set_title('Top 10 Models by Total Consumption', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    # Average consumption per event by model
    model_avg = df.groupby('car_name')['consumption_liters'].mean().sort_values(ascending=False)
    top_10_avg = model_avg.head(10)
    
    axes[1].barh(range(len(top_10_avg)), top_10_avg.values)
    axes[1].set_yticks(range(len(top_10_avg)))
    axes[1].set_yticklabels(top_10_avg.index)
    axes[1].set_xlabel('Average Consumption per Event (liters)')
    axes[1].set_title('Top 10 Models by Average Consumption', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('data/model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: data/model_comparison.png")

def plot_consumption_distribution(df):
    """Plot distribution of consumption values"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histogram
    axes[0].hist(df['consumption_liters'], bins=30, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Consumption (liters)')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Distribution of Consumption Events', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Box plot by model type
    type_data = [df[df['model_type'] == t]['consumption_liters'] for t in sorted(df['model_type'].unique())]
    axes[1].boxplot(type_data, labels=[f"Type {t}" for t in sorted(df['model_type'].unique())])
    axes[1].set_ylabel('Consumption (liters)')
    axes[1].set_title('Consumption Distribution by Model Type', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('data/consumption_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: data/consumption_distribution.png")

def main():
    # Load data
    df = load_consumption_data()
    if df is None or len(df) == 0:
        print("No data available for analysis")
        return
    
    # Print statistics
    print_summary_statistics(df)
    print_model_breakdown(df)
    
    # Create visualizations
    print("\n" + "=" * 60)
    print("GENERATING PLOTS")
    print("=" * 60)
    
    try:
        plot_consumption_over_time(df)
        plot_model_comparison(df)
        plot_consumption_distribution(df)
        print("\nAll plots generated successfully!")
    except Exception as e:
        print(f"Error generating plots: {e}")
        print("Note: Install matplotlib with: pip install matplotlib pandas")

if __name__ == "__main__":
    main()
