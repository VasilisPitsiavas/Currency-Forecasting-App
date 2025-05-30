import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, TextField, Button, MenuItem, Box, Alert } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const cryptocurrencies = [
  { value: 'BTC', label: 'Bitcoin' },
  { value: 'ETH', label: 'Ethereum' },
  { value: 'ADA', label: 'Cardano' },
  { value: 'SOL', label: 'Solana' },
  { value: 'DOT', label: 'Polkadot' },
];

function RealTime() {
  const [selectedCrypto, setSelectedCrypto] = useState('ETH');
  const [liveData, setLiveData] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let eventSource;

    if (isStreaming) {
      eventSource = new EventSource('http://localhost:5001/stream_realtime?symbol=ETH&currency=USD');

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLiveData((prevData) => {
          const newData = [...prevData, data];
          // Keep only the last 50 data points
          return newData.slice(-50);
        });
      };

      eventSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        setError('Failed to connect to real-time data stream');
        setIsStreaming(false);
        eventSource.close();
      };
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [isStreaming, selectedCrypto]);

  const toggleStreaming = () => {
    if (!isStreaming) {
      setLiveData([]); // Clear previous data when starting new stream
      setError(null);
    }
    setIsStreaming(!isStreaming);
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h5" gutterBottom>
            Real-time Cryptocurrency Monitoring
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
              disabled={isStreaming}
              sx={{ minWidth: 200 }}
            >
              {cryptocurrencies.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>

            <Button
              variant="contained"
              onClick={toggleStreaming}
              color={isStreaming ? 'error' : 'primary'}
              sx={{ minWidth: 120 }}
            >
              {isStreaming ? 'Stop Monitoring' : 'Start Monitoring'}
            </Button>
          </Box>

          {liveData.length > 0 && (
            <Box sx={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart
                  data={liveData}
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
                    dataKey="price" 
                    stroke="#8884d8" 
                    name="Current Price"
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

export default RealTime; 