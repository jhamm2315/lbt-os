import { NavLink } from 'react-router-dom'
import { useOrganization, UserButton } from '@clerk/clerk-react'

const nav = [
  { to: '/app',             label: 'Dashboard',   icon: '▦' },
  { to: '/app/connections', label: 'Connections', icon: '⇄' },
  { to: '/app/leads',       label: 'Leads',       icon: '◎' },
  { to: '/app/sales',       label: 'Sales',       icon: '$' },
  { to: '/app/customers',   label: 'Customers',   icon: '◉' },
  { to: '/app/expenses',    label: 'Expenses',    icon: '↗' },
  { to: '/app/insights',    label: 'AI Insights', icon: '✦', pro: true },
  { to: '/app/billing',     label: 'Billing',     icon: '◌' },
]

export default function Sidebar() {
  const { organization } = useOrganization()

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-white/8 bg-[linear-gradient(180deg,#09111f_0%,#0f172a_48%,#1e3a5f_100%)] text-white shadow-[20px_0_40px_-38px_rgba(15,23,42,0.85)]">
      {/* Logo */}
      <div className="border-b border-white/10 px-6 py-6">
        <div className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.22em] text-blue-100/60">
          Operating System
        </div>
        <div className="mt-4 text-xl font-semibold tracking-tight">LBT OS</div>
        <div className="mt-1 text-xs text-white/50">{organization?.name || 'Your Business'}</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">
        {nav.map(({ to, label, icon, pro }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/app'}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-white/14 text-white shadow-[0_18px_28px_-22px_rgba(15,23,42,0.95)]'
                  : 'text-white/60 hover:bg-white/8 hover:text-white'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className={`flex h-9 w-9 items-center justify-center rounded-lg text-base transition-all duration-300 ${isActive ? 'bg-white/12 text-white' : 'bg-white/5 text-white/70 group-hover:bg-white/10 group-hover:text-white'}`}>
                  {icon}
                </span>
                <span>{label}</span>
                {isActive && <span className="ml-auto h-2.5 w-2.5 rounded-full bg-brand-300 shadow-[0_0_18px_rgba(147,197,253,0.9)]" />}
                {!isActive && pro && (
                  <span className="ml-auto rounded-full border border-brand-300/30 bg-brand-400/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-brand-200">
                    Pro
                  </span>
                )}
                {isActive && pro && (
                  <span className="ml-2 rounded-full border border-brand-300/30 bg-brand-400/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-brand-200">
                    Pro
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="flex items-center gap-3 border-t border-white/10 px-4 py-4">
        <UserButton afterSignOutUrl="/" />
        <div>
          <div className="text-xs font-medium text-white/80">Account</div>
          <div className="text-[11px] text-white/45">Secure workspace</div>
        </div>
      </div>
    </aside>
  )
}
