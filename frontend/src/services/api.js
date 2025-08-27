/**
 * Centralized API Service
 * Handles all API calls to the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

class ApiService {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    /**
     * Generic API call method
     */
    async apiCall(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API call failed for ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Get API documentation
     */
    async getApiDocs() {
        return this.apiCall('/api/docs');
    }

    /**
     * Get available prediction models
     */
    async getAvailableModels() {
        return this.apiCall('/api/models');
    }

    /**
     * Get available cryptocurrency symbols
     */
    async getAvailableSymbols() {
        return this.apiCall('/api/symbols');
    }

    /**
     * Get historical data
     */
    async getHistory(symbol, currency = 'USD', limit = 30) {
        const params = new URLSearchParams({
            symbol,
            currency,
            limit: limit.toString(),
        });
        return this.apiCall(`/api/history?${params}`);
    }

    /**
     * Get ARIMAX predictions
     */
    async getArimaxPrediction(symbol, currency = 'USD', steps = 10) {
        return this.apiCall('/api/predict/arimax', {
            method: 'POST',
            body: JSON.stringify({
                symbol,
                currency,
                steps,
            }),
        });
    }

    /**
     * Get XGBoost predictions
     */
    async getXgboostPrediction(symbol, currency = 'USD', steps = 10) {
        return this.apiCall('/api/predict/xgboost', {
            method: 'POST',
            body: JSON.stringify({
                symbol,
                currency,
                steps,
            }),
        });
    }

    /**
     * Fetch historical data from external API
     */
    async fetchHistoricalData(symbol, currency = 'USD', daysBack = 30) {
        return this.apiCall('/fetch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                symbol,
                currency,
                days_back: daysBack.toString(),
            }),
        });
    }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
