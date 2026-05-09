import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, TrendingUp, Brain, History, FlaskConical,
  Link2, Settings, LogOut, Menu, X, ChevronLeft, Wallet
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/trading', icon: TrendingUp, label: 'Trading' },
  { to: '/signals', icon: Brain, label: 'AI Signals' },
  { to: '/backtest', icon: History, label: 'Backtest' },
  { to: '/paper', icon: FlaskConical, label: 'Paper Trading' },
  { to: '/exchange', icon: Link2, label: 'Exchange' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <div className="flex h-screen overflow-hidden">
      <motion.aside
        animate={{ width: collapsed ? 72 : 240 }}
        className="bg-dark-900 border-r border-dark-800 flex flex-col shrink-0"
      >
        <div className="flex items-center gap-3 px-4 h-16 border-b border-dark-800">
          <div className="w-8 h-8 bg-accent-blue rounded-lg flex items-center justify-center font-bold text-sm shrink-0">BT</div>
          {!collapsed && <span className="font-bold text-lg tracking-tight">BungTrade</span>}
          <button onClick={() => setCollapsed(!collapsed)} className="ml-auto text-dark-400 hover:text-white">
            {collapsed ? <Menu size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        <nav className="flex-1 py-4 space-y-1 px-2 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-accent-blue/10 text-accent-blue border border-accent-blue/20'
                    : 'text-dark-400 hover:text-white hover:bg-dark-800'
                }`
              }
            >
              <Icon size={20} className="shrink-0" />
              {!collapsed && <span className="text-sm font-medium">{label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-dark-800">
          {!collapsed && (
            <div className="flex items-center gap-2 px-2 mb-3">
              <Wallet size={16} className="text-dark-400" />
              <span className="text-xs text-dark-400 truncate">{user?.username}</span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-dark-400 hover:text-accent-red hover:bg-dark-800 transition-all w-full"
          >
            <LogOut size={18} />
            {!collapsed && <span className="text-sm">Logout</span>}
          </button>
        </div>
      </motion.aside>

      <main className="flex-1 overflow-y-auto bg-dark-950">
        <Outlet />
      </main>
    </div>
  )
}
