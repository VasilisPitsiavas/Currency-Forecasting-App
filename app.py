# app.py
import json
import pandas as pd
from datetime import datetime
from source.api import fetch_historical_data
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
from source.models.arimax_forecast import arimax_forecast
from source.models.xgboost_forecast import xgboost_forecast, predict_usd_realtime, train_live_model
from source.config import API_KEY
from source.api import fetch_historical_data, fetch_live_data, preprocess_live_data
from source.plotting import visualize_predictions
import os 
import time
from joblib import load

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch', methods=['GET', 'POST'])
def fetch_data():
    if request.method == 'POST':
        api_key = API_KEY  
        symbol = request.form.get('symbol', 'ETH')
        currency = request.form.get('currency', 'USD')
        aggregate = int(request.form.get('aggregate', 10))
        limit = int(request.form.get('limit', 2000))
        days_back = int(request.form.get('days_back', 30))

        df = fetch_historical_data(api_key, symbol, currency, aggregate, limit, days_back)
        print(f"Fetching data for {symbol} in {currency} with {aggregate}-minute aggregation, {days_back} days back.")

        if df is None or df.empty:
            return jsonify({"error": "No data available for the specified range."}), 400

        try:
            data = df.to_dict(orient='records')
            return render_template('display_data.html', data=data, symbol=symbol, currency=currency)
        except Exception as e:
            print(f"Error converting DataFrame to JSON: {e}")
            return jsonify({"error": "Failed to process data."}), 500

    return render_template('fetch_form.html')

@app.route('/predict', methods=['GET'])
def predict():
    model_choice = request.args.get('model_choice', 'arimax')  
    symbol = request.args.get('symbol', 'ETH')  
    currency = request.args.get('currency', 'USD')  

    csv_file = f'crypto_data_{symbol}_{currency}.csv'
    if not os.path.exists(csv_file):
        return jsonify({'error': f'CSV file {csv_file} not found. Please fetch the data first.'}), 404

    print(f"Using {csv_file} for predictions with model: {model_choice}")

    if model_choice == 'arimax':
        predictions, metrics = arimax_forecast(csv_file)
    elif model_choice == 'xgboost':
        predictions, metrics = xgboost_forecast(csv_file)
    else:
        return jsonify({'error': 'Invalid model choice. Choose "arimax" or "xgboost".'}), 400

    if predictions.empty:
        return jsonify({'error': 'The model returned no predictions. Check the data or model configuration.'}), 400

    predictions['time'] = predictions['time'].dt.strftime('%Y-%m-%d %H:%M:%S') 

    predictions_list = predictions.to_dict(orient='records')

    #For debug reasons
    #prediction_data = [
    #    {'time': '2024-11-15 12:20:00', 'actual': 3105.68, 'predicted': 3109.61},
    #    {'time': '2024-11-15 12:30:00', 'actual': 3095.33, 'predicted': 3097.44},
    #    {'time': '2024-11-15 12:40:00', 'actual': 3102.1, 'predicted': 3097.04}
    #]

    #print(predictions_list[:5])


    return render_template('predictions.html', model_choice=model_choice, predictions=predictions_list, metrics=metrics)

@app.route('/realtime', methods=['GET'])
def realtime():
    return render_template('realtime.html')

@app.route('/stream_realtime', methods=['GET'])
def stream_realtime():
    api_key = API_KEY    
    symbol = request.args.get('symbol', 'ETH')
    currency = request.args.get('currency', 'USD')
    model_path = 'models/usd_only_xgboost_model.pkl'

    if not os.path.exists(model_path):
        print(f"USD-only model not found at {model_path}. Training a new model...")
        train_live_model(
            file_path=f'crypto_data_{symbol}_{currency}.csv', 
            target_column='close',
            save_model_path=model_path
        )

    def generate():
        for live_data in fetch_live_data(api_key, symbol=symbol, currency=currency, interval=5):
            try:
                print(f"Live data received: {live_data}")

                prediction = predict_usd_realtime(model_path=model_path, live_data=live_data)
                live_data['prediction'] = prediction

                yield f"data: {json.dumps(live_data)}\n\n"
            except ValueError as e:
                print(f"Prediction Error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            except Exception as e:
                print(f"Unexpected Error: {e}")
                yield f"data: {json.dumps({'error': 'Unexpected error during prediction'})}\n\n"
            finally:
                time.sleep(1)

    return Response(stream_with_context(generate()), content_type='text/event-stream')

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

