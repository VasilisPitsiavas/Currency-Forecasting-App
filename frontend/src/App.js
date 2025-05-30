import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import RealTimeTable from './components/RealTimeTable';
import PredictionDashboard from './components/PredictionDashboard';
import Login from './components/Login';
import Signup from './components/Signup';


// import RealTimeTable from './components/RealTimeTable'; // Uncomment if you have this component

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* Uncomment the next line if you have a RealTimeTable component */}
        {/* <Route path="/realtime" element={<RealTimeTable symbol="ETH" currency="USD" />} /> */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/predict" element={<PredictionDashboard />} />
        <Route path="/realtime" element={<RealTimeTable symbol="ETH" currency="USD" />} />
      </Routes>
    </Router>
  );
}

export default App; 