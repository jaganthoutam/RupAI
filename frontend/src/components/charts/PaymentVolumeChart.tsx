import React from 'react';
import { Box, Typography } from '@mui/material';

interface PaymentVolumeChartProps {
  data?: any;
  loading?: boolean;
}

const PaymentVolumeChart: React.FC<PaymentVolumeChartProps> = ({ data, loading }) => {
  return (
    <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Typography color="text.secondary">
        {loading ? 'Loading chart...' : 'Payment Volume Chart (Coming Soon)'}
      </Typography>
    </Box>
  );
};

export default PaymentVolumeChart; 