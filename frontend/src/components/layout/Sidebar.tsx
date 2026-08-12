import { BookMarked, LayoutGrid, MessagesSquare, UploadCloud } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Overview', icon: LayoutGrid, end: true },
  { to: '/chat', label: 'Ask', icon: MessagesSquare, end: false },
  { to: '/library', label: 'Library', icon: BookMarked, end: false },
  { to: '/upload', label: 'Upload', icon: UploadCloud, end: false },
]

export function Sidebar() {
  return (
    <aside className="hidden md:flex flex-col w-60 shrink-0 border-r border-paper-line bg-paper h-screen sticky top-0">
      <div className="px-5 pt-6 pb-5 border-b border-paper-line">
        <div className="flex items-center gap-2">
          <div className="relative h-8 w-8 shrink-0">
            <div className="absolute inset-0 rounded bg-ink" />
            <div className="absolute left-[3px] top-[3px] right-[7px] bottom-[3px] rounded-[2px] bg-paper" />
            <div className="absolute right-0 top-0 bottom-0 w-[6px] rounded-r bg-highlighter" />
          </div>
          <div>
            <p className="font-display text-base leading-none text-ink">Marginal</p>
            <p className="text-[11px] text-ink-faint mt-0.5">study on your own materials</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `group flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? 'bg-ink text-paper font-medium'
                  : 'text-ink-soft hover:bg-ink/[0.05] hover:text-ink'
              }`
            }
          >
            <item.icon className="h-4 w-4" strokeWidth={1.9} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 pb-5">
        <div className="rounded-card border border-paper-line bg-white p-3.5">
          <p className="text-xs font-medium text-ink mb-1">Course library</p>
          <p className="text-[11px] text-ink-soft leading-relaxed">
            Answers are generated only from what you've uploaded, with page citations attached.
          </p>
        </div>
      </div>
    </aside>
  )
}
