import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FlaskConical, Plus, RotateCcw } from 'lucide-react'
import api from '../services/api'

export default function PaperTrading() {
  const [accounts, setAccounts] = useState([])
  const [trades, setTrades] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [balance, setBalance] = useState(10000)

  useEffect(() => {
    fetchAccounts()
    fetchTrades()
  }, [])

  const fetchAccounts = async () => {
    try {
      const res = await api.get('/api/paper/account')
      setAccounts(res.data)
    } catch (err) { console.error(err) }
  }

  const fetchTrades = async () => {
    try {
      const res = await api.get('/api/trading/history?limit=20')
      setTrades(res.data.filter(t => t.is_paper))
    } catch (err) { console.error(err) }
  }

  const createAccount = async () => {
    try {
      await api.post('/api/paper/account', { initial_balance: balance })
      setShowCreate(false)
      fetchAccounts()
    } catch (err) { alert('Failed to create account') }
  }

  const resetAccount = async (id) => {
    if (!confirm('Reset this paper account? All paper trades will remain.')) return
    try {
      await api.post(`/api/paper/reset/${id}`)
      fetchAccounts()
    } catch (err) { alert('Failed to reset') }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Paper Trading</h1>
          <p className="text-dark-400 text-sm">Risk-free simulated trading</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> New Account
        </button>
      </div>

      {showCreate && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Create Paper Account</h3>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="text-sm text-dark-400 mb-1 block">Initial Balance (USDT)</label>
              <input type="number" value={balance} onChange={e => setBalance(parseFloat(e.target.value))} className="input-field" />
            </div>
            <button onClick={createAccount} className="btn-primary">Create</button>
            <button onClick={() => setShowCreate(false)} className="px-4 py-2.5 bg-dark-800 rounded-lg">Cancel</button>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {accounts.map(acc => (
          <motion.div key={acc.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FlaskConical size={20} className="text-accent-purple" />
                <span className="font-medium">Paper #{acc.id}</span>
              </div>
              <button onClick={() => resetAccount(acc.id)} className="text-dark-400 hover:text-white"><RotateCcw size={16} /></button>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-dark-400 text-sm">Balance</span>
                <span className="font-bold">${acc.balance.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400 text-sm">Initial</span>
                <span className="text-sm">${acc.initial_balance.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400 text-sm">PNL</span>
                <span className={`font-medium ${acc.total_pnl >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {acc.total_pnl >= 0 ? '+' : ''}${acc.total_pnl.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400 text-sm">Trades</span>
                <span className="text-sm">{acc.total_trades}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-400 text-sm">Win/Loss</span>
                <span className="text-sm">{acc.winning_trades}/{acc.losing_trades}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">Paper Trade History</h3>
        {trades.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-dark-400 border-b border-dark-800">
                  <th className="text-left py-3">Symbol</th>
                  <th className="text-left py-3">Side</th>
                  <th className="text-right py-3">Entry</th>
                  <th className="text-right py-3">Exit</th>
                  <th className="text-right py-3">Qty</th>
                  <th className="text-right py-3">PNL</th>
                  <th className="text-left py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {trades.map(t => (
                  <tr key={t.id} className="border-b border-dark-800/50">
                    <td className="py-2 font-medium">{t.symbol}</td>
                    <td className={`py-2 ${t.side === 'buy' ? 'text-accent-green' : 'text-accent-red'}`}>{t.side.toUpperCase()}</td>
                    <td className="py-2 text-right">${t.entry_price}</td>
                    <td className="py-2 text-right">{t.exit_price ? `$${t.exit_price}` : '-'}</td>
                    <td className="py-2 text-right">{t.quantity}</td>
                    <td className={`py-2 text-right font-medium ${t.pnl >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>${t.pnl.toFixed(2)}</td>
                    <td className="py-2"><span className={`text-xs px-2 py-1 rounded-full ${t.status === 'open' ? 'bg-accent-blue/10 text-accent-blue' : 'bg-dark-700 text-dark-400'}`}>{t.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-dark-500 text-center py-8">No paper trades yet. Go to Trading page and place paper orders.</p>
        )}
      </div>
    </div>
  )
}
