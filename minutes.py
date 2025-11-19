import numpy as np
import pandas as pd

def estimate_temperature(temp_min, temp_max, hour, minute=0, t_peak=15):
    """
    Estimate temperature at a given hour and minute using sinusoidal model.
    
    Parameters:
    - temp_min: daily minimum temperature
    - temp_max: daily maximum temperature
    - hour: hour of day (0-23)
    - minute: minute of hour (0-59)
    - t_peak: hour of peak temperature (default 15:00)
    
    Returns:
    - Estimated temperature at the given time
    """
    # Convert to decimal hours
    t = hour + minute / 60.0
    
    t_avg = (temp_min + temp_max) / 2
    amplitude = (temp_max - temp_min) / 2
    
    # Sinusoidal model: T(t) = T_avg + A * sin(π(t - t_peak)/12)
    temperature = t_avg + amplitude * np.sin(np.pi * (t - t_peak) / 12)
    
    return temperature

# Create minute-level data for the full year 2012
# Start from midnight on 31 Dec 2011 to midnight on 31 Dec 2012
start_date = pd.Timestamp('2011-12-31 00:00:00')
end_date = pd.Timestamp('2012-12-31 23:59:00')

# Create minute-by-minute timestamps
minute_index = pd.date_range(start=start_date, end=end_date, freq='1min')

print(f"Creating dataset with {len(minute_index)} rows")
print(f"Date range: {minute_index[0]} to {minute_index[-1]}")

# Extract date for merging with daily data
resampled_data = pd.DataFrame({
    'datetime': minute_index,
    'date': minute_index.date,
    'hour': minute_index.hour,
    'minute': minute_index.minute
})

# Merge with daily temperature data
merged_with_temps = resampled_data.merge(
    merged_df[['date', 'temp_min', 'temp_max', 'Location']].drop_duplicates(subset=['date']),
    on='date',
    how='left'
)

# Apply the sinusoidal temperature model
merged_with_temps['estimated_temp'] = merged_with_temps.apply(
    lambda row: estimate_temperature(
        row['temp_min'], 
        row['temp_max'], 
        row['hour'], 
        row['minute']
    ),
    axis=1
)

# Select final columns
final_data = merged_with_temps[['datetime', 'estimated_temp', 'Location']].copy()

print(f"\nFinal dataset shape: {final_data.shape}")
print(f"Expected rows: 527,040")
print(f"Actual rows: {len(final_data)}")
print(f"\nFirst few rows:")
print(final_data.head())
print(f"\nLast few rows:")
print(final_data.tail())
print(f"\nTemperature statistics:")
print(final_data['estimated_temp'].describe())



# Save the resampled data
output_file = 'data/resampled_minute_data.csv'
final_data.to_csv(output_file, index=False)
print(f"Saved resampled data to {output_file}")

# Also save as Excel for easy viewing
output_excel = 'data/resampled_minute_data.xlsx'
final_data.to_excel(output_excel, index=False)
print(f"Saved resampled data to {output_excel}")