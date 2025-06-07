import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Grid,
  useTheme,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
  Storage,
  Memory,
  Speed,
  Cloud,
} from '@mui/icons-material';

interface SystemHealthIndicatorProps {
  status: 'healthy' | 'warning' | 'critical';
  health: number;
  components: {
    database: string;
    cache: string;
    queue: string;
    payments: string;
  };
  loading?: boolean;
}

const SystemHealthIndicator: React.FC<SystemHealthIndicatorProps> = ({
  status,
  health,
  components,
  loading = false,
}) => {
  const theme = useTheme();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'critical':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle sx={{ color: theme.palette.success.main }} />;
      case 'warning':
        return <Warning sx={{ color: theme.palette.warning.main }} />;
      case 'critical':
        return <Error sx={{ color: theme.palette.error.main }} />;
      default:
        return <Warning sx={{ color: theme.palette.grey[500] }} />;
    }
  };

  const getComponentIcon = (component: string) => {
    switch (component) {
      case 'database':
        return <Storage fontSize="small" />;
      case 'cache':
        return <Memory fontSize="small" />;
      case 'queue':
        return <Speed fontSize="small" />;
      case 'payments':
        return <Cloud fontSize="small" />;
      default:
        return <CheckCircle fontSize="small" />;
    }
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          {getStatusIcon(status)}
          <Typography variant="h6" sx={{ ml: 1, fontWeight: 600 }}>
            System Health
          </Typography>
          <Chip
            label={status.toUpperCase()}
            size="small"
            sx={{
              ml: 'auto',
              backgroundColor: getStatusColor(status) + '20',
              color: getStatusColor(status),
              fontWeight: 600,
            }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body1" fontWeight={500}>
              Overall Health
            </Typography>
            <Typography variant="body1" fontWeight={600}>
              {loading ? '...' : `${health}%`}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={loading ? 0 : health}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: theme.palette.grey[200],
              '& .MuiLinearProgress-bar': {
                backgroundColor: getStatusColor(status),
                borderRadius: 4,
              },
            }}
          />
        </Box>

        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
          Component Status
        </Typography>

        <Grid container spacing={2}>
          {Object.entries(components).map(([component, componentStatus]) => (
            <Grid item xs={6} key={component}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  p: 1.5,
                  borderRadius: 2,
                  backgroundColor: theme.palette.grey[50],
                  border: `1px solid ${theme.palette.grey[200]}`,
                }}
              >
                <Box sx={{ mr: 1, color: getStatusColor(componentStatus) }}>
                  {getComponentIcon(component)}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    {component.charAt(0).toUpperCase() + component.slice(1)}
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {componentStatus}
                  </Typography>
                </Box>
                <Box sx={{ color: getStatusColor(componentStatus) }}>
                  {componentStatus === 'healthy' ? (
                    <CheckCircle fontSize="small" />
                  ) : componentStatus === 'warning' ? (
                    <Warning fontSize="small" />
                  ) : (
                    <Error fontSize="small" />
                  )}
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SystemHealthIndicator; 