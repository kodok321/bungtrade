import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Trading from './pages/Trading'
import Signals from './pages/Signals'
import Backtest from './pages/Backtest'
import Settings from './pages/Settings'
import Exchange from './pages/Exchange'
import PaperTrading from './pages/PaperTrading'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen"><div className="animate-spin w-8 h-8 border-2 border-accent-blue border-t-transparent rounded-full" /></div>
  if (!user) return <Navigate to="/login" />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="trading" element={<Trading />} />
        <Route path="signals" element={<Signals />} />
        <Route path="backtest" element={<Backtest />} />
        <Route path="paper" element={<PaperTrading />} />
        <Route path="exchange" element={<Exchange />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
