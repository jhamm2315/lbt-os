import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useOrganization, UserButton } from '@clerk/clerk-react'
import { useQuery } from '@tanstack/react-query'
import { orgApi } from '../../lib/api'

const navGroups = [
  {
    label: 'Operate',
    items: [
      { to: '/app', label: 'Dashboard', icon: '▦' },
      { to: '/app/messages', label: 'Signal Desk', icon: '◫' },
      { to: '/app/connections', label: 'Sources', icon: '⇄' },
    ],
  },
  {
    label: 'Records',
    items: [
      { to: '/app/leads', label: 'Leads', icon: '◎' },
      { to: '/app/sales', label: 'Sales', icon: '$' },
      { to: '/app/customers', label: 'Customers', icon: '◉' },
      { to: '/app/expenses', label: 'Expenses', icon: '↗' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { to: '/app/insights', label: 'AI Audit', icon: '✦', pro: true },
      { to: '/app/strategy', label: 'Strategy', icon: '◈', pro: true },
      { to: '/app/revenue-intelligence', label: 'Revenue Intel', icon: '◑', pro: true },
    ],
  },
  {
    label: 'Account',
    items: [
      { to: '/app/billing', label: 'Billing', icon: '◌' },
    ],
  },
]

export default function Sidebar() {
  const { organization } = useOrganization()
  const [collapsedGroups, setCollapsedGroups] = useState({})
  const { data: workspaceStatus } = useQuery({
    queryKey: ['workspace-status'],
    queryFn: () => orgApi.workspaceStatus().then((r) => r.data),
    retry: false,
  })
  const mode = workspaceStatus?.workspace_mode || 'blank'
  const modeStyles = {
    live: 'border-emerald-300/25 bg-emerald-400/10 text-emerald-200',
    demo: 'border-amber-300/25 bg-amber-300/10 text-amber-100',
    blank: 'border-white/10 bg-white/5 text-white/55',
  }
  const modeLabel = mode === 'live' ? 'Live Data' : mode === 'demo' ? 'Demo Workspace' : 'Setup Ready'
  const toggleGroup = (label) => {
    setCollapsedGroups((current) => ({
      ...current,
      [label]: !current[label],
    }))
  }

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-slate-900/5 bg-slate-950 text-white">
      {/* Logo */}
      <div className="border-b border-white/8 px-5 py-5">
        <div className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-white/45">
          LBT OS
        </div>
        <div className="mt-4 text-lg font-semibold tracking-tight">Command Center</div>
        <div className="mt-1 text-xs text-white/50">{organization?.name || 'Your Business'}</div>
        <div className={`mt-3 inline-flex rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${modeStyles[mode] || modeStyles.blank}`}>
          {modeLabel}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-5">
        {navGroups.map((group) => (
          <div key={group.label}>
            <button
              type="button"
              onClick={() => toggleGroup(group.label)}
              className="mb-2 flex w-full items-center justify-between rounded-lg px-3 py-1.5 text-left text-[10px] font-semibold uppercase tracking-[0.2em] text-white/34 transition-colors hover:bg-white/5 hover:text-white/62"
              aria-expanded={!collapsedGroups[group.label]}
              aria-controls={`sidebar-group-${group.label.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <span>{group.label}</span>
              <span className={`text-xs transition-transform ${collapsedGroups[group.label] ? '-rotate-90' : 'rotate-0'}`}>⌄</span>
            </button>
            {!collapsedGroups[group.label] && (
              <div id={`sidebar-group-${group.label.toLowerCase().replace(/\s+/g, '-')}`} className="space-y-1">
                {group.items.map(({ to, label, icon, pro }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === '/app'}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-white/10 text-white'
                          : 'text-white/52 hover:bg-white/6 hover:text-white/84'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <span className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm transition-colors ${isActive ? 'bg-white/10 text-white' : 'bg-white/4 text-white/55 group-hover:bg-white/8 group-hover:text-white/80'}`}>
                          {icon}
                        </span>
                        <span>{label}</span>
                        {pro && (
                          <span className="ml-auto rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.14em] text-white/42">
                            Pro
                          </span>
                        )}
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
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
