import os
import pandas as pd
import requests
from datetime import datetime, timedelta
import time

# Bristol coordinates (approximate)
BRISTOL_LAT = 51.4545
BRISTOL_LON = -2.5879

# Output directory
DATA_DIR = 'Data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# UK Met Office API endpoint (example, you need a real API key for production)
# For demonstration, we'll use Open-Meteo's free API (no key required)
API_URL = 'https://archive-api.open-meteo.com/v1/archive'

# Generate list of months from 2010-01 to current month
start_date = datetime(2010, 1, 1)
end_date = datetime.now()
months = []
current = start_date
while current <= end_date:
    months.append(current.strftime('%Y-%m'))
    if current.month == 12:
        current = current.replace(year=current.year+1, month=1)
    else:
        current = current.replace(month=current.month+1)

weather_records = []
for month in months:
    year, mon = month.split('-')
    first_day = f"{year}-{mon}-01"
    # Get last day of month
    if mon == '12':
        last_day = f"{int(year)+1}-01-01"
    else:
        last_day = f"{year}-{int(mon)+1:02d}-01"
    # API expects ISO dates
    params = {
        'latitude': BRISTOL_LAT,
        'longitude': BRISTOL_LON,
        'start_date': first_day,
        'end_date': (datetime.strptime(last_day, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d'),
        'daily': ['temperature_2m_max','temperature_2m_min','precipitation_sum','windspeed_10m_max','weathercode'],
        'timezone': 'Europe/London'
    }
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Each day in the month
        for i, date in enumerate(data['daily']['time']):
            record = {
                'date': date,
                'temperature_max': data['daily']['temperature_2m_max'][i],
                'temperature_min': data['daily']['temperature_2m_min'][i],
                'precipitation_sum': data['daily']['precipitation_sum'][i],
                'windspeed_max': data['daily']['windspeed_10m_max'][i],
                'weather_code': data['daily']['weathercode'][i]
            }
            weather_records.append(record)
        print(f"Fetched weather for {month}")
    except Exception as e:
        print(f"Error fetching weather for {month}: {e}")
    time.sleep(1)

# Convert to DataFrame and clean
df_weather = pd.DataFrame(weather_records)
df_weather = df_weather.dropna(how='all')
df_weather = df_weather.drop_duplicates(subset=['date'])
df_weather = df_weather.reset_index(drop=True)

# Save cleaned weather data
output_path = os.path.join(DATA_DIR, 'bristol_weather_2010_2025.csv')
df_weather.to_csv(output_path, index=False)
print(f"Cleaned Bristol weather data saved to {output_path} ({len(df_weather)} rows)")
