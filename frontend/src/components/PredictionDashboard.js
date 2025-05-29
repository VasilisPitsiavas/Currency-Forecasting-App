import React, { useState } from 'react';
import { Button, Select, MenuItem, TextField, Box, Typography, Paper, Card, CardContent, CircularProgress, Alert, Container } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

const models = [
  { value: 'arimax', label: 'ARIMAX' },
  { value: 'xgboost', label: 'XGBoost' }
];

const symbols = [
  { value: 'ETH', label: 'Ethereum' },
  { value: 'BTC', label: 'Bitcoin' },
  { value: 'SOL', label: 'Solana' },
  { value: 'ADA', label: 'Cardano' },
  { value: 'DOT', label: 'Polkadot' },
  { value: 'AVAX', label: 'Avalanche' },
  { value: 'MATIC', label: 'Polygon' },
  { value: 'LINK', label: 'Chainlink' }
];

export default function PredictionDashboard() {
  const [model, setModel] = useState('arimax');
  const [symbol, setSymbol] = useState('ETH');
  const [currency, setCurrency] = useState('USD');
  const [steps, setSteps] = useState(10);
  const [predictions, setPredictions] = useState([]);
  const [actuals, setActuals] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchActuals = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/history?symbol=${symbol}&currency=${currency}&limit=30`);
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        return;
      }
      setActuals(data.history || []);
    } catch (err) {
      setError('Failed to fetch historical data');
      setActuals([]);
    }
  };

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    setPredictions([]);
    setMetrics(null);
    
    try {
      await fetchActuals();
      const response = await fetch(`${API_BASE_URL}/api/predict/${model}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, currency, steps })
      });
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
        return;
      }
      
      setPredictions(data.predictions || []);
      setMetrics(data.metrics || null);
    } catch (err) {
      setError('Failed to fetch predictions');
    } finally {
      setLoading(false);
    }
  };

  // Combine actuals and predictions for the chart
  const actualMap = {};
  actuals.forEach(a => { actualMap[a.time] = a.actual; });

  const predictedMap = {};
  predictions.forEach(p => { predictedMap[p.time] = p.predicted; });

  const allTimes = Array.from(new Set([
    ...actuals.map(a => a.time),
    ...predictions.map(p => p.time)
  ])).sort((a, b) => new Date(a) - new Date(b));

  const combinedData = allTimes.map(time => ({
    time,
    actual: actualMap[time] !== undefined ? actualMap[time] : null,
    predicted: predictedMap[time] !== undefined ? predictedMap[time] : null
  }));

  return (
    <Box sx={{ background: 'linear-gradient(135deg, #e3f2fd 0%, #f4f6fa 100%)', minHeight: '100vh', py: 6 }}>
      <Container maxWidth="md">
        <Paper elevation={4} sx={{ p: 4, borderRadius: 4, mb: 4, boxShadow: 6 }}>
          <Typography variant="h4" align="center" sx={{ fontWeight: 700, mb: 3, color: 'primary.main' }}>
            Crypto Price Prediction
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Select 
              value={model} 
              onChange={e => setModel(e.target.value)} 
              size="small"
              sx={{ minWidth: 120 }}
            >
              {models.map(m => <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>)}
            </Select>
            <Select 
              value={symbol} 
              onChange={e => setSymbol(e.target.value)} 
              size="small"
              sx={{ minWidth: 120 }}
            >
              {symbols.map(s => <MenuItem key={s.value} value={s.value}>{s.label}</MenuItem>)}
            </Select>
            <TextField 
              label="Currency" 
              value={currency} 
              onChange={e => setCurrency(e.target.value)} 
              size="small" 
              sx={{ width: 100 }}
            />
            <TextField 
              label="Steps" 
              type="number" 
              value={steps} 
              onChange={e => setSteps(Number(e.target.value))} 
              size="small"
              sx={{ width: 100 }}
            />
            <Button 
              variant="contained" 
              onClick={fetchPredictions} 
              disabled={loading} 
              size="medium" 
              sx={{ fontWeight: 600 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Predict'}
            </Button>
          </Box>

          {metrics && (
            <Card sx={{ mb: 3, background: '#e3f2fd', display: 'inline-block', px: 3, py: 2, borderRadius: 2, boxShadow: 2 }}>
              <CardContent sx={{ p: 0 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Prediction Metrics</Typography>
                <Typography variant="body2">RMSE: <b>{metrics.RMSE && metrics.RMSE.toFixed(3)}</b></Typography>
                <Typography variant="body2">MAE: <b>{metrics.MAE && metrics.MAE.toFixed(3)}</b></Typography>
                <Typography variant="body2">MSE: <b>{metrics.MSE && metrics.MSE.toFixed(3)}</b></Typography>
                <Typography variant="body2">MdAE: <b>{metrics.MdAE && metrics.MdAE.toFixed(3)}</b></Typography>
              </CardContent>
            </Card>
          )}

          <Box sx={{ width: '100%', height: 420, background: '#fff', borderRadius: 2, p: 2, boxShadow: 1 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                <CircularProgress />
              </Box>
            ) : combinedData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={combinedData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                  <XAxis 
                    dataKey="time" 
                    tick={{ fontSize: 12 }} 
                    angle={-30} 
                    textAnchor="end" 
                    minTickGap={20} 
                  />
                  <YAxis 
                    domain={['auto', 'auto']} 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `$${value.toFixed(2)}`}
                  />
                  <Tooltip 
                    formatter={(value) => [`$${value.toFixed(2)}`, '']}
                    labelFormatter={(label) => `Time: ${label}`}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#4caf50" 
                    name="Actual" 
                    dot={false} 
                    strokeWidth={2} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted" 
                    stroke="#1976d2" 
                    name="Predicted" 
                    dot={{ r: 3 }} 
                    strokeWidth={2} 
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                <Typography variant="h6" color="text.secondary">
                  Select parameters and click Predict to see the forecast
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
} 