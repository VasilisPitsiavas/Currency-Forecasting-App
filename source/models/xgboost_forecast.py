import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error
from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd
import joblib 
import os
import json


def load_data(file_path):
    """Load time series data from a CSV file."""
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    return df


def preprocess_data(data, target_column, additional_features):
    """
    Prepare target and feature variables for model training without lagging.
    """
    required_columns = [target_column] + additional_features
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in the dataset: {missing_columns}")

    target = data[target_column]
    features = data[additional_features]
    
    if target.isnull().any() or features.isnull().any().any():
        print("Warning: Missing data detected! Dropping NaN rows.")
        data = data.dropna(subset=required_columns)

    return features, target

def create_lagged_features(data, target_column, lags):
    """
    Create lagged features for the target column.
    """
    for lag in range(1, lags + 1):
        data[f'{target_column}_lag_{lag}'] = data[target_column].shift(lag)
    data.dropna(inplace=True)
    return data

def split_data(features, target, train_ratio=0.8):
    """
    Split target and feature variables into train and test sets.
    """
    if len(target) < 2:
        print("Dataset too small for splitting. Using entire dataset for training.")
        return features, features, target, target

    split_idx = max(1, int(len(target) * train_ratio))  # Ensure at least one training sample
    print(f"Split index: {split_idx}, Total rows: {len(target)}")

    X_train = features.iloc[:split_idx]
    X_test = features.iloc[split_idx:]
    y_train = target.iloc[:split_idx]
    y_test = target.iloc[split_idx:]

    print(f"Train samples: {len(y_train)}, Test samples: {len(y_test)}")
    print(f"Train features: {X_train.shape}, Test features: {X_test.shape}")

    return X_train, X_test, y_train, y_test


def grid_search_xgboost(X_train, y_train):
    """Perform grid search for hyperparameter tuning."""
    model = xgb.XGBRegressor(objective='reg:squarederror')

    param_grid = {
        'max_depth': [3],
        'learning_rate': [0.1],
        'n_estimators': [100],
        'objective': ['reg:squarederror'],
        'random_state': [42]
    }

    if len(X_train) < 2: 
        print("Training data too small for cross-validation. Training without CV.")
        model.fit(X_train, y_train)
        return model

    cv_splits = min(3, len(X_train))  
    print(f"Using {cv_splits} splits for cross-validation.")

    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=cv_splits, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)

    return grid_search.best_estimator_


def make_predictions(best_model, X_test):
    """Make predictions using the trained model."""
    return best_model.predict(X_test)


def evaluate_model(y_test, preds):
    """Evaluate the model's performance using RMSE."""
    return np.sqrt(mean_squared_error(y_test, preds))

def train_live_model(data_dir=None, file_path=None, symbol='USD', target_column='close', train_ratio=0.8, save_model_path=None, lags=1):
    """
    Train an XGBoost model using lagged features for the specified target column.
    Can train using a single file or multiple files in a directory.
    """
    # Load data from a directory or a single file
    if data_dir:
        all_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv') and symbol in f]
        combined_data = pd.DataFrame()
        for file in all_files:
            try:
                df = load_data(file)
                combined_data = pd.concat([combined_data, df], ignore_index=True)
            except Exception as e:
                print(f"Error reading file {file}: {e}")
        if combined_data.empty:
            raise ValueError(f"No data found in directory: {data_dir} for symbol: {symbol}")
        data = combined_data
    elif file_path:
        data = load_data(file_path)
    else:
        raise ValueError("Either 'data_dir' or 'file_path' must be provided.")

    # Prepare data
    data.rename(columns={target_column: 'USD'}, inplace=True)
    data = create_lagged_features(data, target_column='USD', lags=lags)

    # Define features and target
    features = data[[f'USD_lag_{i}' for i in range(1, lags + 1)]]
    target = data['USD']

    # Split data
    X_train, X_test, y_train, y_test = split_data(features, target, train_ratio=train_ratio)

    # Train model
    best_model = grid_search_xgboost(X_train, y_train)

    # Save model and metadata
    if save_model_path:
        os.makedirs(os.path.dirname(save_model_path), exist_ok=True)
        model_package = {
            'model': best_model,
            'features': [f'USD_lag_{i}' for i in range(1, lags + 1)],
            'lags': lags,
        }
        joblib.dump(model_package, save_model_path)
        print(f"Trained model saved to: {save_model_path}")

    # Make predictions and calculate metrics
    predictions = make_predictions(best_model, X_test)
    metrics = {
        "RMSE": evaluate_model(y_test, predictions),
        "MSE": mean_squared_error(y_test, predictions),
        "MAE": mean_absolute_error(y_test, predictions),
        "MdAE": median_absolute_error(y_test, predictions),
    }

    return predictions, metrics

def xgboost_forecast(file_path, target_column='close', train_ratio=0.8):
    """
    Forecast using XGBoost without creating lagged features.
    """
    data = load_data(file_path)
    print(f"Columns in dataset: {data.columns}")
    print(f"Loaded data shape: {data.shape}")

    additional_features = ['volumefrom', 'volumeto', 'high', 'low']

    features, target = preprocess_data(data, target_column, additional_features)

    X_train, X_test, y_train, y_test = split_data(features, target, train_ratio=train_ratio)

    best_model = grid_search_xgboost(X_train, y_train)
    predictions = make_predictions(best_model, X_test)

    ''' 
    if save_model_path:
        os.makedirs(os.path.dirname(save_model_path), exist_ok=True)
        joblib.dump(best_model, save_model_path)
        print(f"Trained model saved to: {save_model_path}")
    '''

    rmse = evaluate_model(y_test, predictions)
    print(f"XGBoost RMSE: {rmse}")

    error = evaluate_model(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    mdae = median_absolute_error(y_test, predictions)
    print(f'RMSE: {error}')

    metrics = {
        "RMSE": error,
        "MSE": mse,
        "MAE": mae,
        "MdAE": mdae  
    }

    result = pd.DataFrame({
        'time': y_test.index,
        'actual': y_test.values,
        'predicted': predictions
    })
    result.to_csv('xgboost_predictions_no_lags.csv', index=False)

    return result, metrics

rolling_buffer = []

def predict_usd_realtime(model_path, live_data, lags=2):
    """
    Predict real-time cryptocurrency values using a pre-trained model with lagged features.
    """
    global rolling_buffer

    model_package = joblib.load(model_path)
    model = model_package['model']
    required_features = model_package['features']

    rolling_buffer.append(live_data['USD'])
    
    if len(rolling_buffer) > lags:
        rolling_buffer = rolling_buffer[-lags:]
    
    if len(rolling_buffer) < lags:
        print(f"Prediction Error: Waiting for enough data to generate lagged features. "
              f"Current buffer size: {len(rolling_buffer)}, Required: {lags}")
        return None

    lagged_features = {f'USD_lag_{i+1}': rolling_buffer[-(i+1)] for i in range(lags)}
    lagged_df = pd.DataFrame([lagged_features])

    # Check if the features match the model's requirements
    if set(lagged_df.columns) != set(required_features):
        raise ValueError(f"Feature shape mismatch, expected: {len(required_features)}, got: {len(lagged_df.columns)}")

    # Make the prediction
    prediction = model.predict(lagged_df.values)
    return float(prediction[0])
    
def train_usd_model_future_steps(file_path, target_column='close', train_ratio=0.8, save_model_path=None, lags=1):
    """
    Train an XGBoost model to predict the next step using lagged features.
    """
    data = load_data(file_path)
    data.rename(columns={target_column: 'USD'}, inplace=True)

    data['USD_target'] = data['USD'].shift(-1)
    data = create_lagged_features(data, target_column='USD', lags=lags)

    data.dropna(inplace=True)

    features = data[[f'USD_lag_{i}' for i in range(1, lags + 1)]]
    target = data['USD_target']

    X_train, X_test, y_train, y_test = split_data(features, target, train_ratio=train_ratio)

    best_model = grid_search_xgboost(X_train, y_train)

    if save_model_path:
        os.makedirs(os.path.dirname(save_model_path), exist_ok=True)
        model_package = {
            'model': best_model,
            'features': [f'USD_lag_{i}' for i in range(1, lags + 1)],
            'lags': lags,
        }
        joblib.dump(model_package, save_model_path)
        print(f"Trained future-step model saved to: {save_model_path}")

    return best_model

    
def predict_usd_next_step(model_path, live_data, previous_values):
    """
    Predict the next USD value based on live data and lagged features.
    """
    try:
        model_package = joblib.load(model_path)
        model = model_package['model']
        required_features = model_package['features']  
        lags = model_package['lags']  

        print(f"Loaded model from: {model_path}")
        print(f"Required features: {required_features}")
        print(f"Lags required: {lags}")

        if len(previous_values) < lags:
            raise ValueError(f"Not enough previous values for prediction. Expected {lags}, got {len(previous_values)}.")

        feature_row = {f'USD_lag_{i+1}': previous_values[-(i+1)] for i in range(lags)}
        live_df = pd.DataFrame([feature_row])

        prediction = model.predict(live_df.values)
        return float(prediction[0])
    except KeyError as e:
        raise ValueError(f"Missing required feature in live data: {e}")
    except Exception as e:
        raise ValueError(f"Prediction error: {e}")
    

def predict_usd_future_step(model_path, live_data, previous_values):
    """
    Predict the future USD value (e.g., 5 minutes ahead) based on live data and lagged features.
    """
    try:
        model_package = joblib.load(model_path)
        model = model_package['model']
        required_features = model_package['features']  

        if len(previous_values) < len(required_features):
            raise ValueError(f"Not enough previous values for prediction. Expected {len(required_features)}, got {len(previous_values)}.")

        feature_row = {f'USD_lag_{i+1}': previous_values[-(i+1)] for i in range(len(required_features))}
        live_df = pd.DataFrame([feature_row])

        prediction = model.predict(live_df.values)
        return float(prediction[0])
    except KeyError as e:
        raise ValueError(f"Missing required feature in live data: {e}")
    except Exception as e:
        raise ValueError(f"Prediction error: {e}")
    
def combine_data_from_directory(data_dir, target_column='close'):
    """
    Combine multiple CSV files from a directory into a single DataFrame.
    
    Args:
        data_dir (str): Path to the directory containing the CSV files.
        target_column (str): The target column to ensure exists in all files.

    Returns:
        pd.DataFrame: A combined DataFrame with data from all CSV files.
    """
    combined_data = []
    
    # Iterate through all files in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):  # Check if the file is a CSV
            file_path = os.path.join(data_dir, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)
                # Check if the target column exists in the file
                if target_column not in df.columns:
                    print(f"Skipping {filename}: Missing target column '{target_column}'")
                    continue
                # Append the data to the list
                combined_data.append(df)
                print(f"Loaded data from {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    # Combine all data into a single DataFrame
    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        # Sort by time column if it exists
        if 'time' in combined_df.columns:
            combined_df['time'] = pd.to_datetime(combined_df['time'], errors='coerce')
            combined_df.sort_values(by='time', inplace=True)
        print("Successfully combined data from all files.")
        return combined_df
    else:
        print("No valid data files found in the directory.")
        return pd.DataFrame()  # Return an empty DataFrame if no data was combined

def train_model_from_directory(data_dir, target_column='close', save_model_path=None, lags=1):
    """
    Combine data from the directory, save it, and train the model.
    """
    # Combine data from the directory
    combined_data = combine_data_from_directory(data_dir, target_column)

    # Save combined data to a temporary CSV file
    combined_file_path = os.path.join(data_dir, 'combined_data.csv')
    combined_data.to_csv(combined_file_path, index=False)
    print(f"Combined data saved to: {combined_file_path}")

    # Call train_live_model with the combined file path
    train_live_model(
        file_path=combined_file_path, 
        target_column=target_column,
        save_model_path=save_model_path,
        lags=lags
    )
