import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Settings as SettingsIcon, Shield, Bell, Bot, Save } from 'lucide-react'
import api from '../services/api'

export default function Settings() {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => { fetchSettings() }, [])

  const fetchSettings = async () => {
    try {
      const res = await api.get('/api/settings/')
      setSettings(res.data)
    } catch (err) { console.error(err) }
    finally { setLoading(false) }
  }

  const saveSettings = async () => {
    setSaving(true)
    try {
      const res = await api.put('/api/settings/', settings)
      setSettings(res.data)
      alert('Settings saved!')
    } catch (err) { alert('Failed to save settings') }
    finally { setSaving(false) }
  }

  if (loading) return <div className="flex items-center justify-center h-full"><div className="animate-spin w-8 h-8 border-2 border-accent-blue border-t-transparent rounded-full" /></div>

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-dark-400 text-sm">Configure your trading preferences</p>
      </div>

      <div className="space-y-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Bot size={20} className="text-accent-blue" />
            <h3 className="text-lg font-semibold">Auto Trading</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Trading Mode</label>
              <select value={settings?.auto_trading_mode || 'manual'} onChange={e => setSettings({ ...settings, auto_trading_mode: e.target.value })} className="input-field max-w-sm">
                <option value="manual">Manual</option>
                <option value="semi_auto">Semi Auto</option>
                <option value="full_auto">Full Auto</option>
              </select>
              <p className="text-xs text-dark-500 mt-1">Manual: You control everything. Semi Auto: AI suggests, you approve. Full Auto: AI trades automatically.</p>
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Active Strategy</label>
              <select value={settings?.active_strategy || 'ema_cross'} onChange={e => setSettings({ ...settings, active_strategy: e.target.value })} className="input-field max-w-sm">
                <option value="ema_cross">EMA Cross</option>
                <option value="rsi">RSI</option>
                <option value="macd">MACD</option>
                <option value="scalping">Scalping</option>
                <option value="breakout">Breakout</option>
              </select>
            </div>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={settings?.paper_trading || false} onChange={e => setSettings({ ...settings, paper_trading: e.target.checked })} className="w-4 h-4" />
                <span className="text-sm">Paper Trading Mode</span>
              </label>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={20} className="text-accent-red" />
            <h3 className="text-lg font-semibold">Risk Management</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Risk Per Trade (%)</label>
              <input type="number" step="0.1" value={settings?.risk_per_trade || 2} onChange={e => setSettings({ ...settings, risk_per_trade: parseFloat(e.target.value) })} className="input-field" />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Max Daily Loss (%)</label>
              <input type="number" step="0.1" value={settings?.max_daily_loss || 5} onChange={e => setSettings({ ...settings, max_daily_loss: parseFloat(e.target.value) })} className="input-field" />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Max Drawdown (%)</label>
              <input type="number" step="0.1" value={settings?.max_drawdown || 10} onChange={e => setSettings({ ...settings, max_drawdown: parseFloat(e.target.value) })} className="input-field" />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Max Concurrent Trades</label>
              <input type="number" value={settings?.max_concurrent_trades || 5} onChange={e => setSettings({ ...settings, max_concurrent_trades: parseInt(e.target.value) })} className="input-field" />
            </div>
            <div>
              <label className="text-sm text-dark-400 mb-1 block">Default Leverage</label>
              <input type="number" value={settings?.default_leverage || 1} onChange={e => setSettings({ ...settings, default_leverage: parseInt(e.target.value) })} className="input-field" />
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Bell size={20} className="text-accent-yellow" />
            <h3 className="text-lg font-semibold">Telegram Notifications</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={settings?.telegram_enabled || false} onChange={e => setSettings({ ...settings, telegram_enabled: e.target.checked })} className="w-4 h-4" />
                <span className="text-sm">Enable Telegram Notifications</span>
              </label>
            </div>
            {settings?.telegram_enabled && (
              <div>
                <label className="text-sm text-dark-400 mb-1 block">Telegram Chat ID</label>
                <input type="text" value={settings?.telegram_chat_id || ''} onChange={e => setSettings({ ...settings, telegram_chat_id: e.target.value })} className="input-field max-w-sm" placeholder="Enter your Telegram Chat ID" />
                <p className="text-xs text-dark-500 mt-1">Get your Chat ID by messaging @userinfobot on Telegram</p>
              </div>
            )}
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={saveSettings}
          disabled={saving}
          className="btn-primary flex items-center gap-2 px-6 py-3 disabled:opacity-50"
        >
          <Save size={16} /> {saving ? 'Saving...' : 'Save Settings'}
        </motion.button>
      </div>
    </div>
  )
}
