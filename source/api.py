# api.py
import requests
import pandas as pd
import json
from datetime import datetime, timedelta, timezone

def fetch_historical_data(api_key, symbol='ETH', currency='USD', aggregate=10, limit=2000, days_back=30):
    """
    Fetches historical minute data of a cryptocurrency from the specified time range.
    
    :param api_key: The API key for CryptoCompare.
    :param symbol: The symbol of the cryptocurrency (e.g., 'ETH' for Ethereum).
    :param currency: The target currency (e.g., 'USD').
    :param aggregate: The aggregation level for the data (e.g., 10 minutes).
    :param limit: The number of data points to return.
    :param days_back: The number of days to look back for historical data.
    :return: A pandas DataFrame containing the historical data.
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
        'e': 'CCCAGG',  # Data source
        'api_key': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()['Data']['Data']
        if not data:
            print("No data found. The time range might be too large or the API might not support it.")
        save_to_json(data, 'historical_data.json')  # Save to JSON file
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert timestamps to datetime
        return df[['time', 'close']]
    else:
        print(f"Error fetching historical data: {response.status_code} - {response.text}")
        return None


def fetch_current_price(api_key, symbol='ETH', currency='USD'):
    """
    Fetches the current price of a cryptocurrency.
    
    :param api_key: The API key for CryptoCompare.
    :param symbol: The symbol of the cryptocurrency (e.g., 'ETH' for Ethereum).
    :param currency: The target currency (e.g., 'USD').
    :return: A dictionary containing the current price data.
    """
    url = 'https://min-api.cryptocompare.com/data/price'
    params = {
        'fsym': symbol,
        'tsyms': currency,
        'api_key': api_key
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        save_to_json(data, 'current_price.json')  
        return data
    else:
        print(f"Error fetching current price: {response.status_code}")
        return None

def save_to_json(data, filename):
    """
    Saves data to a JSON file.
    
    :param data: The data to be saved.
    :param filename: The name of the file where the data will be saved.
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4) 