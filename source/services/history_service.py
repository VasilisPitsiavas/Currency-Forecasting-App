"""
History Service Layer
Handles business logic for historical cryptocurrency data
"""
import logging
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import os

from source.api_schemas import HistoryRequest, HistoryResponse

logger = logging.getLogger(__name__)

class HistoryService:
    """Service class for handling historical data requests"""
    
    def __init__(self):
        self.data_dir = 'data'
    
    def get_history(self, request: HistoryRequest) -> HistoryResponse:
        """
        Get historical data based on the request parameters
        
        Args:
            request: HistoryRequest object with validated parameters
            
        Returns:
            HistoryResponse object with results or error
        """
        try:
            logger.info(f"Fetching history for {request.symbol} in {request.currency}")
            
            # Validate request
            errors = request.validate()
            if errors:
                error_msg = "; ".join(errors)
                logger.error(f"Validation errors: {error_msg}")
                return HistoryResponse(
                    success=False,
                    history=[],
                    symbol=request.symbol,
                    currency=request.currency,
                    count=0,
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )
            
            # Check if data file exists
            file_path = f'{self.data_dir}/crypto_data_{request.symbol}_{request.currency}_30d.csv'
            if not os.path.exists(file_path):
                error_msg = f"Data file not found for {request.symbol}/{request.currency}. Please fetch data first."
                logger.error(error_msg)
                return HistoryResponse(
                    success=False,
                    history=[],
                    symbol=request.symbol,
                    currency=request.currency,
                    count=0,
                    timestamp=datetime.now().isoformat(),
                    error=error_msg
                )
            
            # Load and process data
            df = pd.read_csv(file_path)
            df = self._clean_data(df)
            
            # Get the requested number of records
            recent_data = df.tail(request.limit)
            
            # Format history
            history = self._format_history(recent_data, request.currency)
            
            logger.info(f"Successfully retrieved {len(history)} history records for {request.symbol}")
            
            return HistoryResponse(
                success=True,
                history=history,
                symbol=request.symbol,
                currency=request.currency,
                count=len(history),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            error_msg = f"Error fetching history: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return HistoryResponse(
                success=False,
                history=[],
                symbol=request.symbol,
                currency=request.currency,
                count=0,
                timestamp=datetime.now().isoformat(),
                error=error_msg
            )
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare the data"""
        # Remove rows with missing values
        df = df.dropna(subset=['time', 'close'])
        
        # Convert time column to datetime
        df['time'] = pd.to_datetime(df['time'])
        
        # Sort by time
        df = df.sort_values('time')
        
        return df
    
    def _format_history(self, df: pd.DataFrame, currency: str) -> List[Dict[str, Any]]:
        """Format historical data for API response"""
        history = []
        
        for _, row in df.iterrows():
            history.append({
                'time': row['time'].strftime('%Y-%m-%d %H:%M:%S'),
                'close': float(row['close']),
                'open': float(row['open']) if 'open' in row else None,
                'high': float(row['high']) if 'high' in row else None,
                'low': float(row['low']) if 'low' in row else None,
                'volume': float(row['volumeto']) if 'volumeto' in row else None
            })
        
        return history
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available cryptocurrency symbols"""
        try:
            if not os.path.exists(self.data_dir):
                return []
            
            symbols = set()
            for filename in os.listdir(self.data_dir):
                if filename.startswith('crypto_data_') and filename.endswith('.csv'):
                    # Extract symbol from filename: crypto_data_SYMBOL_CURRENCY_30d.csv
                    parts = filename.replace('.csv', '').split('_')
                    if len(parts) >= 3:
                        symbols.add(parts[2])  # SYMBOL part
            
            return sorted(list(symbols))
            
        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return []
    
    def get_data_summary(self, symbol: str, currency: str = "USD") -> Dict[str, Any]:
        """Get summary statistics for a symbol"""
        try:
            file_path = f'{self.data_dir}/crypto_data_{symbol}_{currency}_30d.csv'
            if not os.path.exists(file_path):
                return {}
            
            df = pd.read_csv(file_path)
            df = self._clean_data(df)
            
            if df.empty:
                return {}
            
            return {
                'symbol': symbol,
                'currency': currency,
                'total_records': len(df),
                'date_range': {
                    'start': df['time'].min().strftime('%Y-%m-%d %H:%M:%S'),
                    'end': df['time'].max().strftime('%Y-%m-%d %H:%M:%S')
                },
                'price_stats': {
                    'min': float(df['close'].min()),
                    'max': float(df['close'].max()),
                    'mean': float(df['close'].mean()),
                    'std': float(df['close'].std())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}
