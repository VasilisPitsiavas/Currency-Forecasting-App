# app.py
import json
import pandas as pd
#import matplotlib.pyplot as plt
from datetime import datetime
from source.api import fetch_historical_data
from flask import Flask, request, jsonify
from source.models.arimax_forecast import arimax_forecast
from source.models.xgboost_forecast import xgboost_forecast
from source.config import API_KEY
from source.api import fetch_historical_data
import os 


app = Flask(__name__)
''' 
def main():
    api_key = API_KEY
    # User inputs for cryptocurrency, currency, and time period
    symbol = input("Enter cryptocurrency symbol (e.g., 'ETH' for Ethereum): ") or 'ETH'
    currency = input("Enter target currency (e.g., 'USD' for US Dollar): ") or 'USD'
    aggregate = int(input("Enter aggregation level (e.g., 5 for 5-minute intervals): ") or 5)
    limit = int(input("Enter the limit for number of data points (default is 2000): ") or 2000)
    days_back = int(input("Enter the number of days to look back for historical data (default is 100): ") or 100)


    # Fetch and process the data
    print(f"Fetching historical data for {symbol} ({currency}) for the past {days_back} days with {aggregate}-minute aggregation.")
    df = fetch_historical_data(api_key, symbol, currency, aggregate, limit, days_back)
    
    if df is not None:
        print(f"Data fetched successfully for {symbol} in {currency}.")
        save_to_csv(df, 'crypto_data1.csv')
    else:
        print(f"Failed to fetch data for {symbol} in {currency}.")
    #csv_file = 'crypto_data.csv'
    #model_choice = input("Choose the prediction model (arimax/xgboost): ").strip().lower()
    #predictions = run_model(csv_file, model_choice)
    
    query_time = '2024-11-11 15:30:00'
    #extract_current_value(df, query_time)
'''

@app.route('/fetch', methods=['GET'])
def fetch_data():
    api_key = API_KEY 
    symbol = request.args.get('symbol', 'ETH')  
    currency = request.args.get('currency', 'USD') 
    aggregate = int(request.args.get('aggregate', 10))
    limit = int(request.args.get('limit', 2000))
    days_back = int(request.args.get('days_back', 30))

    df = fetch_historical_data(api_key, symbol, currency, aggregate, limit, days_back)
    print(f"Fetching data for {symbol} in {currency} with {aggregate}-minute aggregation, {days_back} days back.")

    if df is None:
        return jsonify({'error': 'Unable to fetch data'}), 500

    return df.to_json(orient='records')

''' 
def fetch_data(api_key, symbol, currency, aggregate, limit, days_back):
    """
    Fetches historical cryptocurrency data and saves it as a JSON file.
    """
    fetch_historical_data(api_key, symbol, currency, aggregate, limit, days_back)
    print("Data fetched and saved as 'historical_data.json'")
'''

@app.route('/predict', methods=['GET'])
def predict():
    # Get the query parameters from the URL (with defaults if not provided)
    model_choice = request.args.get('model_choice', 'arimax')  # Default to 'arimax'
    symbol = request.args.get('symbol', 'ETH')  # Default to 'ETH'
    currency = request.args.get('currency', 'USD')  # Default to 'USD'

    csv_file = f'crypto_data_{symbol}_{currency}.csv'

    if not os.path.exists(csv_file):
        return jsonify({'error': f'CSV file {csv_file} not found. Please fetch the data first.'}), 404

    print(f"Using {csv_file} for predictions with model: {model_choice}")

    if model_choice == 'arimax':
        predictions = arimax_forecast(csv_file)  # Run ARIMA model with the saved CSV
        print(predictions)
    elif model_choice == 'xgboost':
        predictions = xgboost_forecast(csv_file)  # Run XGBoost model with the saved CSV
    else:
        return jsonify({'error': 'Invalid model choice. Choose "arimax" or "xgboost".'}), 400

    return jsonify(predictions)

@app.route('/extract_value', methods=['GET'])
def extract_current_value():
    query_time = request.args.get('query_time')
    if not query_time:
        return jsonify({'error': 'query_time parameter is required.'}), 400

    try:
        df = pd.read_csv('crypto_data.csv')
        df['time'] = pd.to_datetime(df['time'])
        query_time = pd.to_datetime(query_time)
        current_value = df[df['time'] == query_time]

        if not current_value.empty:
            close_price = current_value['close'].values[0]
            return jsonify({'time': query_time, 'close': close_price})
        else:
            return jsonify({'error': f'No data found for the time {query_time}'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)

''' 

def run_model(csv_file, model_choice):
    """
    Runs the chosen model and returns predictions.
    """
    if model_choice == 'arimax':
        print("Running ARIMAX model...")
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
'''