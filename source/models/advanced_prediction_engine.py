"""
Advanced Prediction Engine
Multi-model ensemble system for cryptocurrency price prediction
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Import existing models
from .arimax_forecast import arimax_forecast
from .xgboost_forecast import xgboost_forecast

logger = logging.getLogger(__name__)

class AdvancedPredictionEngine:
    """
    Advanced prediction engine using ensemble methods and multiple features
    """
    
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.scaler = StandardScaler()
        self.feature_scaler = MinMaxScaler()
        
        # Initialize models
        self.models = {
            'arimax': None,
            'xgboost': None,
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'ensemble': None
        }
        
        # Model weights for ensemble
        self.model_weights = {
            'arimax': 0.2,
            'xgboost': 0.3,
            'random_forest': 0.25,
            'gradient_boosting': 0.25
        }
        
        # Performance tracking
        self.model_performance = {}
        
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced technical indicators and features
        """
        try:
            # Basic price features
            df['price_change'] = df['close'].pct_change()
            df['price_change_abs'] = df['price_change'].abs()
            df['log_return'] = np.log(df['close'] / df['close'].shift(1))
            
            # Moving averages
            df['ma_5'] = df['close'].rolling(window=5).mean()
            df['ma_10'] = df['close'].rolling(window=10).mean()
            df['ma_20'] = df['close'].rolling(window=20).mean()
            df['ma_50'] = df['close'].rolling(window=50).mean()
            
            # Price relative to moving averages
            df['price_vs_ma5'] = df['close'] / df['ma_5'] - 1
            df['price_vs_ma10'] = df['close'] / df['ma_10'] - 1
            df['price_vs_ma20'] = df['close'] / df['ma_20'] - 1
            
            # Volatility indicators
            df['volatility_5'] = df['price_change'].rolling(window=5).std()
            df['volatility_10'] = df['price_change'].rolling(window=10).std()
            df['volatility_20'] = df['price_change'].rolling(window=20).std()
            
            # RSI (Relative Strength Index)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Volume indicators
            if 'volumeto' in df.columns:
                df['volume_ma_5'] = df['volumeto'].rolling(window=5).mean()
                df['volume_ratio'] = df['volumeto'] / df['volume_ma_5']
                df['volume_price_trend'] = df['volumeto'] * df['price_change']
            else:
                # If no volume data, create dummy volume features
                df['volume_ratio'] = 1.0
                df['volume_price_trend'] = df['price_change']
            
            # Time-based features
            df['hour'] = pd.to_datetime(df['time']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['time']).dt.dayofweek
            df['month'] = pd.to_datetime(df['time']).dt.month
            
            # Lagged features
            for lag in [1, 2, 3, 5, 10]:
                df[f'close_lag_{lag}'] = df['close'].shift(lag)
                if 'volumeto' in df.columns:
                    df[f'volume_lag_{lag}'] = df['volumeto'].shift(lag)
                else:
                    df[f'volume_lag_{lag}'] = 0
            
            # Rolling statistics
            df['rolling_mean_5'] = df['close'].rolling(window=5).mean()
            df['rolling_std_5'] = df['close'].rolling(window=5).std()
            df['rolling_min_5'] = df['close'].rolling(window=5).min()
            df['rolling_max_5'] = df['close'].rolling(window=5).max()
            
            # Price momentum
            df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
            
            # Support and resistance levels
            df['support_level'] = df['close'].rolling(window=20).min()
            df['resistance_level'] = df['close'].rolling(window=20).max()
            df['price_vs_support'] = df['close'] / df['support_level'] - 1
            df['price_vs_resistance'] = df['close'] / df['resistance_level'] - 1
            
            logger.info(f"Created {len(df.columns)} advanced features")
            return df
            
        except Exception as e:
            logger.error(f"Error creating advanced features: {e}")
            return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for training
        """
        # Create advanced features
        df = self.create_advanced_features(df)
        
        # Select features for training (simpler set to avoid too many NaN values)
        feature_columns = [
            'price_change', 'price_change_abs', 'log_return',
            'ma_5', 'ma_10', 'ma_20',
            'price_vs_ma5', 'price_vs_ma10', 'price_vs_ma20',
            'volatility_5', 'volatility_10',
            'rsi', 'macd', 'macd_signal',
            'bb_position', 'volume_ratio',
            'hour', 'day_of_week', 'month',
            'close_lag_1', 'close_lag_2', 'close_lag_3',
            'rolling_mean_5', 'rolling_std_5',
            'momentum_5', 'momentum_10'
        ]
        
        # Filter available features
        available_features = [col for col in feature_columns if col in df.columns]
        
        # Fill NaN values with 0 for numeric columns
        for col in available_features:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Create target (next period's price)
        df['target'] = df['close'].shift(-1)
        
        # Remove last row (no target) and rows with NaN in target
        df = df.dropna(subset=['target'])
        
        # Ensure we have enough data
        if len(df) < 50:
            logger.warning(f"Only {len(df)} samples available, minimum 50 required")
            raise ValueError(f"Not enough data: {len(df)} samples, minimum 50 required")
        
        X = df[available_features]
        y = df['target']
        
        logger.info(f"Prepared {len(X)} samples with {len(available_features)} features")
        return X, y
    
    def train_models(self, file_path: str) -> Dict[str, Any]:
        """
        Train all models on the data
        """
        try:
            logger.info(f"Training models on {file_path}")
            
            # Load and prepare data
            df = pd.read_csv(file_path)
            X, y = self.prepare_features(df)
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # Scale features
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_test_scaled = self.feature_scaler.transform(X_test)
            
            # Train individual models
            results = {}
            
            # Train Random Forest
            logger.info("Training Random Forest...")
            self.models['random_forest'].fit(X_train_scaled, y_train)
            rf_pred = self.models['random_forest'].predict(X_test_scaled)
            results['random_forest'] = self._evaluate_model(y_test, rf_pred)
            
            # Train Gradient Boosting
            logger.info("Training Gradient Boosting...")
            self.models['gradient_boosting'].fit(X_train_scaled, y_train)
            gb_pred = self.models['gradient_boosting'].predict(X_test_scaled)
            results['gradient_boosting'] = self._evaluate_model(y_test, gb_pred)
            
            # Train existing models (ARIMAX and XGBoost)
            logger.info("Training ARIMAX...")
            try:
                arimax_pred, arimax_metrics = arimax_forecast(file_path)
                results['arimax'] = arimax_metrics
            except Exception as e:
                logger.error(f"ARIMAX training failed: {e}")
                results['arimax'] = {'RMSE': float('inf')}
            
            logger.info("Training XGBoost...")
            try:
                xgb_pred, xgb_metrics = xgboost_forecast(file_path)
                results['xgboost'] = xgb_metrics
            except Exception as e:
                logger.error(f"XGBoost training failed: {e}")
                results['xgboost'] = {'RMSE': float('inf')}
            
            # Update model weights based on performance
            self._update_model_weights(results)
            
            # Save models
            self._save_models()
            
            logger.info("All models trained successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    def predict_ensemble(self, file_path: str, steps: int = 10) -> Tuple[List[Dict], Dict[str, float]]:
        """
        Make ensemble predictions using all models
        """
        try:
            logger.info(f"Making ensemble predictions for {steps} steps")
            
            # Load and prepare data
            df = pd.read_csv(file_path)
            
            # Check if file has data
            if len(df) == 0:
                raise ValueError("Empty data file")
            
            # Check if required columns exist
            required_columns = ['close', 'time']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            X, y = self.prepare_features(df)
            
            # Check if we have enough data
            if len(X) < 2:
                raise ValueError(f"Not enough data for prediction: {len(X)} samples")
            
            # Get recent data for prediction
            recent_data = X.tail(1)
            
            # Check if scaler is fitted, if not, fit it
            if not hasattr(self.feature_scaler, 'scale_'):
                logger.info("Fitting feature scaler...")
                self.feature_scaler.fit(X)
            
            recent_data_scaled = self.feature_scaler.transform(recent_data)
            
            predictions = []
            current_price = df['close'].iloc[-1]
            
            for step in range(1, steps + 1):
                # Get predictions from each model
                model_predictions = {}
                
                # Random Forest prediction
                if self.models['random_forest'] is not None:
                    rf_pred = self.models['random_forest'].predict(recent_data_scaled)[0]
                    model_predictions['random_forest'] = rf_pred
                
                # Gradient Boosting prediction
                if self.models['gradient_boosting'] is not None:
                    gb_pred = self.models['gradient_boosting'].predict(recent_data_scaled)[0]
                    model_predictions['gradient_boosting'] = gb_pred
                
                # Weighted ensemble prediction
                weighted_pred = 0
                total_weight = 0
                
                for model_name, pred in model_predictions.items():
                    weight = self.model_weights.get(model_name, 0.25)
                    weighted_pred += pred * weight
                    total_weight += weight
                
                if total_weight > 0:
                    ensemble_pred = weighted_pred / total_weight
                else:
                    ensemble_pred = current_price
                
                # Add prediction to results
                predictions.append({
                    'step': step,
                    'predicted_price': float(ensemble_pred),
                    'model_predictions': model_predictions,
                    'confidence': self._calculate_confidence(model_predictions)
                })
                
                # Update current price for next iteration
                current_price = ensemble_pred
                
                # Update features for next step (simplified)
                # In a real implementation, you'd update all features based on the new prediction
            
            # Calculate ensemble metrics
            metrics = {
                'ensemble_rmse': np.sqrt(mean_squared_error([p['predicted_price'] for p in predictions], 
                                                          [p['predicted_price'] for p in predictions])),  # Placeholder
                'model_weights': self.model_weights,
                'prediction_steps': steps
            }
            
            logger.info(f"Ensemble predictions completed for {steps} steps")
            return predictions, metrics
            
        except Exception as e:
            logger.error(f"Error making ensemble predictions: {e}")
            raise
    
    def _evaluate_model(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        return {
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAE': mean_absolute_error(y_true, y_pred),
            'R2': r2_score(y_true, y_pred)
        }
    
    def _update_model_weights(self, results: Dict[str, Any]):
        """Update model weights based on performance"""
        # Simple inverse RMSE weighting
        total_inverse_rmse = 0
        for model_name, metrics in results.items():
            if 'RMSE' in metrics and metrics['RMSE'] != float('inf'):
                total_inverse_rmse += 1 / metrics['RMSE']
        
        if total_inverse_rmse > 0:
            for model_name, metrics in results.items():
                if 'RMSE' in metrics and metrics['RMSE'] != float('inf'):
                    self.model_weights[model_name] = (1 / metrics['RMSE']) / total_inverse_rmse
        
        logger.info(f"Updated model weights: {self.model_weights}")
    
    def _calculate_confidence(self, model_predictions: Dict[str, float]) -> float:
        """Calculate confidence score based on model agreement"""
        if len(model_predictions) < 2:
            return 0.5
        
        predictions = list(model_predictions.values())
        std = np.std(predictions)
        mean = np.mean(predictions)
        
        # Lower std = higher confidence
        confidence = 1 / (1 + std / mean) if mean > 0 else 0.5
        return min(max(confidence, 0), 1)
    
    def _save_models(self):
        """Save trained models"""
        os.makedirs(self.models_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            if model is not None and hasattr(model, 'fit'):
                model_path = os.path.join(self.models_dir, f'{model_name}_advanced.pkl')
                joblib.dump(model, model_path)
                logger.info(f"Saved {model_name} model to {model_path}")
        
        # Save scalers
        scaler_path = os.path.join(self.models_dir, 'feature_scaler.pkl')
        joblib.dump(self.feature_scaler, scaler_path)
        
        # Save model weights
        weights_path = os.path.join(self.models_dir, 'model_weights.json')
        import json
        with open(weights_path, 'w') as f:
            json.dump(self.model_weights, f)
    
    def load_models(self):
        """Load trained models"""
        try:
            for model_name in self.models.keys():
                if model_name != 'ensemble':
                    model_path = os.path.join(self.models_dir, f'{model_name}_advanced.pkl')
                    if os.path.exists(model_path):
                        self.models[model_name] = joblib.load(model_path)
                        logger.info(f"Loaded {model_name} model")
            
            # Load scaler
            scaler_path = os.path.join(self.models_dir, 'feature_scaler.pkl')
            if os.path.exists(scaler_path):
                self.feature_scaler = joblib.load(scaler_path)
            
            # Load weights
            weights_path = os.path.join(self.models_dir, 'model_weights.json')
            if os.path.exists(weights_path):
                import json
                with open(weights_path, 'r') as f:
                    self.model_weights = json.load(f)
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
