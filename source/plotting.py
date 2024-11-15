import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

def visualize_predictions(result_df):
    plt.figure(figsize=(12, 6))
    plt.plot(result_df['time'], result_df['actual'], label='Actual', color='blue')
    plt.plot(result_df['time'], result_df['predicted'], label='Predicted', color='red')
    plt.xlabel('Minute Intervals')
    plt.ylabel('Cryptocurrency value')
    plt.title('Actual vs Predicted')
    plt.legend()
    plt.grid(True)
    plt.show()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url


def plot_feature_importance(model, features, title="Feature Importance"):
    """
    Plots the feature importance for the XGBoost model.

    """
    import xgboost as xgb
    importance = model.get_booster().get_score(importance_type='weight')
    feature_names = list(importance.keys())
    feature_scores = list(importance.values())
    
    # Sort features by importance
    sorted_idx = sorted(range(len(feature_scores)), key=lambda i: feature_scores[i], reverse=True)
    sorted_feature_names = [feature_names[i] for i in sorted_idx]
    sorted_feature_scores = [feature_scores[i] for i in sorted_idx]
    
    plt.figure(figsize=(10, 6))
    plt.barh(sorted_feature_names, sorted_feature_scores, color='green')
    plt.title(title)
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.show()

def plot_forecast_comparison(df, forecast, title="Forecast Comparison", xlabel="Time", ylabel="Price"):
    """
    Plots the comparison between the actual data and forecasted values.
    
    """
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['close'], label="Actual", color="blue")
    plt.plot(df.index[-len(forecast):], forecast, label="Forecast", color="red", linestyle="--")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()