import React, { useState } from 'react';
import { Button, Select, MenuItem, TextField, Box, Typography, Paper, Card, CardContent, CircularProgress, AppBar, Toolbar } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Container from '@mui/material/Container';

const models = [
  { value: 'arimax', label: 'ARIMAX' },
  { value: 'xgboost', label: 'XGBoost' }
];

const symbols = [
  { value: 'ETH', label: 'Ethereum' },
  { value: 'BTC', label: 'Bitcoin' },
  // Add more as needed
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

  const fetchActuals = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/history?symbol=${symbol}&currency=${currency}&limit=30`);
      const data = await response.json();
      setActuals(data.history || []);
    } catch (err) {
      setActuals([]);
    }
  };

  const fetchPredictions = async () => {
    setLoading(true);
    setPredictions([]);
    setMetrics(null);
    await fetchActuals();
    try {
      const response = await fetch(`http://localhost:5001/api/predict/${model}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, currency, steps })
      });
      const data = await response.json();
      setPredictions(data.predictions || []);
      setMetrics(data.metrics || null);
    } catch (err) {
      alert('Error fetching predictions');
    }
    setLoading(false);
  };

  // Combine actuals and predictions for the chart
  const combinedData = [
    ...actuals.map(a => ({ ...a, predicted: null })),
    ...predictions.map(p => ({ ...p, actual: null }))
  ];

  return (
    <Box sx={{ background: '#f4f6fa', minHeight: '100vh' }}>
      <AppBar position="static" color="primary" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: 1 }}>
            Currency Forecasting Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
            Crypto Price Prediction
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
            <Select value={model} onChange={e => setModel(e.target.value)} size="small">
              {models.map(m => <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>)}
            </Select>
            <Select value={symbol} onChange={e => setSymbol(e.target.value)} size="small">
              {symbols.map(s => <MenuItem key={s.value} value={s.value}>{s.label}</MenuItem>)}
            </Select>
            <TextField label="Currency" value={currency} onChange={e => setCurrency(e.target.value)} size="small" />
            <TextField label="Steps" type="number" value={steps} onChange={e => setSteps(Number(e.target.value))} size="small" />
            <Button variant="contained" onClick={fetchPredictions} disabled={loading} size="medium" sx={{ fontWeight: 600 }}>
              {loading ? <CircularProgress size={24} /> : 'Predict'}
            </Button>
          </Box>
          {metrics && (
            <Card sx={{ mb: 3, background: '#e3f2fd', display: 'inline-block', px: 3, py: 2 }}>
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
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={combinedData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                  <XAxis dataKey="time" tick={{ fontSize: 12 }} angle={-30} textAnchor="end" minTickGap={20} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend verticalAlign="top" height={36} />
                  <Line type="monotone" dataKey="actual" stroke="#4caf50" name="Actual" dot={false} strokeWidth={2} />
                  <Line type="monotone" dataKey="predicted" stroke="#1976d2" name="Predicted" dot={{ r: 3 }} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
} 