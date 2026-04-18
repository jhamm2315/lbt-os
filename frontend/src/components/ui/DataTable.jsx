export default function DataTable({ columns, data, onRowClick, emptyMessage = 'No data yet.' }) {
  if (!data?.length) {
    return (
      <div className="card p-12 text-center text-sm text-slate-400">{emptyMessage}</div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-[linear-gradient(180deg,#f8fafc_0%,#f1f5f9_100%)]">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3.5 text-left text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500"
                  style={{ width: col.width }}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((row, i) => (
              <tr
                key={row.id || i}
                onClick={() => onRowClick?.(row)}
                className={`${onRowClick ? 'cursor-pointer hover:bg-brand-50/45' : ''} transition-colors duration-200`}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3.5 text-slate-700">
                    {col.render ? col.render(row[col.key], row) : (row[col.key] ?? '—')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
