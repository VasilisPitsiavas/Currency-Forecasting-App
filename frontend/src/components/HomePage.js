import React from 'react';
import { Box, Typography, Button, Container, Grid, Paper } from '@mui/material';
import { TrendingUp, Timeline } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <Box sx={{ background: 'linear-gradient(135deg, #e3f2fd 0%, #f4f6fa 100%)', minHeight: '100vh', pb: 8 }}>
      <Container maxWidth="md" sx={{ pt: 8, textAlign: 'center' }}>
        <Typography variant="h2" sx={{ fontWeight: 800, mb: 2, color: 'primary.main', letterSpacing: 1 }}>
          Welcome to the Currency Forecasting App
        </Typography>
        <Typography variant="h5" sx={{ mb: 4, color: 'text.secondary', fontWeight: 400 }}>
          Real-time monitoring and future price predictions for your favorite cryptocurrencies, powered by advanced machine learning models.
        </Typography>
        <Grid container spacing={2} justifyContent="center" sx={{ mb: 4 }}>
          <Grid item>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<Timeline />}
              sx={{ fontWeight: 700, px: 4 }}
              onClick={() => navigate('/realtime')}
            >
              Real-Time Dashboard
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              color="primary"
              size="large"
              startIcon={<TrendingUp />}
              sx={{ fontWeight: 700, px: 4 }}
              onClick={() => navigate('/predict')}
            >
              Prediction Dashboard
            </Button>
          </Grid>
        </Grid>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 3, background: '#fff', maxWidth: 800, mx: 'auto', mb: 6 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}>
            What Can You Do With This App?
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                📈 Real-Time Crypto Monitoring
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Track live prices and trends for top cryptocurrencies. Instantly see market movements and price changes with beautiful, interactive dashboards.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                🤖 AI-Powered Price Predictions
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Generate future price forecasts using ARIMAX and XGBoost models. Visualize predictions, compare with actuals, and make informed decisions.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                📊 Performance Metrics
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Evaluate prediction accuracy with RMSE, MAE, and more. Transparent analytics help you trust and understand the models.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                🌐 User-Friendly & Modern UI
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Enjoy a clean, responsive interface designed for both beginners and advanced users. Navigate easily between dashboards and features.
              </Typography>
            </Grid>
          </Grid>
        </Paper>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 4 }}>
          © {new Date().getFullYear()} Currency Forecasting App. Built with ❤️ for crypto enthusiasts and data-driven investors.
        </Typography>
      </Container>
    </Box>
  );
}
