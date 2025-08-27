import React from 'react';
import { Box, Typography, Button, Container, Grid, Card, CardContent, Alert } from '@mui/material';
import { Link } from 'react-router-dom';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TimelineIcon from '@mui/icons-material/Timeline';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import { useAppContext } from '../context/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export default function HomePage() {
  const { state, actions } = useAppContext();

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      {state.error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={actions.clearError}>
          {state.error}
        </Alert>
      )}

      <Box textAlign="center" mb={6}>
        <Typography variant="h2" component="h1" gutterBottom color="primary">
          Cryptocurrency Forecasting Platform
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Advanced AI-powered cryptocurrency price predictions and real-time monitoring
        </Typography>
      </Box>

      {state.loading ? (
        <LoadingSpinner message="Loading available data..." />
      ) : (
        <>
          <Grid container spacing={4} mb={6}>
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%', textAlign: 'center' }}>
                <CardContent>
                  <ShowChartIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h5" component="h2" gutterBottom>
                    Price Predictions
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Get accurate price forecasts using advanced machine learning models (ARIMAX & XGBoost)
                  </Typography>
                  <Button 
                    component={Link} 
                    to="/predict" 
                    variant="contained" 
                    size="large"
                    fullWidth
                  >
                    View Predictions
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%', textAlign: 'center' }}>
                <CardContent>
                  <TimelineIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h5" component="h2" gutterBottom>
                    Real-Time Monitoring
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Monitor live cryptocurrency prices with real-time updates and price change tracking
                  </Typography>
                  <Button 
                    component={Link} 
                    to="/realtime" 
                    variant="contained" 
                    size="large"
                    fullWidth
                  >
                    Live Monitoring
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%', textAlign: 'center' }}>
                <CardContent>
                  <TrendingUpIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h5" component="h2" gutterBottom>
                    Market Analysis
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Comprehensive market analysis with historical data and trend visualization
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="large"
                    fullWidth
                    disabled
                  >
                    Coming Soon
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box textAlign="center" mb={4}>
            <Typography variant="h4" gutterBottom>
              Supported Cryptocurrencies
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              {state.availableSymbols.length > 0 
                ? state.availableSymbols.join(', ')
                : 'Bitcoin (BTC), Ethereum (ETH), Cardano (ADA), Polkadot (DOT), and more...'
              }
            </Typography>
            
            {state.availableModels && Object.keys(state.availableModels).length > 0 && (
              <Typography variant="body1" color="text.secondary">
                Available Models: {Object.keys(state.availableModels).map(model => 
                  state.availableModels[model]
                ).join(', ')}
              </Typography>
            )}
          </Box>
        </>
      )}
    </Container>
  );
}
