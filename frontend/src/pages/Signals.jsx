import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Brain, RefreshCw, TrendingUp, TrendingDown, Search } from 'lucide-react'
import api from '../services/api'

function SignalCard({ signal }) {
  const isBuy = signal.side === 'BUY'
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card p-5 border-l-4 ${isBuy ? 'border-l-accent-green' : 'border-l-accent-red'}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {isBuy ? <TrendingUp size={18} className="text-accent-green" /> : <TrendingDown size={18} className="text-accent-red" />}
          <span className="font-bold text-lg">{signal.symbol}</span>
        </div>
        <span className={`text-sm font-medium px-3 py-1 rounded-full ${isBuy ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red'}`}>
          {signal.side}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <p className="text-xs text-dark-400">Confidence</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${signal.confidence > 70 ? 'bg-accent-green' : signal.confidence > 50 ? 'bg-accent-yellow' : 'bg-accent-red'}`} style={{ width: `${signal.confidence}%` }} />
            </div>
            <span className="text-sm font-bold">{signal.confidence}%</span>
          </div>
        </div>
        <div>
          <p className="text-xs text-dark-400">Trend</p>
          <p className="text-sm font-medium">{signal.trend || 'N/A'}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="bg-dark-900 rounded-lg p-2 text-center">
          <p className="text-xs text-dark-400">Entry</p>
          <p className="font-medium">${signal.entry_price?.toLocaleString()}</p>
        </div>
        <div className="bg-dark-900 rounded-lg p-2 text-center">
          <p className="text-xs text-accent-green">TP</p>
          <p className="font-medium text-accent-green">${signal.take_profit?.toLocaleString() || '-'}</p>
        </div>
        <div className="bg-dark-900 rounded-lg p-2 text-center">
          <p className="text-xs text-accent-red">SL</p>
          <p className="font-medium text-accent-red">${signal.stop_loss?.toLocaleString() || '-'}</p>
        </div>
      </div>

      <p className="text-xs text-dark-500 mt-3">
        {signal.strategy} | {new Date(signal.created_at).toLocaleString()}
      </p>
    </motion.div>
  )
}

export default function Signals() {
  const [signals, setSignals] = useState([])
  const [scanResults, setScanResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [genSymbol, setGenSymbol] = useState('BTCUSDT')

  useEffect(() => {
    fetchSignals()
  }, [])

  const fetchSignals = async () => {
    try {
      const res = await api.get('/api/signals/')
      setSignals(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const generateSignal = async () => {
    setLoading(true)
    try {
      await api.post(`/api/signals/generate?symbol=${genSymbol}`)
      fetchSignals()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate signal')
    } finally {
      setLoading(false)
    }
  }

  const scanPairs = async () => {
    setScanning(true)
    try {
      const res = await api.get('/api/signals/scanner')
      setScanResults(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setScanning(false)
    }
  }

  const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT']

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">AI Signals</h1>
          <p className="text-dark-400 text-sm">AI-powered trading analysis & multi-pair scanner</p>
        </div>
        <div className="flex items-center gap-3">
          <select value={genSymbol} onChange={e => setGenSymbol(e.target.value)} className="input-field w-40">
            {symbols.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <button onClick={generateSignal} disabled={loading} className="btn-primary flex items-center gap-2 disabled:opacity-50">
            <Brain size={16} /> {loading ? 'Analyzing...' : 'Generate Signal'}
          </button>
          <button onClick={scanPairs} disabled={scanning} className="btn-primary flex items-center gap-2 bg-accent-purple hover:bg-accent-purple/80 disabled:opacity-50">
            <Search size={16} /> {scanning ? 'Scanning...' : 'Scan All Pairs'}
          </button>
        </div>
      </div>

      {scanResults.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Scanner Results</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-dark-400 border-b border-dark-800">
                  <th className="text-left py-2">Symbol</th>
                  <th className="text-left py-2">Side</th>
                  <th className="text-right py-2">Confidence</th>
                  <th className="text-left py-2">Trend</th>
                  <th className="text-right py-2">Entry</th>
                  <th className="text-right py-2">TP</th>
                  <th className="text-right py-2">SL</th>
                </tr>
              </thead>
              <tbody>
                {scanResults.map((s, i) => (
                  <tr key={i} className="border-b border-dark-800/50">
                    <td className="py-2 font-medium">{s.symbol}</td>
                    <td className={`py-2 ${s.side === 'BUY' ? 'text-accent-green' : 'text-accent-red'}`}>{s.side}</td>
                    <td className="py-2 text-right font-bold">{s.confidence?.toFixed(1)}%</td>
                    <td className="py-2">{s.trend}</td>
                    <td className="py-2 text-right">${s.entry_price?.toLocaleString()}</td>
                    <td className="py-2 text-right text-accent-green">${s.take_profit?.toLocaleString()}</td>
                    <td className="py-2 text-right text-accent-red">${s.stop_loss?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {signals.map(s => <SignalCard key={s.id} signal={s} />)}
        {signals.length === 0 && (
          <div className="col-span-full text-center py-16 text-dark-500">
            <Brain size={48} className="mx-auto mb-4 opacity-30" />
            <p>No signals yet. Generate your first AI signal.</p>
          </div>
        )}
      </div>
    </div>
  )
}
