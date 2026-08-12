import type { ReactNode } from 'react'

interface PageHeaderProps {
  eyebrow?: string
  title: string
  description?: string
  action?: ReactNode
}

export function PageHeader({ eyebrow, title, description, action }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-4 mb-8 flex-wrap">
      <div>
        {eyebrow && (
          <p className="text-xs font-mono uppercase tracking-widest text-denim mb-2">{eyebrow}</p>
        )}
        <h1 className="font-display text-[28px] leading-tight text-ink">{title}</h1>
        {description && <p className="text-sm text-ink-soft mt-1.5 max-w-xl">{description}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  )
}
