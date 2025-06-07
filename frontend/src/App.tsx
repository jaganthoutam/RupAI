import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { HelmetProvider } from 'react-helmet-async';
import { ErrorBoundary } from 'react-error-boundary';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Auth Components
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginForm from './components/auth/LoginForm';

// Layout Components
import DashboardLayout from './components/layout/DashboardLayout';
import LoadingSpinner from './components/common/LoadingSpinner';
import ErrorFallback from './components/common/ErrorFallback';

// Page Components
import Dashboard from './pages/Dashboard';
import Payments from './pages/Payments';
import WalletManagement from './pages/WalletManagement';
import PaymentAnalytics from './pages/PaymentAnalytics';
import UserAnalytics from './pages/UserAnalytics';
import RevenueAnalytics from './pages/RevenueAnalytics';
import SystemMonitoring from './pages/SystemMonitoring';
import FraudDetection from './pages/FraudDetection';
import AlertsManagement from './pages/AlertsManagement';
import AuditLogs from './pages/AuditLogs';
import Settings from './pages/Settings';
import AIAssistant from './components/AIAssistant';

// Hooks and Utils
// import { useSystemStore } from './store/systemStore';

// Create a theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ff9800',
    },
    success: {
      main: '#4caf50',
    },
    info: {
      main: '#2196f3',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
    },
    body2: {
      fontSize: '0.875rem',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  in: {
    opacity: 1,
    y: 0,
  },
  out: {
    opacity: 0,
    y: -20,
  },
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.3,
};

function App() {
  // const { isLoading, error } = useSystemStore();

  // if (isLoading) {
  //   return <LoadingSpinner />;
  // }

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        console.error('Application error:', error, errorInfo);
        // Send to error tracking service in production
      }}
    >
      <HelmetProvider>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <CssBaseline />
              
              <AuthProvider>
                <Router>
                  <Routes>
                    {/* Public Login Route */}
                    <Route path="/login" element={<LoginForm />} />
                    
                    {/* Protected Admin Routes */}
                    <Route path="/*" element={
                      <ProtectedRoute>
                        <DashboardLayout>
                          <AnimatePresence mode="wait">
                            <Routes>
                              <Route
                                path="/"
                                element={
                                  <motion.div
                                    key="dashboard"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <Dashboard />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/ai-assistant"
                                element={
                                  <motion.div
                                    key="ai-assistant"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <AIAssistant />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/payments"
                                element={
                                  <motion.div
                                    key="payments"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <Payments />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/wallet-management"
                                element={
                                  <motion.div
                                    key="wallet-management"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <WalletManagement />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/analytics/payments"
                                element={
                                  <motion.div
                                    key="payment-analytics"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <PaymentAnalytics />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/analytics/users"
                                element={
                                  <motion.div
                                    key="user-analytics"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <UserAnalytics />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/analytics/revenue"
                                element={
                                  <motion.div
                                    key="revenue-analytics"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <RevenueAnalytics />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/monitoring/system"
                                element={
                                  <motion.div
                                    key="system-monitoring"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <SystemMonitoring />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/monitoring/alerts"
                                element={
                                  <motion.div
                                    key="alerts-management"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <AlertsManagement />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/security/fraud"
                                element={
                                  <motion.div
                                    key="fraud-detection"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <FraudDetection />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/audit/logs"
                                element={
                                  <motion.div
                                    key="audit-logs"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <AuditLogs />
                                  </motion.div>
                                }
                              />
                              
                              <Route
                                path="/settings"
                                element={
                                  <motion.div
                                    key="settings"
                                    initial="initial"
                                    animate="in"
                                    exit="out"
                                    variants={pageVariants}
                                    transition={pageTransition}
                                  >
                                    <Settings />
                                  </motion.div>
                                }
                              />
                              
                              {/* Redirect unknown routes to dashboard */}
                              <Route path="*" element={<Navigate to="/" replace />} />
                            </Routes>
                          </AnimatePresence>
                        </DashboardLayout>
                      </ProtectedRoute>
                    } />
                  </Routes>
                </Router>
              </AuthProvider>
              
              {/* Global notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#ffffff',
                    color: '#1f2937',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb',
                  },
                  success: {
                    iconTheme: {
                      primary: '#10b981',
                      secondary: '#ffffff',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#ffffff',
                    },
                  },
                }}
              />
            </LocalizationProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </HelmetProvider>
    </ErrorBoundary>
  );
}

export default App; 