import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import ShowChartIcon from '@mui/icons-material/ShowChart';

export default function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <ShowChartIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          CryptoForecast
        </Typography>
        <Box>
          <Button 
            color="inherit" 
            component={Link} 
            to="/"
          >
            Home
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            to="/predict"
          >
            Predictions
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            to="/realtime"
          >
            Real-Time
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
