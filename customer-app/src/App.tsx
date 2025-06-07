import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'

// Import pages
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import Dashboard from './pages/Dashboard'
import PaymentPage from './pages/PaymentPage'
import WalletPage from './pages/WalletPage'
import SubscriptionsPage from './pages/SubscriptionsPage'
import TransactionHistory from './pages/TransactionHistory'
import ProfilePage from './pages/ProfilePage'
import SupportPage from './pages/SupportPage'

// Import components
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuth } from './contexts/AuthContext'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }}
      >
        <div className="loading-spinner" />
      </Box>
    )
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={!isAuthenticated ? <LandingPage /> : <Navigate to="/dashboard" replace />} />
      <Route path="/auth" element={!isAuthenticated ? <AuthPage /> : <Navigate to="/dashboard" replace />} />
      
      {/* Protected routes */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/pay" element={<PaymentPage />} />
                <Route path="/wallet" element={<WalletPage />} />
                <Route path="/subscriptions" element={<SubscriptionsPage />} />
                <Route path="/transactions" element={<TransactionHistory />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/support" element={<SupportPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App 