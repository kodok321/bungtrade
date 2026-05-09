import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { History, Play } from 'lucide-react'
import api from '../services/api'

export default function Backtest() {
  const [form, setForm] = useState({ strategy: 'ema_cross', symbol: 'BTCUSDT', timeframe: '1h', start_date: '2024-01-01', end_date: '2024-12-31', initial_balance: 10000 })
  const [results, setResults] = useState([])
  const [current, setCurrent] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchResults()
  }, [])

  const fetchResults = async () => {
    try {
      const res = await api.get('/api/backtest/results')
      setResults(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const runBacktest = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.post('/api/backtest/run', form)
      setCurrent(res.data)
      fetchResults()
    } catch (err) {
      alert(err.response?.data?.detail || 'Backtest failed')
    } finally {
      setLoading(false)
    }
  }

  const strategies = ['ema_cross', 'rsi', 'macd', 'scalping', 'breakout']
  const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'BNBUSDT']

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Backtesting</h1>
        <p className="text-dark-400 text-sm">Test strategies against historical data</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Configuration</h3>
          <form onSubmit={runBacktest} className="space-y-4">
            <div>
              <label className="text-xs text-dark-400 mb-1 block">Strategy</label>
              <select value={form.strategy} onChange={e => setForm({ ...form, strategy: e.target.value })} className="input-field">
                {strategies.map(s => <option key={s} value={s}>{s.replace('_', ' ').toUpperCase()}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-dark-400 mb-1 block">Symbol</label>
              <select value={form.symbol} onChange={e => setForm({ ...form, symbol: e.target.value })} className="input-field">
                {symbols.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-dark-400 mb-1 block">Timeframe</label>
              <select value={form.timeframe} onChange={e => setForm({ ...form, timeframe: e.target.value })} className="input-field">
                {['15m', '1h', '4h', '1d'].map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-dark-400 mb-1 block">Start Date</label>
                <input type="date" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} className="input-field" />
              </div>
              <div>
                <label className="text-xs text-dark-400 mb-1 block">End Date</label>
                <input type="date" value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} className="input-field" />
              </div>
            </div>
            <div>
              <label className="text-xs text-dark-400 mb-1 block">Initial Balance</label>
              <input type="number" value={form.initial_balance} onChange={e => setForm({ ...form, initial_balance: parseFloat(e.target.value) })} className="input-field" />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50">
              <Play size={16} /> {loading ? 'Running...' : 'Run Backtest'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {current && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Results: {current.strategy.toUpperCase()} - {current.symbol}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Final Balance</p>
                  <p className="text-lg font-bold">${current.final_balance?.toLocaleString()}</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Win Rate</p>
                  <p className="text-lg font-bold text-accent-green">{current.winrate}%</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Max Drawdown</p>
                  <p className="text-lg font-bold text-accent-red">{current.max_drawdown}%</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Trades</p>
                  <p className="text-lg font-bold">{current.total_trades}</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Profit Factor</p>
                  <p className="text-lg font-bold">{current.profit_factor}</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Sharpe Ratio</p>
                  <p className="text-lg font-bold">{current.sharpe_ratio}</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Win / Loss</p>
                  <p className="text-lg font-bold">{current.winning_trades} / {current.losing_trades}</p>
                </div>
                <div className="bg-dark-900 rounded-lg p-3 text-center">
                  <p className="text-xs text-dark-400">Return</p>
                  <p className={`text-lg font-bold ${(current.final_balance - current.initial_balance) >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                    {((current.final_balance - current.initial_balance) / current.initial_balance * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              {current.equity_curve && current.equity_curve.length > 0 && (
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={current.equity_curve}>
                      <defs>
                        <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2979ff" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#2979ff" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={t => new Date(t * 1000).toLocaleDateString()} />
                      <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                      <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }} />
                      <Area type="monotone" dataKey="balance" stroke="#2979ff" fill="url(#eqGrad)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </motion.div>
          )}

          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">History</h3>
            {results.length > 0 ? (
              <div className="space-y-3">
                {results.map(r => (
                  <div key={r.id} onClick={() => setCurrent(r)} className="flex items-center justify-between bg-dark-900 rounded-lg p-3 cursor-pointer hover:bg-dark-800 transition-colors">
                    <div>
                      <span className="font-medium">{r.strategy.toUpperCase()}</span>
                      <span className="text-dark-400 text-sm ml-2">{r.symbol} - {r.timeframe}</span>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${(r.final_balance - r.initial_balance) >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                        {((r.final_balance - r.initial_balance) / r.initial_balance * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-dark-400">WR: {r.winrate}%</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-dark-500 text-center py-8">No backtest results yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
