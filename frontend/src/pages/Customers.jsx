import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { customersApi } from '../lib/api'
import DataTable from '../components/ui/DataTable'
import Modal from '../components/ui/Modal'
import { format } from 'date-fns'

const TAGS = ['loyal', 'vip', 'at_risk', 'inactive', 'new']
const EMPTY_FORM = { name: '', email: '', phone: '', address: '', tags: [], notes: '' }

export default function Customers() {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const qc = useQueryClient()

  const { data: customers = [] } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.list({ limit: 100 }).then((r) => r.data),
  })

  const save = useMutation({
    mutationFn: (d) => editing ? customersApi.update(editing.id, d) : customersApi.create(d),
    onSuccess: () => { qc.invalidateQueries(['customers']); closeModal() },
  })

  const openNew  = () => { setEditing(null); setForm(EMPTY_FORM); setOpen(true) }
  const openEdit = (row) => { setEditing(row); setForm({ ...row, tags: row.tags || [] }); setOpen(true) }
  const closeModal = () => { setOpen(false); setEditing(null) }

  const toggleTag = (t) => {
    setForm((f) => ({ ...f, tags: f.tags.includes(t) ? f.tags.filter((x) => x !== t) : [...f.tags, t] }))
  }

  const columns = [
    { key: 'name',            label: 'Name',          render: (v) => <span className="font-medium">{v}</span> },
    { key: 'phone',           label: 'Phone' },
    { key: 'total_orders',    label: 'Orders' },
    { key: 'lifetime_value',  label: 'LTV',           render: (v) => `$${Number(v).toLocaleString()}` },
    { key: 'last_purchase_at',label: 'Last Purchase',  render: (v) => v ? format(new Date(v), 'MMM d, yyyy') : '—' },
    { key: 'tags',            label: 'Tags',          render: (v) => (v || []).map((t) => (
      <span key={t} className="badge bg-gray-100 text-gray-600 mr-1">{t}</span>
    ))},
  ]

  const totalLTV = customers.reduce((s, c) => s + (c.lifetime_value || 0), 0)
  const repeatPct = customers.length ? (customers.filter((c) => c.total_orders > 1).length / customers.length * 100).toFixed(0) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Customers</h1>
        <button className="btn-primary" onClick={openNew}>+ Add Customer</button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Total Customers</div>
          <div className="text-xl font-bold">{customers.length}</div>
        </div>
        <div className="card p-4">
          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Total LTV</div>
          <div className="text-xl font-bold">${totalLTV.toLocaleString()}</div>
        </div>
        <div className="card p-4">
          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Repeat Rate</div>
          <div className="text-xl font-bold">{repeatPct}%</div>
        </div>
      </div>

      <DataTable columns={columns} data={customers} onRowClick={openEdit} emptyMessage="No customers yet. Convert a lead or add one manually." />

      <Modal open={open} onClose={closeModal} title={editing ? 'Edit Customer' : 'Add Customer'}>
        <form onSubmit={(e) => { e.preventDefault(); save.mutate(form) }} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Name *</label>
              <input required className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div>
              <label className="label">Address</label>
              <input className="input" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">Tags</label>
            <div className="flex gap-2 flex-wrap mt-1">
              {TAGS.map((t) => (
                <button
                  key={t} type="button"
                  className={`badge text-sm cursor-pointer border transition-colors ${form.tags.includes(t) ? 'bg-brand-500 text-white border-brand-500' : 'bg-gray-50 text-gray-600 border-gray-200 hover:border-brand-300'}`}
                  onClick={() => toggleTag(t)}
                >{t}</button>
              ))}
            </div>
          </div>
          <div>
            <label className="label">Notes</label>
            <textarea rows={2} className="input" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button type="button" className="btn-secondary" onClick={closeModal}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
