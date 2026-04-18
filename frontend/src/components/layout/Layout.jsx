import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[radial-gradient(circle_at_top,rgba(37,99,235,0.10),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(15,23,42,0.08),transparent_24%),linear-gradient(180deg,#f8fafc_0%,#e9eef6_100%)]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-7xl px-6 py-8 xl:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
