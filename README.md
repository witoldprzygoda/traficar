# Traficar Fleet Monitor

Simple monitoring of the Traficar car-sharing fleet using data from the [Fioletowe API](https://fioletowe.live/docs/).

## What It Does

- Fetches current car data from API (location, fuel, availability, etc.)
- Stores **everything** to SQLite database
- That's it. Simple.

## Files

- **`monitor_traficar.py`** - Fetches and stores car data to SQLite
- **`read_database.py`** - Example script to read and analyze the database
- **`data/traficar.db`** - SQLite database with all car readings

## Installation

```bash
pip install requests
```

## Usage

### Collect Data

```bash
python monitor_traficar.py
```

This fetches all car data from the API and stores it to `data/traficar.db`.

Run this regularly (e.g., every 10 minutes via GitHub Actions) to build a dataset.

### Read Data

```bash
python read_database.py
```

This shows:
- Total readings in database
- Date range
- Number of unique cars
- Latest readings sample
- Simple fuel consumption analysis

## Database Schema

```sql
CREATE TABLE car_readings (
    id INTEGER PRIMARY KEY,
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
);
```

## Accessing Data from Other Code

```python
import sqlite3

conn = sqlite3.connect('data/traficar.db')
cursor = conn.cursor()

# Get all readings for a specific car
cursor.execute("""
    SELECT timestamp, fuel, available
    FROM car_readings
    WHERE car_id = ?
    ORDER BY timestamp
""", (49853,))

for row in cursor.fetchall():
    timestamp, fuel, available = row
    print(f"{timestamp}: {fuel}% fuel, available={available}")

conn.close()
```

## GitHub Actions

The monitoring script runs automatically every 10 minutes via GitHub Actions. Results are committed back to the repository.

## API Information

- **Base URL**: `https://fioletowe.live/api/v1`
- **Endpoint**: `/cars?zoneId=1`
- **Documentation**: https://fioletowe.live/docs/
