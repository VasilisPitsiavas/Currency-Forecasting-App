from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib


def create_lagged_features(data, target_column, lags):
    """
    Create lagged features for a time series dataset.
    """
    for lag in range(1, lags + 1):
        data[f'{target_column}_lag_{lag}'] = data[target_column].shift(lag)

    data = data.dropna().reset_index(drop=True)

    return data


def train_linear_model(data, target_column='USD', lags=3, save_model_path='models/linear_model.pkl'):
    """
    Train a linear regression model for future predictions using lagged features.
    """
    data = create_lagged_features(data, target_column, lags)
    features = [f'{target_column}_lag_{i}' for i in range(1, lags + 1)]
    X = data[features]
    y = data[target_column]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    model_package = {
        'model': model,
        'features': features,
        'lags': lags,
    }
    joblib.dump(model_package, save_model_path)
    print(f"Linear regression model saved to: {save_model_path}")
    return model, model_package
