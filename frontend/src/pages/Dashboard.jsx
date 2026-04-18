import { useQuery } from '@tanstack/react-query'
import { metricsApi, orgApi } from '../lib/api'
import StatCard from '../components/ui/StatCard'
import RevenueChart from '../components/charts/RevenueChart'

const fmt$ = (n) => `$${(n || 0).toLocaleString('en-US', { minimumFractionDigits: 0 })}`
const fmtPct = (n) => `${(n || 0).toFixed(1)}%`

export default function Dashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics', 30],
    queryFn: () => metricsApi.dashboard(30).then((r) => r.data),
  })

  const { data: trend } = useQuery({
    queryKey: ['revenue-trend'],
    queryFn: () => metricsApi.revenueTrend(12).then((r) => r.data),
  })

  const { data: org } = useQuery({
    queryKey: ['org-me'],
    queryFn: () => orgApi.getMe().then((r) => r.data),
  })

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-7 shadow-[0_24px_60px_-32px_rgba(15,23,42,0.35)]">
          <div className="h-4 w-28 rounded-full bg-slate-200" />
          <div className="mt-4 h-10 w-72 rounded-full bg-slate-200" />
          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            {[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-[1.5rem] bg-slate-100" />)}
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-40 rounded-[1.5rem] bg-slate-200" />)}
        </div>
        <div className="grid gap-5 xl:grid-cols-[1.55fr_1fr]">
          <div className="h-80 rounded-[1.75rem] bg-slate-100" />
          <div className="h-80 rounded-[1.75rem] bg-slate-100" />
        </div>
      </div>
    )
  }

  const r = metrics?.revenue   || {}
  const l = metrics?.leads     || {}
  const c = metrics?.customers || {}
  const e = metrics?.expenses  || {}
  const brief = metrics?.analyst_brief || {}
  const isPro = org?.plan === 'pro' || org?.plan === 'premium'
  const hasActivity = [r.total, l.total, c.total, e.total].some((value) => Number(value) > 0)
  const highlightItems = [
    {
      label: 'Pipeline health',
      value: l.total ? `${l.total} active lead${l.total === 1 ? '' : 's'}` : 'No leads yet',
      detail: l.total ? `${l.won} marked won in this window` : 'Add your first inbound lead to unlock conversion reporting.',
    },
    {
      label: 'Cash position',
      value: e.total ? `${fmt$(e.total)} tracked spend` : 'Expenses are clear',
      detail: e.total ? 'Margin and profit update automatically as you add sales and costs.' : 'Your operating margin will appear once expenses are logged.',
    },
    {
      label: 'Retention signal',
      value: c.total ? `${fmtPct(c.repeat_pct)} repeat rate` : 'No customer history yet',
      detail: c.total ? `${c.repeat} returning customer${c.repeat === 1 ? '' : 's'} identified in the last 30 days.` : 'Won leads and customer orders will build this view.',
    },
  ]
  const revenueMix = Object.entries(r.by_source || {}).sort(([, a], [, b]) => b - a)

  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/80 bg-[linear-gradient(135deg,#0f172a_0%,#111827_55%,#1d4ed8_100%)] px-7 py-7 text-white shadow-[0_28px_80px_-40px_rgba(15,23,42,0.9)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(96,165,250,0.35),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.12),transparent_28%)]" />
        <div className="relative flex flex-col gap-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <p className="text-[0.72rem] font-semibold uppercase tracking-[0.3em] text-blue-100/70">Operating snapshot</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Dashboard</h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-blue-100/72">
                Free gives you your business audit. Pro gives you an analyst team on demand.
              </p>
            </div>
            <HealthPill score={brief.health_score} label={brief.health_label} fallback={hasActivity ? 'Live business activity is flowing in' : 'Connected and ready for first entries'} />
          </div>

          <div className="grid gap-3 lg:grid-cols-3">
            {highlightItems.map((item) => (
              <div key={item.label} className="rounded-[1.4rem] border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                <div className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-100/55">{item.label}</div>
                <div className="mt-3 text-lg font-semibold text-white">{item.value}</div>
                <div className="mt-2 text-sm leading-6 text-blue-100/70">{item.detail}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Revenue" value={fmt$(r.total)} sub={`${fmtPct(r.margin_pct)} margin across the current period`} color="blue" />
        <StatCard label="Gross Profit" value={fmt$(r.profit)} sub={`${fmt$(e.total)} in tracked operating expenses`} color="green" />
        <StatCard label="Lead Conversion" value={fmtPct(l.conversion_rate_pct)} sub={`${l.won || 0} won out of ${l.total || 0} tracked leads`} color="violet" />
        <StatCard label="Repeat Customers" value={fmtPct(c.repeat_pct)} sub={`${c.repeat || 0} of ${c.total || 0} customers came back`} color="amber" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="card-surface p-6">
          <div className="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-start sm:justify-between">
            <div className="max-w-2xl">
              <p className="text-[0.7rem] font-semibold uppercase tracking-[0.24em] text-slate-400">Analyst Brief</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">Executive Summary</h2>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                {brief.executive_summary || 'Once activity is flowing, LBT OS will summarize what changed, what matters, and where to focus next.'}
              </p>
            </div>
            <div className="rounded-[1.4rem] border border-slate-200 bg-slate-50/90 px-5 py-4 text-right">
              <div className="text-[0.7rem] font-semibold uppercase tracking-[0.22em] text-slate-400">Health Score</div>
              <div className="mt-2 text-4xl font-semibold tracking-tight text-slate-950">{brief.health_score ?? '--'}</div>
              <div className="mt-1 text-sm font-medium text-slate-500">{brief.health_label || 'Pending data'}</div>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            {(brief.what_changed || []).map((item) => (
              <ChangeTile key={item.label} item={item} />
            ))}
          </div>

          <div className="mt-6 rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50/80 p-4">
            <div className="text-[0.72rem] font-semibold uppercase tracking-[0.22em] text-slate-400">Benchmark Note</div>
            <div className="mt-2 text-sm leading-6 text-slate-600">{brief.benchmark_note}</div>
          </div>
        </div>

        <div className="card-surface p-6">
          <div className="text-[0.7rem] font-semibold uppercase tracking-[0.24em] text-slate-400">Action Board</div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">Where To Focus This Week</h2>
          <div className="mt-5 space-y-3">
            {(brief.focus_this_week || []).map((item) => (
              <FocusCard key={item.priority} item={item} />
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <InsightList
          title="Top Risks"
          subtitle="Where money, speed, or margin is leaking right now."
          items={brief.top_risks || []}
          tone="risk"
          emptyMessage="No critical risks are standing out yet. Keep the data flowing so the audit can stay honest."
        />
        <InsightList
          title="Top Opportunities"
          subtitle="The quickest ways to create better performance with the data already coming in."
          items={brief.top_opportunities || []}
          tone="opportunity"
          emptyMessage="Add more operating activity and the system will start highlighting the most recoverable wins."
        />
      </section>

      {!isPro && (
        <section className="relative overflow-hidden rounded-[2rem] border border-brand-100 bg-[linear-gradient(135deg,#eff6ff_0%,#ffffff_45%,#dbeafe_100%)] p-6 shadow-[0_22px_65px_-35px_rgba(37,99,235,0.4)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.12),transparent_30%)]" />
          <div className="relative grid gap-5 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
            <div>
              <div className="text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-brand-700">Pro Analyst Pod</div>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">{brief.pro_positioning?.headline}</h2>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">{brief.pro_positioning?.detail}</p>
            </div>
            <div className="space-y-3">
              {(brief.pro_positioning?.features || []).map((feature) => (
                <div key={feature} className="rounded-[1.25rem] border border-white/80 bg-white/80 px-4 py-3 text-sm leading-6 text-slate-700">
                  {feature}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="grid gap-5 xl:grid-cols-[1.55fr_1fr]">
        <div className="card-surface p-6">
          <div className="mb-5">
            <div className="text-[0.7rem] font-semibold uppercase tracking-[0.24em] text-slate-400">Deep Dive</div>
          </div>
          <div className="flex flex-col gap-2 border-b border-slate-100 pb-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold tracking-tight text-slate-950">Revenue trend</h2>
              <p className="mt-1 text-sm leading-6 text-slate-500">
                Weekly motion across the last 12 weeks. Use this to spot momentum shifts quickly.
              </p>
            </div>
            <div className="text-sm font-medium text-slate-500">Updated from live sales data</div>
          </div>
          <div className="mt-5">
            <RevenueChart data={trend || []} />
          </div>
        </div>

        <div className="card-surface p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold tracking-tight text-slate-950">Revenue mix</h2>
              <p className="mt-1 text-sm leading-6 text-slate-500">Where closed revenue is coming from right now.</p>
            </div>
          </div>

          {revenueMix.length === 0 ? (
            <div className="mt-6 rounded-[1.5rem] border border-dashed border-slate-200 bg-slate-50/80 p-5">
              <div className="text-sm font-semibold text-slate-700">No source attribution yet</div>
              <div className="mt-2 text-sm leading-6 text-slate-500">
                When you tag lead sources on sales, this panel will show which channels actually convert into revenue.
              </div>
            </div>
          ) : (
            <div className="mt-6 space-y-4">
              {revenueMix.map(([src, amt]) => {
                const pct = r.total > 0 ? (amt / r.total) * 100 : 0
                return (
                  <div key={src}>
                    <div className="mb-2 flex items-center justify-between text-sm">
                      <span className="font-medium capitalize text-slate-700">{src.replaceAll('_', ' ')}</span>
                      <span className="font-semibold text-slate-950">{fmt$(amt)}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-[linear-gradient(90deg,#2563eb_0%,#60a5fa_100%)]"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <div className="mt-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">{pct.toFixed(1)}% of revenue</div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="card-surface p-6">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">Business signals</h2>
          <p className="mt-1 text-sm leading-6 text-slate-500">Operational context pulled from your current KPI mix.</p>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <SignalTile
              title="Lead velocity"
              value={l.total || 0}
              caption={l.total ? 'Leads tracked in the active window' : 'Start logging new opportunities to measure velocity'}
            />
            <SignalTile
              title="Won work"
              value={l.won || 0}
              caption={l.won ? 'Closed deals feeding revenue and customer history' : 'Won deals will unlock retention and revenue insights'}
            />
            <SignalTile
              title="Customer base"
              value={c.total || 0}
              caption={c.total ? 'Known customers tied to this org' : 'Customer records appear as leads are converted or added directly'}
            />
            <SignalTile
              title="Expense load"
              value={fmt$(e.total)}
              caption={e.total ? 'Captured expenses impacting current profit' : 'Keep expenses current to make margin alerts trustworthy'}
            />
          </div>
        </div>

        <div className="card-surface p-6">
          <h2 className="text-lg font-semibold tracking-tight text-slate-950">Alerts</h2>
          <p className="mt-1 text-sm leading-6 text-slate-500">Shortlist of what needs attention first.</p>

          <div className="mt-6 space-y-3">
            {l.missed_follow_ups > 0 && (
              <Alert type="warning" message={`${l.missed_follow_ups} lead${l.missed_follow_ups > 1 ? 's' : ''} have a follow-up due but haven't been contacted.`} />
            )}
            {l.conversion_rate_pct < 20 && l.total > 5 && (
              <Alert type="danger" message={`Conversion rate is ${fmtPct(l.conversion_rate_pct)}. Review your follow-up speed and quoting process.`} />
            )}
            {c.repeat_pct < 20 && c.total > 10 && (
              <Alert type="warning" message={`Only ${fmtPct(c.repeat_pct)} of customers are returning. Consider a reactivation or loyalty campaign.`} />
            )}
            {l.missed_follow_ups === 0 && l.conversion_rate_pct >= 20 && (
              <Alert type="success" message={hasActivity ? 'No critical issues detected in the current operating window.' : 'Your workspace is ready. Add leads, sales, and expenses to light up insights.'} />
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

function SignalTile({ title, value, caption }) {
  return (
    <div className="rounded-[1.4rem] border border-slate-200/80 bg-slate-50/80 p-4">
      <div className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">{title}</div>
      <div className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">{value}</div>
      <div className="mt-2 text-sm leading-6 text-slate-500">{caption}</div>
    </div>
  )
}

function Alert({ type, message }) {
  const styles = {
    warning: 'border-amber-200 bg-amber-50 text-amber-900',
    danger: 'border-rose-200 bg-rose-50 text-rose-900',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
  }
  const icons = {
    warning: 'Watch',
    danger: 'Urgent',
    success: 'Clear',
  }

  return (
    <div className={`rounded-[1.35rem] border p-4 ${styles[type]}`}>
      <div className="text-[11px] font-semibold uppercase tracking-[0.24em] opacity-70">{icons[type]}</div>
      <div className="mt-2 text-sm leading-6">{message}</div>
    </div>
  )
}

function HealthPill({ score, label, fallback }) {
  if (score === undefined) {
    return (
      <div className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-blue-50/88 backdrop-blur">
        {fallback}
      </div>
    )
  }

  return (
    <div className="rounded-[1.3rem] border border-white/15 bg-white/10 px-4 py-3 text-right backdrop-blur">
      <div className="text-[0.7rem] font-semibold uppercase tracking-[0.22em] text-blue-100/60">Business Health</div>
      <div className="mt-2 text-3xl font-semibold text-white">{score}</div>
      <div className="text-sm text-blue-100/70">{label}</div>
    </div>
  )
}

function ChangeTile({ item }) {
  const directionStyles = {
    up: 'text-emerald-700 bg-emerald-50 border-emerald-100',
    down: 'text-rose-700 bg-rose-50 border-rose-100',
    flat: 'text-slate-600 bg-slate-50 border-slate-100',
  }
  const directionLabel = item.direction === 'up' ? 'Improved' : item.direction === 'down' ? 'Declined' : 'Flat'

  return (
    <div className={`rounded-[1.35rem] border p-4 ${directionStyles[item.direction] || directionStyles.flat}`}>
      <div className="text-[0.7rem] font-semibold uppercase tracking-[0.22em] opacity-70">{item.label}</div>
      <div className="mt-3 text-lg font-semibold">{directionLabel}</div>
      <div className="mt-1 text-sm leading-6 opacity-80">{item.detail}</div>
    </div>
  )
}

function FocusCard({ item }) {
  return (
    <div className="rounded-[1.35rem] border border-slate-200 bg-slate-50/85 p-4">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-sm font-semibold text-white">
          {item.priority}
        </div>
        <div className="text-sm font-semibold text-slate-900">{item.title}</div>
      </div>
      <div className="mt-3 text-sm leading-6 text-slate-600">{item.detail}</div>
    </div>
  )
}

function InsightList({ title, subtitle, items, tone, emptyMessage }) {
  const toneStyles = {
    risk: {
      shell: 'border-rose-100 bg-rose-50/60',
      badge: 'text-rose-700 bg-rose-100',
    },
    opportunity: {
      shell: 'border-emerald-100 bg-emerald-50/60',
      badge: 'text-emerald-700 bg-emerald-100',
    },
  }
  const selected = toneStyles[tone]

  return (
    <div className="card-surface p-6">
      <h2 className="text-lg font-semibold tracking-tight text-slate-950">{title}</h2>
      <p className="mt-1 text-sm leading-6 text-slate-500">{subtitle}</p>
      {items.length === 0 ? (
        <div className="mt-5 rounded-[1.35rem] border border-dashed border-slate-200 bg-slate-50/80 p-4 text-sm leading-6 text-slate-500">
          {emptyMessage}
        </div>
      ) : (
        <div className="mt-5 space-y-3">
          {items.map((item) => (
            <div key={item.title} className={`rounded-[1.35rem] border p-4 ${selected.shell}`}>
              <div className="flex items-start justify-between gap-3">
                <div className="text-sm font-semibold text-slate-900">{item.title}</div>
                {item.severity && (
                  <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${selected.badge}`}>
                    {item.severity}
                  </span>
                )}
                {item.impact_hint && (
                  <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${selected.badge}`}>
                    {item.impact_hint}
                  </span>
                )}
              </div>
              <div className="mt-2 text-sm leading-6 text-slate-600">{item.detail}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
