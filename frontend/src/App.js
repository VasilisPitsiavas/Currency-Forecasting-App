import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import PredictionDashboard from './components/PredictionDashboard';
import HomePage from './components/HomePage';
import RealTimeTable from './components/RealTimeTable';
import Navbar from './components/Navbar';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/predict" element={<PredictionDashboard />} />
          <Route path="/realtime" element={<RealTimeTable />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 