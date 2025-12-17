import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './services/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import VehicleMonitoring from './pages/VehicleMonitoring'
import ServiceCenterDashboard from './pages/ServiceCenterDashboard'
import ServiceCenterBookings from './pages/ServiceCenterBookings'
import ServiceCenterOngoing from './pages/ServiceCenterOngoing'
import ServiceCenterTechnicians from './pages/ServiceCenterTechnicians'
import ServiceCenterReviews from './pages/ServiceCenterReviews'
import ManufacturingDashboard from './pages/ManufacturingDashboard'
import SystemDashboard from './pages/SystemDashboard'
import ServiceHistory from './pages/ServiceHistory'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'

function App() {
  return (
    <AuthProvider>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          {/* Vehicle Monitoring - For Customers, Service Center, and Admin */}
          <Route
            path="/monitoring"
            element={
              <PrivateRoute>
                <Layout>
                  <VehicleMonitoring />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/service-center"
            element={
              <PrivateRoute requiredRole="service_center">
                <Layout>
                  <ServiceCenterDashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/service-center/bookings"
            element={
              <PrivateRoute requiredRole="service_center">
                <Layout>
                  <ServiceCenterBookings />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/service-center/ongoing"
            element={
              <PrivateRoute requiredRole="service_center">
                <Layout>
                  <ServiceCenterOngoing />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/service-center/technicians"
            element={
              <PrivateRoute requiredRole="service_center">
                <Layout>
                  <ServiceCenterTechnicians />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/service-center/reviews"
            element={
              <PrivateRoute requiredRole="service_center">
                <Layout>
                  <ServiceCenterReviews />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/service-history"
            element={
              <PrivateRoute requiredRole="customer">
                <Layout>
                  <ServiceHistory />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/manufacturing"
            element={
              <PrivateRoute requiredRole="manufacturing">
                <Layout>
                  <ManufacturingDashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/system"
            element={
              <PrivateRoute requiredRole="admin">
                <Layout>
                  <SystemDashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

