import React from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log the error to console and set state
        console.error('Error caught by boundary:', error, errorInfo);
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            return (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '50vh',
                        p: 3,
                        textAlign: 'center'
                    }}
                >
                    <ErrorOutlineIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
                    
                    <Typography variant="h4" component="h1" gutterBottom color="error.main">
                        Oops! Something went wrong
                    </Typography>
                    
                    <Typography variant="body1" color="text.secondary" paragraph sx={{ maxWidth: 600 }}>
                        We encountered an unexpected error. Please try refreshing the page or contact support if the problem persists.
                    </Typography>

                    <Alert severity="error" sx={{ mb: 3, maxWidth: 600 }}>
                        <Typography variant="body2">
                            {this.state.error && this.state.error.toString()}
                        </Typography>
                    </Alert>

                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                            variant="contained"
                            onClick={this.handleReset}
                            sx={{ minWidth: 120 }}
                        >
                            Try Again
                        </Button>
                        
                        <Button
                            variant="outlined"
                            onClick={() => window.location.reload()}
                            sx={{ minWidth: 120 }}
                        >
                            Refresh Page
                        </Button>
                    </Box>

                    {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                        <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.100', borderRadius: 1, maxWidth: 800, overflow: 'auto' }}>
                            <Typography variant="h6" gutterBottom>
                                Error Details (Development Only)
                            </Typography>
                            <pre style={{ fontSize: '12px', margin: 0 }}>
                                {this.state.errorInfo.componentStack}
                            </pre>
                        </Box>
                    )}
                </Box>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
