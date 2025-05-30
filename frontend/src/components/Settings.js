import React, { useState } from 'react';
import { Grid, Paper, Typography, TextField, Button, MenuItem, Box, Switch, FormControlLabel, Alert } from '@mui/material';

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

function Settings() {
  const [settings, setSettings] = useState({
    defaultCrypto: 'ETH',
    defaultModel: 'arimax',
    darkMode: true,
    autoRefresh: false,
    refreshInterval: 60,
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    setSettings((prev) => ({
      ...prev,
      [name]: event.target.type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = async () => {
    setError(null);
    setSuccess(false);
    try {
      // Here you would typically save settings to your backend
      // For now, we'll just simulate a successful save
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      setError('Failed to save settings. Please try again.');
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h5" gutterBottom>
            Settings
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Settings saved successfully!
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Default Cryptocurrency"
                name="defaultCrypto"
                value={settings.defaultCrypto}
                onChange={handleChange}
              >
                {cryptocurrencies.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Default Model"
                name="defaultModel"
                value={settings.defaultModel}
                onChange={handleChange}
              >
                {models.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Refresh Interval (seconds)"
                name="refreshInterval"
                value={settings.refreshInterval}
                onChange={handleChange}
                InputProps={{ inputProps: { min: 30, max: 3600 } }}
                helperText="Minimum 30 seconds, maximum 1 hour"
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.darkMode}
                      onChange={handleChange}
                      name="darkMode"
                    />
                  }
                  label="Dark Mode"
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.autoRefresh}
                      onChange={handleChange}
                      name="autoRefresh"
                    />
                  }
                  label="Auto-refresh Data"
                />
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleSave}
                sx={{ minWidth: 120 }}
              >
                Save Settings
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default Settings; 