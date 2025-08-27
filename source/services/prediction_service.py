"""
Prediction Service Layer
Handles business logic for cryptocurrency predictions
"""
import logging
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import os

from source.models.arimax_forecast import arimax_forecast
from source.models.xgboost_forecast import xgboost_forecast
from source.api_schemas import PredictionRequest, PredictionResponse, create_error_response

logger = logging.getLogger(__name__)

class PredictionService:
    """Service class for handling prediction requests"""
    
    def __init__(self):
        self.supported_models = {
            'arimax': self._run_arimax_prediction,
            'xgboost': self._run_xgboost_prediction
        }
    
    def get_prediction(self, request: PredictionRequest) -> PredictionResponse:
        """
        Get predictions based on the request parameters
        
        Args:
            request: PredictionRequest object with validated parameters
            
        Returns:
            PredictionResponse object with results or error
        """
        try:
            logger.info(f"Starting prediction for {request.symbol} using {request.model} model")
            
            # Validate request
            errors = request.validate()
            if errors:
                error_msg = "; ".join(errors)
                logger.error(f"Validation errors: {error_msg}")
                return PredictionResponse(
                    success=False,
                    predictions=[],
                    metrics={},
                    model_used=request.model,
                    symbol=request.symbol,
                    currency=request.currency,
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )
            
            # Check if data file exists
            file_path = f'data/crypto_data_{request.symbol}_{request.currency}_30d.csv'
            if not os.path.exists(file_path):
                error_msg = f"Data file not found for {request.symbol}/{request.currency}. Please fetch data first."
                logger.error(error_msg)
                return PredictionResponse(
                    success=False,
                    predictions=[],
                    metrics={},
                    model_used=request.model,
                    symbol=request.symbol,
                    currency=request.currency,
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )
            
            # Run prediction
            if request.model not in self.supported_models:
                error_msg = f"Unsupported model: {request.model}"
                logger.error(error_msg)
                return PredictionResponse(
                    success=False,
                    predictions=[],
                    metrics={},
                    model_used=request.model,
                    symbol=request.symbol,
                    currency=request.currency,
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )
            
            predictions, metrics = self.supported_models[request.model](file_path)
            
            # Format predictions
            formatted_predictions = self._format_predictions(predictions, request.steps)
            
            logger.info(f"Successfully generated predictions for {request.symbol} using {request.model}")
            
            return PredictionResponse(
                success=True,
                predictions=formatted_predictions,
                metrics=metrics,
                model_used=request.model,
                symbol=request.symbol,
                currency=request.currency,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            error_msg = f"Error generating predictions: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return PredictionResponse(
                success=False,
                predictions=[],
                metrics={},
                model_used=request.model,
                symbol=request.symbol,
                currency=request.currency,
                timestamp=datetime.now().isoformat(),
                error=error_msg
            )
    
    def _run_arimax_prediction(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Run ARIMAX prediction"""
        logger.info(f"Running ARIMAX prediction on {file_path}")
        return arimax_forecast(file_path)
    
    def _run_xgboost_prediction(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Run XGBoost prediction"""
        logger.info(f"Running XGBoost prediction on {file_path}")
        return xgboost_forecast(file_path)
    
    def _format_predictions(self, predictions_df: pd.DataFrame, steps: int) -> list:
        """Format predictions for API response"""
        if predictions_df.empty:
            return []
        
        # Get the last 'steps' predictions
        recent_predictions = predictions_df.tail(steps)
        
        formatted = []
        for _, row in recent_predictions.iterrows():
            formatted.append({
                'time': row['time'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row['time'], 'strftime') else str(row['time']),
                'predicted': float(row['predicted']),
                'actual': float(row['actual']) if 'actual' in row else None
            })
        
        return formatted
    
    def get_available_models(self) -> Dict[str, str]:
        """Get list of available prediction models"""
        return {
            'arimax': 'ARIMAX Time Series Model',
            'xgboost': 'XGBoost Machine Learning Model'
        }
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model"""
        model_info = {
            'arimax': {
                'name': 'ARIMAX',
                'description': 'Autoregressive Integrated Moving Average with Exogenous Variables',
                'type': 'Time Series',
                'best_for': 'Trend analysis and seasonal patterns',
                'parameters': ['p', 'd', 'q', 'exogenous variables']
            },
            'xgboost': {
                'name': 'XGBoost',
                'description': 'Extreme Gradient Boosting',
                'type': 'Machine Learning',
                'best_for': 'Complex patterns and feature relationships',
                'parameters': ['learning_rate', 'max_depth', 'n_estimators']
            }
        }
        
        return model_info.get(model_name)
