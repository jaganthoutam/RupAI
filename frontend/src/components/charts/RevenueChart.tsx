import React from 'react';
import { Box, Typography } from '@mui/material';

interface RevenueChartProps {
  data?: any;
  loading?: boolean;
}

const RevenueChart: React.FC<RevenueChartProps> = ({ data, loading }) => {
  return (
    <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Typography color="text.secondary">
        {loading ? 'Loading chart...' : 'Revenue Chart (Coming Soon)'}
      </Typography>
    </Box>
  );
};

export default RevenueChart; 