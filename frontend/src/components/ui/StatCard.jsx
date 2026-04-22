const tones = {
  blue: {
    accent: 'bg-sky-50 text-sky-700 border-sky-100',
  },
  green: {
    accent: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  },
  amber: {
    accent: 'bg-amber-50 text-amber-700 border-amber-100',
  },
  violet: {
    accent: 'bg-violet-50 text-violet-700 border-violet-100',
  },
}

export default function StatCard({ label, value, sub, trend, color = 'blue' }) {
  const tone = tones[color] || tones.blue

  return (
    <section className="metric-chip">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="metric-label">{label}</p>
          <p className="metric-value">{value}</p>
        </div>
        {trend !== undefined && (
          <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold ${tone.accent}`}>
            {trend > 0 ? 'Up' : trend < 0 ? 'Down' : 'Flat'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      {sub && <p className="mt-3 text-sm leading-6 text-slate-500">{sub}</p>}
    </section>
  )
}
