import { Component } from 'react'
import { Link } from 'react-router-dom'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    // In production wire this to your error reporting service
    if (import.meta.env.DEV) {
      console.error('[ErrorBoundary]', error, info.componentStack)
    }
  }

  render() {
    if (!this.state.error) return this.props.children

    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 text-center">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-rose-100 text-3xl">
          ⚠
        </div>
        <h1 className="text-xl font-semibold text-slate-900">Something went wrong</h1>
        <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
          An unexpected error occurred. Try refreshing the page — if it keeps happening, contact support.
        </p>
        <div className="mt-6 flex gap-3">
          <button
            className="btn-primary"
            onClick={() => { this.setState({ error: null }); window.location.reload() }}
          >
            Refresh page
          </button>
          <Link to="/app" className="btn-secondary" onClick={() => this.setState({ error: null })}>
            Back to dashboard
          </Link>
        </div>
        {import.meta.env.DEV && (
          <pre className="mt-8 max-w-xl overflow-auto rounded-xl bg-slate-100 p-4 text-left text-xs text-slate-600">
            {this.state.error.message}
          </pre>
        )}
      </div>
    )
  }
}
