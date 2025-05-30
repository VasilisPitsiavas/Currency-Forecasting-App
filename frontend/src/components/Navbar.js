import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { TrendingUp, Timeline, Settings, Home as HomeIcon, Login as LoginIcon, PersonAdd as PersonAddIcon } from '@mui/icons-material';
import { Link as RouterLink, useLocation } from 'react-router-dom';

// Free SVG icon (currency/finance theme)
const LogoIcon = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: 10 }}>
    <circle cx="12" cy="12" r="10" fill="#1976d2" />
    <path d="M8 12h4.5a2.5 2.5 0 100-5H11" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M12 17v-10" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

function Navbar() {
  const location = useLocation();
  const navLinks = [
    { label: 'Home', to: '/', icon: <HomeIcon /> },
    { label: 'Predictions', to: '/predict', icon: <TrendingUp /> },
    { label: 'Real-Time', to: '/realtime', icon: <Timeline /> },
    { label: 'Settings', to: '/settings', icon: <Settings /> },
  ];

  return (
    <AppBar position="static" sx={{ boxShadow: 3, background: 'linear-gradient(90deg, #1976d2 60%, #2196f3 100%)' }}>
      <Toolbar>
        <LogoIcon />
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit', fontWeight: 700 }}
        >
          Currency Forecasting App
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {navLinks.map(link => (
            <Button
              key={link.to}
              color="inherit"
              startIcon={link.icon}
              component={RouterLink}
              to={link.to}
              sx={{
                fontWeight: 600,
                borderBottom: location.pathname === link.to ? '3px solid #fff' : 'none',
                borderRadius: 0,
                background: location.pathname === link.to ? 'rgba(255,255,255,0.08)' : 'none',
                color: location.pathname === link.to ? '#fff' : 'inherit',
                transition: 'background 0.2s',
                '&:hover': {
                  background: 'rgba(255,255,255,0.15)',
                },
              }}
            >
              {link.label}
            </Button>
          ))}
          <Button
            color="inherit"
            startIcon={<LoginIcon />}
            component={RouterLink}
            to="/login"
            sx={{ fontWeight: 600 }}
          >
            Log In
          </Button>
          <Button
            color="inherit"
            startIcon={<PersonAddIcon />}
            component={RouterLink}
            to="/signup"
            sx={{ fontWeight: 600 }}
          >
            Sign Up
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar; 