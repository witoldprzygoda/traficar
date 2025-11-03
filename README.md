# Traficar Fleet Fuel Consumption Monitor

This project monitors the Traficar car-sharing fleet and tracks fuel consumption in **absolute liters** (not percentages) using data from the [Fioletowe API](https://fioletowe.live/docs/).

## Key Changes from Previous Version

### What Was Fixed

The previous version had a critical flaw - it calculated consumption in **percentages** instead of absolute fuel amounts. This led to incorrect metrics like:
- Total consumption: 1936% 
- Average: 64.53% per 10 minutes

### New Implementation

The updated version:

1. **Fetches car model data** including `maxFuel` capacity for each model
2. **Converts percentages to liters** using the formula: `liters = (percent / 100) * maxFuel`
3. **Tracks only actual consumption**:
   - Same fuel level → no change recorded
   - Higher fuel level → refueling detected, state updated but no consumption logged
   - Lower fuel level → consumption calculated in liters and recorded
4. **Stores rich data** for analysis: timestamp, car ID, car name, model type, consumption

## Files

- **`monitor_traficar.py`** - Main monitoring script (runs on GitHub Actions every 10 minutes)
- **`analyze_consumption.py`** - Analysis and visualization script
- **`data/consumption.csv`** - Detailed consumption records
- **`data/last_state.csv`** - Current state of all vehicles
- **`data/car_models.json`** - Cached car model data (auto-generated)
- **`.github/workflows/monitor.yml`** - GitHub Actions workflow

## Data Structure

### consumption.csv
```csv
timestamp,car_id,car_name,model_type,consumption_liters,prev_fuel_liters,curr_fuel_liters
2025-11-03 14:23:15,49853,RENAULT Clio IV,1,3.50,28.00,24.50
```

### Columns
- `timestamp` - When the consumption was detected
- `car_id` - Unique car identifier
- `car_name` - Car model name (e.g., "RENAULT Clio IV")
- `model_type` - Model type (1 or 2, as filtered from API)
- `consumption_liters` - Fuel consumed in liters
- `prev_fuel_liters` - Previous fuel level in liters
- `curr_fuel_liters` - Current fuel level in liters

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running the Monitor Manually

```bash
python monitor_traficar.py
```

This will:
1. Fetch current car data from the API
2. Load car models (cached after first run)
3. Compare with previous state
4. Record consumption events
5. Save current state

### Analyzing Data

```bash
python analyze_consumption.py
```

This generates:
- Summary statistics (total consumption, events, averages)
- Breakdown by car model
- Breakdown by model type
- Three visualization plots:
  - `consumption_over_time.png` - Hourly and cumulative consumption
  - `model_comparison.png` - Top models by total and average consumption
  - `consumption_distribution.png` - Distribution histograms and box plots

## GitHub Actions

The monitoring script runs automatically every 10 minutes via GitHub Actions. Results are committed back to the repository.

To trigger manually:
1. Go to Actions tab in GitHub
2. Select "Monitor Traficar Fleet"
3. Click "Run workflow"

## Logic Details

### Consumption Detection

```python
if previous_fuel_liters > current_fuel_liters:
    # Consumption detected
    consumption = previous_fuel_liters - current_fuel_liters
    
elif previous_fuel_liters < current_fuel_liters:
    # Refueling detected - update state, no consumption logged
    
else:
    # No change - car not used
```

### Model Filtering

Only tracks vehicles with `modelType` 1 or 2 (excludes electric vehicles and other types).

## Example Output

```
[2025-11-03 14:23:15] Starting monitoring cycle...
Cached 50 car models
Retrieved data for 832 cars
Recorded 45 consumption events
Total consumption: 178.50 liters

Consumption by model:
  RENAULT Clio IV: 89.25L (23 events)
  RENAULT Clio V: 67.80L (18 events)
  DACIA Sandero: 21.45L (4 events)
```

## API Information

- **Base URL**: `https://fioletowe.live/api/v1`
- **Endpoints used**:
  - `/cars?zoneId=1` - Current car data
  - `/car-models?modelType={1,2}&electric=false` - Car specifications
- **Documentation**: https://fioletowe.live/docs/

## Notes

- Consumption is only recorded when fuel decreases by > 0.1 liters (avoids rounding errors)
- Cars with unknown models are skipped
- First run establishes baseline (no consumption recorded)
- Model data is cached to reduce API calls

## Future Improvements

Potential enhancements:
- Track distance driven (if available in API)
- Calculate fuel efficiency (L/100km)
- Detect anomalies (unusually high consumption)
- Add geographic analysis by zone
- Create dashboard for real-time monitoring
