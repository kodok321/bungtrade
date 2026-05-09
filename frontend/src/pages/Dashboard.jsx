import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, Activity, Target, BarChart3, Zap, AlertTriangle } from 'lucide-react'
import api from '../services/api'

function StatCard({ icon: Icon, label, value, change, color = 'blue' }) {
  const colors = {
    blue: 'text-accent-blue bg-accent-blue/10 border-accent-blue/20',
    green: 'text-accent-green bg-accent-green/10 border-accent-green/20',
    red: 'text-accent-red bg-accent-red/10 border-accent-red/20',
    yellow: 'text-accent-yellow bg-accent-yellow/10 border-accent-yellow/20',
    purple: 'text-accent-purple bg-accent-purple/10 border-accent-purple/20',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <div className="flex items-center justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color]}`}>
          <Icon size={20} />
        </div>
        {change !== undefined && (
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${change >= 0 ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red'}`}>
            {change >= 0 ? '+' : ''}{change}%
          </span>
        )}
      </div>
      <p className="stat-value">{value}</p>
      <p className="stat-label mt-1">{label}</p>
    </motion.div>
  )
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [fearGreed, setFearGreed] = useState(null)
  const [topMovers, setTopMovers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, fgRes, moversRes] = await Promise.allSettled([
          api.get('/api/dashboard/'),
          api.get('/api/market/fear-greed'),
          api.get('/api/market/top-movers'),
        ])
        if (dashRes.status === 'fulfilled') setDashboard(dashRes.value.data)
        if (fgRes.status === 'fulfilled') setFearGreed(fgRes.value.data)
        if (moversRes.status === 'fulfilled') setTopMovers(moversRes.value.data?.slice(0, 10) || [])
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="flex items-center justify-center h-full"><div className="animate-spin w-8 h-8 border-2 border-accent-blue border-t-transparent rounded-full" /></div>

  const d = dashboard || { total_balance: 10000, unrealized_pnl: 0, daily_profit: 0, winrate: 0, active_positions: 0, total_trades: 0, equity_curve: [] }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-dark-400 text-sm">AI Trading Overview</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
          <span className="text-xs text-dark-400">Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={DollarSign} label="Total Balance" value={`$${d.total_balance.toLocaleString()}`} color="blue" />
        <StatCard icon={d.unrealized_pnl >= 0 ? TrendingUp : TrendingDown} label="Unrealized PNL" value={`${d.unrealized_pnl >= 0 ? '+' : ''}$${d.unrealized_pnl.toLocaleString()}`} color={d.unrealized_pnl >= 0 ? 'green' : 'red'} />
        <StatCard icon={Activity} label="Daily Profit" value={`${d.daily_profit >= 0 ? '+' : ''}$${d.daily_profit.toLocaleString()}`} color={d.daily_profit >= 0 ? 'green' : 'red'} />
        <StatCard icon={Target} label="Winrate" value={`${d.winrate}%`} color="purple" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard icon={BarChart3} label="Active Positions" value={d.active_positions} color="yellow" />
        <StatCard icon={Zap} label="Total Trades" value={d.total_trades} color="blue" />
        <StatCard
          icon={AlertTriangle}
          label="Fear & Greed"
          value={fearGreed ? `${fearGreed.value} - ${fearGreed.value_classification}` : 'N/A'}
          color={fearGreed && parseInt(fearGreed.value) > 50 ? 'green' : 'red'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
          <div className="h-[300px]">
            {d.equity_curve.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={d.equity_curve}>
                  <defs>
                    <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2979ff" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#2979ff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 12 }} tickFormatter={v => v?.slice(5, 10)} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }} />
                  <Area type="monotone" dataKey="balance" stroke="#2979ff" fill="url(#balanceGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-dark-500">No data yet. Start trading to see your equity curve.</div>
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Top Movers</h3>
          <div className="space-y-3">
            {topMovers.length > 0 ? topMovers.map((m, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-dark-800 last:border-0">
                <div>
                  <p className="text-sm font-medium">{m.symbol}</p>
                  <p className="text-xs text-dark-400">${m.last?.toLocaleString()}</p>
                </div>
                <span className={`text-sm font-medium ${(m.change || 0) >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {(m.change || 0) >= 0 ? '+' : ''}{(m.change || 0).toFixed(2)}%
                </span>
              </div>
            )) : (
              <p className="text-dark-500 text-sm">Loading market data...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
