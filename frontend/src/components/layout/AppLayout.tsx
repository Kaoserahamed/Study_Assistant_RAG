import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { MobileNav } from './MobileNav'

export function AppLayout() {
  return (
    <div className="min-h-screen flex bg-paper">
      <Sidebar />
      <div className="flex-1 min-w-0 pb-16 md:pb-0">
        <Outlet />
      </div>
      <MobileNav />
    </div>
  )
}
