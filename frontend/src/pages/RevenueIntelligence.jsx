import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { revenueIntelligenceApi } from '../lib/api'

// ─── tiny helpers ───────────────────────────────────────────────────────────

function fmt$(n) {
  if (n == null) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}
function fmtPct(n) { return n == null ? '—' : `${n}%` }
function fmtHrs(h) {
  if (h == null) return '—'
  return h < 24 ? `${h}h` : `${(h / 24).toFixed(1)}d`
}

function Stat({ label, value, sub, accent }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/4 p-5">
      <div className="text-xs text-white/45 uppercase tracking-widest mb-1">{label}</div>
      <div className={`text-2xl font-semibold ${accent || 'text-white'}`}>{value}</div>
      {sub && <div className="text-xs text-white/40 mt-0.5">{sub}</div>}
    </div>
  )
}

function Card({ title, children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-white/8 bg-white/4 p-6 ${className}`}>
      <div className="text-sm font-semibold text-white/80 mb-4">{title}</div>
      {children}
    </div>
  )
}

function LoadingCard({ title }) {
  return (
    <Card title={title}>
      <div className="h-24 flex items-center justify-center text-white/30 text-sm">Loading…</div>
    </Card>
  )
}

function EmptyCard({ title, msg }) {
  return (
    <Card title={title}>
      <div className="h-24 flex items-center justify-center text-white/30 text-sm">{msg || 'No data yet'}</div>
    </Card>
  )
}

// ─── grade badge ────────────────────────────────────────────────────────────

function GradeBadge({ grade }) {
  const colors = { A: 'text-emerald-300 border-emerald-300/30', B: 'text-blue-300 border-blue-300/30', C: 'text-amber-300 border-amber-300/30', D: 'text-red-400 border-red-300/30' }
  return (
    <span className={`inline-flex h-9 w-9 items-center justify-center rounded-full border text-lg font-bold ${colors[grade] || 'text-white/50 border-white/20'}`}>
      {grade}
    </span>
  )
}

// ─── stage bar ──────────────────────────────────────────────────────────────

const STAGE_COLORS = {
  new: 'bg-slate-400',
  contacted: 'bg-blue-400',
  qualified: 'bg-violet-400',
  proposal: 'bg-amber-400',
  won: 'bg-emerald-400',
  lost: 'bg-red-400',
}

function StageBar({ stage, value, max, sub }) {
  const pct = max ? Math.round((value / max) * 100) : 0
  return (
    <div className="flex items-center gap-3 py-1.5">
      <div className="w-20 text-right text-xs text-white/50 capitalize">{stage}</div>
      <div className="flex-1 h-2 rounded-full bg-white/8 overflow-hidden">
        <div className={`h-full rounded-full ${STAGE_COLORS[stage] || 'bg-white/30'}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="w-16 text-xs text-white/70 text-right">{sub}</div>
    </div>
  )
}

// ─── LTV panel ──────────────────────────────────────────────────────────────

function LtvPanel() {
  const { data, isLoading } = useQuery({ queryKey: ['ri-ltv'], queryFn: () => revenueIntelligenceApi.ltv().then(r => r.data) })
  if (isLoading) return <LoadingCard title="Customer LTV" />
  return (
    <Card title="Customer Lifetime Value">
      <div className="grid grid-cols-3 gap-3 mb-5">
        <Stat label="Customers" value={data.total_customers} />
        <Stat label="Avg LTV" value={fmt$(data.avg_ltv)} accent="text-emerald-300" />
        <Stat label="Total Revenue" value={fmt$(data.total_revenue)} accent="text-blue-300" />
      </div>
      <div className="space-y-1">
        <div className="text-xs text-white/35 uppercase tracking-widest mb-2">Top 10 Customers</div>
        {data.top_customers.map((c, i) => (
          <div key={c.id} className="flex items-center gap-3 py-1.5 border-b border-white/5 last:border-0">
            <span className="text-xs text-white/30 w-5">{i + 1}</span>
            <span className="flex-1 text-sm text-white/80 truncate">{c.name}</span>
            <span className="text-xs text-white/45">{c.total_orders} orders</span>
            <span className="text-sm font-medium text-emerald-300">{fmt$(c.lifetime_value)}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}

// ─── Stage velocity panel ───────────────────────────────────────────────────

function VelocityPanel() {
  const [days, setDays] = useState(90)
  const { data, isLoading } = useQuery({
    queryKey: ['ri-velocity', days],
    queryFn: () => revenueIntelligenceApi.stageVelocity(days).then(r => r.data),
  })
  if (isLoading) return <LoadingCard title="Stage Velocity" />
  const stages = data?.stages || []
  const maxDays = Math.max(...stages.map(s => s.avg_days), 1)
  return (
    <Card title="Stage Velocity">
      <div className="flex gap-2 mb-4">
        {[30, 60, 90].map(d => (
          <button key={d} onClick={() => setDays(d)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${days === d ? 'bg-blue-500/20 text-blue-300 border border-blue-400/30' : 'text-white/40 hover:text-white/70'}`}>
            {d}d
          </button>
        ))}
      </div>
      {!stages.length
        ? <div className="text-sm text-white/30 py-4 text-center">No stage transitions yet — start moving leads through the pipeline</div>
        : stages.map(s => (
            <StageBar key={s.stage} stage={s.stage} value={s.avg_days} max={maxDays}
              sub={`${s.avg_days}d avg`} />
          ))
      }
    </Card>
  )
}

// ─── Win/Loss cohort panel ──────────────────────────────────────────────────

function WinLossPanel() {
  const [days, setDays] = useState(90)
  const { data, isLoading } = useQuery({
    queryKey: ['ri-winloss', days],
    queryFn: () => revenueIntelligenceApi.winLoss(days).then(r => r.data),
  })
  if (isLoading) return <LoadingCard title="Win/Loss by Source" />
  const cohorts = data?.cohorts || []
  return (
    <Card title="Win/Loss by Source">
      <div className="flex gap-2 mb-4">
        {[30, 60, 90].map(d => (
          <button key={d} onClick={() => setDays(d)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${days === d ? 'bg-blue-500/20 text-blue-300 border border-blue-400/30' : 'text-white/40 hover:text-white/70'}`}>
            {d}d
          </button>
        ))}
      </div>
      {!cohorts.length
        ? <div className="text-sm text-white/30 py-4 text-center">No closed leads in this period</div>
        : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-white/30 uppercase tracking-wider border-b border-white/8">
                <th className="pb-2 text-left font-medium">Source</th>
                <th className="pb-2 text-right font-medium">Won</th>
                <th className="pb-2 text-right font-medium">Lost</th>
                <th className="pb-2 text-right font-medium">Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {cohorts.map(c => (
                <tr key={c.source} className="border-b border-white/5 last:border-0">
                  <td className="py-2 capitalize text-white/75">{c.source}</td>
                  <td className="py-2 text-right text-emerald-300">{c.won}</td>
                  <td className="py-2 text-right text-red-400">{c.lost}</td>
                  <td className="py-2 text-right font-semibold text-white/90">{fmtPct(c.win_rate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      }
    </Card>
  )
}

// ─── Data quality panel ──────────────────────────────────────────────────────

function DataQualityPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['ri-dq'],
    queryFn: () => revenueIntelligenceApi.dataQuality().then(r => r.data),
  })
  if (isLoading) return <LoadingCard title="Data Quality" />
  if (!data) return <EmptyCard title="Data Quality" />
  const fields = data.fields || []
  return (
    <Card title="Data Quality Scorecard">
      <div className="flex items-center gap-4 mb-5">
        <GradeBadge grade={data.grade} />
        <div>
          <div className="text-lg font-semibold text-white">{data.overall_score}% complete</div>
          <div className="text-xs text-white/40">{data.lead_count} leads · {data.customer_count} customers · {data.sale_count} sales</div>
        </div>
      </div>
      <div className="space-y-0.5">
        {fields.map(f => (
          <div key={`${f.entity}-${f.field}`} className="flex items-center gap-3 py-1">
            <span className="w-20 text-[10px] text-white/35 uppercase tracking-wider truncate">{f.entity}</span>
            <span className="w-28 text-xs text-white/60 capitalize">{f.field.replace(/_/g, ' ')}</span>
            <div className="flex-1 h-1.5 rounded-full bg-white/8 overflow-hidden">
              <div className={`h-full rounded-full ${f.pct >= 80 ? 'bg-emerald-400' : f.pct >= 50 ? 'bg-amber-400' : 'bg-red-400'}`}
                style={{ width: `${f.pct}%` }} />
            </div>
            <span className="w-10 text-right text-xs text-white/50">{f.pct}%</span>
          </div>
        ))}
      </div>
    </Card>
  )
}

// ─── Expansion signals panel ─────────────────────────────────────────────────

function ExpansionPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['ri-expansion'],
    queryFn: () => revenueIntelligenceApi.expansion().then(r => r.data),
  })
  if (isLoading) return <LoadingCard title="Expansion Signals" />
  const signals = data?.signals || []
  return (
    <Card title="Re-engagement Targets">
      <div className="text-xs text-white/35 mb-3">High-LTV customers inactive 90+ days</div>
      {!signals.length
        ? <div className="text-sm text-white/30 py-4 text-center">No dormant high-value customers — great sign!</div>
        : (
          <div className="space-y-2">
            {signals.map(s => (
              <div key={s.id} className="flex items-center gap-3 rounded-xl border border-white/6 bg-white/3 px-4 py-3">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-white/85 truncate">{s.name}</div>
                  <div className="text-xs text-white/40 truncate">{s.email || '—'}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-emerald-300">{fmt$(s.lifetime_value)}</div>
                  <div className="text-[10px] text-amber-300/70">{s.days_inactive != null ? `${s.days_inactive}d inactive` : 'never purchased'}</div>
                </div>
              </div>
            ))}
          </div>
        )
      }
    </Card>
  )
}

// ─── Speed to lead panel ─────────────────────────────────────────────────────

function SpeedToLeadPanel() {
  const [days, setDays] = useState(30)
  const { data, isLoading } = useQuery({
    queryKey: ['ri-speed', days],
    queryFn: () => revenueIntelligenceApi.speedToLead(days).then(r => r.data),
  })
  if (isLoading) return <LoadingCard title="Speed to Lead" />
  const sources = data?.by_source || []
  const maxH = Math.max(...sources.map(s => s.avg_hours), 1)
  return (
    <Card title="Speed to Lead">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs text-white/35">Overall avg: </span>
          <span className="text-sm font-semibold text-blue-300">{fmtHrs(data?.overall_avg_hours)}</span>
        </div>
        <div className="flex gap-2">
          {[14, 30, 90].map(d => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${days === d ? 'bg-blue-500/20 text-blue-300 border border-blue-400/30' : 'text-white/40 hover:text-white/70'}`}>
              {d}d
            </button>
          ))}
        </div>
      </div>
      {!sources.length
        ? <div className="text-sm text-white/30 py-4 text-center">No contacted leads in this period</div>
        : sources.map(s => (
            <StageBar key={s.source} stage={s.source} value={s.avg_hours} max={maxH}
              sub={fmtHrs(s.avg_hours)} />
          ))
      }
    </Card>
  )
}

// ─── Stage aging panel ───────────────────────────────────────────────────────

function StageAgingPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ['ri-aging'],
    queryFn: () => revenueIntelligenceApi.stageAging().then(r => r.data),
  })
  if (isLoading) return <LoadingCard title="Pipeline Aging" />
  const stages = data?.stages || []
  const maxCount = Math.max(...stages.map(s => s.count), 1)
  return (
    <Card title="Pipeline Aging">
      <div className="text-xs text-white/35 mb-3">{data?.total_open || 0} open leads · stale = &gt;14 days in stage</div>
      {!data?.total_open
        ? <div className="text-sm text-white/30 py-4 text-center">No open leads</div>
        : stages.map(s => (
            <div key={s.stage} className="py-2 border-b border-white/5 last:border-0">
              <div className="flex justify-between mb-1">
                <span className="text-xs capitalize text-white/70">{s.stage}</span>
                <span className="text-xs text-white/45">
                  {s.count} leads · {s.avg_days_in_stage}d avg
                  {s.stale_count > 0 && <span className="ml-2 text-amber-400">⚠ {s.stale_count} stale</span>}
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-white/8 overflow-hidden">
                <div className={`h-full rounded-full ${s.stale_count > 0 ? 'bg-amber-400' : STAGE_COLORS[s.stage] || 'bg-blue-400'}`}
                  style={{ width: `${Math.round(s.count / maxCount * 100)}%` }} />
              </div>
            </div>
          ))
      }
    </Card>
  )
}

// ─── Main page ───────────────────────────────────────────────────────────────

function DemoBanner() {
  return (
    <div className="mb-6 rounded-xl border border-blue-400/20 bg-blue-500/10 px-5 py-3 flex items-center gap-3">
      <span className="text-blue-300 text-lg">◈</span>
      <p className="text-sm text-blue-200/80">
        <span className="font-semibold text-blue-200">Demo data</span> — you're seeing sample metrics.
        Add real customers, leads, and sales to replace this with your actual pipeline intelligence.
      </p>
    </div>
  )
}

export default function RevenueIntelligence() {
  // Check if any panel is returning demo data
  const { data: ltvData } = useQuery({ queryKey: ['ri-ltv'], queryFn: () => revenueIntelligenceApi.ltv().then(r => r.data) })
  const isDemo = ltvData?.is_demo === true

  return (
    <div className="min-h-screen bg-[#0c1525] text-white">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="text-xs text-white/35 uppercase tracking-widest mb-1">Analytics</div>
          <h1 className="text-2xl font-semibold tracking-tight">Revenue Intelligence</h1>
          <p className="text-sm text-white/45 mt-1">Pipeline health, cohort analysis, and CRM data quality</p>
        </div>

        {isDemo && <DemoBanner />}

        {/* Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          <LtvPanel />
          <DataQualityPanel />
          <VelocityPanel />
          <WinLossPanel />
          <SpeedToLeadPanel />
          <ExpansionPanel />
          <div className="lg:col-span-2">
            <StageAgingPanel />
          </div>
        </div>
      </div>
    </div>
  )
}
