# xgboost_forecasting.py
import xgboost as xgb
from sklearn.metrics import mean_squared_error
import numpy as np

def xgboost_forecast(train_data, test_data, exog_train=None, exog_test=None):
    """Trains an XGBoost model and makes predictions."""
    # Convert data to DMatrix format, which is optimized for XGBoost
    dtrain = xgb.DMatrix(train_data, label=train_data)
    dtest = xgb.DMatrix(test_data, label=test_data)

    # Define XGBoost parameters (tune these for optimal performance)
    params = {'objective': 'reg:squarederror', 'max_depth': 3, 'learning_rate': 0.1}
    model = xgb.train(params, dtrain, num_boost_round=100)

    # Make predictions
    preds = model.predict(dtest)
    rmse = np.sqrt(mean_squared_error(test_data, preds))
    print(f"XGBoost RMSE: {rmse}")

    return preds