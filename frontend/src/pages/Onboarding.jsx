import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUser, useAuth } from '@clerk/clerk-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { orgApi, setAuthToken } from '../lib/api'
import { trackVisitorEvent } from '../lib/analytics'

const INDUSTRY_OPTIONS = [
  { key: 'hvac',        label: 'HVAC',         icon: '❄️' },
  { key: 'plumbing',    label: 'Plumbing',      icon: '🔧' },
  { key: 'electrician', label: 'Electrician',   icon: '⚡' },
  { key: 'landscaping', label: 'Landscaping',   icon: '🌿' },
  { key: 'cleaning_service', label: 'Cleaning', icon: '🧼' },
  { key: 'gig_worker',  label: 'Gig Worker',    icon: '🛵' },
  { key: 'salon_spa',   label: 'Salon / Spa',   icon: '✨' },
  { key: 'restaurant',  label: 'Restaurant',    icon: '🍽️' },
  { key: 'gym',         label: 'Gym / Fitness', icon: '💪' },
  { key: 'real_estate', label: 'Real Estate',   icon: '🏠' },
  { key: 'other',       label: 'Other',         icon: '💼' },
]

export default function Onboarding() {
  const [step, setStep]         = useState(0)
  const [industry, setIndustry] = useState('')
  const [orgName, setOrgName]   = useState('')
  const [city, setCity]         = useState('Denver')
  const [replaceExistingDemo, setReplaceExistingDemo] = useState(false)
  const navigate      = useNavigate()
  const { user }      = useUser()
  const { getToken }  = useAuth()

  useEffect(() => {
    setReplaceExistingDemo(false)
  }, [industry])

  useEffect(() => {
    trackVisitorEvent('page_view', {
      page: 'onboarding',
      signed_in: Boolean(user?.id),
    })
  }, [user?.id])

  const submittedInfo = (mode) => ({
    page: 'onboarding',
    mode,
    clerk_user_id: user?.id || null,
    business_name: orgName || user?.fullName || 'My Business',
    industry: industry === 'other' ? null : industry,
    city,
    state: 'CO',
  })

  const { data: template } = useQuery({
    queryKey: ['industry-template', industry],
    queryFn: () => orgApi.getTemplate(industry).then((r) => r.data),
    enabled: Boolean(industry) && industry !== 'other',
  })

  const create = useMutation({
    mutationFn: async () => {
      // Always get a fresh token right before the call — avoids race with AuthSync
      const token = await getToken()
      setAuthToken(token)
      return orgApi.create({
        name:     orgName || user?.fullName || 'My Business',
        industry: industry === 'other' ? null : industry,
        city,
        state: 'CO',
      })
    },
    onSuccess: () => {
      trackVisitorEvent('info_submitted', submittedInfo('create_workspace'))
      navigate('/app')
    },
  })

  const launchDemo = useMutation({
    mutationFn: async () => {
      const token = await getToken()
      setAuthToken(token)
      return orgApi.bootstrapDemo({
        industry,
        name: orgName || undefined,
        city,
        state: 'CO',
        replace_existing: replaceExistingDemo,
      })
    },
    onSuccess: () => {
      trackVisitorEvent('info_submitted', submittedInfo('launch_demo'))
      navigate('/app')
    },
  })

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-5/12 bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex-col justify-between p-10">
        <div>
          <div className="text-white text-2xl font-bold tracking-tight">LBT OS</div>
          <div className="text-blue-300 text-sm mt-1">Lean Business Tracker</div>
        </div>
        <div className="space-y-6">
          <h1 className="text-white text-4xl font-bold leading-tight">
            Run your business<br />smarter.
          </h1>
          <p className="text-blue-200 text-base leading-relaxed">
            Track leads, revenue, and expenses in one place — then let AI tell you exactly where you're losing money.
          </p>
          <div className="space-y-3 pt-2">
            {['Lead & sales pipeline tracking', 'Real-time profit dashboard', 'AI-powered revenue audit', 'Built for Denver businesses'].map((f) => (
              <div key={f} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center shrink-0">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-blue-100 text-sm">{f}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="text-blue-400 text-xs">Built by Aera Analytics · Denver, CO</div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center bg-gray-50 p-6">
        <div className="w-full max-w-md">

          {/* Progress */}
          <div className="flex items-center gap-2 mb-8">
            {['Industry', 'Details'].map((label, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-colors ${i <= step ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'}`}>
                  {i < step ? (
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : i + 1}
                </div>
                <span className={`text-sm font-medium ${i <= step ? 'text-gray-800' : 'text-gray-400'}`}>{label}</span>
                {i < 1 && <div className={`h-px w-8 mx-1 ${step > i ? 'bg-blue-600' : 'bg-gray-200'}`} />}
              </div>
            ))}
          </div>

          {step === 0 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">What type of business?</h2>
                <p className="text-gray-500 text-sm mt-1">We'll pre-configure your dashboard and templates.</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {INDUSTRY_OPTIONS.map((opt) => (
                  <button
                    key={opt.key}
                    onClick={() => setIndustry(opt.key)}
                    className={`p-4 rounded-xl border-2 text-left transition-all hover:border-blue-300 hover:bg-blue-50 ${
                      industry === opt.key ? 'border-blue-600 bg-blue-50 shadow-sm' : 'border-gray-200 bg-white'
                    }`}
                  >
                    <div className="text-2xl mb-2">{opt.icon}</div>
                    <div className={`text-sm font-semibold ${industry === opt.key ? 'text-blue-700' : 'text-gray-700'}`}>{opt.label}</div>
                  </button>
                ))}
              </div>
              {industry && industry !== 'other' && template && (
                <div className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white via-blue-50/70 to-slate-50 p-5 shadow-[0_18px_45px_-30px_rgba(37,99,235,0.35)]">
                  <div className="flex flex-col gap-4">
                    <div>
                      <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-blue-600">Template Preview</div>
                      <h3 className="mt-2 text-lg font-semibold text-slate-950">{template.label} starter workspace</h3>
                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        This preview shows how LBT OS will frame your first dashboard, audit, and test data.
                      </p>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3">
                      <PreviewBlock
                        title="Example services"
                        items={template.services?.slice(0, 4)}
                      />
                      <PreviewBlock
                        title="Lead sources"
                        items={template.lead_sources?.slice(0, 4)?.map(formatLabel)}
                      />
                      <PreviewBlock
                        title="KPI focus"
                        items={template.key_metrics?.slice(0, 4)?.map(formatLabel)}
                      />
                    </div>

                    <div className="rounded-2xl border border-white/80 bg-white/80 px-4 py-4">
                      <div className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Quick wins your audit will look for</div>
                      <div className="mt-3 space-y-2">
                        {(template.quick_wins || []).slice(0, 2).map((item) => (
                          <div key={item} className="text-sm leading-6 text-slate-600">
                            {item}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <button
                disabled={!industry}
                onClick={() => setStep(1)}
                className="w-full py-3 rounded-xl bg-blue-600 text-white font-semibold text-sm hover:bg-blue-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Continue →
              </button>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-6">
              <div>
                <button onClick={() => setStep(0)} className="text-sm text-gray-400 hover:text-gray-600 mb-4 flex items-center gap-1">
                  ← Back
                </button>
                <h2 className="text-2xl font-bold text-gray-900">Business details</h2>
                <p className="text-gray-500 text-sm mt-1">You can update these any time.</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Business Name</label>
                  <input
                    autoFocus
                    className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white placeholder:text-gray-400"
                    placeholder={user?.fullName || 'My Business LLC'}
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">City</label>
                  <input
                    className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                  />
                </div>
              </div>
              <button
                onClick={() => create.mutate()}
                disabled={create.isPending}
                className="w-full py-3 rounded-xl bg-blue-600 text-white font-semibold text-sm hover:bg-blue-700 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
              >
                {create.isPending ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    Setting up your dashboard...
                  </>
                ) : 'Launch My Dashboard →'}
              </button>
              {industry && industry !== 'other' && (
                <button
                  onClick={() => launchDemo.mutate()}
                  disabled={launchDemo.isPending}
                  className="w-full py-3 rounded-xl border border-slate-200 bg-white text-slate-800 font-semibold text-sm hover:border-blue-300 hover:text-blue-700 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
                >
                  {launchDemo.isPending ? 'Building demo workspace...' : replaceExistingDemo ? `Replace current data with ${template?.label || 'industry'} demo` : `Launch ${template?.label || 'industry'} demo with sample data`}
                </button>
              )}
              {create.isError && (
                <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
                  {create.error?.response?.data?.detail || 'Could not connect to backend. Is it running on port 8002?'}
                </div>
              )}
              {launchDemo.isError && (
                <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
                  <div>{launchDemo.error?.response?.data?.detail || 'Could not launch the demo workspace.'}</div>
                  {launchDemo.error?.response?.status === 409 && !replaceExistingDemo && (
                    <button
                      onClick={() => setReplaceExistingDemo(true)}
                      className="mt-3 inline-flex rounded-full border border-red-200 bg-white px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-red-700 transition-colors hover:border-red-300 hover:bg-red-100"
                    >
                      Enable demo replacement
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}

function formatLabel(value) {
  return value.replaceAll('_', ' ')
}

function PreviewBlock({ title, items = [] }) {
  return (
    <div className="rounded-2xl border border-white/80 bg-white/80 p-4">
      <div className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">{title}</div>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.map((item) => (
          <span key={item} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700">
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
