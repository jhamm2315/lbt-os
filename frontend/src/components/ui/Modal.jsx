import { useEffect } from 'react'

export default function Modal({ open, onClose, title, children, size = 'md' }) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [open])

  if (!open) return null

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-md" onClick={onClose} />
      <div className={`relative w-full overflow-y-auto rounded-[1.75rem] border border-white/70 bg-white/92 shadow-[0_35px_90px_-40px_rgba(15,23,42,0.65)] ${sizes[size]} max-h-[90vh] animate-riseIn`}>
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5">
          <div>
            <div className="section-kicker">Editor</div>
            <h2 className="mt-2 text-lg font-semibold text-slate-900">{title}</h2>
          </div>
          <button
            onClick={onClose}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-xl leading-none text-slate-400 transition-all duration-300 hover:-translate-y-0.5 hover:text-slate-700"
          >
            ×
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}
