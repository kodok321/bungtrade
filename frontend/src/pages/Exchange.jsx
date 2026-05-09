import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link2, Plus, Trash2, Wifi, WifiOff, Eye, EyeOff } from 'lucide-react'
import api from '../services/api'

export default function Exchange() {
  const [keys, setKeys] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ api_key: '', api_secret: '', label: 'Default', trading_mode: 'spot', is_testnet: false })
  const [showSecret, setShowSecret] = useState(false)
  const [loading, setLoading] = useState(false)
  const [testResults, setTestResults] = useState({})

  useEffect(() => { fetchKeys() }, [])

  const fetchKeys = async () => {
    try {
      const res = await api.get('/api/exchange/keys')
      setKeys(res.data)
    } catch (err) { console.error(err) }
  }

  const addKey = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/api/exchange/keys', form)
      setForm({ api_key: '', api_secret: '', label: 'Default', trading_mode: 'spot', is_testnet: false })
      setShowForm(false)
      fetchKeys()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add key')
    } finally { setLoading(false) }
  }

  const deleteKey = async (id) => {
    if (!confirm('Delete this API key?')) return
    try {
      await api.delete(`/api/exchange/keys/${id}`)
      fetchKeys()
    } catch (err) { alert('Failed to delete') }
  }

  const testConnection = async (id) => {
    setTestResults(prev => ({ ...prev, [id]: { loading: true } }))
    try {
      const res = await api.post(`/api/exchange/test-connection/${id}`)
      setTestResults(prev => ({ ...prev, [id]: res.data }))
    } catch (err) {
      setTestResults(prev => ({ ...prev, [id]: { success: false, message: 'Connection failed' } }))
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Exchange Connection</h1>
          <p className="text-dark-400 text-sm">Connect your Binance account via API</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Add API Key
        </button>
      </div>

      {showForm && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Add Binance API Key</h3>
          <form onSubmit={addKey} className="space-y-4">
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Label</label>
              <input type="text" value={form.label} onChange={e => setForm({ ...form, label: e.target.value })} className="input-field" placeholder="Account label" />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">API Key</label>
              <input type="text" value={form.api_key} onChange={e => setForm({ ...form, api_key: e.target.value })} className="input-field font-mono text-sm" placeholder="Enter your Binance API Key" required />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Secret Key</label>
              <div className="relative">
                <input type={showSecret ? 'text' : 'password'} value={form.api_secret} onChange={e => setForm({ ...form, api_secret: e.target.value })} className="input-field font-mono text-sm pr-10" placeholder="Enter your Binance Secret Key" required />
                <button type="button" onClick={() => setShowSecret(!showSecret)} className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-400">
                  {showSecret ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-dark-400 mb-1 block">Trading Mode</label>
                <select value={form.trading_mode} onChange={e => setForm({ ...form, trading_mode: e.target.value })} className="input-field">
                  <option value="spot">Spot</option>
                  <option value="futures">Futures</option>
                </select>
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.is_testnet} onChange={e => setForm({ ...form, is_testnet: e.target.checked })} className="w-4 h-4 rounded border-dark-600" />
                  <span className="text-sm">Testnet</span>
                </label>
              </div>
            </div>
            <div className="flex gap-3">
              <button type="submit" disabled={loading} className="btn-primary disabled:opacity-50">
                {loading ? 'Saving...' : 'Save API Key'}
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors">Cancel</button>
            </div>
          </form>
          <div className="mt-4 p-3 bg-dark-900 rounded-lg">
            <p className="text-xs text-dark-400">
              Your API keys are encrypted with AES-256 before being stored. We never store plain-text keys.
              For security, enable IP whitelist in your Binance API settings and only grant necessary permissions.
            </p>
          </div>
        </motion.div>
      )}

      <div className="space-y-4">
        {keys.map(key => (
          <motion.div key={key.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-accent-yellow/10 rounded-lg flex items-center justify-center">
                  <Link2 size={20} className="text-accent-yellow" />
                </div>
                <div>
                  <p className="font-medium">{key.label}</p>
                  <p className="text-xs text-dark-400 font-mono">{key.api_key_masked}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${key.trading_mode === 'futures' ? 'bg-accent-purple/10 text-accent-purple' : 'bg-accent-blue/10 text-accent-blue'}`}>
                  {key.trading_mode.toUpperCase()}
                </span>
                {key.is_testnet && <span className="text-xs px-2 py-1 rounded-full bg-accent-yellow/10 text-accent-yellow">TESTNET</span>}
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => testConnection(key.id)} className="btn-primary text-sm py-1.5 flex items-center gap-1">
                  <Wifi size={14} /> Test
                </button>
                <button onClick={() => deleteKey(key.id)} className="p-2 text-dark-400 hover:text-accent-red transition-colors">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            {testResults[key.id] && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${testResults[key.id].loading ? 'bg-dark-800 text-dark-400' : testResults[key.id].success ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red'}`}>
                {testResults[key.id].loading ? 'Testing connection...' : testResults[key.id].message}
                {testResults[key.id].balance && (
                  <p className="mt-1 text-xs">USDT Balance: {testResults[key.id].balance.total_usdt || testResults[key.id].balance.total_balance || 'N/A'}</p>
                )}
              </div>
            )}
          </motion.div>
        ))}
        {keys.length === 0 && !showForm && (
          <div className="text-center py-16 text-dark-500">
            <Link2 size={48} className="mx-auto mb-4 opacity-30" />
            <p>No API keys configured. Add your Binance API key to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}
