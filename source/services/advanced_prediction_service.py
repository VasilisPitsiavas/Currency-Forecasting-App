"""
Advanced Prediction Service
Service layer for the advanced prediction engine
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from source.models.advanced_prediction_engine import AdvancedPredictionEngine
from source.api import fetch_historical_data
from source.api_schemas import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)

class AdvancedPredictionService:
    """Service for advanced prediction engine"""
    
    def __init__(self):
        self.engine = AdvancedPredictionEngine()
        self.models_dir = 'models'
        
    def train_advanced_models(self, symbol: str, currency: str = 'USD') -> Dict[str, Any]:
        """Train all advanced models for a symbol"""
        try:
            file_path = f'data/crypto_data_{symbol}_{currency}_30d.csv'
            
            if not os.path.exists(file_path):
                logger.info(f"Data file not found, fetching data for {symbol}/{currency}")
                
                # Fetch data
                api_key = os.getenv('CRYPTOCOMPARE_API_KEY', 'demo')
                data = fetch_historical_data(api_key, symbol, currency, limit=200)
                
                if data is None or len(data) == 0:
                    raise ValueError(f"Failed to fetch data for {symbol}/{currency}")
                
                logger.info(f"Successfully fetched {len(data)} data points")
            
            logger.info(f"Training advanced models for {symbol}/{currency}")
            results = self.engine.train_models(file_path)
            
            return {
                'success': True,
                'symbol': symbol,
                'currency': currency,
                'training_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training advanced models: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_advanced_predictions(self, request: PredictionRequest) -> PredictionResponse:
        """Get advanced ensemble predictions"""
        try:
            file_path = f'data/crypto_data_{request.symbol}_{request.currency}_30d.csv'
            
            if not os.path.exists(file_path):
                return PredictionResponse(
                    success=False,
                    predictions=[],
                    metrics={},
                    model_used='ensemble',
                    symbol=request.symbol,
                    currency=request.currency,
                    timestamp=datetime.now().isoformat(),
                    error=f"Data file not found for {request.symbol}/{request.currency}"
                )
            
            # Load models if not already loaded
            try:
                self.engine.load_models()
            except:
                logger.info("No pre-trained models found, training new models...")
                self.engine.train_models(file_path)
            
            # Get ensemble predictions
            predictions, metrics = self.engine.predict_ensemble(file_path, request.steps)
            
            # Format predictions for API response
            formatted_predictions = []
            for pred in predictions:
                formatted_predictions.append({
                    'step': pred['step'],
                    'predicted_price': pred['predicted_price'],
                    'confidence': pred['confidence'],
                    'model_breakdown': pred['model_predictions']
                })
            
            return PredictionResponse(
                success=True,
                predictions=formatted_predictions,
                metrics=metrics,
                model_used='ensemble',
                symbol=request.symbol,
                currency=request.currency,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting advanced predictions: {e}")
            return PredictionResponse(
                success=False,
                predictions=[],
                metrics={},
                model_used='ensemble',
                symbol=request.symbol,
                currency=request.currency,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def get_model_performance(self, symbol: str, currency: str = 'USD') -> Dict[str, Any]:
        """Get performance metrics for all models"""
        try:
            file_path = f'data/crypto_data_{symbol}_{currency}_30d.csv'
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f"Data file not found for {symbol}/{currency}"
                }
            
            # Train models and get performance
            results = self.engine.train_models(file_path)
            
            return {
                'success': True,
                'symbol': symbol,
                'currency': currency,
                'model_performance': results,
                'model_weights': self.engine.model_weights,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
