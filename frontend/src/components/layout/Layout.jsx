import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[linear-gradient(180deg,#fbfdff_0%,#eef3f8_100%)]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-[86rem] px-5 py-6 xl:px-7">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
