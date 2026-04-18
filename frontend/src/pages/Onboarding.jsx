import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUser, useAuth } from '@clerk/clerk-react'
import { useMutation } from '@tanstack/react-query'
import { orgApi, setAuthToken } from '../lib/api'

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
  const navigate      = useNavigate()
  const { user }      = useUser()
  const { getToken }  = useAuth()

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
    onSuccess: () => navigate('/app'),
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
              {create.isError && (
                <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
                  {create.error?.response?.data?.detail || 'Could not connect to backend. Is it running on port 8002?'}
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
