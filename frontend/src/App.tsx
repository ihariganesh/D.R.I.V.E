import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'

// Pages
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import EventsPage from './pages/EventsPage'
import EmergencyPage from './pages/EmergencyPage'
import DecisionsPage from './pages/DecisionsPage'
import SimulationsPage from './pages/SimulationsPage'
import CamerasPage from './pages/CamerasPage'

// Layout
import Layout from './components/Layout'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check for auth token
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
  }, [])

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={() => setIsAuthenticated(true)} />} />
        
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Layout onLogout={() => setIsAuthenticated(false)}>
                <Dashboard />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        <Route
          path="/events"
          element={
            isAuthenticated ? (
              <Layout onLogout={() => setIsAuthenticated(false)}>
                <EventsPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        <Route
          path="/emergency"
          element={
            isAuthenticated ? (
              <Layout onLogout={() => setIsAuthenticated(false)}>
                <EmergencyPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        <Route
          path="/decisions"
          element={
            isAuthenticated ? (
              <Layout onLogout={() => setIsAuthenticated(false)}>
                <DecisionsPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        <Route
          path="/simulations"
          element={
            isAuthenticated ? (
              <Layout onLogout={() => setIsAuthenticated(false)}>
                <SimulationsPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        <Route
          path="/cameras"
          element={
            isAuthenticated ? (
              <Layout onLogout={() => setIsAuthenticated(false)}>
                <CamerasPage />
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </Router>
  )
}

export default App
