# app.py
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from source.api import fetch_current_price, fetch_historical_data
from source.models.arimax_forecast import arimax_forecast
from source.models.xgboost_forecast import xgboost_forecast
from source.data_processing import load_and_process_data, save_to_csv
from source.config import API_KEY

def main():
    api_key = API_KEY
    symbol = 'ETH'
    currency = 'USD'
    aggregate = 5
    limit = 2000
    days_back = 100

    # Fetch and process data
    #fetch_data(api_key, symbol, currency, aggregate, limit, days_back)
    df = load_and_process_data('historical_data.json')
    #save_to_csv(df, 'crypto_data.csv')

    csv_file = 'crypto_data.csv'
    model_choice = input("Choose the prediction model (arimax/xgboost): ").strip().lower()
    predictions = run_model(csv_file, model_choice)
    
    query_time = '2024-11-11 15:30:00'
    #extract_current_value(df, query_time)

def fetch_data(api_key, symbol, currency, aggregate, limit, days_back):
    """
    Fetches historical cryptocurrency data and saves it as a JSON file.
    """
    fetch_historical_data(api_key, symbol, currency, aggregate, limit, days_back)
    print("Data fetched and saved as 'historical_data.json'")

def run_model(csv_file, model_choice):
    """
    Runs the chosen model and returns predictions.
    """
    if model_choice == 'arimax':
        print("Running ARIMAX model...")
        arimax_forecast(csv_file)  

        return arimax_forecast(csv_file)
    elif model_choice == 'xgboost':
        print("Running XGBoost model...")
        return xgboost_forecast(csv_file)
    else:
        print("Invalid choice. Please select either 'arimax' or 'xgboost'.")
        return None

def extract_current_value(df, query_time):
    """
    Filters the DataFrame for a specific time and prints the current value (close price) at that time.
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