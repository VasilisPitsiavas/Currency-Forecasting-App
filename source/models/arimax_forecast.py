import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error
from itertools import product
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")  

def load_data(file_path):
    """Load time series data from a CSV file."""
    data = pd.read_csv(file_path, parse_dates=['time'], index_col='time')
    return data

def preprocess_data(data):
    """Prepare target and exogenous variables for ARIMAX model."""
    target = data['close']
    exog = data[['volumefrom', 'volumeto', 'high', 'low']]
    return target, exog

def split_data(target, exog, train_ratio=0.8):
    """
    Split target and exogenous variables into train and test sets.

    Ensures test_target and test_exog have the same length, using slicing.
    """
    split_idx = int(len(target) * train_ratio)
    
    train_target = target.iloc[:split_idx]
    test_target = target.iloc[split_idx:]
    train_exog = exog.iloc[:split_idx]
    test_exog = exog.iloc[split_idx:]
    
    if len(test_target) != len(test_exog):
        print(f"Warning: Test target length ({len(test_target)}) and test exog length ({len(test_exog)}) differ!")
        min_length = min(len(test_target), len(test_exog))
        test_target = test_target.iloc[:min_length]
        test_exog = test_exog.iloc[:min_length]
    
    return train_target, test_target, train_exog, test_exog

def grid_search_arimax(train_target, train_exog, p_range=(0, 2), d_range=(0, 2), q_range=(0, 2)):
    """Perform grid search to find the best ARIMAX(p, d, q) parameters."""
    best_rmse = float("inf")
    best_order = None
    
    for p, d, q in product(range(*p_range), range(*d_range), range(*q_range)):
        try:
            model = ARIMA(train_target, exog=train_exog, order=(p, d, q))
            model_fit = model.fit()
            
            train_pred = model_fit.predict(start=train_target.index[0], end=train_target.index[-1], exog=train_exog)
            rmse = np.sqrt(mean_squared_error(train_target, train_pred))
            
            if rmse < best_rmse:
                best_rmse = rmse
                best_order = (p, d, q)
        except Exception as e:
            continue 
    return best_order

def fit_arimax_model(train_target, train_exog, order):
    """Fit the ARIMAX model using the best order from grid search."""
    model = ARIMA(train_target, exog=train_exog, order=order)
    model_fit = model.fit()
    return model_fit

def make_predictions(model_fit, test_exog):
    """Make predictions using the fitted ARIMAX model."""
    predictions = model_fit.forecast(steps=len(test_exog), exog=test_exog[-len(test_exog):])
    return predictions

def evaluate_model(test_target, predictions):
    """Evaluate the model using RMSE metric."""
    rmse = np.sqrt(mean_squared_error(test_target, predictions))
    return rmse

def plot_results(test_target, predictions):
    """Plot the actual vs predicted values."""
    plt.figure(figsize=(12, 6))
    plt.plot(test_target.index, test_target, label="Actual", color="blue")
    plt.plot(test_target.index, predictions, label="Predicted", color="red")
    plt.xlabel("Time")
    plt.ylabel("Close Price")
    plt.title("ARIMAX Model Predictions")
    plt.legend()
    plt.show()

def arimax_forecast(file_path):
    data = load_data(file_path)
    target, exog = preprocess_data(data)
    
    train_target, test_target, train_exog, test_exog = split_data(target, exog)
    
    best_order = grid_search_arimax(train_target, train_exog, p_range=(0, 3), d_range=(0, 2), q_range=(0, 3))
    print(f"Best ARIMA order: {best_order}")
    
    arimax_model = fit_arimax_model(train_target, train_exog, order=best_order)
    
    predictions = make_predictions(arimax_model, test_exog)
    
    error = evaluate_model(test_target, predictions)
    mse = mean_squared_error(test_target, predictions)
    mae = mean_absolute_error(test_target, predictions)
    mdae = median_absolute_error(test_target, predictions)
    print(f'RMSE: {error}')

    metrics = {
        "RMSE": error,
        "MSE": mse,
        "MAE": mae,
        "MdAE": mdae  
    }
    #predictions_list = predictions.tolist()

    #print("Length of predictions:", len(predictions))
    #print("Length of actual values:", len(test_exog))
    #print("Length of timestamps:", len(test_exog))

    
    
    result = pd.DataFrame({
        'time': test_target.index,
        'actual': test_target.values,
        'predicted': predictions
    })
   
    result.to_csv('arima_predictions.csv', index=False)
    
    return result, metrics