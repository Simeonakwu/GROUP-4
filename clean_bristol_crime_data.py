import os
import glob
import pandas as pd
import numpy as np

# Directory containing monthly CSVs
data_dir = 'Data'
all_files = glob.glob(os.path.join(data_dir, 'bristol_crime_*.csv'))

# Combine all CSVs into one DataFrame
df_list = []
for file in all_files:
    try:
        df = pd.read_csv(file)
        df_list.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

if not df_list:
    print("No data files found.")
    exit()

crimes_df = pd.concat(df_list, ignore_index=True)

# Clean and preprocess
def clean_crime_data(df):
    # Remove empty rows
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(how='all')
    # Extract features from location
    if 'location' in df.columns:
        df['lat'] = df['location'].apply(lambda x: float(eval(x)['latitude']) if pd.notnull(x) and 'latitude' in eval(x) else np.nan)
        df['lng'] = df['location'].apply(lambda x: float(eval(x)['longitude']) if pd.notnull(x) and 'longitude' in eval(x) else np.nan)
        df['street_name'] = df['location'].apply(lambda x: eval(x)['street']['name'] if pd.notnull(x) and 'street' in eval(x) and 'name' in eval(x)['street'] else None)
    # Parse date
    if 'month' in df.columns:
        df['year'] = pd.to_datetime(df['month'], errors='coerce').dt.year
        df['month_num'] = pd.to_datetime(df['month'], errors='coerce').dt.month
    # Encode category
    if 'category' in df.columns:
        df['category_code'] = df['category'].astype('category').cat.codes
    # Drop rows with missing essential info
    df = df.dropna(subset=['lat', 'lng', 'category', 'month'])
    # Reset index
    df = df.reset_index(drop=True)
    return df

cleaned_df = clean_crime_data(crimes_df)

# Save cleaned, ML-ready data
output_path = os.path.join(data_dir, 'bristol_crime_ml_ready.csv')
cleaned_df.to_csv(output_path, index=False)
print(f"Cleaned ML-ready data saved to {output_path} ({len(cleaned_df)} rows)")
