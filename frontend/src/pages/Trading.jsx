import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { TrendingUp, TrendingDown, ShoppingCart, X } from 'lucide-react'
import api from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'

export default function Trading() {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [klines, setKlines] = useState([])
  const [positions, setPositions] = useState([])
  const [orderForm, setOrderForm] = useState({ side: 'buy', quantity: '', price: '', tp: '', sl: '' })
  const [loading, setLoading] = useState(false)
  const [interval, setTimeInterval] = useState('1h')
  const { data: tickerData } = useWebSocket(`/ws/market/${symbol}?stream=ticker`)

  useEffect(() => {
    fetchKlines()
    fetchPositions()
  }, [symbol, interval])

  const fetchKlines = async () => {
    try {
      const res = await api.get(`/api/market/klines/${symbol}?interval=${interval}&limit=100`)
      setKlines(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchPositions = async () => {
    try {
      const res = await api.get('/api/trading/positions')
      setPositions(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleOrder = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/api/trading/order', {
        symbol,
        side: orderForm.side,
        quantity: parseFloat(orderForm.quantity),
        price: orderForm.price ? parseFloat(orderForm.price) : null,
        take_profit: orderForm.tp ? parseFloat(orderForm.tp) : null,
        stop_loss: orderForm.sl ? parseFloat(orderForm.sl) : null,
        is_paper: true,
      })
      setOrderForm({ ...orderForm, quantity: '', price: '', tp: '', sl: '' })
      fetchPositions()
    } catch (err) {
      alert(err.response?.data?.detail || 'Order failed')
    } finally {
      setLoading(false)
    }
  }

  const closeTrade = async (id) => {
    try {
      await api.post(`/api/trading/close/${id}`)
      fetchPositions()
    } catch (err) {
      alert('Failed to close trade')
    }
  }

  const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'BNBUSDT']
  const intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
  const currentPrice = tickerData?.c ? parseFloat(tickerData.c) : (klines.length > 0 ? klines[klines.length - 1]?.close : 0)

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Trading</h1>
          <p className="text-dark-400 text-sm">Chart & Order Management</p>
        </div>
        <div className="flex items-center gap-3">
          <select value={symbol} onChange={e => setSymbol(e.target.value)} className="input-field w-40">
            {symbols.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <div className="flex gap-1 bg-dark-900 rounded-lg p-1">
            {intervals.map(i => (
              <button key={i} onClick={() => setTimeInterval(i)} className={`px-3 py-1 rounded text-xs font-medium transition-colors ${interval === i ? 'bg-accent-blue text-white' : 'text-dark-400 hover:text-white'}`}>{i}</button>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 glass-card p-4">
        <span className="text-2xl font-bold">${currentPrice?.toLocaleString()}</span>
        {tickerData && (
          <>
            <span className={`text-sm font-medium ${parseFloat(tickerData.P || 0) >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
              {parseFloat(tickerData.P || 0) >= 0 ? '+' : ''}{parseFloat(tickerData.P || 0).toFixed(2)}%
            </span>
            <span className="text-xs text-dark-400">Vol: {parseFloat(tickerData.v || 0).toLocaleString()}</span>
            <span className="text-xs text-dark-400">H: ${parseFloat(tickerData.h || 0).toLocaleString()}</span>
            <span className="text-xs text-dark-400">L: ${parseFloat(tickerData.l || 0).toLocaleString()}</span>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Price Chart - {symbol}</h3>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={klines}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={t => new Date(t * 1000).toLocaleTimeString()} />
                <YAxis domain={['auto', 'auto']} tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }} labelFormatter={t => new Date(t * 1000).toLocaleString()} />
                <Line type="monotone" dataKey="close" stroke="#2979ff" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="h-[120px] mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={klines}>
                <XAxis dataKey="time" tick={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Bar dataKey="volume" fill="#2979ff33" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Place Order</h3>
          <form onSubmit={handleOrder} className="space-y-4">
            <div className="flex gap-2">
              <button type="button" onClick={() => setOrderForm({ ...orderForm, side: 'buy' })} className={`flex-1 py-2 rounded-lg font-medium text-sm transition-colors ${orderForm.side === 'buy' ? 'bg-accent-green text-white' : 'bg-dark-800 text-dark-400'}`}>
                <TrendingUp size={14} className="inline mr-1" /> Buy
              </button>
              <button type="button" onClick={() => setOrderForm({ ...orderForm, side: 'sell' })} className={`flex-1 py-2 rounded-lg font-medium text-sm transition-colors ${orderForm.side === 'sell' ? 'bg-accent-red text-white' : 'bg-dark-800 text-dark-400'}`}>
                <TrendingDown size={14} className="inline mr-1" /> Sell
              </button>
            </div>
            <div>
              <label className="text-xs text-dark-400 mb-1 block">Price (USDT)</label>
              <input type="number" step="any" value={orderForm.price} onChange={e => setOrderForm({ ...orderForm, price: e.target.value })} className="input-field text-sm" placeholder="Market price" />
            </div>
            <div>
              <label className="text-xs text-dark-400 mb-1 block">Quantity</label>
              <input type="number" step="any" value={orderForm.quantity} onChange={e => setOrderForm({ ...orderForm, quantity: e.target.value })} className="input-field text-sm" placeholder="0.00" required />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-dark-400 mb-1 block">TP</label>
                <input type="number" step="any" value={orderForm.tp} onChange={e => setOrderForm({ ...orderForm, tp: e.target.value })} className="input-field text-sm" placeholder="Take Profit" />
              </div>
              <div>
                <label className="text-xs text-dark-400 mb-1 block">SL</label>
                <input type="number" step="any" value={orderForm.sl} onChange={e => setOrderForm({ ...orderForm, sl: e.target.value })} className="input-field text-sm" placeholder="Stop Loss" />
              </div>
            </div>
            <button type="submit" disabled={loading} className={`w-full py-3 rounded-lg font-medium text-sm ${orderForm.side === 'buy' ? 'btn-success' : 'btn-danger'} disabled:opacity-50`}>
              {loading ? 'Processing...' : `${orderForm.side.toUpperCase()} ${symbol}`}
            </button>
          </form>
        </div>
      </div>

      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Open Positions</h3>
          <span className="text-sm text-dark-400">{positions.length} active</span>
        </div>
        {positions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-dark-400 border-b border-dark-800">
                  <th className="text-left py-3 px-2">Symbol</th>
                  <th className="text-left py-3 px-2">Side</th>
                  <th className="text-right py-3 px-2">Entry</th>
                  <th className="text-right py-3 px-2">Qty</th>
                  <th className="text-right py-3 px-2">TP</th>
                  <th className="text-right py-3 px-2">SL</th>
                  <th className="text-right py-3 px-2">PNL</th>
                  <th className="text-right py-3 px-2">Action</th>
                </tr>
              </thead>
              <tbody>
                {positions.map(p => (
                  <tr key={p.id} className="border-b border-dark-800/50 hover:bg-dark-800/30">
                    <td className="py-3 px-2 font-medium">{p.symbol}</td>
                    <td className={`py-3 px-2 ${p.side === 'buy' ? 'text-accent-green' : 'text-accent-red'}`}>{p.side.toUpperCase()}</td>
                    <td className="py-3 px-2 text-right">${p.entry_price}</td>
                    <td className="py-3 px-2 text-right">{p.quantity}</td>
                    <td className="py-3 px-2 text-right text-accent-green">{p.take_profit || '-'}</td>
                    <td className="py-3 px-2 text-right text-accent-red">{p.stop_loss || '-'}</td>
                    <td className={`py-3 px-2 text-right font-medium ${p.pnl >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>${p.pnl.toFixed(2)}</td>
                    <td className="py-3 px-2 text-right">
                      <button onClick={() => closeTrade(p.id)} className="text-accent-red hover:text-accent-red/80"><X size={16} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-dark-500 text-center py-8">No open positions</p>
        )}
      </div>
    </div>
  )
}
