import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth, SignIn, SignUp } from '@clerk/clerk-react'
import { setAuthToken } from './lib/api'
import Layout from './components/layout/Layout'
import MarketingHome from './pages/MarketingHome'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Sales from './pages/Sales'
import Customers from './pages/Customers'
import Expenses from './pages/Expenses'
import AIInsights from './pages/AIInsights'
import Onboarding from './pages/Onboarding'
import Connections from './pages/Connections'
import Billing from './pages/Billing'

function AuthSync() {
  const { getToken, isSignedIn } = useAuth()

  useEffect(() => {
    if (!isSignedIn) return
    const sync = async () => {
      const token = await getToken()
      setAuthToken(token)
    }
    sync()
    const interval = setInterval(sync, 55_000)
    return () => clearInterval(interval)
  }, [getToken, isSignedIn])

  return null
}

function RequireAuth({ children }) {
  const { isLoaded, isSignedIn } = useAuth()
  if (!isLoaded) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-400 text-sm">
        Loading...
      </div>
    )
  }
  if (!isSignedIn) return <Navigate to="/sign-in" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthSync />
      <Routes>
        <Route path="/" element={<MarketingHome />} />

        {/* Clerk auth pages — hash routing avoids redirect loop in dev */}
        <Route
          path="/sign-in"
          element={
            <div className="flex h-screen items-center justify-center bg-gray-50">
              <SignIn
                routing="hash"
                afterSignInUrl="/onboarding"
                signUpUrl="/sign-up"
              />
            </div>
          }
        />
        <Route
          path="/sign-up"
          element={
            <div className="flex h-screen items-center justify-center bg-gray-50">
              <SignUp
                routing="hash"
                afterSignUpUrl="/onboarding"
                signInUrl="/sign-in"
              />
            </div>
          }
        />

        {/* Onboarding — shown once after first sign-up */}
        <Route
          path="/onboarding"
          element={<RequireAuth><Onboarding /></RequireAuth>}
        />

        {/* Main app */}
        <Route path="/app" element={<RequireAuth><Layout /></RequireAuth>}>
          <Route index element={<Dashboard />} />
          <Route path="connections" element={<Connections />} />
          <Route path="leads" element={<Leads />} />
          <Route path="sales" element={<Sales />} />
          <Route path="customers" element={<Customers />} />
          <Route path="expenses" element={<Expenses />} />
          <Route path="insights" element={<AIInsights />} />
          <Route path="billing" element={<Billing />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
