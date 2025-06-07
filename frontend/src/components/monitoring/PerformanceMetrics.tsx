import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Grid,
  Box,
  LinearProgress,
  Chip,
  useTheme,
} from '@mui/material';
import {
  Speed,
  Memory,
  Storage,
  NetworkCheck,
} from '@mui/icons-material';

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  threshold: number;
  icon: React.ReactElement;
}

interface PerformanceMetricsProps {
  metrics?: {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
  };
  loading?: boolean;
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  metrics = {
    cpu: 45,
    memory: 67,
    disk: 23,
    network: 12,
  },
  loading = false,
}) => {
  const theme = useTheme();

  const performanceMetrics: PerformanceMetric[] = [
    {
      name: 'CPU Usage',
      value: metrics.cpu,
      unit: '%',
      threshold: 80,
      icon: <Speed />,
    },
    {
      name: 'Memory Usage',
      value: metrics.memory,
      unit: '%',
      threshold: 85,
      icon: <Memory />,
    },
    {
      name: 'Disk Usage',
      value: metrics.disk,
      unit: '%',
      threshold: 90,
      icon: <Storage />,
    },
    {
      name: 'Network I/O',
      value: metrics.network,
      unit: 'MB/s',
      threshold: 100,
      icon: <NetworkCheck />,
    },
  ];

  const getStatusColor = (value: number, threshold: number) => {
    if (value >= threshold) {
      return theme.palette.error.main;
    }
    if (value >= threshold * 0.7) {
      return theme.palette.warning.main;
    }
    return theme.palette.success.main;
  };

  const getStatusText = (value: number, threshold: number) => {
    if (value >= threshold) {
      return 'Critical';
    }
    if (value >= threshold * 0.7) {
      return 'Warning';
    }
    return 'Normal';
  };

  return (
    <Card elevation={2}>
      <CardHeader
        title="Performance Metrics"
        subheader="Real-time system performance monitoring"
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ pt: 0 }}>
        <Grid container spacing={3}>
          {performanceMetrics.map((metric) => (
            <Grid item xs={12} sm={6} key={metric.name}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  backgroundColor: theme.palette.grey[50],
                  border: `1px solid ${theme.palette.grey[200]}`,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1,
                      backgroundColor: theme.palette.primary.main + '20',
                      color: theme.palette.primary.main,
                      mr: 2,
                    }}
                  >
                    {metric.icon}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {metric.name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6" fontWeight={700}>
                        {loading ? '...' : metric.value}
                        <Typography component="span" variant="body2" color="text.secondary">
                          {metric.unit}
                        </Typography>
                      </Typography>
                      <Chip
                        label={getStatusText(metric.value, metric.threshold)}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(metric.value, metric.threshold) + '20',
                          color: getStatusColor(metric.value, metric.threshold),
                          fontWeight: 600,
                          fontSize: '0.7rem',
                        }}
                      />
                    </Box>
                  </Box>
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={loading ? 0 : Math.min(metric.value, 100)}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: theme.palette.grey[200],
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getStatusColor(metric.value, metric.threshold),
                      borderRadius: 4,
                    },
                  }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    0{metric.unit}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Threshold: {metric.threshold}{metric.unit}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 3, p: 2, backgroundColor: theme.palette.info.main + '10', borderRadius: 2 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Performance Summary:</strong> System is operating within normal parameters. 
            CPU and network usage are low, while memory usage is moderate. All metrics are below critical thresholds.
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PerformanceMetrics; 