"""
API Schemas for input validation and standardized responses
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class PredictionRequest:
    """Schema for prediction API requests"""
    symbol: str
    currency: str = "USD"
    steps: int = 10
    model: str = "arimax"  # "arimax" or "xgboost"
    
    def validate(self) -> List[str]:
        """Validate the request and return list of errors"""
        errors = []
        
        if not self.symbol or len(self.symbol) < 2:
            errors.append("Symbol must be at least 2 characters")
        
        if self.currency not in ["USD", "EUR", "GBP"]:
            errors.append("Currency must be USD, EUR, or GBP")
        
        if self.steps < 1 or self.steps > 100:
            errors.append("Steps must be between 1 and 100")
        
        if self.model not in ["arimax", "xgboost"]:
            errors.append("Model must be 'arimax' or 'xgboost'")
        
        return errors

@dataclass
class PredictionResponse:
    """Schema for prediction API responses"""
    success: bool
    predictions: List[Dict[str, Any]]
    metrics: Dict[str, float]
    model_used: str
    symbol: str
    currency: str
    timestamp: str
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "success": self.success,
            "predictions": self.predictions,
            "metrics": self.metrics,
            "model_used": self.model_used,
            "symbol": self.symbol,
            "currency": self.currency,
            "timestamp": self.timestamp,
            "error": self.error
        }

@dataclass
class HistoryRequest:
    """Schema for historical data requests"""
    symbol: str
    currency: str = "USD"
    limit: int = 30
    
    def validate(self) -> List[str]:
        """Validate the request and return list of errors"""
        errors = []
        
        if not self.symbol or len(self.symbol) < 2:
            errors.append("Symbol must be at least 2 characters")
        
        if self.currency not in ["USD", "EUR", "GBP"]:
            errors.append("Currency must be USD, EUR, or GBP")
        
        if self.limit < 1 or self.limit > 1000:
            errors.append("Limit must be between 1 and 1000")
        
        return errors

@dataclass
class HistoryResponse:
    """Schema for historical data responses"""
    success: bool
    history: List[Dict[str, Any]]
    symbol: str
    currency: str
    count: int
    timestamp: str
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "success": self.success,
            "history": self.history,
            "symbol": self.symbol,
            "currency": self.currency,
            "count": self.count,
            "timestamp": self.timestamp,
            "error": self.error
        }

# Standard API Response Formats
def create_success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def create_error_response(error: str, status_code: int = 400) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "success": False,
        "error": error,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }

# API Documentation
API_DOCS = {
    "info": {
        "title": "Cryptocurrency Forecasting API",
        "version": "1.0.0",
        "description": "Advanced AI-powered cryptocurrency price predictions and real-time monitoring"
    },
    "endpoints": {
        "/api/predict/arimax": {
            "method": "POST",
            "description": "Get ARIMAX model predictions",
            "request_body": {
                "symbol": "string (required)",
                "currency": "string (optional, default: USD)",
                "steps": "integer (optional, default: 10)"
            },
            "response": {
                "success": "boolean",
                "predictions": "array",
                "metrics": "object",
                "model_used": "string",
                "timestamp": "string"
            }
        },
        "/api/predict/xgboost": {
            "method": "POST",
            "description": "Get XGBoost model predictions",
            "request_body": {
                "symbol": "string (required)",
                "currency": "string (optional, default: USD)",
                "steps": "integer (optional, default: 10)"
            },
            "response": {
                "success": "boolean",
                "predictions": "array",
                "metrics": "object",
                "model_used": "string",
                "timestamp": "string"
            }
        },
        "/api/history": {
            "method": "GET",
            "description": "Get historical cryptocurrency data",
            "query_params": {
                "symbol": "string (required)",
                "currency": "string (optional, default: USD)",
                "limit": "integer (optional, default: 30)"
            },
            "response": {
                "success": "boolean",
                "history": "array",
                "count": "integer",
                "timestamp": "string"
            }
        }
    }
}
