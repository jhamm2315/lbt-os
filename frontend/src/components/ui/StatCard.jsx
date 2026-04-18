const tones = {
  blue: {
    shell: 'from-slate-950 via-slate-900 to-brand-900 text-white',
    accent: 'bg-white/12 text-blue-100 ring-1 ring-white/10',
    meta: 'text-blue-100/72',
  },
  green: {
    shell: 'from-emerald-950 via-slate-900 to-emerald-900 text-white',
    accent: 'bg-white/12 text-emerald-100 ring-1 ring-white/10',
    meta: 'text-emerald-100/72',
  },
  amber: {
    shell: 'from-amber-950 via-slate-900 to-amber-900 text-white',
    accent: 'bg-white/12 text-amber-100 ring-1 ring-white/10',
    meta: 'text-amber-100/72',
  },
  violet: {
    shell: 'from-violet-950 via-slate-900 to-violet-900 text-white',
    accent: 'bg-white/12 text-violet-100 ring-1 ring-white/10',
    meta: 'text-violet-100/72',
  },
}

export default function StatCard({ label, value, sub, trend, color = 'blue' }) {
  const tone = tones[color] || tones.blue

  return (
    <section className={`group relative overflow-hidden rounded-[1.6rem] bg-gradient-to-br p-[1px] shadow-[0_20px_60px_-28px_rgba(15,23,42,0.55)] transition-transform duration-300 hover:-translate-y-0.5 ${tone.shell}`}>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.16),transparent_34%)]" />
      <div className="relative rounded-[calc(1.6rem-1px)] bg-slate-950/80 px-5 py-5 backdrop-blur">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[0.7rem] font-semibold uppercase tracking-[0.24em] text-white/48">{label}</p>
            <p className="mt-3 text-3xl font-semibold tracking-tight text-white">{value}</p>
          </div>
          {trend !== undefined && (
            <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ${tone.accent}`}>
              {trend > 0 ? 'Up' : trend < 0 ? 'Down' : 'Flat'} {Math.abs(trend)}%
            </span>
          )}
        </div>
        {sub && <p className={`mt-4 text-sm leading-6 ${tone.meta}`}>{sub}</p>}
      </div>
    </section>
  )
}
