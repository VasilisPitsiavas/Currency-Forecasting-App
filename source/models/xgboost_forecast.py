import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error
from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd


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

    cv_splits = min(3, len(X_train))
    print(f"Using {cv_splits} splits for cross-validation.")

    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=cv_splits, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    return best_model


def make_predictions(best_model, X_test):
    """Make predictions using the trained model."""
    return best_model.predict(X_test)


def evaluate_model(y_test, preds):
    """Evaluate the model's performance using RMSE."""
    return np.sqrt(mean_squared_error(y_test, preds))


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
