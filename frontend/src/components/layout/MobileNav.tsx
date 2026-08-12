import { BookMarked, LayoutGrid, MessagesSquare, UploadCloud } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Overview', icon: LayoutGrid, end: true },
  { to: '/chat', label: 'Ask', icon: MessagesSquare, end: false },
  { to: '/library', label: 'Library', icon: BookMarked, end: false },
  { to: '/upload', label: 'Upload', icon: UploadCloud, end: false },
]

export function MobileNav() {
  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-paper border-t border-paper-line flex justify-around px-2 py-1.5">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            `flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-md text-[11px] ${
              isActive ? 'text-ink font-medium' : 'text-ink-faint'
            }`
          }
        >
          <item.icon className="h-5 w-5" strokeWidth={1.9} />
          {item.label}
        </NavLink>
      ))}
    </nav>
  )
}
