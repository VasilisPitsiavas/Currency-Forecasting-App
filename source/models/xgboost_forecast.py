import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd
from source.plotting import plot_actual_vs_predicted, plot_forecast_comparison


def create_lagged_features(df, target_column, lags=[1, 2, 3]):
    """Creates lagged features for the dataset."""
    for lag in lags:
        df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
    return df

def xgboost_forecast(file_path, target_column='close', lags=[1, 2, 3]):
    """
    Trains an XGBoost model, performs grid search for hyperparameters,
    and makes predictions.

    :param file_path: Path to the CSV file containing the data.
    :param target_column: The column name of the target variable (default is 'close').
    :param lags: List of lag values to create lagged features (default is [1, 2, 3]).
    :return: Predictions for the test data.
    """
    
    df = pd.read_csv(file_path)

    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)

    df = create_lagged_features(df, target_column, lags)

    df.dropna(inplace=True)

    X = df.drop(columns=[target_column])
    y = df[target_column]

    train_size = int(len(df) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    model = xgb.XGBRegressor(objective='reg:squarederror')

    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'n_estimators': [100, 200],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }

    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_

    preds = best_model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"XGBoost RMSE: {rmse}")

    #print(preds)
     # Plot the actual vs predicted values
    #plot_actual_vs_predicted(y_test, preds)

    # Plot the forecast comparison (actual vs forecasted)
    plot_forecast_comparison(df, preds)
    return preds