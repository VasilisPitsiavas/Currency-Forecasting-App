/**
 * App Context for State Management
 * Provides global state for the application
 */
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import apiService from '../services/api';

// Initial state
const initialState = {
    // API Data
    availableSymbols: [],
    availableModels: {},
    apiDocs: null,
    
    // Current Selection
    selectedSymbol: 'ETH',
    selectedCurrency: 'USD',
    selectedModel: 'arimax',
    
    // Data States
    historicalData: [],
    predictions: [],
    metrics: {},
    
    // UI States
    loading: false,
    error: null,
    
    // Real-time Data
    realtimeData: {},
};

// Action types
const ACTIONS = {
    SET_LOADING: 'SET_LOADING',
    SET_ERROR: 'SET_ERROR',
    CLEAR_ERROR: 'CLEAR_ERROR',
    
    SET_AVAILABLE_SYMBOLS: 'SET_AVAILABLE_SYMBOLS',
    SET_AVAILABLE_MODELS: 'SET_AVAILABLE_MODELS',
    SET_API_DOCS: 'SET_API_DOCS',
    
    SET_SELECTED_SYMBOL: 'SET_SELECTED_SYMBOL',
    SET_SELECTED_CURRENCY: 'SET_SELECTED_CURRENCY',
    SET_SELECTED_MODEL: 'SET_SELECTED_MODEL',
    
    SET_HISTORICAL_DATA: 'SET_HISTORICAL_DATA',
    SET_PREDICTIONS: 'SET_PREDICTIONS',
    SET_METRICS: 'SET_METRICS',
    
    SET_REALTIME_DATA: 'SET_REALTIME_DATA',
    UPDATE_REALTIME_DATA: 'UPDATE_REALTIME_DATA',
};

// Reducer function
function appReducer(state, action) {
    switch (action.type) {
        case ACTIONS.SET_LOADING:
            return { ...state, loading: action.payload };
        
        case ACTIONS.SET_ERROR:
            return { ...state, error: action.payload, loading: false };
        
        case ACTIONS.CLEAR_ERROR:
            return { ...state, error: null };
        
        case ACTIONS.SET_AVAILABLE_SYMBOLS:
            return { ...state, availableSymbols: action.payload };
        
        case ACTIONS.SET_AVAILABLE_MODELS:
            return { ...state, availableModels: action.payload };
        
        case ACTIONS.SET_API_DOCS:
            return { ...state, apiDocs: action.payload };
        
        case ACTIONS.SET_SELECTED_SYMBOL:
            return { ...state, selectedSymbol: action.payload };
        
        case ACTIONS.SET_SELECTED_CURRENCY:
            return { ...state, selectedCurrency: action.payload };
        
        case ACTIONS.SET_SELECTED_MODEL:
            return { ...state, selectedModel: action.payload };
        
        case ACTIONS.SET_HISTORICAL_DATA:
            return { ...state, historicalData: action.payload };
        
        case ACTIONS.SET_PREDICTIONS:
            return { ...state, predictions: action.payload };
        
        case ACTIONS.SET_METRICS:
            return { ...state, metrics: action.payload };
        
        case ACTIONS.SET_REALTIME_DATA:
            return { ...state, realtimeData: action.payload };
        
        case ACTIONS.UPDATE_REALTIME_DATA:
            return {
                ...state,
                realtimeData: {
                    ...state.realtimeData,
                    [action.payload.symbol]: action.payload.data,
                },
            };
        
        default:
            return state;
    }
}

// Create context
const AppContext = createContext();

// Provider component
export function AppProvider({ children }) {
    const [state, dispatch] = useReducer(appReducer, initialState);

    // Actions
    const actions = {
        setLoading: (loading) => dispatch({ type: ACTIONS.SET_LOADING, payload: loading }),
        setError: (error) => dispatch({ type: ACTIONS.SET_ERROR, payload: error }),
        clearError: () => dispatch({ type: ACTIONS.CLEAR_ERROR }),
        
        setSelectedSymbol: (symbol) => dispatch({ type: ACTIONS.SET_SELECTED_SYMBOL, payload: symbol }),
        setSelectedCurrency: (currency) => dispatch({ type: ACTIONS.SET_SELECTED_CURRENCY, payload: currency }),
        setSelectedModel: (model) => dispatch({ type: ACTIONS.SET_SELECTED_MODEL, payload: model }),
        
        // API Actions
        fetchAvailableSymbols: async () => {
            try {
                actions.setLoading(true);
                const response = await apiService.getAvailableSymbols();
                dispatch({ type: ACTIONS.SET_AVAILABLE_SYMBOLS, payload: response.data });
            } catch (error) {
                actions.setError(error.message);
            } finally {
                actions.setLoading(false);
            }
        },
        
        fetchAvailableModels: async () => {
            try {
                actions.setLoading(true);
                const response = await apiService.getAvailableModels();
                dispatch({ type: ACTIONS.SET_AVAILABLE_MODELS, payload: response.data });
            } catch (error) {
                actions.setError(error.message);
            } finally {
                actions.setLoading(false);
            }
        },
        
        fetchHistoricalData: async (symbol, currency, limit) => {
            try {
                actions.setLoading(true);
                actions.clearError();
                
                const response = await apiService.getHistory(
                    symbol || state.selectedSymbol,
                    currency || state.selectedCurrency,
                    limit || 30
                );
                
                if (response.success) {
                    dispatch({ type: ACTIONS.SET_HISTORICAL_DATA, payload: response.history });
                } else {
                    actions.setError(response.error || 'Failed to fetch historical data');
                }
            } catch (error) {
                actions.setError(error.message);
            } finally {
                actions.setLoading(false);
            }
        },
        
        fetchPredictions: async (symbol, currency, model, steps) => {
            try {
                actions.setLoading(true);
                actions.clearError();
                
                const selectedSymbol = symbol || state.selectedSymbol;
                const selectedCurrency = currency || state.selectedCurrency;
                const selectedModel = model || state.selectedModel;
                const selectedSteps = steps || 10;
                
                let response;
                if (selectedModel === 'arimax') {
                    response = await apiService.getArimaxPrediction(selectedSymbol, selectedCurrency, selectedSteps);
                } else {
                    response = await apiService.getXgboostPrediction(selectedSymbol, selectedCurrency, selectedSteps);
                }
                
                if (response.success) {
                    dispatch({ type: ACTIONS.SET_PREDICTIONS, payload: response.predictions });
                    dispatch({ type: ACTIONS.SET_METRICS, payload: response.metrics });
                } else {
                    actions.setError(response.error || 'Failed to generate predictions');
                }
            } catch (error) {
                actions.setError(error.message);
            } finally {
                actions.setLoading(false);
            }
        },
        
        updateRealtimeData: (symbol, data) => {
            dispatch({ type: ACTIONS.UPDATE_REALTIME_DATA, payload: { symbol, data } });
        },
    };

    // Load initial data
    useEffect(() => {
        actions.fetchAvailableSymbols();
        actions.fetchAvailableModels();
    }, []);

    const value = {
        state,
        actions,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Custom hook to use the context
export function useAppContext() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within an AppProvider');
    }
    return context;
}
