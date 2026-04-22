import { Link, useLocation } from 'react-router-dom'

export default function NotFound() {
  const { pathname } = useLocation()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 text-center">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-brand-50 text-3xl font-bold text-brand-600">
        404
      </div>
      <h1 className="text-xl font-semibold text-slate-900">Page not found</h1>
      <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
        <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs">{pathname}</code>{' '}
        doesn't exist. Check the URL or head back to the dashboard.
      </p>
      <div className="mt-6 flex gap-3">
        <Link to="/app" className="btn-primary">Go to dashboard</Link>
        <Link to="/" className="btn-secondary">Marketing home</Link>
      </div>
    </div>
  )
}
