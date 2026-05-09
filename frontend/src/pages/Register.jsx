import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { motion } from 'framer-motion'
import { TrendingUp } from 'lucide-react'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(username, email, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-accent-blue rounded-2xl flex items-center justify-center mx-auto mb-4">
            <TrendingUp size={32} />
          </div>
          <h1 className="text-3xl font-bold">BungTrade</h1>
          <p className="text-dark-400 mt-2">Create your account</p>
        </div>
        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold mb-6">Register</h2>
          {error && <div className="bg-accent-red/10 border border-accent-red/20 rounded-lg px-4 py-3 mb-4 text-sm text-accent-red">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Username</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)} className="input-field" required />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="input-field" required />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="input-field" required />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3 disabled:opacity-50">
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
          <p className="text-center text-sm text-dark-400 mt-6">
            Already have an account? <Link to="/login" className="text-accent-blue hover:underline">Sign In</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
