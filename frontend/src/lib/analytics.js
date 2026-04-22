const BASE_URL = import.meta.env.VITE_API_URL || ''
const VISITOR_KEY = 'lbt_visitor_id'
const SESSION_KEY = 'lbt_session_id'

function randomId(prefix) {
  const cryptoId = window.crypto?.randomUUID?.()
  if (cryptoId) return `${prefix}_${cryptoId}`
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2)}`
}

function storedId(key, prefix, storage = window.localStorage) {
  try {
    const existing = storage.getItem(key)
    if (existing) return existing
    const id = randomId(prefix)
    storage.setItem(key, id)
    return id
  } catch {
    return randomId(prefix)
  }
}

export function getVisitorContext() {
  return {
    visitor_id: storedId(VISITOR_KEY, 'vis'),
    session_id: storedId(SESSION_KEY, 'ses', window.sessionStorage),
  }
}

export function trackVisitorEvent(eventType, metadata = {}, options = {}) {
  if (typeof window === 'undefined') return

  const payload = {
    event_type: eventType,
    ...getVisitorContext(),
    path: options.path || `${window.location.pathname}${window.location.search}`,
    source: options.source || 'frontend',
    metadata,
    occurred_at: new Date().toISOString(),
  }
  const body = JSON.stringify(payload)
  const url = `${BASE_URL}/api/v1/visitor-events`

  if (navigator.sendBeacon && options.beacon !== false) {
    const blob = new Blob([body], { type: 'application/json' })
    if (navigator.sendBeacon(url, blob)) return
  }

  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
    keepalive: true,
  }).catch(() => {})
}

