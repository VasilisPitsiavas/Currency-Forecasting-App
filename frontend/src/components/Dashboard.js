import React, { useState } from 'react';
import { Grid, Paper, Typography, TextField, Button, MenuItem, Box, Alert, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const cryptocurrencies = [
  { value: 'BTC', label: 'Bitcoin' },
  { value: 'ETH', label: 'Ethereum' },
  { value: 'ADA', label: 'Cardano' },
  { value: 'SOL', label: 'Solana' },
  { value: 'DOT', label: 'Polkadot' },
];

const models = [
  { value: 'arimax', label: 'ARIMAX' },
  { value: 'xgboost', label: 'XGBoost' },
];

function Dashboard() {
  const [selectedCrypto, setSelectedCrypto] = useState('ETH');
  const [selectedModel, setSelectedModel] = useState('arimax');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:5000/api/predict?model_choice=${selectedModel}&symbol=${selectedCrypto}&currency=USD`
      );
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setPredictions(data.predictions);
        setMetrics(data.metrics);
      }
    } catch (error) {
      setError('Failed to fetch predictions. Please try again.');
      console.error('Error fetching predictions:', error);
    }
    setLoading(false);
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h5" gutterBottom>
            Cryptocurrency Price Predictions
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
            <TextField
              select
              label="Cryptocurrency"
              value={selectedCrypto}
              onChange={(e) => setSelectedCrypto(e.target.value)}
              sx={{ minWidth: 200 }}
            >
              {cryptocurrencies.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            
            <TextField
              select
              label="Model"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              sx={{ minWidth: 200 }}
            >
              {models.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>

            <Button
              variant="contained"
              onClick={handlePredict}
              disabled={loading}
              sx={{ minWidth: 120 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Predict'}
            </Button>
          </Box>

          {metrics && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Model Performance Metrics
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(metrics).map(([key, value]) => (
                  <Grid item xs={12} sm={6} md={3} key={key}>
                    <Paper sx={{ p: 1, textAlign: 'center' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        {key}
                      </Typography>
                      <Typography variant="h6">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {predictions.length > 0 && (
            <Box sx={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart
                  data={predictions}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="time" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#8884d8" 
                    name="Actual Price"
                    dot={false}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted" 
                    stroke="#82ca9d" 
                    name="Predicted Price"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
}

export default Dashboard; 