import os
import requests
import time
import csv
from datetime import datetime, timedelta

# Bristol coordinates (city center)
BRISTOL_LAT = 51.4545
BRISTOL_LON = -2.5879
# Radius in miles (max allowed by API is 10 miles)
RADIUS_MILES = 10

# Output directory
DATA_DIR = 'Data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# API endpoint
API_URL = 'https://data.police.uk/api/crimes-street/all-crime'

# Generate list of months from 2010-01 to current month
start_date = datetime(2010, 1, 1)
end_date = datetime.now()
months = []
current = start_date
while current <= end_date:
    months.append(current.strftime('%Y-%m'))
    # Go to next month
    if current.month == 12:
        current = current.replace(year=current.year+1, month=1)
    else:
        current = current.replace(month=current.month+1)

# Fetch and save data for each month (overwrite existing files to ensure all data is up to date)
for month in months:
    out_path = os.path.join(DATA_DIR, f'bristol_crime_{month}.csv')
    print(f"Fetching data for {month} (overwriting if exists)...")
    params = {
        'lat': BRISTOL_LAT,
        'lng': BRISTOL_LON,
        'date': month
    }
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        crimes = response.json()
        if crimes:
            # Save to CSV
            keys = crimes[0].keys()
            with open(out_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(crimes)
            print(f"Saved {len(crimes)} records to {out_path}")
        else:
            print(f"No data for {month}")
    except Exception as e:
        print(f"Error fetching data for {month}: {e}")
    time.sleep(1)  # Be polite to the API

print("Done fetching Bristol crime data.")
