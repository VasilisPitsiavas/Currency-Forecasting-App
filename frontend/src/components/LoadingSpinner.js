import React from 'react';
import { Box, CircularProgress, Typography, Skeleton } from '@mui/material';

export function LoadingSpinner({ message = 'Loading...', size = 'medium' }) {
    const sizeMap = {
        small: 24,
        medium: 40,
        large: 60
    };

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                p: 3,
                minHeight: '200px'
            }}
        >
            <CircularProgress size={sizeMap[size]} sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
                {message}
            </Typography>
        </Box>
    );
}

export function LoadingSkeleton({ variant = 'rectangular', width = '100%', height = 200 }) {
    return (
        <Skeleton
            variant={variant}
            width={width}
            height={height}
            animation="wave"
        />
    );
}

export function TableLoadingSkeleton({ rows = 5, columns = 4 }) {
    return (
        <Box sx={{ p: 2 }}>
            {Array.from({ length: rows }).map((_, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 2, mb: 1 }}>
                    {Array.from({ length: columns }).map((_, colIndex) => (
                        <Skeleton
                            key={colIndex}
                            variant="rectangular"
                            width={colIndex === 0 ? 120 : 100}
                            height={40}
                            animation="wave"
                        />
                    ))}
                </Box>
            ))}
        </Box>
    );
}

export function CardLoadingSkeleton({ cards = 3 }) {
    return (
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {Array.from({ length: cards }).map((_, index) => (
                <Box key={index} sx={{ minWidth: 200, flex: 1 }}>
                    <Skeleton variant="rectangular" height={120} animation="wave" />
                    <Box sx={{ p: 1 }}>
                        <Skeleton variant="text" width="60%" animation="wave" />
                        <Skeleton variant="text" width="40%" animation="wave" />
                    </Box>
                </Box>
            ))}
        </Box>
    );
}
