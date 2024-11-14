import requests
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
import os
from source.data_processing import load_and_process_data

def fetch_historical_data(api_key, symbol='ETH', currency='USD', aggregate=10, limit=2000, days_back=30):
    """
    Fetches historical minute data of a cryptocurrency from the specified time range.
    
    """
    
    to_timestamp = int(datetime.now(timezone.utc).timestamp())
    from_timestamp = int((datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp())

    print(f"Fetching data from {datetime.utcfromtimestamp(from_timestamp)} to {datetime.utcfromtimestamp(to_timestamp)}")

    url = 'https://min-api.cryptocompare.com/data/v2/histominute'
    
    params = {
        'fsym': symbol,
        'tsym': currency,
        'limit': limit,
        'aggregate': aggregate,
        'toTs': to_timestamp,
        'e': 'CCCAGG',  
        'api_key': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical data: {e}")
        return None

    data = response.json().get('Data', {}).get('Data', [])
    if not data:
        print("No data found. The time range might be too large or the API might not support it.")
        return None

    save_to_json(data, f'historical_data_{symbol}_{currency}_{aggregate}min_{days_back}d.json')

    print(data)

    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert timestamps to datetime

    return df

def fetch_current_price(api_key, symbol='ETH', currency='USD'):
    """
    Fetches the current price of a cryptocurrency.
    
    """
    url = 'https://min-api.cryptocompare.com/data/price'
    params = {
        'fsym': symbol,
        'tsyms': currency,
        'api_key': api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current price: {e}")
        return None

    data = response.json()
    df = load_and_process_data(data)
    save_to_json(df, 'current_price.json')
    
    return data


def save_to_json(data, filename):
    """
    Saves data to a JSON file.

    """
    try:
        print(f"Saving data to: {filename}")
        
        dir_name = os.path.dirname(filename)
        
        if dir_name:
            print(f"Ensuring directory exists: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
        
        if not data:
            print("Warning: No data to save.")
            return  

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
            print(f"Data successfully saved to {filename}")
    
    except Exception as e:
        print(f"Error occurred while saving data to {filename}: {e}")