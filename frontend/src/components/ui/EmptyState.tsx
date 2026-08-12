import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: ReactNode
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6 border border-dashed border-paper-line rounded-card bg-white/40">
      <div className="h-11 w-11 rounded-full bg-ink/[0.06] flex items-center justify-center mb-4">
        <Icon className="h-5 w-5 text-ink-faint" strokeWidth={1.75} />
      </div>
      <h3 className="font-display text-lg text-ink mb-1">{title}</h3>
      <p className="text-sm text-ink-soft max-w-sm mb-5">{description}</p>
      {action}
    </div>
  )
}
