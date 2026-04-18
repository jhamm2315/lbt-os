import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

// Inject Clerk token on every request
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// ---- Organizations ----
export const orgApi = {
  create: (data)          => api.post('/organizations', data),
  getMe: ()               => api.get('/organizations/me'),
  updateMe: (data)        => api.patch('/organizations/me', data),
  getTemplates: ()        => api.get('/organizations/templates'),
  getTemplate: (industry) => api.get(`/organizations/templates/${industry}`),
}

// ---- Leads ----
export const leadsApi = {
  list:    (params) => api.get('/leads', { params }),
  create:  (data)   => api.post('/leads', data),
  get:     (id)     => api.get(`/leads/${id}`),
  update:  (id, d)  => api.patch(`/leads/${id}`, d),
  delete:  (id)     => api.delete(`/leads/${id}`),
  convert: (id)     => api.post(`/leads/${id}/convert`),
}

// ---- Customers ----
export const customersApi = {
  list:   (params) => api.get('/customers', { params }),
  create: (data)   => api.post('/customers', data),
  get:    (id)     => api.get(`/customers/${id}`),
  update: (id, d)  => api.patch(`/customers/${id}`, d),
  delete: (id)     => api.delete(`/customers/${id}`),
}

// ---- Sales ----
export const salesApi = {
  list:   (params) => api.get('/sales', { params }),
  create: (data)   => api.post('/sales', data),
  get:    (id)     => api.get(`/sales/${id}`),
  update: (id, d)  => api.patch(`/sales/${id}`, d),
  delete: (id)     => api.delete(`/sales/${id}`),
}

// ---- Expenses ----
export const expensesApi = {
  list:   (params) => api.get('/expenses', { params }),
  create: (data)   => api.post('/expenses', data),
  get:    (id)     => api.get(`/expenses/${id}`),
  update: (id, d)  => api.patch(`/expenses/${id}`, d),
  delete: (id)     => api.delete(`/expenses/${id}`),
}

// ---- Metrics ----
export const metricsApi = {
  dashboard:     (days = 30) => api.get('/metrics/dashboard', { params: { days } }),
  revenueTrend:  (weeks = 12) => api.get('/metrics/revenue-trend', { params: { weeks } }),
}

// ---- AI Audit ----
export const auditApi = {
  run:     () => api.post('/audit/run'),
  latest:  () => api.get('/audit/latest'),
  history: () => api.get('/audit/history'),
}

// ---- Billing ----
export const billingApi = {
  checkout: (plan)   => api.post(`/billing/checkout?plan=${plan}`),
  portal:   ()       => api.post('/billing/portal'),
}

// ---- Integrations ----
export const integrationsApi = {
  providers:   () => api.get('/integrations/providers'),
  connections: () => api.get('/integrations/connections'),
  syncRuns:    (limit = 20) => api.get('/integrations/sync-runs', { params: { limit } }),
  startOAuth:  (provider) => api.post(`/integrations/oauth/${provider}/start`),
  syncOne:     (id) => api.post(`/integrations/connections/${id}/sync`),
  syncAll:     () => api.post('/integrations/sync-all'),
}

export default api
