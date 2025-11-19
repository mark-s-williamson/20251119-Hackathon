import pandas as pd

STRATHSPEY_COLUMNS = {
    'date':pd.Timestamp,
    'temp_mean': str,
    'temp_min': str,
    'temp_max': str,
    'rain_mm': str,
    'pressure_early': int,
    'pressure_late': int,
    'wind_mean':float,
    'wind_max':float,
    'wind_dir':str,
    'sun_hours': float
}

