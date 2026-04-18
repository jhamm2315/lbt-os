import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { integrationsApi, orgApi } from '../lib/api'

export default function Connections() {
  const qc = useQueryClient()

  const { data: providers = [] } = useQuery({
    queryKey: ['integration-providers'],
    queryFn: () => integrationsApi.providers().then((r) => r.data),
  })
  const { data: connections = [] } = useQuery({
    queryKey: ['integration-connections'],
    queryFn: () => integrationsApi.connections().then((r) => r.data),
  })
  const { data: syncRuns = [] } = useQuery({
    queryKey: ['integration-sync-runs'],
    queryFn: () => integrationsApi.syncRuns().then((r) => r.data),
  })
  const { data: org } = useQuery({
    queryKey: ['org-me'],
    queryFn: () => orgApi.getMe().then((r) => r.data),
  })

  const startOAuth = useMutation({
    mutationFn: (provider) => integrationsApi.startOAuth(provider).then((r) => r.data),
    onSuccess: (data) => {
      window.location.href = data.authorization_url
    },
  })
  const syncAll = useMutation({
    mutationFn: () => integrationsApi.syncAll().then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['integration-sync-runs'] })
      qc.invalidateQueries({ queryKey: ['integration-connections'] })
      qc.invalidateQueries({ queryKey: ['metrics', 30] })
    },
  })
  const syncOne = useMutation({
    mutationFn: (connectionId) => integrationsApi.syncOne(connectionId).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['integration-sync-runs'] })
      qc.invalidateQueries({ queryKey: ['integration-connections'] })
      qc.invalidateQueries({ queryKey: ['metrics', 30] })
    },
  })

  const providerMap = useMemo(
    () => Object.fromEntries(providers.map((provider) => [provider.key, provider])),
    [providers],
  )

  return (
    <div className="page-shell">
      <section className="relative overflow-hidden card-surface p-6">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.10),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(15,23,42,0.08),transparent_26%)]" />
        <div className="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="section-kicker">Connect Data</div>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Integration Pipeline</h1>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
              Connect accounting and CRM systems so LBT OS can ingest raw records, map them into your schema,
              validate the data, and produce a business audit without manual cleanup every time.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button className="btn-secondary" onClick={() => syncAll.mutate()} disabled={syncAll.isPending}>
              {syncAll.isPending ? 'Running sync...' : 'Run Full Sync'}
            </button>
            <div className="rounded-full border border-brand-100 bg-white/80 px-4 py-2 text-sm font-medium text-brand-700 shadow-sm backdrop-blur">
              Plan: {org?.plan || 'basic'}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.08fr_0.92fr]">
        <div className="card-surface p-6">
          <h2 className="text-xl font-semibold tracking-tight text-slate-950">Connector Catalog</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Start with a real OAuth connection. Credentials stay server-side and are encrypted before storage.
          </p>
          <div className="mt-5 space-y-4">
            {providers.map((provider) => {
              const connection = connections.find((item) => item.provider === provider.key)
              return (
                <div key={provider.key} className="group relative overflow-hidden rounded-[1.65rem] border border-slate-200 bg-[linear-gradient(180deg,rgba(248,250,252,0.95)_0%,rgba(255,255,255,0.95)_100%)] p-5 shadow-[0_18px_40px_-34px_rgba(15,23,42,0.45)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_28px_60px_-36px_rgba(15,23,42,0.42)]">
                  <div className="absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(37,99,235,0.75),transparent)] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div className="flex items-center gap-3">
                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#dbeafe_0%,#bfdbfe_100%)] text-lg text-brand-700 shadow-inner">
                          {provider.category === 'accounting' ? '◫' : '◎'}
                        </div>
                        <div className="text-lg font-semibold text-slate-950">{provider.label}</div>
                      </div>
                      <div className="mt-1 text-sm leading-6 text-slate-500">{provider.description}</div>
                      <div className="mt-3 inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 shadow-sm">
                        {provider.category}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-3">
                      {connection ? (
                        <>
                          <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
                            Connected
                          </span>
                          <button
                            className="btn-primary"
                            onClick={() => syncOne.mutate(connection.id)}
                            disabled={syncOne.isPending}
                          >
                            Sync Now
                          </button>
                        </>
                      ) : (
                        <button
                          className="btn-primary"
                          onClick={() => startOAuth.mutate(provider.key)}
                          disabled={startOAuth.isPending}
                        >
                          Connect {provider.label}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="card-surface p-6">
          <h2 className="text-xl font-semibold tracking-tight text-slate-950">Visible Ingestion Flow</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            This is the pipeline we show the customer so the data journey stays transparent.
          </p>
          <div className="mt-5 space-y-3">
            {[
              ['Raw source data', 'Contacts, deals, invoices, purchases, and company records are pulled directly from the source system.'],
              ['Mapped fields', 'Provider fields are translated into your internal schema for leads, customers, sales, and expenses.'],
              ['Validation errors', 'Missing IDs, empty names, negative amounts, and unsupported shapes are flagged before they hit the dashboard.'],
              ['Cleaned records', 'Normalized rows are written into tenant-scoped tables with consistent categories and timestamps.'],
              ['Final dashboard output', 'Metrics, analyst brief, and AI audit layers read from the standardized tables.'],
            ].map(([title, detail], idx) => (
              <div key={title} className="rounded-[1.3rem] border border-slate-200 bg-white/92 px-4 py-4 shadow-[0_14px_30px_-28px_rgba(15,23,42,0.35)]">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[linear-gradient(135deg,#2563eb_0%,#1d4ed8_100%)] text-sm font-semibold text-white shadow-[0_14px_28px_-18px_rgba(37,99,235,0.75)]">{idx + 1}</div>
                  <div className="text-sm font-semibold text-slate-900">{title}</div>
                </div>
                <div className="mt-3 text-sm leading-6 text-slate-500">{detail}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[1.08fr_0.92fr]">
        <div className="card-surface p-6">
          <h2 className="text-xl font-semibold tracking-tight text-slate-950">Schema Mapper</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Every provider has a different shape. We normalize those shapes into the LBT OS operating schema below.
          </p>
          <div className="mt-5 space-y-4">
            {providers.map((provider) => (
              <div key={provider.key} className="rounded-[1.4rem] border border-slate-200 bg-slate-50/80 p-4 shadow-[0_16px_32px_-28px_rgba(15,23,42,0.28)]">
                <div className="text-sm font-semibold text-slate-950">{provider.label}</div>
                <div className="mt-3 space-y-2">
                  {(provider.schema_mapping || []).map((mapping, idx) => (
                    <div key={`${provider.key}-${mapping.raw_object}`} className="rounded-xl border border-white bg-white px-4 py-3 shadow-[0_12px_24px_-22px_rgba(15,23,42,0.25)]">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">{idx + 1}</div>
                          <div className="text-sm font-medium text-slate-900">{mapping.raw_object}</div>
                        </div>
                        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-700">
                          {mapping.mapped_table}
                        </div>
                      </div>
                      <div className="mt-2 text-sm leading-6 text-slate-500">
                        Key fields: {(mapping.key_fields || []).join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card-surface p-6">
          <h2 className="text-xl font-semibold tracking-tight text-slate-950">Recent Sync Activity</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            Run logs make the pipeline debuggable without exposing secrets.
          </p>
          <div className="mt-5 space-y-3">
            {syncRuns.length === 0 ? (
              <div className="rounded-[1.35rem] border border-dashed border-slate-200 bg-slate-50/80 p-4 text-sm leading-6 text-slate-500">
                No syncs yet. Connect a provider and run the first import to populate this feed.
              </div>
            ) : (
              syncRuns.slice(0, 8).map((run) => (
                <div key={run.id} className="rounded-[1.35rem] border border-slate-200 bg-slate-50/80 p-4 shadow-[0_14px_30px_-28px_rgba(15,23,42,0.3)]">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-semibold text-slate-900">{providerMap[run.provider]?.label || run.provider}</div>
                    <StatusBadge status={run.status} />
                  </div>
                  <div className="mt-2 text-sm leading-6 text-slate-500">
                    Trigger: {run.trigger_source} · Imported: {Object.entries(run.stats || {}).map(([key, value]) => `${key} ${value}`).join(', ') || 'No counts yet'}
                  </div>
                  {run.error && <div className="mt-2 text-sm leading-6 text-rose-600">{run.error}</div>}
                </div>
              ))
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

function StatusBadge({ status }) {
  const styles = {
    success: 'bg-emerald-50 text-emerald-700 shadow-[0_10px_24px_-18px_rgba(16,185,129,0.8)]',
    partial: 'bg-amber-50 text-amber-700 shadow-[0_10px_24px_-18px_rgba(245,158,11,0.8)]',
    running: 'bg-blue-50 text-blue-700 shadow-[0_10px_24px_-18px_rgba(37,99,235,0.75)]',
    failed: 'bg-rose-50 text-rose-700 shadow-[0_10px_24px_-18px_rgba(244,63,94,0.75)]',
  }
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${styles[status] || 'bg-slate-100 text-slate-600'}`}>
      {status}
    </span>
  )
}
