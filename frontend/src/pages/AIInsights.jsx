import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { auditApi } from '../lib/api'
import { format } from 'date-fns'

const SEVERITY_STYLES = {
  high:   { bar: 'bg-red-500',    badge: 'bg-red-50 text-red-700' },
  medium: { bar: 'bg-yellow-500', badge: 'bg-yellow-50 text-yellow-700' },
  low:    { bar: 'bg-blue-400',   badge: 'bg-blue-50 text-blue-700' },
}

const TYPE_ICONS = {
  revenue_leak:      '⚠',
  missed_opportunity:'◎',
  inefficiency:      '↻',
  strength:          '✓',
}

function HealthScore({ score }) {
  const color = score >= 70 ? '#22c55e' : score >= 45 ? '#f59e0b' : '#ef4444'
  const label = score >= 70 ? 'Healthy' : score >= 45 ? 'Needs Attention' : 'Critical'

  return (
    <div className="flex items-center gap-6">
      <div className="relative w-24 h-24">
        <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f1f5f9" strokeWidth="3" />
          <circle
            cx="18" cy="18" r="15.9" fill="none"
            stroke={color} strokeWidth="3"
            strokeDasharray={`${score} 100`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-gray-900">{score}</span>
        </div>
      </div>
      <div>
        <div className="text-lg font-semibold" style={{ color }}>{label}</div>
        <div className="text-sm text-gray-500">Business Health Score</div>
      </div>
    </div>
  )
}

export default function AIInsights() {
  const qc = useQueryClient()

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['audit-latest'],
    queryFn: () => auditApi.latest().then((r) => r.data),
    retry: false,
  })

  const trigger = useMutation({
    mutationFn: () => auditApi.run(),
    onSuccess: (res) => qc.setQueryData(['audit-latest'], res.data),
  })

  const is404 = error?.response?.status === 404
  const is402 = error?.response?.status === 402 || error?.response?.status === 403

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Insights</h1>
          {report && (
            <p className="text-sm text-gray-500 mt-0.5">
              Last run: {format(new Date(report.generated_at), 'MMM d, yyyy h:mm a')} ·
              Period: {report.period_start} → {report.period_end}
            </p>
          )}
        </div>
        <button
          className="btn-primary"
          onClick={() => trigger.mutate()}
          disabled={trigger.isPending}
        >
          {trigger.isPending ? '⟳ Analyzing...' : '✦ Run AI Audit'}
        </button>
      </div>

      {/* Upgrade prompt */}
      {is402 && (
        <div className="card p-8 text-center space-y-4">
          <div className="text-4xl">✦</div>
          <h2 className="text-xl font-bold">AI Insights — Pro Feature</h2>
          <p className="text-gray-500 max-w-md mx-auto">
            Upgrade to Pro to unlock AI-powered analysis of your leads, conversions, revenue trends, and expense patterns — with specific dollar-impact recommendations.
          </p>
          <Link to="/app/billing" className="btn-primary mx-auto">Upgrade to Pro →</Link>
        </div>
      )}

      {/* No report yet */}
      {(is404 || (!report && !isLoading && !is402)) && (
        <div className="card p-8 text-center space-y-3">
          <div className="text-3xl">◎</div>
          <h2 className="text-lg font-semibold">No audit report yet</h2>
          <p className="text-gray-500 text-sm">Run your first AI audit to get personalized insights about your business.</p>
        </div>
      )}

      {isLoading && (
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-gray-100 rounded-xl" />
          <div className="h-48 bg-gray-100 rounded-xl" />
        </div>
      )}

      {report && (
        <>
          {/* Health Score */}
          <div className="card p-6">
            <HealthScore score={report.health_score} />
          </div>

          {/* Insights */}
          <div className="card p-6 space-y-4">
            <h2 className="text-base font-semibold">What the AI found</h2>
            {(report.insights || []).map((ins, i) => (
              <div key={i} className="flex gap-4 p-4 rounded-xl bg-gray-50 border border-gray-100">
                <div className="text-xl mt-0.5">{TYPE_ICONS[ins.type] || '•'}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900 text-sm">{ins.title}</span>
                    <span className={`badge text-xs ${SEVERITY_STYLES[ins.severity]?.badge || 'bg-gray-50 text-gray-600'}`}>
                      {ins.severity}
                    </span>
                    {ins.estimated_impact && (
                      <span className="text-xs text-gray-500 ml-auto">{ins.estimated_impact}</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{ins.detail}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Recommendations */}
          <div className="card p-6 space-y-4">
            <h2 className="text-base font-semibold">Recommended actions</h2>
            {(report.recommendations || []).map((rec, i) => (
              <div key={i} className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center text-sm font-bold shrink-0">
                  {rec.priority}
                </div>
                <div className="flex-1 pb-4 border-b border-gray-100 last:border-0">
                  <div className="font-medium text-gray-900 text-sm">{rec.action}</div>
                  <div className="text-sm text-gray-500 mt-1">{rec.why}</div>
                  <div className="text-xs font-medium text-brand-600 mt-1">⏱ {rec.timeframe}</div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
