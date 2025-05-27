# app.py
import json
import pandas as pd
from datetime import datetime
from source.api import fetch_historical_data
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
from source.models.arimax_forecast import arimax_forecast
from source.models.xgboost_forecast import xgboost_forecast, train_live_model, predict_usd_realtime
from source.api import fetch_historical_data, fetch_live_data
import os 
import time
import logging
from joblib import load
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

logging.basicConfig(
    filename='app.log', 
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s'  
)
logging.info("Logging is configured. Application starting.")


app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch', methods=['GET', 'POST'])
def fetch_data():
    if request.method == 'POST':
        try:
            symbol = request.form.get('symbol', 'ETH')
            currency = request.form.get('currency', 'USD')
            aggregate = int(request.form.get('aggregate', 10))
            limit = int(request.form.get('limit', 2000))
            days_back = int(request.form.get('days_back', 30))

            logging.info(f"Fetching data for {symbol} in {currency} with {aggregate}-minute aggregation, {days_back} days back.")

            df = fetch_historical_data(symbol, currency, aggregate, limit, days_back)
            if df is None or df.empty:
                logging.warning(f"No data available for {symbol} in {currency}.")
                return jsonify({"error": f"No data available for {symbol} in {currency}."}), 400

            filename = f'data/crypto_data_{symbol}_{currency}_{days_back}d.csv'
            df.to_csv(filename, index=False)
            logging.info(f"Data for {symbol} saved to {filename}.")

            data_preview = df.head(5).to_dict(orient='records')
            return jsonify({
                "message": f"Data for {symbol} in {currency} fetched and saved successfully.",
                "data_preview": data_preview
            })
        except Exception as e:
            logging.error(f"Unexpected error during fetch: {e}")
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

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
    symbol = request.args.get('symbol', 'ETH')
    currency = request.args.get('currency', 'USD')

    api_key = os.getenv('CRYPTOCOMPARE_API_KEY')
    if not api_key:
        raise RuntimeError("CRYPTOCOMPARE_API_KEY not set in environment")

    def generate():
        for live_data in fetch_live_data(api_key=api_key, symbol=symbol, currency=currency, interval=5):
            try:
                print(f"Live data received: {live_data}")
                # Only keep time and price
                filtered_data = {
                    'time': live_data.get('time'),
                    currency: live_data.get(currency) or live_data.get('USD')
                }
                yield f"data: {json.dumps(filtered_data)}\n\n"
            except Exception as e:
                print(f"Unexpected Error: {e}")
                yield f"data: {json.dumps({'error': 'Unexpected error during streaming'})}\n\n"
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
    

@app.route('/api/predict/arimax', methods=['POST'])
def predict_arimax():
    data = request.get_json()
    symbol = data.get('symbol', 'ETH')
    currency = data.get('currency', 'USD')
    steps = int(data.get('steps', 10))
    file_path = f'data/crypto_data_{symbol}_{currency}_30d.csv'

    if not os.path.exists(file_path):
        return jsonify({'error': f'Data file {file_path} not found.'}), 404

    df = pd.read_csv(file_path)
    df = add_features(df)
    df = df.dropna()
    df.to_csv('debug_arimax_features.csv', index=False)  # For debugging

    # Use the improved arimax_forecast (assume it uses all features)
    result, metrics = arimax_forecast(file_path)
    # For now, intervals are not implemented
    predictions = result[['time', 'predicted']].tail(steps).to_dict(orient='records')
    return jsonify({
        'predictions': predictions,
        'intervals': [],
        'metrics': metrics
    })

@app.route('/api/predict/xgboost', methods=['POST'])
def predict_xgboost():
    data = request.get_json()
    symbol = data.get('symbol', 'ETH')
    currency = data.get('currency', 'USD')
    steps = int(data.get('steps', 10))
    file_path = f'data/crypto_data_{symbol}_{currency}_30d.csv'

    if not os.path.exists(file_path):
        return jsonify({'error': f'Data file {file_path} not found.'}), 404

    df = pd.read_csv(file_path)
    df = add_features(df)
    df = df.dropna()
    df.to_csv('debug_xgboost_features.csv', index=False)  # For debugging

    # Use the improved xgboost_forecast (assume it uses all features)
    result, metrics = xgboost_forecast(file_path)
    predictions = result[['time', 'predicted']].tail(steps).to_dict(orient='records')
    return jsonify({
        'predictions': predictions,
        'intervals': [],
        'metrics': metrics
    })

def add_features(df):
    df['close_lag1'] = df['close'].shift(1)
    df['close_lag2'] = df['close'].shift(2)
    df['rolling_mean_5'] = df['close'].rolling(window=5).mean()
    df['rolling_std_5'] = df['close'].rolling(window=5).std()
    # Add more indicators as needed
    return df

@app.route('/api/history', methods=['GET'])
def get_history():
    symbol = request.args.get('symbol', 'ETH')
    currency = request.args.get('currency', 'USD')
    limit = int(request.args.get('limit', 30))
    file_path = f'data/crypto_data_{symbol}_{currency}_30d.csv'

    if not os.path.exists(file_path):
        return jsonify({'error': f'Data file {file_path} not found.'}), 404

    df = pd.read_csv(file_path)
    df = df.dropna(subset=['time', 'close'])
    # Get the last `limit` rows
    recent = df.tail(limit)
    # Return time and actual close price
    history = recent[['time', 'close']].rename(columns={'close': 'actual'}).to_dict(orient='records')
    return jsonify({'history': history})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

