import { useMutation, useQuery } from '@tanstack/react-query'
import { billingApi, orgApi } from '../lib/api'

const plans = [
  {
    key: 'basic',
    name: 'Free Audit',
    price: '$0',
    description: 'A sharp operating brief built from connected data.',
    features: ['Business health score', 'Executive summary', 'Top risks and opportunities', 'Core dashboard and connector flow'],
  },
  {
    key: 'pro',
    name: 'Pro Analyst Pod',
    price: '$99/mo',
    description: 'For teams that want live analyst-level depth.',
    features: ['AI drill-down', 'Recurring scans', 'Forecasts', 'Scenario modeling', 'Deeper segmentation'],
  },
  {
    key: 'premium',
    name: 'Premium',
    price: '$299/mo',
    description: 'For hands-on consulting and higher-touch strategy.',
    features: ['Everything in Pro', 'Consulting support', 'Priority implementations', 'Custom playbooks'],
  },
]

export default function Billing() {
  const { data: org } = useQuery({
    queryKey: ['org-me'],
    queryFn: () => orgApi.getMe().then((r) => r.data),
  })

  const checkout = useMutation({
    mutationFn: (plan) => billingApi.checkout(plan).then((r) => r.data),
    onSuccess: (data) => {
      window.location.href = data.checkout_url
    },
  })

  const portal = useMutation({
    mutationFn: () => billingApi.portal().then((r) => r.data),
    onSuccess: (data) => {
      window.location.href = data.portal_url
    },
  })

  return (
    <div className="page-shell">
      <section className="relative overflow-hidden card-surface p-6">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.12),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(15,23,42,0.08),transparent_26%)]" />
        <div className="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="section-kicker">Paywall & Access</div>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Pricing & Feature Gating</h1>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
              Free should feel complete. Pro should feel like a full analyst pod working beside the customer.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-full border border-brand-100 bg-white/80 px-4 py-2 text-sm font-medium text-brand-700 shadow-sm backdrop-blur">
              Current plan: {org?.plan || 'basic'}
            </div>
            {org?.plan && org.plan !== 'basic' && (
              <button className="btn-secondary" onClick={() => portal.mutate()} disabled={portal.isPending}>
                Manage Billing
              </button>
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        {plans.map((plan) => {
          const isCurrent = org?.plan === plan.key
          const isUpgrade = plan.key !== 'basic' && org?.plan !== plan.key
          return (
            <div key={plan.key} className={`group relative overflow-hidden card-surface p-6 ${plan.key === 'pro' ? 'ring-2 ring-brand-500/40' : ''}`}>
              <div className={`absolute inset-x-0 top-0 h-1 ${plan.key === 'pro' ? 'bg-[linear-gradient(90deg,#2563eb_0%,#60a5fa_100%)]' : 'bg-[linear-gradient(90deg,rgba(148,163,184,0.15),rgba(148,163,184,0.55),rgba(148,163,184,0.15))]'}`} />
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-[0.7rem] font-semibold uppercase tracking-[0.22em] text-slate-400">{plan.name}</div>
                  <div className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">{plan.price}</div>
                  <div className="mt-2 text-sm leading-6 text-slate-500">{plan.description}</div>
                </div>
                {plan.key === 'pro' && (
                  <div className="animate-glowPulse rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-brand-700">
                    Recommended
                  </div>
                )}
              </div>
              <div className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <div key={feature} className="flex items-start gap-3 text-sm leading-6 text-slate-600">
                    <div className={`mt-2 h-2.5 w-2.5 rounded-full ${plan.key === 'pro' ? 'bg-brand-500' : plan.key === 'premium' ? 'bg-violet-500' : 'bg-emerald-500'}`} />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8">
                {isCurrent ? (
                  <div className="inline-flex rounded-full border border-emerald-100 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 shadow-sm">
                    Current plan
                  </div>
                ) : isUpgrade ? (
                  <button className="btn-primary w-full justify-center" onClick={() => checkout.mutate(plan.key)} disabled={checkout.isPending}>
                    Upgrade to {plan.name}
                  </button>
                ) : (
                  <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-500 shadow-sm">
                    Included by default
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </section>
    </div>
  )
}
