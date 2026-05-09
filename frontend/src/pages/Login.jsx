import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { motion } from 'framer-motion'
import { TrendingUp, Eye, EyeOff } from 'lucide-react'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-accent-blue rounded-2xl flex items-center justify-center mx-auto mb-4">
            <TrendingUp size={32} />
          </div>
          <h1 className="text-3xl font-bold">BungTrade</h1>
          <p className="text-dark-400 mt-2">AI Trading Platform</p>
        </div>

        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold mb-6">Sign In</h2>
          {error && <div className="bg-accent-red/10 border border-accent-red/20 rounded-lg px-4 py-3 mb-4 text-sm text-accent-red">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Username</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)} className="input-field" placeholder="Enter username" required />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Password</label>
              <div className="relative">
                <input type={showPass ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} className="input-field pr-10" placeholder="Enter password" required />
                <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-400">
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3 disabled:opacity-50">
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
          <p className="text-center text-sm text-dark-400 mt-6">
            Don't have an account? <Link to="/register" className="text-accent-blue hover:underline">Register</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
