# app.py
import json
import pandas as pd
from source.api import fetch_current_price, fetch_historical_data
from source.forecast import arimax_forecast
import matplotlib.pyplot as plt
from source.data_processing import load_and_process_data, save_to_csv
from datetime import datetime

def main():
    api_key = 'ff516c6fbb6924b87fe43d32dd038266a4236489c1b7fda5b75e76f22548ba28'
    symbol = 'ETH'
    currency = 'USD'
    aggregate = 5
    limit = 2000
    days_back = 100

    #fetch_historical_data(api_key, symbol, currency, aggregate, limit, days_back)  
    
    json_file = 'historical_data.json' 
    csv_file = '/Users/vasilispitsiavas/Documents/currency-forecasting-app/currency-forecasting-app/crypto_data.csv'
    df = load_and_process_data(json_file)
    #save_to_csv(df, 'crypto_data.csv')
    arimax_forecast(csv_file)
    extract_current_value(df, '2024-11-11 15:30:00')  

def extract_current_value(df, query_time):
    """
    Filters the DataFrame for a specific time and prints the current value (close price) at that time.
    
    :param df: The DataFrame containing the cryptocurrency data.
    :param query_time: The time for which to retrieve the close price (in 'YYYY-MM-DD HH:MM:SS' format).
    """
    df['time'] = pd.to_datetime(df['time'])
    
    query_time = pd.to_datetime(query_time)
    
    current_value = df[df['time'] == query_time]
    
    if not current_value.empty:
        print(f"Current value at {query_time}: {current_value['close'].values[0]}")
    else:
        print(f"No data found for the time {query_time}")

if __name__ == '__main__':
    main()