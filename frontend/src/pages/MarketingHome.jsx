import { Link } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'

const proof = [
  'Connect QuickBooks and CRM tools',
  'Clean and map business data automatically',
  'Get a dashboard that tells owners what to do next',
]

const trustStrip = [
  'QuickBooks',
  'HubSpot',
  'Stripe',
  'Supabase',
]

const productMoments = [
  {
    title: 'Raw source data',
    detail: 'Invoices, purchases, contacts, and deals land in one stream instead of scattered tools.',
  },
  {
    title: 'Schema mapping',
    detail: 'Provider-specific fields get normalized into leads, customers, sales, and expenses.',
  },
  {
    title: 'Audit output',
    detail: 'The dashboard returns a health score, plain-English summary, risks, and next actions.',
  },
]

const analystCards = [
  {
    label: 'Biggest concern',
    value: 'Follow-up speed is leaking warm demand before quotes turn into closed work.',
  },
  {
    label: 'Best opportunity',
    value: 'Referral leads are producing the highest-margin revenue and deserve more investment.',
  },
  {
    label: 'This week',
    value: 'Clear the overdue lead queue and inspect materials spend before margin slips further.',
  },
]

const freeVsPro = [
  {
    title: 'Free',
    subtitle: 'Your business audit',
    bullets: [
      'Health score, summary, top risks, and top opportunities',
      'Schema-aware dashboard from connected systems',
      'A clean operating brief for owners who need clarity fast',
    ],
  },
  {
    title: 'Pro',
    subtitle: 'Your analyst team on demand',
    bullets: [
      'AI drill-down on root causes and recurring scans',
      'Forecasting, scenario modeling, and deeper segmentation',
      'Monitoring that feels like multiple analysts watching the business together',
    ],
  },
]

export default function MarketingHome() {
  const { isSignedIn } = useAuth()
  const primaryHref = isSignedIn ? '/app' : '/sign-up'
  const secondaryHref = isSignedIn ? '/app/connections' : '/sign-in'

  return (
    <div className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,rgba(37,99,235,0.14),transparent_22%),radial-gradient(circle_at_bottom_right,rgba(15,23,42,0.08),transparent_25%),linear-gradient(180deg,#f8fafc_0%,#e8edf5_100%)] text-slate-950">
      <div className="absolute inset-x-0 top-0 h-[36rem] bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.18),transparent_30%),radial-gradient(circle_at_left,rgba(255,255,255,0.6),transparent_35%)] pointer-events-none" />

      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6 xl:px-8">
        <div>
          <Link to="/" className="text-xl font-semibold tracking-tight text-slate-950">LBT OS</Link>
          <div className="mt-1 text-[11px] font-medium uppercase tracking-[0.22em] text-slate-500">Lean Business Tracker</div>
        </div>
        <div className="hidden items-center gap-8 text-sm font-medium text-slate-600 md:flex">
          <a href="#how-it-works" className="transition-colors hover:text-slate-950">How It Works</a>
          <a href="#pricing" className="transition-colors hover:text-slate-950">Free vs Pro</a>
          <a href="#security" className="transition-colors hover:text-slate-950">Security</a>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/sign-in" className="btn-secondary">Sign In</Link>
          <Link to={primaryHref} className="btn-primary">Get My Business Audit</Link>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-7xl px-6 pb-24 pt-6 xl:px-8">
        <section className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="animate-riseIn">
            <div className="inline-flex rounded-full border border-brand-100 bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-brand-700 shadow-sm backdrop-blur">
              Business audit software
            </div>
            <h1 className="mt-6 max-w-3xl text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl xl:text-[4.35rem] xl:leading-[0.95]">
              Connect your business data. Get a clear audit in minutes.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
              LBT OS pulls in accounting and CRM data, cleans it, and turns it into one dashboard with a health score, key risks, and next steps.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to={primaryHref} className="btn-primary px-5 py-3 text-base">Get My Business Audit</Link>
              <Link to={secondaryHref} className="btn-secondary px-5 py-3 text-base">
                {isSignedIn ? 'Open Product Workspace' : 'See The Product'}
              </Link>
            </div>
            <div className="mt-8 space-y-3">
              {proof.map((item) => (
                <div key={item} className="flex items-start gap-3 text-sm leading-6 text-slate-600">
                  <div className="mt-2 h-2.5 w-2.5 rounded-full bg-brand-500 shadow-[0_0_18px_rgba(37,99,235,0.55)]" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
            <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-3 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
              {trustStrip.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-8 rounded-[2.8rem] bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.22),transparent_34%),radial-gradient(circle_at_bottom_left,rgba(15,23,42,0.2),transparent_32%)] blur-3xl" />
            <div className="relative overflow-hidden rounded-[2.2rem] border border-white/70 bg-[linear-gradient(180deg,#08101d_0%,#0f172a_58%,#162340_100%)] p-5 shadow-[0_45px_110px_-52px_rgba(15,23,42,0.95)]">
              <div className="rounded-[1.7rem] border border-white/10 bg-[radial-gradient(circle_at_top_right,rgba(96,165,250,0.24),transparent_28%),linear-gradient(135deg,#0f172a_0%,#111827_48%,#1d4ed8_100%)] p-5 text-white">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="text-[0.68rem] font-semibold uppercase tracking-[0.26em] text-blue-100/55">Analyst Brief Preview</div>
                    <div className="mt-2 text-2xl font-semibold tracking-tight">6ix Bio Composites Inc</div>
                    <div className="mt-2 text-sm leading-6 text-blue-100/72">Connected accounting and CRM activity.</div>
                  </div>
                  <div className="rounded-[1.25rem] border border-white/15 bg-white/10 px-4 py-3 text-right backdrop-blur">
                    <div className="text-[11px] uppercase tracking-[0.18em] text-blue-100/58">Health Score</div>
                    <div className="mt-1 text-4xl font-semibold tracking-tight">81</div>
                    <div className="text-sm text-blue-100/72">Strong</div>
                  </div>
                </div>

                <div className="mt-5 rounded-[1.45rem] border border-white/10 bg-white/10 p-4 text-sm leading-7 text-blue-50/88">
                  Revenue is steady, but profit can improve if the team fixes follow-up speed and protects the best lead sources.
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  {analystCards.map((item) => (
                    <div key={item.label} className="rounded-[1.25rem] border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                      <div className="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-blue-100/50">{item.label}</div>
                      <div className="mt-3 text-sm leading-6 text-white">{item.value}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-[1.08fr_0.92fr]">
                <div className="rounded-[1.6rem] border border-white/70 bg-white/94 p-5 shadow-[0_20px_45px_-35px_rgba(15,23,42,0.45)]">
                  <div className="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-slate-400">Pipeline Visibility</div>
                  <div className="mt-4 space-y-3">
                    {productMoments.map((item, idx) => (
                      <div key={item.title} className="rounded-[1.15rem] border border-slate-200 bg-slate-50/90 p-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[linear-gradient(135deg,#2563eb_0%,#1d4ed8_100%)] text-sm font-semibold text-white shadow-[0_12px_24px_-14px_rgba(37,99,235,0.7)]">
                            {idx + 1}
                          </div>
                          <div className="text-sm font-semibold text-slate-950">{item.title}</div>
                        </div>
                        <div className="mt-3 text-sm leading-6 text-slate-500">{item.detail}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-[1.6rem] border border-white/70 bg-white/94 p-5 shadow-[0_20px_45px_-35px_rgba(15,23,42,0.45)]">
                  <div className="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-slate-400">What You Get</div>
                  <div className="mt-4 space-y-3">
                    {[
                      'A dashboard that explains the business in plain English',
                      'A clean connection flow for QuickBooks and CRM systems',
                      'A free audit with Pro reserved for deeper analysis and monitoring',
                    ].map((item) => (
                      <div key={item} className="rounded-[1.15rem] border border-brand-100 bg-brand-50/60 p-4 text-sm leading-6 text-slate-700">
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="mt-24 grid gap-5 lg:grid-cols-[0.78fr_1.22fr] lg:items-start">
          <div className="pt-2">
            <div className="section-kicker">How It Works</div>
            <h2 className="mt-3 max-w-lg text-3xl font-semibold tracking-tight text-slate-950">
              From sign-in to business audit.
            </h2>
            <p className="mt-4 max-w-md text-sm leading-7 text-slate-600">
              Connect the tools, clean the data, compute the metrics, and return a dashboard the owner can use right away.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {[
              ['1. Sign up', 'The user lands on a polished page, sees the dashboard preview, and starts with a single CTA.'],
              ['2. Connect systems', 'QuickBooks and CRM connectors bring in real operating records without manual exports.'],
              ['3. Schema match', 'Provider fields are mapped into leads, customers, sales, and expenses.'],
              ['4. Validate + clean', 'Bad shapes and missing values are flagged before they distort the dashboard.'],
              ['5. Compute KPIs', 'Metrics and operating patterns are calculated from the normalized tables.'],
              ['6. Return the audit', 'The owner gets an analyst-style summary, risks, opportunities, and next actions.'],
            ].map(([title, detail]) => (
              <div key={title} className="glass-panel p-5">
                <div className="text-lg font-semibold tracking-tight text-slate-950">{title}</div>
                <div className="mt-2 text-sm leading-7 text-slate-600">{detail}</div>
              </div>
            ))}
          </div>
        </section>

        <section id="pricing" className="mt-24 grid gap-5 xl:grid-cols-2">
          {freeVsPro.map((item, idx) => (
            <div key={item.title} className={`card-surface p-6 ${idx === 1 ? 'ring-2 ring-brand-500/30' : ''}`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="section-kicker">{item.title}</div>
                  <h3 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">{item.subtitle}</h3>
                </div>
                {idx === 1 && (
                  <div className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-brand-700">
                    Premium motion
                  </div>
                )}
              </div>
              <div className="mt-6 space-y-3">
                {item.bullets.map((bullet) => (
                  <div key={bullet} className="flex items-start gap-3 text-sm leading-7 text-slate-600">
                    <div className={`mt-2 h-2.5 w-2.5 rounded-full ${idx === 1 ? 'bg-brand-500' : 'bg-emerald-500'}`} />
                    <span>{bullet}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>

        <section id="security" className="mt-24 overflow-hidden rounded-[2rem] border border-slate-200 bg-[linear-gradient(135deg,#ffffff_0%,#f8fafc_55%,#dbeafe_100%)] p-6 shadow-[0_30px_80px_-44px_rgba(15,23,42,0.45)]">
          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
            <div>
              <div className="section-kicker">Security & Trust</div>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
                Secure by design.
              </h2>
              <p className="mt-4 max-w-lg text-sm leading-7 text-slate-600">
                Tokens stay server-side, credentials are encrypted, and imported data is validated before it reaches the dashboard.
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {[
                'Encrypted integration credentials',
                'Server-side OAuth token exchange',
                'Org-scoped queries and RLS support',
                'Validation before normalization',
                'Sync logs without exposing secrets',
                'A paywall that gates advanced AI features cleanly',
              ].map((item) => (
                <div key={item} className="rounded-[1.3rem] border border-white/80 bg-white/80 p-4 text-sm leading-6 text-slate-700 shadow-[0_14px_34px_-28px_rgba(15,23,42,0.32)] backdrop-blur">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
