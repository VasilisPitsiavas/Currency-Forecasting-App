import React, { useEffect, useState } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Badge
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

const CRYPTOCURRENCIES = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK'];
const CURRENCY = 'USD';

const columns = [
  { id: 'time', label: 'Time', minWidth: 120 },
  { id: 'symbol', label: 'Cryptocurrency', minWidth: 100 },
  { id: 'price', label: 'Price (USD)', minWidth: 100 },
  { id: 'change', label: 'Change', minWidth: 100 },
];

export default function RealTimeTable() {
  const [liveData, setLiveData] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previousPrices, setPreviousPrices] = useState({});
  const [summaryData, setSummaryData] = useState({});

  const validateData = (data) => {
    if (!data || typeof data !== 'object') return false;
    if (!data.time || !data[CURRENCY]) return false;
    return true;
  };

  const calculatePriceChange = (symbol, currentPrice) => {
    if (!previousPrices[symbol]) return null;
    const change = ((currentPrice - previousPrices[symbol]) / previousPrices[symbol]) * 100;
    return change.toFixed(2);
  };

  const updateSummaryData = (symbol, price, change) => {
    setSummaryData(prev => ({
      ...prev,
      [symbol]: { price, change }
    }));
  };

  useEffect(() => {
    const sources = new Map();
    setLoading(true);
    setError(null);
    setLiveData({});
    setPreviousPrices({});

    CRYPTOCURRENCIES.forEach(symbol => {
      const eventSource = new EventSource(
        `${API_BASE_URL}/stream_realtime?symbol=${symbol}&currency=${CURRENCY}`
      );
      sources.set(symbol, eventSource);

      eventSource.onmessage = (event) => {
        setLoading(false);
        try {
          const data = JSON.parse(event.data);
          if (data.error) {
            setError(data.error);
            return;
          }

          if (!validateData(data)) {
            setError('Invalid data received from server');
            return;
          }

          const currentPrice = data[CURRENCY] || data.price || data.USD;
          const priceChange = calculatePriceChange(symbol, currentPrice);
          
          setPreviousPrices(prev => ({
            ...prev,
            [symbol]: currentPrice
          }));

          updateSummaryData(symbol, currentPrice, priceChange);

          setLiveData(prev => {
            const symbolData = prev[symbol] || [];
            const newRow = {
              time: data.time,
              symbol: symbol,
              price: currentPrice,
              change: priceChange,
            };

            // Only add if timestamp is new
            if (symbolData.length === 0 || symbolData[0].time !== newRow.time) {
              const updated = [newRow, ...symbolData].slice(0, 40);
              return { ...prev, [symbol]: updated };
            }
            return prev;
          });
        } catch (err) {
          setError('Failed to parse server response');
        }
      };

      eventSource.onerror = (err) => {
        setLoading(false);
        setError('Failed to connect to real-time data stream');
        eventSource.close();
      };
    });

    return () => {
      sources.forEach(source => source.close());
    };
  }, []);

  const renderPriceChange = (change) => {
    if (change === null) return 'N/A';
    const isPositive = parseFloat(change) > 0;
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', color: isPositive ? 'success.main' : 'error.main' }}>
        {isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
        <Typography variant="body2" sx={{ ml: 1 }}>
          {change}%
        </Typography>
      </Box>
    );
  };

  const renderSummaryCards = () => (
    <Grid container spacing={2} sx={{ mb: 4 }}>
      {CRYPTOCURRENCIES.map(symbol => {
        const data = summaryData[symbol] || { price: 0, change: null };
        return (
          <Grid item xs={12} sm={6} md={3} key={symbol}>
            <Card sx={{ 
              minWidth: 150, 
              textAlign: 'center',
              boxShadow: 2,
              '&:hover': { boxShadow: 4 }
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {symbol}
                </Typography>
                <Typography variant="h5" sx={{ mb: 1 }}>
                  ${data.price ? data.price.toFixed(2) : '0.00'}
                </Typography>
                {renderPriceChange(data.change)}
              </CardContent>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );

  const renderTable = () => {
    const allData = Object.values(liveData).flat().sort((a, b) => 
      new Date(b.time) - new Date(a.time)
    ).slice(0, 40);

    return (
      <TableContainer component={Paper} sx={{ maxWidth: 1200, mx: 'auto', mt: 2 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col.id} style={{ minWidth: col.minWidth, fontWeight: 'bold' }}>
                  {col.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {allData.length === 0 && !loading ? (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  No data yet.
                </TableCell>
              </TableRow>
            ) : (
              allData.map((row, idx) => (
                <TableRow key={row.time + row.symbol + idx}>
                  <TableCell>{row.time}</TableCell>
                  <TableCell>{row.symbol}</TableCell>
                  <TableCell>${row.price !== undefined ? row.price.toFixed(2) : 'N/A'}</TableCell>
                  <TableCell>{renderPriceChange(row.change)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box sx={{ mt: 4, px: 2 }}>
      <Typography variant="h4" align="center" color="primary" gutterBottom>
        Real-Time Cryptocurrency Monitoring
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}
      {renderSummaryCards()}
      {renderTable()}
    </Box>
  );
} 