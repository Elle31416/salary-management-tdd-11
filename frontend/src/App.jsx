import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, BarChart3, TrendingUp } from 'lucide-react'
import EmployeesPage from './pages/EmployeesPage'
import InsightsPage from './pages/InsightsPage'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/employees', label: 'Employees', icon: Users },
  { to: '/insights', label: 'Insights', icon: BarChart3 },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        {/* Top bar */}
        <header className="h-14 border-b border-[--border] flex items-center px-6 gap-6 sticky top-0 z-40"
          style={{ background: 'rgba(10,10,15,0.92)', backdropFilter: 'blur(12px)' }}>
          <div className="flex items-center gap-2 mr-6">
            <TrendingUp size={18} className="text-[--gold]" />
            <span className="font-display text-lg tracking-tight text-[--gold]">SalaryOS</span>
          </div>
          <nav className="flex items-center gap-1">
            {NAV.map(({ to, label, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all
                  ${isActive
                    ? 'bg-[--surface2] text-[--text]'
                    : 'text-[--muted] hover:text-[--text] hover:bg-[--surface]'}`
                }>
                <Icon size={14} />
                {label}
              </NavLink>
            ))}
          </nav>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<InsightsPage summary />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/insights" element={<InsightsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
